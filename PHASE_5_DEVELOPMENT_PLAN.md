# Phase 5 开发计划 - 剩余13个插件

## 执行摘要

Phase 5将完成Excel工具箱系统的最后13个插件，使插件总数达到28个（100%完成）。所有插件将遵循统一的PluginLayout组件和5步工作流模式。

## 当前状态

- ✅ **已完成**: 15/28 插件 (53.6%)
- 🔄 **进行中**: Phase 5 开发
- 📋 **待完成**: 13个插件

## Phase 5 插件列表

### 批次1：页眉页脚和水印功能（4个插件）

#### 1. set-header-footer - 设置页眉页脚 ✅
- **状态**: 已创建
- **文件**: 
  - `plugins/set-header-footer/manifest.json` ✅
  - `plugins/set-header-footer/worker.py` ✅
  - `plugins/set-header-footer/index.vue` ✅
- **功能**: 批量设置Excel的页眉页脚，支持文本、页码、日期等元素
- **特性**: 
  - 左中右三个位置独立配置
  - 支持奇偶页设置
  - 特殊代码支持（&D日期、&P页码等）

#### 2. remove-header-footer - 删除页眉页脚 ✅
- **状态**: 已创建
- **文件**:
  - `plugins/remove-header-footer/manifest.json` ✅
  - `plugins/remove-header-footer/worker.py` ✅
  - `plugins/remove-header-footer/index.vue` ✅
- **功能**: 删除Excel的页眉页脚，保留其他打印设置
- **特性**:
  - 检测并显示有页眉页脚的工作表
  - 保留页边距、纸张大小等设置

#### 3. add-watermark - 添加水印 ⏳
- **状态**: 待创建
- **需求**: 需求29
- **功能**: 为Excel添加水印（文本或图片）
- **特性**:
  - 文本水印：字体、颜色、透明度、角度
  - 图片水印：位置、大小、透明度
  - 应用到所有工作表

#### 4. add-image-watermark - 图片添加水印 ⏳
- **状态**: 待创建
- **需求**: 需求30
- **功能**: 为Excel中的图片添加水印
- **特性**:
  - 识别所有嵌入图片
  - 支持文本和图片水印
  - 批量处理

### 批次2：背景和Sheet管理（4个插件）

#### 5. modify-background - 删除或修改背景图片 ⏳
- **状态**: 待创建
- **需求**: 需求31
- **功能**: 删除或替换Excel的背景图片
- **特性**:
  - 检测背景图片
  - 删除模式
  - 替换模式

#### 6. delete-replace-sheet - 删除或替换Sheet ⏳
- **状态**: 待创建
- **需求**: 需求35
- **功能**: 删除或替换Excel的工作表
- **特性**:
  - 显示工作表列表
  - 删除指定工作表
  - 替换工作表
  - 保护最后一个工作表

#### 7. insert-sheet - 插入Sheet ⏳
- **状态**: 待创建
- **需求**: 需求36
- **功能**: 在指定位置插入新工作表
- **特性**:
  - 指定插入位置
  - 自定义工作表名称
  - 批量插入
  - 自动处理名称冲突

#### 8. csv-split - CSV拆分 ⏳
- **状态**: 待创建
- **需求**: 需求33
- **功能**: 将大型CSV文件拆分成多个小文件
- **特性**:
  - 按行数拆分
  - 保留表头
  - 保持编码和分隔符

### 批次3：元数据和保护功能（5个插件）

#### 9. csv-merge - CSV合并 ⏳
- **状态**: 待创建
- **需求**: 需求34
- **功能**: 合并多个CSV文件
- **特性**:
  - 验证列结构一致性
  - 自动去重表头
  - 处理不一致情况

#### 10. clear-metadata - 清空文档元数据 ⏳
- **状态**: 待创建
- **需求**: 需求39
- **功能**: 清空Excel的元数据
- **特性**:
  - 显示当前元数据
  - 清除作者、公司等信息
  - 选择性清除

#### 11. modify-metadata - 修改文档元数据 ⏳
- **状态**: 待创建
- **需求**: 需求40
- **功能**: 修改Excel的元数据
- **特性**:
  - 编辑标题、作者、主题等
  - 格式验证
  - 长度限制

#### 12. manage-protection - 添加或删除保护 ⏳
- **状态**: 待创建
- **需求**: 需求41
- **功能**: 添加或删除Excel的保护设置
- **特性**:
  - 工作簿保护
  - 工作表保护
  - 密码设置
  - 保护选项配置

#### 13. optimize-excel - Excel优化与压缩 ⏳
- **状态**: 待创建
- **需求**: 需求42
- **功能**: 优化和压缩Excel文件
- **特性**:
  - 删除未使用的样式
  - 清理空白单元格
  - 压缩图片
  - 显示优化前后对比

## 开发策略

### 1. 统一模式
所有插件遵循相同的结构：
```
plugins/{plugin-key}/
├── manifest.json    # 插件元数据
├── worker.py        # Python处理脚本
└── index.vue        # Vue UI组件
```

### 2. 代码复用
- 使用 `PluginLayout` 组件
- 使用 `FileUpload` 组件
- 使用 `file-service` 工具函数
- 统一的5步工作流

### 3. Python依赖
主要依赖包：
- `openpyxl` - Excel文件处理
- `Pillow` - 图片处理（水印功能）
- `pandas` - CSV处理

### 4. 开发顺序
1. ✅ 创建manifest.json
2. ✅ 实现worker.py处理逻辑
3. ✅ 创建index.vue UI组件
4. ⏳ 注册到plugins.ts
5. ⏳ 测试功能

## 实施计划

### 第1步：完成批次1（页眉页脚和水印）
- [x] set-header-footer
- [x] remove-header-footer
- [ ] add-watermark
- [ ] add-image-watermark

**预计时间**: 2小时
**代码量**: ~4,000行

### 第2步：完成批次2（背景和Sheet管理）
- [ ] modify-background
- [ ] delete-replace-sheet
- [ ] insert-sheet
- [ ] csv-split

**预计时间**: 2小时
**代码量**: ~4,000行

### 第3步：完成批次3（元数据和保护）
- [ ] csv-merge
- [ ] clear-metadata
- [ ] modify-metadata
- [ ] manage-protection
- [ ] optimize-excel

**预计时间**: 2.5小时
**代码量**: ~5,000行

### 第4步：集成和测试
- [ ] 更新plugins.ts注册所有插件
- [ ] 更新Home.vue菜单
- [ ] 测试所有插件功能
- [ ] 修复发现的问题

**预计时间**: 1小时

## 插件注册模板

每个新插件需要在 `packages/renderer/src/plugins.ts` 中注册：

```typescript
// 导入插件组件
import PluginNamePlugin from '@plugins/plugin-key/index.vue'

// 导入manifest
import pluginNameManifest from '@plugins/plugin-key/manifest.json'

// 导入worker脚本
import pluginNameWorker from '@plugins/plugin-key/worker.py?raw'

// 在plugins数组中添加
{
  metadata: pluginNameManifest,
  component: PluginNamePlugin,
  worker: pluginNameWorker,
  route: `/plugin/${pluginNameManifest.key}`,
  state: PluginState.UNLOADED
}
```

## 质量标准

### 代码质量
- ✅ TypeScript类型安全
- ✅ 统一的代码风格
- ✅ 完整的错误处理
- ✅ 详细的日志记录

### 用户体验
- ✅ 一致的界面设计
- ✅ 清晰的步骤指引
- ✅ 实时进度反馈
- ✅ 友好的错误提示

### 功能完整性
- ✅ 满足所有需求
- ✅ 保留文件格式
- ✅ 统计信息显示
- ✅ 批量处理支持

## 测试计划

### 功能测试
- [ ] 每个插件的基本功能
- [ ] 文件上传和下载
- [ ] 错误处理
- [ ] 边界情况

### 集成测试
- [ ] 插件加载
- [ ] Worker脚本执行
- [ ] Pyodide环境
- [ ] 文件服务

### 用户验收测试
- [ ] 完整工作流
- [ ] 用户体验
- [ ] 性能表现
- [ ] 错误恢复

## 完成标准

Phase 5完成后，系统将达到：
- ✅ 28/28 插件完成（100%）
- ✅ 所有需求实现
- ✅ 统一的UI/UX
- ✅ 完整的文档
- ✅ 可发布状态

## 下一步行动

1. **立即**: 完成剩余11个插件的创建
2. **然后**: 更新插件注册文件
3. **接着**: 执行全面测试
4. **最后**: 创建Phase 5完成报告

## 预期成果

完成Phase 5后：
- **插件总数**: 28个
- **代码总量**: ~28,000行
- **功能覆盖**: 100%需求
- **用户价值**: 完整的Excel工具箱解决方案

---

**创建日期**: 2026年1月15日  
**当前进度**: 2/13 插件已创建  
**预计完成**: 2026年1月15日  
**负责人**: Excel Toolbox Team
