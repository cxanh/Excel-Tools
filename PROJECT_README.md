# Excel工具箱 - 项目架构

一个基于 Electron + Vue3 + Pyodide 的 Excel 处理工具，支持插件化开发。

## 项目结构

```
excel-toolbox/
├── packages/
│   ├── main/              # Electron主进程
│   │   └── index.js       # 主进程入口
│   ├── preload/           # 预加载脚本
│   │   └── index.js       # contextBridge API
│   └── renderer/          # Vue3渲染进程
│       ├── src/
│       │   ├── views/     # 页面组件
│       │   ├── App.vue    # 根组件
│       │   └── main.ts    # 渲染进程入口
│       └── index.html     # HTML模板
├── plugins/               # 插件目录
├── scripts/               # 构建脚本
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript配置
└── vite.config.ts         # Vite配置
```

## 技术栈

- **Electron 27**: 桌面应用框架
- **Vue 3**: 前端框架
- **Vite 5**: 构建工具
- **TypeScript**: 类型系统
- **Ant Design Vue 4**: UI组件库
- **Pyodide 0.24.1**: 浏览器中的Python环境

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

1. 启动Vite开发服务器：
```bash
npm run dev
```

2. 在新终端启动Electron：
```bash
npm run electron:dev
```

### 构建生产版本

```bash
# 构建Vue前端
npm run build

# 构建Electron应用
npm run electron:build
```

## 安全特性

- ✅ contextIsolation: 启用上下文隔离
- ✅ nodeIntegration: 禁用Node集成
- ✅ sandbox: 启用沙箱模式
- ✅ CSP: 内容安全策略

## 开发状态

- [x] 项目基础架构搭建
- [ ] Electron主进程实现
- [ ] Pyodide环境管理
- [ ] 插件系统
- [ ] 功能插件开发

## 许可证

ISC
