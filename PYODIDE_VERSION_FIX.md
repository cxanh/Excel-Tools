# Pyodide 版本不匹配问题修复报告

## 问题描述

项目在运行时出现 Pyodide 版本不匹配错误：
```
Error: Pyodide version does not match: '0.24.1' <==> '0.24.0'
```

## 问题根因

1. **package.json** 中使用了 caret 版本号 `^0.24.0`，允许安装 0.24.x 的任何版本
2. **npm** 自动安装了最新的 0.24.1 版本
3. **代码和文档** 中仍然引用 0.24.0 版本的 URL 和配置
4. **版本不一致** 导致 Pyodide 内部版本检查失败

## 修复方案

### 1. 统一版本到 0.24.1

- ✅ 修改 `package.json`: `"pyodide": "0.24.1"` (使用精确版本)
- ✅ 更新 `ELECTRON_PYODIDE_PACKAGING.md` 中所有 v0.24.0 引用为 v0.24.1
- ✅ 更新 `README.md` 中的版本信息
- ✅ 验证 `package-lock.json` 中版本为 0.24.1

### 2. 创建配置管理系统

- ✅ 创建 `pyodide-config.json` 配置文件
- ✅ 修改 `py.ts` 支持配置文件加载
- ✅ 添加 CDN/本地模式切换功能
- ✅ 实现 fallback 机制（CDN 失败时自动切换到本地）

### 3. 增强错误处理

- ✅ 改进重试机制
- ✅ 添加详细的加载进度回调
- ✅ 实现自动 fallback 到本地资源
- ✅ 提供更清晰的错误信息

## 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `package.json` | 版本号从 `^0.24.0` 改为 `0.24.1` |
| `packages/renderer/src/utils/py.ts` | 添加配置加载、fallback机制 |
| `ELECTRON_PYODIDE_PACKAGING.md` | 所有版本引用更新为 0.24.1 |
| `README.md` | 技术栈版本更新为 0.24.1 |
| `pyodide-config.json` | 新增配置文件 |
| `public/pyodide-config.json` | 前端可访问的配置文件 |

## 配置文件说明

新增的 `pyodide-config.json` 支持以下配置：

```json
{
  "version": "0.24.1",           // Pyodide 版本
  "loadMode": "cdn",             // 加载模式: "cdn" 或 "local"
  "localIndexURL": "/pyodide/v0.24.1/full/",
  "cdnIndexURL": "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
  "fallbackMode": "local",       // 失败时的备用模式
  "retryAttempts": 3,           // 重试次数
  "timeout": 30000              // 超时时间(ms)
}
```

## 测试验证

创建了 `test_pyodide_fix.html` 用于验证修复效果：
- 测试配置文件加载
- 验证 Pyodide 版本一致性
- 检查基本 Python 功能

## 使用建议

1. **版本管理**: 今后更新 Pyodide 版本时，只需修改 `pyodide-config.json` 和 `package.json`
2. **本地部署**: 如需离线使用，将 Pyodide 资源下载到 `public/pyodide/v0.24.1/full/` 目录
3. **性能优化**: 可根据网络情况选择 CDN 或本地模式
4. **监控**: 关注控制台日志，了解加载状态和可能的 fallback 情况

## 预防措施

1. 使用精确版本号而非 caret 版本号
2. 定期检查依赖版本一致性
3. 在 CI/CD 中添加版本一致性检查
4. 文档和代码同步更新版本信息