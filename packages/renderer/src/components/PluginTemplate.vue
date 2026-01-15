<template>
  <div class="plugin-template">
    <!-- Pyodide 加载遮罩层 -->
    <div v-if="pyodideLoading" class="pyodide-loading">
      <div class="loading-content">
        <a-spin size="large" tip="正在初始化 Python 环境，请稍候..." />
        <p class="loading-subtitle">这可能需要几分钟时间，取决于您的网络连接</p>
        <div class="loading-progress" v-if="loadingProgress > 0">
          <a-progress :percent="loadingProgress" :show-info="true" />
        </div>
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
          :tooltip="{ title: '支持 .xlsx, .xlsm 格式' }"
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
              <a-menu-divider />
              <a-menu-item key="help" @click="showHelp">查看帮助</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </div>

    <!-- 步骤指示器 -->
    <a-steps
      :current="currentStep"
      class="steps"
      type="navigation"
      size="small"
    >
      <a-step title="选择文件" description="选择待处理的 Excel 文件" />
      <a-step title="设置规则" description="配置处理规则和选项" />
      <a-step title="其他选项" description="设置额外参数" />
      <a-step title="输出设置" description="配置输出选项" />
      <a-step title="开始处理" description="执行处理任务" />
    </a-steps>

    <!-- 信息提示 -->
    <div class="messages-container">
      <a-alert
        v-if="infoMessage"
        :message="infoMessage"
        type="info"
        show-icon
        closable
        @close="$emit('close-info')"
        class="info-alert"
      />
      <a-alert
        v-if="errorMessage"
        :message="errorMessage"
        type="error"
        show-icon
        closable
        @close="$emit('close-error')"
        class="error-alert"
      />
      <a-alert
        v-if="successMessage"
        :message="successMessage"
        type="success"
        show-icon
        closable
        @close="$emit('close-success')"
        class="success-alert"
      />
    </div>

    <!-- 文件列表表格 -->
    <div class="file-table-container">
      <!-- 文件上传提示 -->
      <div v-if="files.length > 0" class="file-count-tip">
        <a-tag color="blue">{{ files.length }} 个文件已选择</a-tag>
        <span class="file-hint">支持拖拽添加更多文件</span>
      </div>

      <a-table
        :columns="columns"
        :data-source="files"
        :pagination="false"
        bordered
        size="small"
        :row-hoverable="true"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'actions'">
            <a-button
              type="text"
              size="small"
              @click="handleRemoveFile(record.key)"
              style="color: #ff4d4f"
              :tooltip="{ title: '删除文件' }"
            >
              删除
            </a-button>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag
              :color="
                record.status === 'success'
                  ? 'green'
                  : record.status === 'error'
                    ? 'red'
                    : 'blue'
              "
            >
              {{
                record.status === "success"
                  ? "已添加"
                  : record.status === "error"
                    ? "添加失败"
                    : "添加中"
              }}
            </a-tag>
          </template>
        </template>
        <template #empty>
          <!-- 拖拽区域 -->
          <div
            class="drop-area"
            :class="{ 'drop-area-hover': dragActive }"
            @dragover.prevent="dragActive = true"
            @dragleave.prevent="dragActive = false"
            @drop.prevent="dragActive = false"
          >
            <div class="drop-content">
              <div class="drop-icon">
                <a-icon
                  type="cloud-upload"
                  :style="{
                    fontSize: '64px',
                    color: '#165dff',
                    transition: 'all 0.3s ease',
                  }"
                  :class="{ 'drop-icon-hover': dragActive }"
                />
              </div>
              <p class="drop-title">拖拽文件到此处</p>
              <p class="drop-subtitle">或</p>
              <a-button
                type="primary"
                icon="plus"
                @click="handleAddFile"
                :size="'large'"
              >
                选择文件
              </a-button>
              <p class="drop-hint">支持 .xlsx, .xlsm 格式文件，可批量添加</p>
              <p class="drop-warning" v-if="maxFileSize > 0">
                <a-icon
                  type="exclamation-circle"
                  :style="{ marginRight: '4px' }"
                />单个文件大小限制：{{ formatFileSize(maxFileSize) }}
              </p>
            </div>
          </div>
        </template>
      </a-table>
    </div>

    <!-- 底部操作区 -->
    <div class="bottom-bar">
      <div class="progress-section">
        <div class="progress-container" v-if="progress > 0">
          <a-progress :percent="progress" :show-info="true" status="active" />
          <span class="progress-text">{{ progressText }}</span>
        </div>
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
          :loading="isProcessing"
        >
          <template #icon>
            <a-spin v-if="isProcessing" />
            <RightOutlined v-else />
          </template>
          {{ isProcessing ? "处理中..." : "下一步" }}
        </a-button>
      </div>
    </div>

    <!-- 帮助文档模态框 -->
    <a-modal
      v-model:open="helpModalVisible"
      title="使用帮助"
      :footer="null"
      :width="800"
    >
      <div class="help-content">
        <slot name="help-content">
          <p>该插件的帮助文档正在准备中...</p>
        </slot>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import {
  DownOutlined,
  LeftOutlined,
  RightOutlined,
  CloudUploadOutlined,
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
  errorMessage: {
    type: String,
    default: "",
  },
  successMessage: {
    type: String,
    default: "",
  },
  currentStep: {
    type: Number,
    default: 0,
  },
  maxFileSize: {
    type: Number,
    default: 0, // 0表示无限制
  },
  isProcessing: {
    type: Boolean,
    default: false,
  },
  loadingProgress: {
    type: Number,
    default: 0,
  },
  progressText: {
    type: String,
    default: "",
  },
});

const emit = defineEmits([
  "add-file",
  "import-folder",
  "more-action",
  "next-step",
  "prev-step",
  "remove-file",
  "close-info",
  "close-error",
  "close-success",
  "show-help",
]);
const files = ref([]);
const progress = ref(0);
const pyodideLoading = ref(false);
const helpModalVisible = ref(false);
const dragActive = ref(false);

// 对外暴露属性
defineExpose({
  files,
  pyodideLoading,
});

const columns = [
  { title: "序号", dataIndex: "index", key: "index", width: 80 },
  { title: "名称", dataIndex: "name", key: "name", ellipsis: true },
  { title: "状态", dataIndex: "status", key: "status", width: 120 },
  { title: "大小", dataIndex: "size", key: "size", width: 100 },
  { title: "扩展名", dataIndex: "extension", key: "extension", width: 100 },
  { title: "创建时间", dataIndex: "createTime", key: "createTime", width: 180 },
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
  if (key === "help") {
    showHelp();
  } else {
    emit("more-action", key);
  }
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

const showHelp = () => {
  helpModalVisible.value = true;
  emit("show-help");
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};
</script>

<style scoped>
.plugin-template {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  transition: all 0.3s ease;
}

/* 顶部操作栏 */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-wrap: wrap;
  gap: 16px;
}

.plugin-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  flex: 1;
  min-width: 200px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 步骤指示器 */
.steps {
  margin-bottom: 24px;
  background: #fafafa;
  padding: 10px 0;
  border-radius: 8px;
}

.steps :deep(.ant-steps-item-title) {
  font-size: 14px;
  font-weight: 500;
}

.steps :deep(.ant-steps-item-description) {
  font-size: 12px;
  color: #666;
}

/* 信息提示 */
.messages-container {
  margin-bottom: 20px;
}

.info-alert,
.error-alert,
.success-alert {
  margin-bottom: 12px;
}

/* 文件列表表格 */
.file-table-container {
  position: relative;
  min-height: 300px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  transition: all 0.3s ease;
}

/* 文件上传提示 */
.file-count-tip {
  padding: 12px 16px;
  background: #f0f5ff;
  border-bottom: 1px solid #e6f0ff;
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-hint {
  font-size: 12px;
  color: #666;
}

/* 拖拽区域 */
.drop-area {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  padding: 60px 40px;
  transition: all 0.3s ease;
  min-height: 300px;
  cursor: pointer;
}

.drop-area:hover,
.drop-area-hover {
  border-color: #165dff;
  background: linear-gradient(135deg, #f0f7ff 0%, #e6f0ff 100%);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.1);
  transform: translateY(-2px);
}

.drop-area-hover {
  border-width: 3px;
  box-shadow: 0 8px 24px rgba(22, 93, 255, 0.15);
}

.drop-content {
  text-align: center;
}

.drop-icon {
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.drop-area:hover .drop-icon,
.drop-icon-hover {
  transform: scale(1.1) rotate(5deg);
  filter: brightness(1.1);
}

.drop-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.drop-subtitle {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
}

.drop-hint {
  font-size: 12px;
  color: #999;
  margin-top: 20px;
}

.drop-warning {
  font-size: 12px;
  color: #faad14;
  margin-top: 8px;
}

/* 底部操作区 */
.bottom-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
  flex-wrap: wrap;
  gap: 16px;
}

.progress-section {
  flex: 1;
  min-width: 200px;
}

.progress-container {
  margin-bottom: 8px;
}

.progress-text {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.bottom-buttons {
  display: flex;
  gap: 16px;
}

/* Pyodide 加载遮罩层 */
.pyodide-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
  transition: all 0.3s ease;
}

.loading-content {
  text-align: center;
  padding: 50px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  animation: fadeIn 0.3s ease;
}

.loading-progress {
  margin-top: 20px;
  width: 100%;
}

.loading-subtitle {
  margin-top: 16px;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

/* 帮助文档 */
.help-content {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 10px;
}

.help-content h1,
.help-content h2,
.help-content h3 {
  margin: 16px 0 12px 0;
  color: #1a1a1a;
}

.help-content h1 {
  font-size: 20px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
}

.help-content h2 {
  font-size: 18px;
}

.help-content h3 {
  font-size: 16px;
}

.help-content p {
  margin: 8px 0;
  line-height: 1.6;
  color: #444;
}

.help-content ul,
.help-content ol {
  margin: 8px 0;
  padding-left: 24px;
}

.help-content li {
  margin: 4px 0;
  line-height: 1.5;
  color: #444;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .plugin-template {
    padding: 16px;
  }

  .top-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .plugin-title {
    font-size: 18px;
  }

  .action-buttons {
    width: 100%;
    justify-content: flex-start;
  }

  .bottom-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .bottom-buttons {
    width: 100%;
    justify-content: space-between;
  }

  .drop-area {
    padding: 40px 20px;
  }

  .drop-title {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .plugin-template {
    padding: 12px;
  }

  .steps :deep(.ant-steps-item) {
    margin-right: 8px;
  }

  .steps :deep(.ant-steps-item-title) {
    font-size: 12px;
  }

  .steps :deep(.ant-steps-item-description) {
    display: none;
  }

  .file-table-container {
    min-height: 200px;
  }

  .bottom-buttons {
    flex-direction: column;
  }

  .bottom-buttons button {
    width: 100%;
  }
}
</style>
