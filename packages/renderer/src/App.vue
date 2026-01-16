<template>
  <a-layout style="min-height: 100vh">
    <!-- 顶部导航栏 -->
    <a-layout-header
      style="
        background: #fff;
        padding: 0 12px;
        border-bottom: 1px solid #f0f0f0;
        height: 48px;
        line-height: 48px;
      "
    >
      <div class="header-content">
        <div class="logo-section">
          <img src="/asset/excel_icon.webp" width="32" height="32" />
          <div class="logo-text">
            <span class="software-name">Excel工具箱</span>
            <span class="version">v1.0.0</span>
          </div>
        </div>

        <div class="search-box">
          <a-input
            placeholder="请选择一个具体的功能，也可输入关键字搜索!"
            allow-clear
          />
        </div>

        <div class="header-actions">
          <a-button type="default" style="margin-right: 16px"
            >登录/注册</a-button
          >
          <a-button type="text" style="margin-right: 16px"
            ><BellOutlined />
          </a-button>
          <a-button
            type="text"
            style="margin-right: 16px"
            @click="showSettingsModal = true"
            ><SettingOutlined />
          </a-button>
        </div>

        <!-- 窗口控制按钮 -->
        <div class="window-controls">
          <div class="control-btn minimize"></div>
          <div class="control-btn maximize"></div>
          <div class="control-btn close"></div>
        </div>
      </div>
    </a-layout-header>

    <a-layout>
      <!-- 左侧侧边栏 -->
      <a-layout-sider
        width="220"
        style="background: #fff; border-right: 1px solid #f0f0f0"
        :class="{ collapsed: false }"
      >
        <a-menu
          mode="inline"
          :default-selected-keys="['home']"
          :open-keys="openKeys"
          :items="sidebarItems"
          @select="handleSidebarSelect"
          @open-change="handleOpenChange"
          :menu-transition-name="'slide-up'"
          :sub-menu-close-delay="0.2"
          :sub-menu-open-delay="0"
        />
      </a-layout-sider>

      <!-- 主内容区 -->
      <a-layout-content style="background: #f5f5f5; padding: 24px">
        <router-view />
      </a-layout-content>
    </a-layout>

    <!-- 设置弹窗 -->
    <SettingsModal
      v-model:visible="showSettingsModal"
      @save="handleSettingsSave"
    />
  </a-layout>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import SettingsModal from "./components/SettingsModal.vue";
import { SettingOutlined, BellOutlined } from "@ant-design/icons-vue";

const router = useRouter();
const route = useRoute();
const sidebarItems = ref([]);
const showSettingsModal = ref(false);
const openKeys = ref(["excel"]);

// 从本地存储加载展开状态
const loadOpenKeys = () => {
  const savedOpenKeys = localStorage.getItem("excelbox_openKeys");
  if (savedOpenKeys) {
    try {
      const parsedKeys = JSON.parse(savedOpenKeys);
      // 确保excel始终在openKeys中，因为它不应该被折叠
      if (!parsedKeys.includes("excel")) {
        parsedKeys.push("excel");
      }
      openKeys.value = parsedKeys;
    } catch (e) {
      console.error("Failed to parse saved open keys:", e);
    }
  }
};

// 保存展开状态到本地存储
const saveOpenKeys = (keys) => {
  localStorage.setItem("excelbox_openKeys", JSON.stringify(keys));
};

// 侧边栏菜单数据
onMounted(() => {
  // 加载保存的展开状态
  loadOpenKeys();

  sidebarItems.value = [
    { key: "home", icon: "home", label: "首页" },
    {
      key: "excel",
      icon: "file-excel",
      label: "Excel 工具",
      // 确保excel菜单项始终展开
      defaultOpen: true,
      children: [
        // 文件内容分类插件
        {
          key: "content-category",
          icon: "edit",
          label: "文件内容",
          // 添加具体功能子项
          children: [
            { key: "replace-content", label: "按规则修改内容" },
            { key: "import-rules", label: "导入规则修改内容" },
            { key: "generate-from-template", label: "根据模板生成" },
            { key: "replace-picture", label: "替换图片" },
            { key: "delete-pictures", label: "删除图片" },
            { key: "delete-empty-row", label: "删除空白内容" },
            { key: "remove-empty-row", label: "移除空行" },
            { key: "delete-formula", label: "删除公式" },
            { key: "delete-duplicate-rows", label: "删除重复行" },
            { key: "url-to-image", label: "URL转图片" },
          ],
        },
        // 合并拆分分类插件
        {
          key: "merge-category",
          icon: "merge-cells",
          label: "合并拆分",
          children: [
            { key: "merge-excel", label: "合并Excel" },
            { key: "split-excel", label: "拆分Excel" },
            { key: "split-csv", label: "拆分CSV" },
          ],
        },
        // 格式转换分类
        {
          key: "format-category",
          icon: "format-painter",
          label: "格式转换",
          children: [
            { key: "convert-format", label: "转换格式" },
            { key: "delete-macro", label: "删除宏" },
          ],
        },
        // 页眉页脚分类
        {
          key: "header-category",
          icon: "header",
          label: "页眉页脚",
          children: [
            { key: "add-header-footer", label: "添加/修改页眉页脚" },
            { key: "delete-header-footer", label: "删除页眉页脚" },
          ],
        },
        // 文件水印分类
        {
          key: "watermark-category",
          icon: "copyright",
          label: "文件水印",
          children: [{ key: "add-watermark", label: "添加文字水印" }],
        },
        // 工作表处理分类
        {
          key: "sheet-category",
          icon: "table",
          label: "工作表处理",
          children: [{ key: "rename-sheets", label: "重命名工作表" }],
        },
        // 数据提取分类
        {
          key: "extract-category",
          icon: "database",
          label: "数据提取",
          children: [
            { key: "extract-content", label: "提取指定内容" },
            { key: "extract-images", label: "提取图片" },
          ],
        },
        // 文件属性分类
        {
          key: "property-category",
          icon: "info-circle",
          label: "文件属性",
          children: [{ key: "update-file-properties", label: "修改文件属性" }],
        },
        // 新增功能分类
        {
          key: "new-features-category",
          icon: "star",
          label: "新增功能",
          children: [
            { key: "sort-data", label: "排序数据" },
            { key: "filter-data", label: "筛选数据" },
            { key: "add-formula", label: "批量添加公式" },
            { key: "batch-rename", label: "批量重命名文件" },
            { key: "compare-files", label: "比较文件差异" },
            { key: "batch-encrypt", label: "批量加密文件" },
          ],
        },
      ],
    },
  ];
});

const handleSidebarSelect = ({ key }) => {
  if (key === "home") {
    router.push("/");
  } else if (key.includes("-category")) {
    // 如果是分类项，跳转到首页并激活对应标签
    router.push({
      path: "/",
      query: { category: key.replace("-category", "") },
    });
  } else {
    // 如果是具体插件，直接跳转到插件页面
    router.push(`/plugin/${key}`);
  }
};

const handleOpenChange = (keys) => {
  // 确保excel始终在openKeys中，因为它不应该被折叠
  const newOpenKeys = keys.filter((key) => key !== "excel");
  openKeys.value = ["excel", ...newOpenKeys];
  // 保存展开状态
  saveOpenKeys(openKeys.value);
};

// 处理设置保存
const handleSettingsSave = (settings) => {
  console.log("保存设置:", settings);
  // 这里可以将设置保存到本地存储或通过IPC发送到主进程
  // 示例：localStorage.setItem('appSettings', JSON.stringify(settings))
  // 或者使用Electron的IPC：window.electron.ipcRenderer.send('save-settings', settings)
};
</script>

<style scoped>
.header-content {
  display: flex;
  align-items: center;
  height: 48px;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  margin-right: 24px;
}

.logo-text {
  margin-left: 12px;
  display: flex;
  align-items: baseline;
}

.software-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-right: 8px;
}

.version {
  font-size: 12px;
  color: #999;
}

.search-box {
  margin: 0 24px;
  flex: 1;
  max-width: 500px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.window-controls {
  display: flex;
  align-items: center;
}

.control-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-left: 4px;
  transition: background-color 0.2s;
}

.control-btn:hover {
  background-color: #f5f5f5;
}

.control-btn.close:hover {
  background-color: #ff4d4f;
  color: white;
}

.control-btn::before {
  content: "";
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #999;
}

.control-btn.close::before {
  border-radius: 0;
  background-color: #ff4d4f;
  width: 12px;
  height: 12px;
  clip-path: polygon(
    20% 0%,
    0% 20%,
    30% 50%,
    0% 80%,
    20% 100%,
    50% 70%,
    80% 100%,
    100% 80%,
    70% 50%,
    100% 20%,
    80% 0%,
    50% 30%
  );
}

.control-btn.maximize::before {
  border-radius: 0;
  background-color: transparent;
  width: 12px;
  height: 12px;
  border: 2px solid #999;
}

.control-btn.minimize::before {
  border-radius: 0;
  background-color: #999;
  width: 12px;
  height: 2px;
}

/* 去除折叠按钮 */
:deep(.ant-menu-submenu-arrow) {
  display: none !important;
}

/* 调整子菜单样式 */
:deep(.ant-menu-submenu-title) {
  padding-right: 16px !important;
}

/* 动画效果 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
}

.slide-up-enter-to,
.slide-up-leave-from {
  max-height: 1000px;
  overflow: hidden;
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.ant-layout-sider) {
    width: 180px !important;
    min-width: 180px !important;
    max-width: 180px !important;
  }

  :deep(.ant-menu-item) {
    font-size: 12px;
  }

  :deep(.ant-menu-submenu-title) {
    font-size: 12px;
  }
}

@media (max-width: 576px) {
  :deep(.ant-layout-sider) {
    width: 160px !important;
    min-width: 160px !important;
    max-width: 160px !important;
  }
}
</style>
