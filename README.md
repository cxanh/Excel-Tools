# Excel工具箱

一个基于 Electron + Vue3 + Pyodide 的 Excel 处理工具，支持插件化开发。

## 技术栈

- **壳**: Electron 27 + electron-builder
- **渲染**: Vue3 + Vite + Ant Design Vue
- **算法**: pyodide@0.24 (CPython 3.11 WASM)
- **插件**: 热插拔，无需重编主程序

## 目录结构

```
excelbox/
├─ packages/
│  ├─ main/          ‑ Electron 主进程
│  ├─ preload/       ‑ 预加载脚本 (contextBridge)
│  └─ renderer/      ‑ Vue3 前端
├─ plugins/          ‑ 独立插件目录
│  ├─ remove-empty-row/    ‑ 删除空白行插件
│  └─ replace-picture/     ‑ 替换图片插件
├─ scripts/          ‑ 构建脚本
└─ dist/             ‑ 输出目录
```

## 已完成功能

### 1. 项目架构搭建
- ✅ Electron 主进程和渲染进程分离
- ✅ Vue3 + Vite 构建配置
- ✅ Pyodide 集成，支持在浏览器中运行 Python
- ✅ 插件化架构设计

### 2. 基础组件
- ✅ ExcelDrop 拖拽上传组件
- ✅ 主题配置 (主色 #165DFF)
- ✅ 侧边栏菜单和路由

### 3. 插件开发
- ✅ 删除空白行插件
  - 支持拖拽上传 Excel 文件
  - 自动删除所有空白行
  - 显示处理日志
  - 下载处理后的文件

- ✅ 替换图片插件
  - 支持选择 Excel 文件和替换图片
  - 图片预览功能
  - 显示处理日志
  - 下载处理后的文件

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

1. 启动 Vite 开发服务器
```bash
npm run dev
```

2. 在新终端启动 Electron
```bash
npm run electron:dev
```

### 构建生产版本

```bash
# 构建 Vue 前端
npm run build

# 构建 Electron 应用
npm run electron:build
```

### 预编译 Pyodide

```bash
npm run build:py
```

## 插件开发

### 创建新插件

1. 在 `plugins/` 目录下创建新文件夹
2. 添加 `manifest.json` 文件
3. 创建 `index.vue` Vue 组件
4. 创建 `worker.py` Python 脚本

### 插件配置示例

```json
{
  "key": "your-plugin-key",
  "name": "插件名称",
  "icon": "插件图标",
  "description": "插件描述"
}
```

## 注意事项

1. 确保 Python 脚本返回 `output` 字典，包含 `buffer` 和 `logs` 字段
2. 插件 Vue 组件需使用 `ExcelDrop` 组件处理文件上传
3. 处理大文件时建议使用进度条提示
4. 错误信息需显示在日志区，避免主进程崩溃

## 后续规划

1. 完善图片替换功能的 Python 实现
2. 添加更多实用插件（如按规则替换文本、数据统计等）
3. 实现自动更新功能
4. 支持本地 FastAPI 微服务模式
5. 开发插件市场

## 许可证

ISC