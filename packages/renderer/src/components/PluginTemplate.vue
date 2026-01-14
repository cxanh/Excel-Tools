<template>
  <div class="plugin-template">
    <!-- Pyodide 加载遮罩层 -->
    <div v-if="pyodideLoading" class="pyodide-loading">
      <div class="loading-content">
        <a-spin size="large" tip="正在初始化 Python 环境，请稍候..." />
        <p class="loading-subtitle">这可能需要几分钟时间，取决于您的网络连接</p>
      </div>
    </div>

    <!-- 顶部操作栏 -->
    <div class="top-bar">
      <a-button type="default" icon="arrow-left" @click="$router.push('/')">
        返回主面板
      </a-button>
      <h2 class="plugin-title">{{ pluginTitle }}</h2>
      <div class="action-buttons">
        <a-button
          type="primary"
          icon="plus"
          @click="handleAddFile"
          :disabled="pyodideLoading"
        >
          添加文件
        </a-button>
        <a-button
          type="default"
          icon="folder-open"
          @click="handleImportFromFolder"
          :disabled="pyodideLoading"
        >
          从文件夹中导入文件
        </a-button>
        <a-dropdown>
          <a-button type="default" :disabled="pyodideLoading">
            更多 <DownOutlined />
          </a-button>
          <template #overlay>
            <a-menu @click="handleMoreAction">
              <a-menu-item key="paste">从剪贴板读取</a-menu-item>
              <a-menu-item key="clear">清空列表</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </div>

    <!-- 步骤指示器 -->
    <a-steps :current="currentStep" class="steps">
      <a-step title="选择待处理文件" />
      <a-step title="设置处理规则" />
      <a-step title="设置其它选项" />
      <a-step title="设置输出目录" />
      <a-step title="开始处理" />
    </a-steps>

    <!-- 信息提示 -->
    <a-alert
      v-if="infoMessage"
      :message="infoMessage"
      type="info"
      show-icon
      class="info-alert"
    />

    <!-- 文件列表表格 -->
    <div class="file-table-container">
      <a-table
        :columns="columns"
        :data-source="files"
        :pagination="false"
        bordered
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'actions'">
            <a-button
              type="text"
              size="small"
              @click="handleRemoveFile(record.key)"
              style="color: #ff4d4f"
            >
              删除
            </a-button>
          </template>
        </template>
      </a-table>

      <!-- 拖拽区域 -->
      <div v-if="files.length === 0" class="drop-area">
        <div class="drop-content">
          <div class="cross-icon">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
              <line
                x1="16"
                y1="32"
                x2="48"
                y2="32"
                stroke="#d9d9d9"
                stroke-width="2"
              />
              <line
                x1="32"
                y1="16"
                x2="32"
                y2="48"
                stroke="#d9d9d9"
                stroke-width="2"
              />
            </svg>
          </div>
          <p class="drop-text">您可以将待处理内容「拖放」到此处</p>
          <p class="drop-tip">
            如果无法拖动，请查看<a href="#" style="color: #165dff">这里</a
            >或使用右上方「更多」中的从剪贴板自动读取
          </p>
        </div>
      </div>
    </div>

    <!-- 底部操作区 -->
    <div class="bottom-bar">
      <div class="progress-container" v-if="progress > 0">
        <a-progress :percent="progress" :show-info="false" />
      </div>
      <div class="bottom-buttons">
        <a-button
          type="default"
          size="large"
          @click="handlePrevStep"
          :disabled="currentStep === 0 || pyodideLoading"
          style="margin-right: 16px"
        >
          <LeftOutlined /> 上一步
        </a-button>
        <a-button
          type="primary"
          size="large"
          @click="handleNextStep"
          :disabled="files.length === 0 || pyodideLoading"
        >
          下一步 <RightOutlined />
        </a-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, defineExpose } from "vue";
import { useRouter } from "vue-router";
import {
  DownOutlined,
  LeftOutlined,
  RightOutlined,
} from "@ant-design/icons-vue";

const props = defineProps({
  pluginTitle: {
    type: String,
    default: "插件功能",
  },
  infoMessage: {
    type: String,
    default: "",
  },
  currentStep: {
    type: Number,
    default: 0,
  },
});

const emit = defineEmits([
  "add-file",
  "import-folder",
  "more-action",
  "next-step",
  "prev-step",
  "remove-file",
]);
const files = ref([]);
const progress = ref(0);
const pyodideLoading = ref(false);

// 对外暴露属性
defineExpose({
  files,
  pyodideLoading,
});

const columns = [
  { title: "序号", dataIndex: "index", key: "index", width: 80 },
  { title: "名称", dataIndex: "name", key: "name" },
  { title: "路径", dataIndex: "path", key: "path", ellipsis: true },
  { title: "扩展名", dataIndex: "extension", key: "extension", width: 100 },
  { title: "创建时间", dataIndex: "createTime", key: "createTime", width: 180 },
  { title: "修改时间", dataIndex: "modifyTime", key: "modifyTime", width: 180 },
  {
    title: "操作",
    dataIndex: "actions",
    key: "actions",
    width: 120,
    fixed: "right",
  },
];

const handleAddFile = () => {
  emit("add-file");
};

const handleImportFromFolder = () => {
  emit("import-folder");
};

const handleMoreAction = ({ key }) => {
  emit("more-action", key);
};

const handleRemoveFile = (key) => {
  files.value = files.value.filter((file) => file.key !== key);
  emit("remove-file", key);
};

const handleNextStep = () => {
  emit("next-step");
};

const handlePrevStep = () => {
  emit("prev-step");
};
</script>

<style scoped>
.plugin-template {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

/* 顶部操作栏 */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.plugin-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

/* 步骤指示器 */
.steps {
  margin-bottom: 24px;
}

/* 信息提示 */
.info-alert {
  margin-bottom: 20px;
}

/* 文件列表表格 */
.file-table-container {
  position: relative;
  min-height: 300px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  overflow: hidden;
}

/* 拖拽区域 */
.drop-area {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d9d9d9;
  border-radius: 4px;
  background: #fafafa;
}

.drop-content {
  text-align: center;
  padding: 40px;
}

.cross-icon {
  margin-bottom: 16px;
}

.drop-text {
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
}

.drop-tip {
  font-size: 12px;
  color: #999;
}

/* 底部操作区 */
.bottom-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.progress-container {
  flex: 1;
  margin-right: 20px;
}

/* Pyodide 加载遮罩层 */
.pyodide-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(2px);
}

.loading-content {
  text-align: center;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.loading-subtitle {
  margin-top: 16px;
  color: #666;
  font-size: 14px;
  max-width: 300px;
}
</style>
