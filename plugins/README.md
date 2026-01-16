# Excel工具箱插件目录

本目录包含所有Excel工具箱的功能插件。每个插件都是一个独立的模块，提供特定的Excel处理功能。

## 📚 开发文档

- **[插件开发指南](./PLUGIN_DEVELOPMENT_GUIDE.md)** - 详细的插件开发教程和API参考

## 📦 已安装的插件

### Phase 2: 基础数据处理插件 (5/5) ✅

1. **删除空白行** (`remove-empty-row`)
   - 自动识别并删除Excel文件中的所有空白行
   - 支持批量处理多个文件
   - 依赖: openpyxl

2. **删除重复行** (`remove-duplicate-row`)
   - 支持全行比较和指定列比较
   - 可选保留第一次出现或最后一次出现
   - 依赖: openpyxl, pandas

3. **按规则修改内容** (`modify-by-rules`)
   - 支持普通文本替换和正则表达式替换
   - 可指定工作表和列范围
   - 依赖: openpyxl

4. **Excel合并** (`merge-excel`)
   - 支持保留工作表结构合并
   - 支持合并到单个工作表
   - 依赖: openpyxl

5. **Excel拆分** (`split-excel`)
   - 按工作表拆分为独立文件
   - 按行数拆分大文件
   - 依赖: openpyxl

### Phase 3: 图片处理插件 (4/4) ✅

6. **删除Excel图片** (`remove-image`)
   - 删除所有嵌入图片和图表
   - 显示文件大小减小比例
   - 依赖: openpyxl

7. **替换图片** (`replace-image`)
   - 将所有图片替换为指定新图片
   - 保持原有位置和大小
   - 依赖: openpyxl, Pillow

8. **图片地址转图片** (`url-to-image`)
   - 将单元格中的图片URL转换为嵌入图片
   - 支持自定义图片尺寸和位置
   - 自动下载网络图片
   - 依赖: openpyxl, Pillow, requests

9. **提取图片** (`extract-image`)
   - 从Excel中提取所有图片
   - 支持多种命名模式和格式转换
   - 输出为ZIP压缩包
   - 依赖: openpyxl, Pillow

### Phase 4: 高级内容处理插件 (6/6) ✅

10. **删除公式** (`remove-formula`)
   - 删除所有公式，保留计算结果值
   - 保留单元格格式和样式
   - 依赖: openpyxl

11. **根据模板生成Excel** (`generate-from-template`)
   - 基于模板和数据源批量生成文档
   - 支持{{变量名}}占位符
   - 灵活的文件命名规则
   - 依赖: openpyxl, pandas

12. **Excel格式转换** (`format-converter`)
   - 转换为CSV、HTML、JSON格式
   - 支持多种编码和格式选项
   - 批量处理多个工作表
   - 依赖: openpyxl, pandas

13. **导入规则修改内容** (`import-rules`)
   - 从JSON/CSV文件导入规则
   - 批量应用替换规则
   - 支持正则表达式
   - 依赖: openpyxl, pandas

14. **提取指定内容** (`extract-content`)
   - 按条件提取特定内容
   - 支持多种筛选条件
   - 灵活的输出格式
   - 依赖: openpyxl, pandas

15. **删除Excel宏** (`remove-macro`)
   - 删除所有VBA宏代码
   - 生成安全的无宏文件
   - 可选转换为.xlsx格式
   - 依赖: openpyxl

## 🚧 待开发的插件

查看 [DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md) 了解完整的插件开发计划。

### Phase 5: 格式和样式 (0/6)
- 设置页眉页脚
- 删除页眉页脚
- 添加水印
- 图片添加水印
- 删除或修改背景图片
- Excel优化与压缩

### Phase 6: CSV处理和工作表管理 (0/4)
- CSV拆分
- CSV合并
- 删除或替换Sheet
- 插入Sheet

### Phase 7: 元数据和保护 (0/3)
- 清空文档元数据
- 修改文档元数据
- 添加或删除保护

## 🔧 插件结构

每个插件包含以下文件：

```
plugin-name/
├── manifest.json    # 插件配置文件
├── index.vue        # Vue组件界面
└── worker.py        # Python处理脚本
```

## 🚀 快速开始

### 创建新插件

1. 复制现有插件目录作为模板
2. 修改manifest.json配置
3. 实现index.vue界面
4. 编写worker.py处理逻辑
5. 在`packages/renderer/src/plugins.ts`中注册

详细步骤请参考 [插件开发指南](./PLUGIN_DEVELOPMENT_GUIDE.md)。

### 测试插件

1. 启动开发服务器: `npm run dev`
2. 在浏览器中访问插件路由: `/#/plugin/your-plugin-name`
3. 上传测试文件并验证功能

## 📋 插件开发规范

### 命名规范
- 插件key: 小写字母、数字、连字符（例如: `remove-empty-row`）
- 目录名: 与插件key相同
- 文件名: `manifest.json`, `index.vue`, `worker.py`

### 代码规范
- TypeScript: 遵循项目ESLint配置
- Python: 遵循PEP 8规范
- Vue: 使用Composition API和`<script setup>`

### 接口规范
- Worker函数必须命名为`process`
- 输入参数为包含`file`和`params`的字典
- 返回值必须包含`success`、`logs`字段

## 🔍 插件发现机制

插件通过以下方式注册到系统：

1. **静态导入**: 在`packages/renderer/src/plugins.ts`中导入
2. **插件管理器**: 使用`pluginManager.registerPlugin()`注册
3. **路由注册**: 使用`registerPluginRoute()`注册路由
4. **依赖安装**: 自动安装manifest.json中声明的Python依赖

## 📊 插件状态

- **UNLOADED**: 未加载
- **LOADING**: 加载中（安装依赖）
- **LOADED**: 已加载并可用
- **ERROR**: 加载失败

## 🛠️ 可用工具

### Vue组件
- `FileUpload`: 文件上传组件
- Ant Design Vue: 完整的UI组件库

### 工具函数
- `processFile()`: 处理单个文件
- `processBatch()`: 批量处理文件
- `downloadResult()`: 下载处理结果
- `validateFile()`: 验证文件

### Python库
- `openpyxl`: Excel文件处理
- `micropip`: Python包管理
- 其他通过manifest.json声明的依赖

## 📝 贡献指南

1. 遵循插件开发指南
2. 确保代码质量和测试覆盖
3. 更新相关文档
4. 提交前运行lint和测试

## 📞 获取帮助

- 查看 [插件开发指南](./PLUGIN_DEVELOPMENT_GUIDE.md)
- 参考现有插件实现
- 查看 [项目文档](../PROJECT_README.md)

---

**当前进度**: 15/28 插件已完成 (53.6%)  
**最后更新**: 2026-01-15
