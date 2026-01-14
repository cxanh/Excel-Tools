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
      >
        <a-menu
          mode="inline"
          :default-selected-keys="['excel']"
          :items="sidebarItems"
          @select="handleSidebarSelect"
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import SettingsModal from "./components/SettingsModal.vue";
import { SettingOutlined, BellOutlined } from "@ant-design/icons-vue";

const router = useRouter();
const sidebarItems = ref([]);
const showSettingsModal = ref(false);

// 侧边栏菜单数据
onMounted(() => {
  sidebarItems.value = [
    { key: "home", icon: "home", label: "首页" },
    {
      key: "excel",
      icon: "file-excel",
      label: "Excel 工具",
      children: [
        // 文件内容分类插件
        {
          key: "content-category",
          icon: "edit",
          label: "文件内容",
        },
        // 合并拆分分类插件
        {
          key: "merge-category",
          icon: "merge-cells",
          label: "合并拆分",
        },
        // 其他分类（暂时为空，后续可扩展）
        {
          key: "format-category",
          icon: "format-painter",
          label: "格式转换",
        },
        {
          key: "header-category",
          icon: "header",
          label: "页眉页脚",
        },
        {
          key: "watermark-category",
          icon: "copyright",
          label: "文件水印",
        },
        {
          key: "sheet-category",
          icon: "table",
          label: "工作表处理",
        },
        {
          key: "extract-category",
          icon: "database",
          label: "数据提取",
        },
        {
          key: "property-category",
          icon: "info-circle",
          label: "文件属性",
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
</style>
