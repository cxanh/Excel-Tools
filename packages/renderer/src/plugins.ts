// 插件初始化和注册
import { pluginManager, type PluginInstance, PluginState } from './utils/plugin-manager'
import { registerPluginRoute } from './router'

// 导入插件组件
import RemoveEmptyRowPlugin from '@plugins/remove-empty-row/index.vue'
import RemoveDuplicateRowPlugin from '@plugins/remove-duplicate-row/index.vue'
import ModifyByRulesPlugin from '@plugins/modify-by-rules/index.vue'
import MergeExcelPlugin from '@plugins/merge-excel/index.vue'
import SplitExcelPlugin from '@plugins/split-excel/index.vue'
import RemoveImagePlugin from '@plugins/remove-image/index.vue'
import ReplaceImagePlugin from '@plugins/replace-image/index.vue'
import UrlToImagePlugin from '@plugins/url-to-image/index.vue'
import ExtractImagePlugin from '@plugins/extract-image/index.vue'
import RemoveFormulaPlugin from '@plugins/remove-formula/index.vue'
import GenerateFromTemplatePlugin from '@plugins/generate-from-template/index.vue'
import FormatConverterPlugin from '@plugins/format-converter/index.vue'
import ImportRulesPlugin from '@plugins/import-rules/index.vue'
import ExtractContentPlugin from '@plugins/extract-content/index.vue'
import RemoveMacroPlugin from '@plugins/remove-macro/index.vue'
import SetHeaderFooterPlugin from '@plugins/set-header-footer/index.vue'
import RemoveHeaderFooterPlugin from '@plugins/remove-header-footer/index.vue'
import AddWatermarkPlugin from '@plugins/add-watermark/index.vue'
import AddImageWatermarkPlugin from '@plugins/add-image-watermark/index.vue'
import ModifyBackgroundPlugin from '@plugins/modify-background/index.vue'
import DeleteReplaceSheetPlugin from '@plugins/delete-replace-sheet/index.vue'
import InsertSheetPlugin from '@plugins/insert-sheet/index.vue'
import CsvSplitPlugin from '@plugins/csv-split/index.vue'
import CsvMergePlugin from '@plugins/csv-merge/index.vue'
import ClearMetadataPlugin from '@plugins/clear-metadata/index.vue'
import ModifyMetadataPlugin from '@plugins/modify-metadata/index.vue'
import ManageProtectionPlugin from '@plugins/manage-protection/index.vue'
import OptimizeExcelPlugin from '@plugins/optimize-excel/index.vue'

// 导入插件manifest
import removeEmptyRowManifest from '@plugins/remove-empty-row/manifest.json'
import removeDuplicateRowManifest from '@plugins/remove-duplicate-row/manifest.json'
import modifyByRulesManifest from '@plugins/modify-by-rules/manifest.json'
import mergeExcelManifest from '@plugins/merge-excel/manifest.json'
import splitExcelManifest from '@plugins/split-excel/manifest.json'
import removeImageManifest from '@plugins/remove-image/manifest.json'
import replaceImageManifest from '@plugins/replace-image/manifest.json'
import urlToImageManifest from '@plugins/url-to-image/manifest.json'
import extractImageManifest from '@plugins/extract-image/manifest.json'
import removeFormulaManifest from '@plugins/remove-formula/manifest.json'
import generateFromTemplateManifest from '@plugins/generate-from-template/manifest.json'
import formatConverterManifest from '@plugins/format-converter/manifest.json'
import importRulesManifest from '@plugins/import-rules/manifest.json'
import extractContentManifest from '@plugins/extract-content/manifest.json'
import removeMacroManifest from '@plugins/remove-macro/manifest.json'
import setHeaderFooterManifest from '@plugins/set-header-footer/manifest.json'
import removeHeaderFooterManifest from '@plugins/remove-header-footer/manifest.json'
import addWatermarkManifest from '@plugins/add-watermark/manifest.json'
import addImageWatermarkManifest from '@plugins/add-image-watermark/manifest.json'
import modifyBackgroundManifest from '@plugins/modify-background/manifest.json'
import deleteReplaceSheetManifest from '@plugins/delete-replace-sheet/manifest.json'
import insertSheetManifest from '@plugins/insert-sheet/manifest.json'
import csvSplitManifest from '@plugins/csv-split/manifest.json'
import csvMergeManifest from '@plugins/csv-merge/manifest.json'
import clearMetadataManifest from '@plugins/clear-metadata/manifest.json'
import modifyMetadataManifest from '@plugins/modify-metadata/manifest.json'
import manageProtectionManifest from '@plugins/manage-protection/manifest.json'
import optimizeExcelManifest from '@plugins/optimize-excel/manifest.json'

// 导入插件worker脚本
import removeEmptyRowWorker from '@plugins/remove-empty-row/worker.py?raw'
import removeDuplicateRowWorker from '@plugins/remove-duplicate-row/worker.py?raw'
import modifyByRulesWorker from '@plugins/modify-by-rules/worker.py?raw'
import mergeExcelWorker from '@plugins/merge-excel/worker.py?raw'
import splitExcelWorker from '@plugins/split-excel/worker.py?raw'
import removeImageWorker from '@plugins/remove-image/worker.py?raw'
import replaceImageWorker from '@plugins/replace-image/worker.py?raw'
import urlToImageWorker from '@plugins/url-to-image/worker.py?raw'
import extractImageWorker from '@plugins/extract-image/worker.py?raw'
import removeFormulaWorker from '@plugins/remove-formula/worker.py?raw'
import generateFromTemplateWorker from '@plugins/generate-from-template/worker.py?raw'
import formatConverterWorker from '@plugins/format-converter/worker.py?raw'
import importRulesWorker from '@plugins/import-rules/worker.py?raw'
import extractContentWorker from '@plugins/extract-content/worker.py?raw'
import removeMacroWorker from '@plugins/remove-macro/worker.py?raw'
import setHeaderFooterWorker from '@plugins/set-header-footer/worker.py?raw'
import removeHeaderFooterWorker from '@plugins/remove-header-footer/worker.py?raw'
import addWatermarkWorker from '@plugins/add-watermark/worker.py?raw'
import addImageWatermarkWorker from '@plugins/add-image-watermark/worker.py?raw'
import modifyBackgroundWorker from '@plugins/modify-background/worker.py?raw'
import deleteReplaceSheetWorker from '@plugins/delete-replace-sheet/worker.py?raw'
import insertSheetWorker from '@plugins/insert-sheet/worker.py?raw'
import csvSplitWorker from '@plugins/csv-split/worker.py?raw'
import csvMergeWorker from '@plugins/csv-merge/worker.py?raw'
import clearMetadataWorker from '@plugins/clear-metadata/worker.py?raw'
import modifyMetadataWorker from '@plugins/modify-metadata/worker.py?raw'
import manageProtectionWorker from '@plugins/manage-protection/worker.py?raw'
import optimizeExcelWorker from '@plugins/optimize-excel/worker.py?raw'

/**
 * 初始化所有插件
 */
export async function initializePlugins(): Promise<void> {
  console.log('开始初始化插件...')

  // 注册插件列表
  const plugins: PluginInstance[] = [
    {
      metadata: removeEmptyRowManifest,
      component: RemoveEmptyRowPlugin,
      worker: removeEmptyRowWorker,
      route: `/plugin/${removeEmptyRowManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: removeDuplicateRowManifest,
      component: RemoveDuplicateRowPlugin,
      worker: removeDuplicateRowWorker,
      route: `/plugin/${removeDuplicateRowManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: modifyByRulesManifest,
      component: ModifyByRulesPlugin,
      worker: modifyByRulesWorker,
      route: `/plugin/${modifyByRulesManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: mergeExcelManifest,
      component: MergeExcelPlugin,
      worker: mergeExcelWorker,
      route: `/plugin/${mergeExcelManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: splitExcelManifest,
      component: SplitExcelPlugin,
      worker: splitExcelWorker,
      route: `/plugin/${splitExcelManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: removeImageManifest,
      component: RemoveImagePlugin,
      worker: removeImageWorker,
      route: `/plugin/${removeImageManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: replaceImageManifest,
      component: ReplaceImagePlugin,
      worker: replaceImageWorker,
      route: `/plugin/${replaceImageManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: urlToImageManifest,
      component: UrlToImagePlugin,
      worker: urlToImageWorker,
      route: `/plugin/${urlToImageManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: extractImageManifest,
      component: ExtractImagePlugin,
      worker: extractImageWorker,
      route: `/plugin/${extractImageManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: removeFormulaManifest,
      component: RemoveFormulaPlugin,
      worker: removeFormulaWorker,
      route: `/plugin/${removeFormulaManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: generateFromTemplateManifest,
      component: GenerateFromTemplatePlugin,
      worker: generateFromTemplateWorker,
      route: `/plugin/${generateFromTemplateManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: formatConverterManifest,
      component: FormatConverterPlugin,
      worker: formatConverterWorker,
      route: `/plugin/${formatConverterManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: importRulesManifest,
      component: ImportRulesPlugin,
      worker: importRulesWorker,
      route: `/plugin/${importRulesManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: extractContentManifest,
      component: ExtractContentPlugin,
      worker: extractContentWorker,
      route: `/plugin/${extractContentManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: removeMacroManifest,
      component: RemoveMacroPlugin,
      worker: removeMacroWorker,
      route: `/plugin/${removeMacroManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: setHeaderFooterManifest,
      component: SetHeaderFooterPlugin,
      worker: setHeaderFooterWorker,
      route: `/plugin/${setHeaderFooterManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: removeHeaderFooterManifest,
      component: RemoveHeaderFooterPlugin,
      worker: removeHeaderFooterWorker,
      route: `/plugin/${removeHeaderFooterManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: addWatermarkManifest,
      component: AddWatermarkPlugin,
      worker: addWatermarkWorker,
      route: `/plugin/${addWatermarkManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: addImageWatermarkManifest,
      component: AddImageWatermarkPlugin,
      worker: addImageWatermarkWorker,
      route: `/plugin/${addImageWatermarkManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: modifyBackgroundManifest,
      component: ModifyBackgroundPlugin,
      worker: modifyBackgroundWorker,
      route: `/plugin/${modifyBackgroundManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: deleteReplaceSheetManifest,
      component: DeleteReplaceSheetPlugin,
      worker: deleteReplaceSheetWorker,
      route: `/plugin/${deleteReplaceSheetManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: insertSheetManifest,
      component: InsertSheetPlugin,
      worker: insertSheetWorker,
      route: `/plugin/${insertSheetManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: csvSplitManifest,
      component: CsvSplitPlugin,
      worker: csvSplitWorker,
      route: `/plugin/${csvSplitManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: csvMergeManifest,
      component: CsvMergePlugin,
      worker: csvMergeWorker,
      route: `/plugin/${csvMergeManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: clearMetadataManifest,
      component: ClearMetadataPlugin,
      worker: clearMetadataWorker,
      route: `/plugin/${clearMetadataManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: modifyMetadataManifest,
      component: ModifyMetadataPlugin,
      worker: modifyMetadataWorker,
      route: `/plugin/${modifyMetadataManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: manageProtectionManifest,
      component: ManageProtectionPlugin,
      worker: manageProtectionWorker,
      route: `/plugin/${manageProtectionManifest.key}`,
      state: PluginState.UNLOADED
    },
    {
      metadata: optimizeExcelManifest,
      component: OptimizeExcelPlugin,
      worker: optimizeExcelWorker,
      route: `/plugin/${optimizeExcelManifest.key}`,
      state: PluginState.UNLOADED
    }
  ]

  // 注册所有插件
  for (const plugin of plugins) {
    try {
      await pluginManager.registerPlugin(plugin)
      registerPluginRoute(plugin.metadata.key, plugin.component, plugin.worker)
      console.log(`✓ 插件 ${plugin.metadata.name} 注册成功`)
    } catch (error) {
      console.error(`✗ 插件 ${plugin.metadata.name} 注册失败:`, error)
    }
  }

  console.log(`插件初始化完成，共注册 ${pluginManager.getPlugins().length} 个插件`)
}
