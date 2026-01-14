<template>
  <div class="plugin-container">
    <div class="header">
      <a-button type="default" @click="goHome">
        <HomeOutlined /> 返回主页
      </a-button>
      <h2>{{ pluginName }}</h2>
    </div>

    <div class="content">
      <component :is="pluginComponent" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { HomeOutlined } from "@ant-design/icons-vue";

const route = useRoute();
const router = useRouter();
const pluginComponent = ref(null);
const pluginName = ref("");

// 根据插件 key 加载对应的组件
const loadPlugin = async () => {
  const { key } = route.params;
  try {
    // 动态导入插件组件
    const module = await import(`@plugins/${key}/index.vue`);
    pluginComponent.value = module.default;

    // 设置插件名称
    const plugins = [
      { key: "replace-content", name: "按规则修改 Excel 内容" },
      { key: "import-rules", name: "导入 Excel 规则修改 Excel 内容" },
      { key: "generate-from-template", name: "根据模板生成 Excel 文档" },
      { key: "replace-picture", name: "替换 Excel 中的图片" },
      { key: "delete-pictures", name: "删除 Excel 中的图片" },
      { key: "remove-empty-row", name: "删除 Excel 空白内容" },
      { key: "delete-formula", name: "删除 Excel 公式" },
      { key: "delete-duplicate-rows", name: "删除 Excel 重复行" },
      { key: "url-to-image", name: "Excel 中图片地址转为图片" },
      { key: "merge-excel", name: "合并Excel文件" },
    ];
    const plugin = plugins.find((p) => p.key === key);
    if (plugin) {
      pluginName.value = plugin.name;
    }
  } catch (error) {
    console.error("Failed to load plugin:", error);
    router.push("/");
  }
};

// 返回主页
const goHome = () => {
  router.push("/");
};

// 当路由参数变化时重新加载插件
watch(
  () => route.params.key,
  () => {
    loadPlugin();
  },
);

// 初始加载插件
onMounted(() => {
  loadPlugin();
});
</script>

<style scoped>
.plugin-container {
  height: 100%;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.header h2 {
  margin: 0 0 0 16px;
  color: #165dff;
}

.content {
  min-height: 400px;
}
</style>
