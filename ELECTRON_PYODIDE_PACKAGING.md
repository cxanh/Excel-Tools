# Electron 打包与 Pyodide 资源处理方案

## 1. 概述

本文档描述了 ExcelBox 应用中 Electron 打包与 Pyodide 资源处理的方案，包括：
- Pyodide 资源的获取和存放方式
- Electron 打包配置的修改
- Pyodide 加载方式的灵活切换
- 性能优化建议

## 2. Pyodide 资源获取与存放

### 2.1 选择合适的 Pyodide 版本
当前使用的 Pyodide 版本：`0.24.0`

### 2.2 资源获取方式

#### 2.2.1 从官方网站下载
```bash
# 创建存放 Pyodide 资源的目录
mkdir -p public/pyodide/v0.24.0/full

# 下载核心文件
wget -P public/pyodide/v0.24.0/full/ https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide.js
wget -P public/pyodide/v0.24.0/full/ https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide.asm.js
wget -P public/pyodide/v0.24.0/full/ https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide.asm.wasm
wget -P public/pyodide/v0.24.0/full/ https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide_py.tar
```

#### 2.2.2 使用 NPM 包（推荐）
利用已安装的 Pyodide 包：
```bash
# 创建符号链接
ln -s ../node_modules/pyodide/dist public/pyodide
```

### 2.3 资源存放结构
```
public/
├── pyodide/
│   └── v0.24.0/
│       └── full/
│           ├── pyodide.js
│           ├── pyodide.asm.js
│           ├── pyodide.asm.wasm
│           └── pyodide_py.tar
└── asset/
    └── ...
```

## 3. Pyodide 加载方式切换

### 3.1 配置文件设计
创建 `pyodide-config.json` 配置文件：
```json
{
  "loadMode": "local",  // "local" 或 "cdn"
  "localIndexURL": "/pyodide/v0.24.0/full/",
  "cdnIndexURL": "https://cdn.jsdelivr.net/pyodide/v0.24.0/full/"
}
```

### 3.2 修改 PyodideManager 类
```typescript
// 更新 packages/renderer/src/utils/py.ts
class PyodideManager {
  // ...
  private pyodideConfig: any = null;

  private async loadConfig(): Promise<any> {
    if (this.pyodideConfig) return this.pyodideConfig;
    
    try {
      const response = await fetch('/pyodide-config.json');
      this.pyodideConfig = await response.json();
      return this.pyodideConfig;
    } catch (error) {
      console.warn('无法加载 Pyodide 配置，使用默认配置', error);
      return {
        loadMode: 'cdn',
        localIndexURL: '/pyodide/v0.24.0/full/',
        cdnIndexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.0/full/'
      };
    }
  }

  private async doLoadPyodide(): Promise<any> {
    try {
      const config = await this.loadConfig();
      const indexURL = config.loadMode === 'local' 
        ? config.localIndexURL 
        : config.cdnIndexURL;
      
      console.log(`开始加载 Pyodide (${config.loadMode})...`);
      const pyodide = await loadPyodide({
        indexURL: indexURL,
        packages: ['micropip']
      });
      console.log('Pyodide 加载完成');
      return pyodide;
    } catch (error) {
      console.error('Pyodide 加载失败:', error);
      throw new Error('Pyodide 加载失败，请检查网络连接或配置');
    }
  }
  // ...
}
```

### 3.3 用户配置界面
在设置界面添加 Pyodide 加载方式选项：
```vue
<!-- packages/renderer/src/components/SettingsModal.vue -->
<a-form-item label="Pyodide 加载方式">
  <a-radio-group v-model:value="settings.pyodideLoadMode">
    <a-radio value="local">本地资源（离线可用）</a-radio>
    <a-radio value="cdn">CDN 资源（减小安装包体积）</a-radio>
  </a-radio-group>
  <div class="setting-tip">
    本地资源：安装包体积较大，但可离线使用<br>
    CDN 资源：安装包体积较小，但需要网络连接
  </div>
</a-form-item>
```

## 4. Electron 打包配置

### 4.1 修改 electron-builder 配置
创建或修改 `electron-builder.json` 文件：
```json
{
  "appId": "com.excelbox.app",
  "productName": "ExcelBox",
  "directories": {
    "output": "electron-build",
    "app": "."
  },
  "files": [
    "dist/**/*",
    "packages/main/index.js",
    "packages/preload/index.js",
    "package.json",
    "public/pyodide/**/*"  // 包含 Pyodide 资源
  ],
  "win": {
    "target": [
      {
        "target": "nsis",
        "arch": ["x64"]
      }
    ],
    "icon": "public/asset/excel_icon.ico"
  },
  "mac": {
    "target": ["dmg"],
    "icon": "public/asset/excel_icon.icns"
  },
  "linux": {
    "target": ["AppImage", "deb"],
    "icon": "public/asset/excel_icon.png"
  },
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "createDesktopShortcut": true,
    "createStartMenuShortcut": true
  },
  "asar": {
    "unpackDir": ["public/pyodide/**/*"]  // 不压缩 Pyodide 资源
  }
}
```

### 4.2 修改 package.json
```json
{
  "scripts": {
    "electron:build": "cross-env NODE_ENV=production electron-builder -c electron-builder.json"
  },
  "build": {
    "extraResources": [
      {"from": "public/pyodide", "to": "public/pyodide"}
    ]
  }
}
```

## 5. 性能优化建议

### 5.1 预加载 Pyodide
在应用启动时预加载 Pyodide：
```javascript
// packages/renderer/src/main.js
import { PyodideManager } from './utils/py';

// 预加载 Pyodide
window.addEventListener('load', () => {
  console.log('开始预加载 Pyodide...');
  const manager = PyodideManager.getInstance();
  // 只加载配置，不立即初始化 Pyodide
  manager.loadConfig().then(() => {
    console.log('Pyodide 配置加载完成');
  });
});
```

### 5.2 资源压缩与优化
```bash
# 使用 Brotli 压缩 Pyodide 资源
gzip -9 public/pyodide/v0.24.0/full/pyodide.js
gzip -9 public/pyodide/v0.24.0/full/pyodide.asm.js
gzip -9 public/pyodide/v0.24.0/full/pyodide_py.tar

# 重命名压缩文件
mv public/pyodide/v0.24.0/full/pyodide.js.gz public/pyodide/v0.24.0/full/pyodide.js.br
mv public/pyodide/v0.24.0/full/pyodide.asm.js.gz public/pyodide/v0.24.0/full/pyodide.asm.js.br
mv public/pyodide/v0.24.0/full/pyodide_py.tar.gz public/pyodide/v0.24.0/full/pyodide_py.tar.br
```

### 5.3 按需加载依赖
```javascript
// 只安装必要的依赖
const installRequiredPackages = async (pyodide, requiredPackages) => {
  const micropip = pyodide.pyimport('micropip');
  
  // 检查依赖是否已安装
  const installedPackages = new Set(await micropip.list());
  const packagesToInstall = requiredPackages.filter(pkg => !installedPackages.has(pkg));
  
  if (packagesToInstall.length > 0) {
    await micropip.install(packagesToInstall);
  }
};
```

## 6. 测试与验证

### 6.1 本地资源加载测试
```bash
# 构建应用
npm run build

# 启动应用
npm run electron:dev
```

### 6.2 离线功能测试
1. 断开网络连接
2. 启动应用
3. 执行 Excel 处理操作
4. 验证功能正常工作

### 6.3 安装包体积测试
```bash
# 构建安装包
npm run electron:build

# 检查安装包体积
du -h electron-build/*.exe
```

## 7. 方案选择建议

### 7.1 默认方案
推荐使用 **本地资源打包 + CDN 可选** 的方案：
- 默认使用本地资源，确保离线可用
- 提供选项让用户切换到 CDN，减小本地存储空间占用

### 7.2 资源更新策略
1. 应用启动时检查 Pyodide 版本
2. 提示用户是否更新 Pyodide 资源
3. 支持从 CDN 增量更新本地资源

## 8. 实施步骤

### 8.1 短期实施（1-2天）
1. 下载 Pyodide 资源到 `public/pyodide` 目录
2. 修改 `py.ts` 中的 PyodideManager 类，支持本地资源加载
3. 修改 Electron 打包配置，包含 Pyodide 资源
4. 测试本地资源加载功能

### 8.2 中期实施（2-3天）
1. 添加用户配置界面，支持切换 Pyodide 加载方式
2. 实现配置文件的读写功能
3. 优化 Pyodide 加载性能
4. 测试离线功能和 CDN 切换功能

### 8.3 长期实施（3-5天）
1. 实现 Pyodide 资源的自动更新功能
2. 添加资源完整性校验
3. 优化安装包体积
4. 进行全面的性能测试和兼容性测试

## 9. 风险评估

### 9.1 安装包体积增大
- 风险：Pyodide 资源约 50-100 MB，会显著增大安装包体积
- 缓解措施：提供 CDN 选项，让用户选择安装包体积或离线功能

### 9.2 资源加载失败
- 风险：本地资源损坏或 CDN 不可用导致 Pyodide 加载失败
- 缓解措施：实现资源完整性校验和自动回退机制

### 9.3 性能影响
- 风险：Pyodide 初始化时间长，影响用户体验
- 缓解措施：实现预加载和进度提示，优化资源加载顺序

## 10. 结论

采用 **本地资源打包 + CDN 可选** 的方案是最优选择，它平衡了离线可用性和安装包体积。通过合理的配置和优化，可以提供良好的用户体验。

该方案的实施将确保 ExcelBox 应用在各种网络环境下都能正常工作，同时提供灵活的选择让用户根据自己的需求调整使用方式。