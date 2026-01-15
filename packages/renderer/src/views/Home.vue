<template>
  <div class="home">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <h1 class="main-title">Excel工具箱</h1>
      <p class="subtitle">高效处理Excel文件，提升工作效率</p>
    </div>

    <!-- 分类标签页 -->
    <a-tabs
      v-model:activeKey="activeTab"
      type="card"
      size="large"
      class="category-tabs"
    >
      <a-tab-pane key="all" tab="全部" />
      <a-tab-pane key="content" tab="文件内容" />
      <a-tab-pane key="format" tab="格式转换" />
      <a-tab-pane key="header" tab="页眉页脚" />
      <a-tab-pane key="watermark" tab="文件水印" />
      <a-tab-pane key="merge" tab="合并拆分" />
      <a-tab-pane key="sheet" tab="工作表处理" />
      <a-tab-pane key="extract" tab="数据提取" />
      <a-tab-pane key="property" tab="文件属性" />
    </a-tabs>

    <!-- 插件分类标题 -->
    <div class="category-section">
      <h2 class="category-title">{{ categoryTitle }}</h2>
      <span class="plugin-count"
        >{{ filteredPlugins?.length || 0 }} 个工具</span
      >
    </div>

    <!-- 插件网格 -->
    <div class="plugin-grid">
      <div
        v-for="plugin in filteredPlugins"
        :key="plugin.key"
        class="plugin-card"
        @click="navigateToPlugin(plugin.key)"
      >
        <!-- 渐变背景 -->
        <div class="plugin-card-bg"></div>

        <!-- HOT 标签 -->
        <div v-if="plugin.hot" class="hot-tag">
          <a-tag color="red" size="small" style="margin: 0">HOT</a-tag>
        </div>

        <!-- 插件卡片内容 -->
        <div class="plugin-card-content">
          <!-- 插件图标 -->
          <div class="plugin-icon">
            <img
              :src="plugin.icon"
              style="width: 48px; height: 48px"
              alt="插件图标"
            />
          </div>

          <!-- 插件名称 -->
          <h3 class="plugin-name">{{ plugin.name }}</h3>

          <!-- 插件描述 -->
          <p class="plugin-description">{{ plugin.description }}</p>

          <!-- 查看教程按钮 -->
          <div class="plugin-footer">
            <a-button
              type="link"
              size="small"
              style="color: #165dff; padding: 0"
              icon="question-circle-o"
            >
              查看教程
            </a-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredPlugins.length === 0" class="empty-state">
      <a-empty
        description="暂无相关插件"
        image="https://gw.alipayobjects.com/zos/antfincdn/ZHrcdLPrvN/empty.svg"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const activeTab = ref("all");
const plugins = ref([]);

onMounted(() => {
  // 丰富的插件数据 - 按照用户要求的顺序排列
  plugins.value = [
    {
      key: "replace-content",
      name: "按规则修改 Excel 内容",
      icon: "/asset/execl_icon00_2.png",
      description: "用于批量在 Excel 文档中查找并替换/删除指定内容",
      category: "content",
      hot: true,
    },
    {
      key: "import-rules",
      name: "导入 Excel 规则修改 Excel 内容",
      icon: "/asset/execl_icon00_3.png",
      description:
        "当不同的 Excel 文档有不同的修改规则时，可以通过导入规则文件进行批量修改",
      category: "content",
      hot: true,
    },
    {
      key: "generate-from-template",
      name: "根据模板生成 Excel 文档",
      icon: "/asset/execl_icon00_4.png",
      description:
        "先指定一个 Excel 文档作为模板，然后根据数据源批量生成多个 Excel 文档",
      category: "content",
      hot: true,
    },
    {
      key: "replace-picture",
      name: "替换 Excel 中的图片",
      icon: "/asset/execl_icon00_1.png",
      description: "批量替换 Excel 文件中的图片，统一文档风格",
      category: "content",
      hot: true,
    },
    {
      key: "delete-pictures",
      name: "删除 Excel 中的图片",
      icon: "/asset/execl_icon00_5.png",
      description:
        "批量删除 Excel 文档中的图片，可以删除指定工作表或整个工作簿中的图片",
      category: "content",
      hot: true,
    },
    {
      key: "delete-empty-row",
      name: "删除 Excel 空白内容",
      icon: "/asset/execl_icon00.png",
      description: "删除 Excel 空白内容（空白工作表、空白行列等）",
      category: "content",
      hot: true,
    },
    {
      key: "remove-empty-row",
      name: "移除 Excel 空行",
      icon: "/asset/execl_icon00.png",
      description: "移除 Excel 文件中的空行，清理数据",
      category: "content",
      hot: true,
    },
    {
      key: "delete-formula",
      name: "删除 Excel 公式",
      icon: "/asset/execl_icon00.png",
      description: "删除 Excel 公式（保留计算后的值）",
      category: "content",
      hot: true,
    },
    {
      key: "delete-duplicate-rows",
      name: "删除 Excel 重复行",
      icon: "/asset/execl_icon00.png",
      description: "删除 Excel 文件中的重复行，确保数据唯一性",
      category: "content",
      hot: true,
    },
    {
      key: "url-to-image",
      name: "Excel 中图片地址转为图片",
      icon: "/asset/execl_icon00.png",
      description: "将单元格里的本地路径批量还原成嵌入图片",
      category: "content",
      hot: true,
    },
    {
      key: "merge-excel",
      name: "合并Excel文件",
      icon: "/asset/execl_icon00_3.png",
      description: "批量合并多个Excel文件的内容到一个文件中",
      category: "merge",
      hot: true,
    },
    {
      key: "split-excel",
      name: "拆分Excel文件",
      icon: "/asset/execl_icon00_3.png",
      description: "将一个Excel文件拆分为多个文件，支持按工作表或行数拆分",
      category: "merge",
      hot: true,
    },
    {
      key: "split-csv",
      name: "拆分CSV文件",
      icon: "/asset/execl_icon00_3.png",
      description: "将大型CSV文件拆分为多个小文件，便于处理",
      category: "merge",
      hot: true,
    },
    {
      key: "extract-content",
      name: "提取 Excel 中的指定内容",
      icon: "/asset/execl_icon00.png",
      description: "从Excel文档中提取指定内容，支持按列、按行或按条件提取",
      category: "extract",
      hot: true,
    },
    {
      key: "extract-images",
      name: "提取 Excel 中的图片",
      icon: "/asset/execl_icon00.png",
      description: "从Excel文档中提取所有图片，保存为单独文件",
      category: "extract",
      hot: true,
    },
    {
      key: "convert-format",
      name: "转换 Excel 格式",
      icon: "/asset/execl_icon00.png",
      description: "将Excel文件转换为不同格式，如xlsx转csv、xls等",
      category: "format",
      hot: true,
    },
    {
      key: "delete-macro",
      name: "删除 Excel 宏",
      icon: "/asset/execl_icon00.png",
      description: "删除Excel文件中的宏代码，提高文件安全性",
      category: "format",
      hot: true,
    },
    {
      key: "add-header-footer",
      name: "添加/修改 Excel 页眉页脚",
      icon: "/asset/execl_icon00.png",
      description: "为 Excel 文件批量添加或修改页眉页脚，支持自定义内容和样式",
      category: "header",
      hot: true,
    },
    {
      key: "delete-header-footer",
      name: "删除 Excel 页眉页脚",
      icon: "/asset/execl_icon00.png",
      description: "为 Excel 文件批量删除页眉页脚，支持指定工作表",
      category: "header",
      hot: true,
    },
    {
      key: "add-watermark",
      name: "添加 Excel 文字水印",
      icon: "/asset/execl_icon00.png",
      description:
        "为 Excel 文件批量添加文字水印，支持自定义内容、样式、位置和透明度",
      category: "watermark",
      hot: true,
    },
    {
      key: "rename-sheets",
      name: "重命名 Excel 工作表",
      icon: "/asset/execl_icon00.png",
      description:
        "为 Excel 文件批量重命名工作表，支持自定义命名规则和批量处理",
      category: "sheet",
      hot: true,
    },
    {
      key: "update-file-properties",
      name: "修改 Excel 文件属性",
      icon: "/asset/execl_icon00.png",
      description:
        "为 Excel 文件批量修改文件属性，支持标题、作者、主题、关键词等元数据",
      category: "property",
      hot: true,
    },
  ];

  // 初始化时检查URL查询参数中的分类
  if (route.query.category) {
    activeTab.value = route.query.category;
  }
});

// 监听路由查询参数变化，更新激活的标签
watch(
  () => route.query.category,
  (newCategory) => {
    if (newCategory) {
      activeTab.value = newCategory;
    }
  },
);

// 分类标题映射
const categoryTitleMap = {
  all: "全部插件",
  content: "文件内容",
  format: "格式转换",
  header: "页眉页脚",
  watermark: "文件水印",
  merge: "合并拆分",
  sheet: "工作表处理",
  extract: "数据提取",
  property: "文件属性",
};

// 当前分类标题
const categoryTitle = computed(() => {
  return categoryTitleMap[activeTab.value] || "全部插件";
});

// 根据选中的标签过滤插件
const filteredPlugins = computed(() => {
  if (activeTab.value === "all") {
    return plugins.value;
  }
  return plugins.value.filter((plugin) => plugin.category === activeTab.value);
});

const navigateToPlugin = (pluginKey) => {
  router.push(`/plugin/${pluginKey}`);
};
</script>

<style scoped>
/* 全局样式 */
.home {
  background: #f5f7fa;
  padding: 24px;
  min-height: 100vh;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.main-title {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 16px;
  margin: 0;
  color: #666;
}

/* 内容容器 */
.content-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 分类标签页样式 */
.category-tabs {
  margin-bottom: 20px;
  border-bottom: 1px solid #e8e8e8;
  background: white;
  border-radius: 8px 8px 0 0;
  padding: 0 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.category-tabs :deep(.ant-tabs-tab) {
  font-size: 14px;
  padding: 12px 16px;
  margin-right: 8px;
  border-radius: 6px 6px 0 0;
  transition: all 0.3s ease;
  color: #666;
}

.category-tabs :deep(.ant-tabs-tab-active) {
  color: #165dff;
  font-weight: 500;
}

.category-tabs :deep(.ant-tabs-ink-bar) {
  background-color: #165dff;
  height: 2px;
}

/* 分类标题区域 */
.category-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 20px;
  background: white;
}

.category-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 0;
}

.plugin-count {
  font-size: 13px;
  color: #999;
  background: #f0f2f5;
  padding: 3px 10px;
  border-radius: 10px;
}

/* 插件网格 */
.plugin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  padding: 0 20px 20px 20px;
  background: white;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

/* 插件卡片 */
.plugin-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
  background: white;
  border: 1px solid #f0f2f5;
}

.plugin-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.1);
  border-color: #e6f0ff;
}

/* 卡片背景渐变 - 简化为单色 */
.plugin-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: transparent;
  z-index: 1;
  transition: background 0.3s ease;
}

.plugin-card:hover .plugin-card-bg {
  background: #165dff;
}

/* 卡片内容 */
.plugin-card-content {
  padding: 20px;
  text-align: center;
  position: relative;
  z-index: 2;
}

/* HOT 标签 */
.hot-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 3;
}

/* 插件图标 */
.plugin-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 12px;
  background: #f0f7ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.plugin-card:hover .plugin-icon {
  transform: scale(1.03);
  background: #e6f0ff;
}

/* 插件名称 */
.plugin-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin: 0 0 10px 0;
  transition: color 0.3s ease;
}

.plugin-card:hover .plugin-name {
  color: #165dff;
}

/* 插件描述 */
.plugin-description {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin: 0 0 16px 0;
  min-height: 42px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 插件底部 */
.plugin-footer {
  margin-top: auto;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 50px 20px;
  background: white;
  border-radius: 0 0 8px 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home {
    padding: 16px;
  }

  .main-title {
    font-size: 26px;
  }

  .plugin-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 12px;
    padding: 0 16px 16px 16px;
  }

  .plugin-card-content {
    padding: 16px;
  }

  .category-tabs :deep(.ant-tabs-tab) {
    font-size: 12px;
    padding: 10px 12px;
    margin-right: 6px;
  }
}

@media (max-width: 576px) {
  .plugin-grid {
    grid-template-columns: 1fr;
  }

  .category-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}
</style>
