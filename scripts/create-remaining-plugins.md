# 创建剩余插件脚本

## Phase 5 - 剩余11个插件快速创建指南

由于每个插件包含约1000行代码（manifest.json + worker.py + index.vue），手动创建所有插件需要大量时间。

### 已完成的插件（2个）
1. ✅ set-header-footer - 设置页眉页脚
2. ✅ remove-header-footer - 删除页眉页脚

### 待创建的插件（11个）

#### 批次1：水印功能（2个）
3. add-watermark - 添加水印
4. add-image-watermark - 图片添加水印

#### 批次2：背景和Sheet管理（4个）
5. modify-background - 删除或修改背景图片
6. delete-replace-sheet - 删除或替换Sheet
7. insert-sheet - 插入Sheet
8. csv-split - CSV拆分

#### 批次3：元数据和保护功能（5个）
9. csv-merge - CSV合并
10. clear-metadata - 清空文档元数据
11. modify-metadata - 修改文档元数据
12. manage-protection - 添加或删除保护
13. optimize-excel - Excel优化与压缩

### 创建策略

每个插件需要3个文件：

1. **manifest.json** (~20行)
   - 插件元数据
   - 依赖声明
   - 权限配置

2. **worker.py** (~150-200行)
   - Python处理逻辑
   - openpyxl操作
   - 错误处理

3. **index.vue** (~800-900行)
   - PluginLayout组件
   - 5步工作流
   - 表单配置
   - 结果展示

### 快速创建方法

#### 方法1：基于模板复制
使用现有插件作为模板：
- 简单处理：参考 `remove-empty-row`
- 复杂配置：参考 `modify-by-rules`
- 双文件上传：参考 `generate-from-template`

#### 方法2：分批创建
1. 先创建所有manifest.json文件
2. 再创建所有worker.py文件
3. 最后创建所有index.vue文件

#### 方法3：渐进式开发
1. 创建基础结构（manifest + 简单worker）
2. 实现核心功能
3. 完善UI界面
4. 添加高级特性

### 推荐流程

由于时间和复杂度考虑，建议采用以下流程：

1. **现在**: 创建所有插件的manifest.json文件
2. **现在**: 创建所有插件的基础worker.py文件
3. **现在**: 创建所有插件的基础index.vue文件
4. **稍后**: 逐个完善和测试每个插件

这样可以：
- ✅ 快速搭建完整的插件架构
- ✅ 确保所有插件可以被注册和加载
- ✅ 为后续开发提供清晰的框架
- ✅ 允许并行开发和测试

### 下一步

继续创建剩余11个插件的基础文件...
