<template>
  <div class="plugin-container">
    <!-- 插件标题区域 -->
    <div class="plugin-header">
      <h1 class="plugin-title">{{ plugin?.name || "插件详情" }}</h1>
      <p class="plugin-description">{{ plugin?.description || "插件描述" }}</p>
    </div>

    <!-- 插件内容区域 -->
    <div class="plugin-content">
      <!-- 插件组件 -->
      <component
        :is="pluginComponent"
        :key="pluginKey"
        @status-update="handleStatusUpdate"
        @error="handleError"
      />
    </div>

    <!-- 操作状态提示 -->
    <a-notification
      v-model:open="notification.open"
      :type="notification.type"
      :title="notification.title"
      :description="notification.description"
      :duration="3"
      :closable="true"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const pluginKey = computed(() => route.params.key);
const pluginComponent = ref(null);
const plugin = ref(null);
const notification = ref({
  open: false,
  type: "info",
  title: "",
  description: "",
});

// 模拟插件数据
const pluginData = [
  {
    key: "replace-content",
    name: "按规则修改 Excel 内容",
    description: "用于批量在 Excel 文档中查找并替换/删除指定内容",
    component: "ReplaceContent",
  },
  {
    key: "import-rules",
    name: "导入 Excel 规则修改 Excel 内容",
    description:
      "当不同的 Excel 文档有不同的修改规则时，可以通过导入规则文件进行批量修改",
    component: "ImportRules",
  },
  {
    key: "generate-from-template",
    name: "根据模板生成 Excel 文档",
    description:
      "先指定一个 Excel 文档作为模板，然后根据数据源批量生成多个 Excel 文档",
    component: "GenerateFromTemplate",
  },
  {
    key: "replace-picture",
    name: "替换 Excel 中的图片",
    description: "批量替换 Excel 文件中的图片，统一文档风格",
    component: "ReplacePicture",
  },
  {
    key: "delete-pictures",
    name: "删除 Excel 中的图片",
    description:
      "批量删除 Excel 文档中的图片，可以删除指定工作表或整个工作簿中的图片",
    component: "DeletePictures",
  },
  {
    key: "delete-empty-row",
    name: "删除 Excel 空白内容",
    description: "删除 Excel 空白内容（空白工作表、空白行列等）",
    component: "DeleteEmptyRow",
  },
  {
    key: "remove-empty-row",
    name: "移除 Excel 空行",
    description: "移除 Excel 文件中的空行，清理数据",
    component: "RemoveEmptyRow",
  },
  {
    key: "delete-formula",
    name: "删除 Excel 公式",
    description: "删除 Excel 公式（保留计算后的值）",
    component: "DeleteFormula",
  },
  {
    key: "delete-duplicate-rows",
    name: "删除 Excel 重复行",
    description: "删除 Excel 文件中的重复行，确保数据唯一性",
    component: "DeleteDuplicateRows",
  },
  {
    key: "url-to-image",
    name: "Excel 中图片地址转为图片",
    description: "将单元格里的本地路径批量还原成嵌入图片",
    component: "UrlToImage",
  },
  {
    key: "merge-excel",
    name: "合并Excel文件",
    description: "批量合并多个Excel文件的内容到一个文件中",
    component: "MergeExcel",
  },
  {
    key: "split-excel",
    name: "拆分Excel文件",
    description: "将一个Excel文件拆分为多个文件，支持按工作表或行数拆分",
    component: "SplitExcel",
  },
  {
    key: "split-csv",
    name: "拆分CSV文件",
    description: "将大型CSV文件拆分为多个小文件，便于处理",
    component: "SplitCsv",
  },
  {
    key: "extract-content",
    name: "提取 Excel 中的指定内容",
    description: "从Excel文档中提取指定内容，支持按列、按行或按条件提取",
    component: "ExtractContent",
  },
  {
    key: "extract-images",
    name: "提取 Excel 中的图片",
    description: "从Excel文档中提取所有图片，保存为单独文件",
    component: "ExtractImages",
  },
  {
    key: "convert-format",
    name: "转换 Excel 格式",
    description: "将Excel文件转换为不同格式，如xlsx转csv、xls等",
    component: "ConvertFormat",
  },
  {
    key: "delete-macro",
    name: "删除 Excel 宏",
    description: "删除Excel文件中的宏代码，提高文件安全性",
    component: "DeleteMacro",
  },
  {
    key: "add-header-footer",
    name: "添加/修改 Excel 页眉页脚",
    description: "为 Excel 文件批量添加或修改页眉页脚，支持自定义内容和样式",
    component: "AddHeaderFooter",
  },
  {
    key: "delete-header-footer",
    name: "删除 Excel 页眉页脚",
    description: "为 Excel 文件批量删除页眉页脚，支持指定工作表",
    component: "DeleteHeaderFooter",
  },
  {
    key: "add-watermark",
    name: "添加 Excel 文字水印",
    description:
      "为 Excel 文件批量添加文字水印，支持自定义内容、样式、位置和透明度",
    component: "AddWatermark",
  },
  {
    key: "rename-sheets",
    name: "重命名 Excel 工作表",
    description: "为 Excel 文件批量重命名工作表，支持自定义命名规则和批量处理",
    component: "RenameSheets",
  },
  {
    key: "update-file-properties",
    name: "修改 Excel 文件属性",
    description:
      "为 Excel 文件批量修改文件属性，支持标题、作者、主题、关键词等元数据",
    component: "UpdateFileProperties",
  },
  {
    key: "sort-data",
    name: "排序数据",
    description: "对Excel文件中的数据进行排序，支持多种排序规则",
    component: "SortData",
  },
  {
    key: "filter-data",
    name: "筛选数据",
    description: "对Excel文件中的数据进行筛选，提取符合条件的数据",
    component: "FilterData",
  },
  {
    key: "add-formula",
    name: "批量添加公式",
    description: "为Excel文件批量添加公式，提高数据处理效率",
    component: "AddFormula",
  },
  {
    key: "batch-rename",
    name: "批量重命名文件",
    description: "批量重命名Excel文件，支持自定义命名规则",
    component: "BatchRename",
  },
  {
    key: "compare-files",
    name: "比较文件差异",
    description: "比较两个Excel文件的内容差异，高亮显示不同之处",
    component: "CompareFiles",
  },
  {
    key: "batch-encrypt",
    name: "批量加密文件",
    description: "批量加密Excel文件，提高文件安全性",
    component: "BatchEncrypt",
  },
];

// 动态导入插件组件
const loadPluginComponent = async (pluginKey) => {
  try {
    // 动态导入插件组件
    const module = await import(`../plugins/${pluginKey}/index.vue`);
    return module.default;
  } catch (error) {
    console.error("加载插件组件失败:", error);
    return {
      render() {
        return h(
          "div",
          { style: { padding: "20px", textAlign: "center", color: "red" } },
          "插件加载失败",
        );
      },
    };
  }
};

// 计算当前插件
const currentPlugin = computed(() => {
  return pluginData.find((p) => p.key === pluginKey.value) || null;
});

// 处理状态更新
const handleStatusUpdate = (status) => {
  notification.value = {
    open: true,
    type: status.type || "info",
    title: status.title || "操作状态",
    description: status.message || "操作完成",
  };
};

// 处理错误
const handleError = (error) => {
  notification.value = {
    open: true,
    type: "error",
    title: "操作失败",
    description: error.message || "未知错误",
  };
};

onMounted(async () => {
  // 加载插件数据
  plugin.value = currentPlugin.value;
  if (!plugin.value) {
    notification.value = {
      open: true,
      type: "error",
      title: "错误",
      description: "插件不存在",
    };
    // 3秒后返回首页
    setTimeout(() => {
      router.push("/");
    }, 3000);
  } else {
    // 加载插件组件 - 使用更可靠的导入方式
    try {
      // 使用绝对路径导入插件组件
      const pluginPath = `/plugins/${pluginKey.value}/index.vue`;
      const module = await import(/* @vite-ignore */ pluginPath);
      pluginComponent.value = module.default;
    } catch (error) {
      console.error("加载插件组件失败:", error);
      pluginComponent.value = {
        render() {
          return h(
            "div",
            { style: { padding: "20px", textAlign: "center", color: "red" } },
            "插件加载失败",
          );
        },
      };
    }
  }
});
</script>

<style scoped>
.plugin-container {
  min-height: 600px;
}

.plugin-header {
  background: white;
  padding: 24px;
  border-radius: 8px 8px 0 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid #f0f0f0;
}

.plugin-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.plugin-description {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.plugin-content {
  background: white;
  padding: 24px;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  min-height: 400px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .plugin-header,
  .plugin-content {
    padding: 16px;
  }

  .plugin-title {
    font-size: 18px;
  }
}
</style>
