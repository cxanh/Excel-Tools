# Excel 工具箱 (Excel Toolkit Desktop)

功能完备、可执行的桌面端 Excel 工具箱，支持对 Excel 文件进行批量操作、格式转换、图像处理、数据清洗等。

## ✨ 功能特性

- 📁 **文件操作**: 加载、保存、备份、恢复
- ✏️ **内容处理**: 删除空白行、删除公式、删除重复行、内容替换
- 🖼️ **图像处理**: 提取图片、替换图片、添加水印
- 📊 **工作表管理**: 插入、删除、重命名工作表
- 🔀 **合并拆分**: Excel/CSV 文件合并与拆分
- 🔄 **格式转换**: Excel 转 PDF、CSV
- 🔒 **属性管理**: 元数据清理、密码保护、文件优化
- 📦 **批量操作**: 多文件批量处理、任务模板
- ↩️ **预览撤销**: 操作预览、撤销功能

## 🏗️ 技术架构

- **前端**: Electron + Vue 3 + TypeScript + Pinia
- **后端**: Python 3.9+ + openpyxl + pandas + Pillow
- **通信**: JSON over stdin/stdout (长连接模式)
- **打包**: electron-builder + PyInstaller

## 📦 安装依赖

### 前端依赖

```bash
npm install
```

### Python 后端依赖

```bash
cd python-backend
pip install -r requirements.txt
```

## 🚀 开发

### 启动开发服务器

```bash
npm run dev
```

这将同时启动：
- Vite 开发服务器 (前端)
- Electron 主进程
- Python 后端进程

### 代码格式化

```bash
# 前端代码格式化
npm run format
npm run lint

# Python 代码格式化
cd python-backend
black .
flake8 .
```

## 📦 打包

### Windows

```bash
npm run build:win
```

### macOS

```bash
npm run build:mac
```

### Linux

```bash
npm run build:linux
```

## 🧪 测试

详细的测试说明请参考 [TESTING.md](TESTING.md)。

### Python 后端测试

```bash
# 运行单元测试
python -m pytest python-backend/tests/test_cli_router.py -v

# 运行集成测试
python python-backend/tests/test_integration.py
```

### Electron 应用测试

```bash
# 启动应用进行手动测试
npm run dev
```

**测试功能**：
- ✅ 后端启动和连接
- ✅ Ping/Echo 命令通信
- ✅ 实时进度更新
- ✅ 错误处理

## 📁 项目结构

```
excel-toolkit-desktop/
├── electron/              # Electron 主进程和 preload
│   ├── main.ts           # 主进程入口
│   └── preload.ts        # Preload 脚本
├── src/                  # Vue 前端源码
│   ├── App.vue           # 主组件
│   └── main.ts           # 前端入口
├── python-backend/       # Python 后端
│   ├── main.py           # 后端入口
│   ├── cli_router.py     # 命令路由器
│   ├── engine/           # 功能模块
│   │   ├── core/         # 核心模块（加载、保存）
│   │   ├── content/      # 内容处理
│   │   ├── image/        # 图像处理
│   │   ├── sheet/        # 工作表管理
│   │   ├── merge_split/  # 合并拆分
│   │   ├── convert/      # 格式转换
│   │   └── property/     # 属性管理
│   └── requirements.txt  # Python 依赖
├── .kiro/                # Kiro 规格说明
│   └── specs/
│       └── excel-toolkit-desktop/
│           ├── requirements.md  # 需求文档
│           ├── design.md        # 设计文档
│           └── tasks.md         # 任务列表
├── package.json          # Node.js 配置
├── vite.config.ts        # Vite 配置
└── README.md             # 项目说明
```

## 📝 开发指南

详细的开发指南请参考：
- [需求文档](.kiro/specs/excel-toolkit-desktop/requirements.md)
- [设计文档](.kiro/specs/excel-toolkit-desktop/design.md)
- [任务列表](.kiro/specs/excel-toolkit-desktop/tasks.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
