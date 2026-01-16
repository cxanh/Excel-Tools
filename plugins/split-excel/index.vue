<template>
  <PluginLayout
    title="拆分Excel"
    :can-proceed="canProceed"
    :processing="processing"
    @step-change="handleStepChange"
    @next="handleNext"
    @add-files="handleAddFiles"
    @import-from-folder="handleImportFromFolder"
    @clear-all="handleClearAll"
    ref="layoutRef"
  >
    <template #default="{ currentStep }">
      <!-- 步骤 0: 选择待处理文件 -->
      <div v-if="currentStep === 0" class="step-content">
        <a-alert
          message="功能说明"
          description="将大型Excel文件拆分为多个小文件，支持按行数或按工作表拆分。"
          type="info"
          show-icon
          style="margin-bottom: 24px"
        />

        <div class="upload-area">
          <FileUpload
            :multiple="true"
            @change="handleFileChange"
            ref="fileUploadRef"
          />
        </div>

        <div v-if="files.length > 0" class="file-list">
          <a-table
            :columns="fileColumns"
            :data-source="files"
            :pagination="false"
            bordered
          >
            <template #bodyCell="{ column, record, index }">
              <template v-if="column.key === 'index'">{{ index + 1 }}</template>
              <template v-else-if="column.key === 'name'">
                <FileExcelOutlined style="color: #52c41a; margin-right: 8px" />
                {{ record.name }}
              </template>
              <template v-else-if="column.key === 'size'">{{
                formatFileSize(record.size)
              }}</template>
              <template v-else-if="column.key === 'type'">{{
                record.type || "Excel"
              }}</template>
              <template v-else-if="column.key === 'createTime'">{{
                formatDate(record.lastModified)
              }}</template>
              <template v-else-if="column.key === 'modifyTime'">{{
                formatDate(record.lastModified)
              }}</template>
              <template v-else-if="column.key === 'actions'">
                <a-button
                  type="link"
                  size="small"
                  danger
                  @click="removeFile(index)"
                  >移除</a-button
                >
              </template>
            </template>
          </a-table>
        </div>

        <div v-else class="empty-state">
          <a-empty description="请拖放文件到此处或点击上方添加文件按钮" />
        </div>
      </div>

      <!-- 步骤 1: 设置拆分规则 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-card title="拆分规则配置" :bordered="false">
          <a-form layout="vertical">
            <a-form-item label="拆分模式">
              <a-radio-group
                v-model:value="formData.splitMode"
                button-style="solid"
              >
                <a-radio-button value="rows">按行数拆分</a-radio-button>
                <a-radio-button value="sheets">按工作表拆分</a-radio-button>
              </a-radio-group>
            </a-form-item>
            <a-form-item
              v-if="formData.splitMode === 'rows'"
              label="每文件行数"
            >
              <a-input-number
                v-model:value="formData.rowsPerFile"
                :min="1"
                :max="100000"
                style="width: 200px"
              />
              <template #extra>每个文件包含的最大行数</template>
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 2: 开始处理 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-result
          :status="
            processing ? 'info' : results.length > 0 ? 'success' : 'info'
          "
          :title="
            processing
              ? '正在处理...'
              : results.length > 0
                ? '处理完成！'
                : '准备开始处理'
          "
          :sub-title="
            processing
              ? `正在拆分第 ${currentFileIndex + 1} / ${files.length} 个文件`
              : results.length > 0
                ? `成功: ${successCount} / ${results.length}`
                : '点击下方开始处理按钮'
          "
        >
          <template #icon>
            <LoadingOutlined
              v-if="processing"
              spin
              style="font-size: 48px; color: #6366f1"
            />
            <CheckCircleOutlined
              v-else-if="results.length > 0"
              style="font-size: 48px; color: #52c41a"
            />
            <FileExcelOutlined v-else style="font-size: 48px; color: #6366f1" />
          </template>
          <template #extra>
            <a-button
              v-if="!processing && results.length === 0"
              type="primary"
              size="large"
              @click="startProcessing"
            >
              开始处理
            </a-button>
          </template>
        </a-result>

        <div v-if="processing || results.length > 0" style="margin-top: 32px">
          <a-card title="处理详情" :bordered="false">
            <a-list :data-source="results" :loading="processing">
              <template #renderItem="{ item, index }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #title>
                      <span>{{ files[index]?.name }}</span>
                      <a-tag
                        :color="item.success ? 'success' : 'error'"
                        style="margin-left: 8px"
                      >
                        {{ item.success ? "成功" : "失败" }}
                      </a-tag>
                    </template>
                    <template #description>
                      <div v-if="item.success">
                        <div>
                          原文件: {{ formatFileSize(files[index]?.size) }}
                        </div>
                        <div>拆分文件数: {{ item.splitFiles.length }}</div>
                        <div>
                          拆分模式:
                          {{
                            formData.splitMode === "rows"
                              ? "按行数"
                              : "按工作表"
                          }}
                        </div>
                      </div>
                      <div v-else style="color: #ff4d4f">
                        {{ item.error }}
                      </div>
                    </template>
                  </a-list-item-meta>
                  <template #actions>
                    <a-button
                      v-if="item.success"
                      type="link"
                      @click="downloadFile(index)"
                    >
                      下载
                    </a-button>
                  </template>
                </a-list-item>
              </template>
            </a-list>
          </a-card>
        </div>
      </div>
    </template>
  </PluginLayout>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { message } from "ant-design-vue";
import {
  LoadingOutlined,
  CheckCircleOutlined,
  FileExcelOutlined,
} from "@ant-design/icons-vue";
import PluginLayout from "@/components/PluginLayout.vue";
import FileUpload from "@/components/FileUpload.vue";
import { runPythonScript } from "@/utils/py";
import { downloadResult, formatFileSize } from "@/utils/file-service";

const layoutRef = ref();
const fileUploadRef = ref();
const files = ref<File[]>([]);
const results = ref<any[]>([]);
const processing = ref(false);
const currentFileIndex = ref(0);
const formData = ref({
  splitMode: "rows",
  rowsPerFile: 1000,
});

const fileColumns = [
  { title: "序号", key: "index", width: 80 },
  { title: "文件名", key: "name" },
  { title: "大小", key: "size", width: 120 },
  { title: "类型", key: "type", width: 100 },
  { title: "创建时间", key: "createTime", width: 180 },
  { title: "修改时间", key: "modifyTime", width: 180 },
  { title: "操作", key: "actions", width: 100 },
];

const canProceed = computed(() => {
  const step = layoutRef.value?.currentStep || 0;
  if (step === 0) return files.value.length > 0;
  if (step === 1 && formData.value.splitMode === "rows")
    return formData.value.rowsPerFile > 0;
  return true;
});

const successCount = computed(() => {
  return results.value.filter((r) => r.success).length;
});

const handleFileChange = (newFiles: File[]) => {
  files.value = newFiles;
};

const handleAddFiles = () => {
  if (fileUploadRef.value) {
    fileUploadRef.value.openFileDialog();
  }
};

const handleImportFromFolder = () => {
  // 从文件夹导入功能 - 暂不实现
  message.info("从文件夹导入功能开发中...");
};

const handleClearAll = () => {
  files.value = [];
  results.value = [];
  formData.value = {
    splitMode: "rows",
    rowsPerFile: 1000,
  };
  if (fileUploadRef.value) {
    fileUploadRef.value.clear();
  }
};

const removeFile = (index: number) => {
  files.value.splice(index, 1);
};

const formatDate = (timestamp: number) => {
  return new Date(timestamp).toLocaleString("zh-CN");
};

const handleStepChange = (step: number) => {
  // 步骤变化时的处理
};

const handleNext = () => {
  // 下一步按钮处理
};

const startProcessing = async () => {
  processing.value = true;
  results.value = [];
  currentFileIndex.value = 0;

  try {
    for (let i = 0; i < files.value.length; i++) {
      currentFileIndex.value = i;
      const file = files.value[i];

      try {
        const fileData = await readFileAsBase64(file);

        const params = {
          fileData: fileData.split(",")[1],
          splitMode: formData.value.splitMode,
          rowsPerFile: formData.value.rowsPerFile,
        };

        const result = await runPythonScript("split-excel", params);
        results.value.push(result);
      } catch (error: any) {
        results.value.push({
          success: false,
          error: error.message || "处理失败",
        });
      }
    }

    message.success(
      `处理完成！成功: ${successCount.value}/${files.value.length}`,
    );
  } catch (error: any) {
    message.error("处理过程中出现错误: " + error.message);
  } finally {
    processing.value = false;
  }
};

const readFileAsBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

const downloadFile = (index: number) => {
  const result = results.value[index];
  const file = files.value[index];

  if (result.success && result.data) {
    const fileName = file.name.replace(/\.[^.]+$/, "_split.zip");
    downloadResult(
      {
        success: true,
        fileName: fileName,
        buffer: result.data,
        logs: [],
        statistics: result.statistics,
      },
      fileName,
    );
  }
};
</script>

<style scoped>
.step-content {
  padding: 24px;
}

.upload-area {
  margin-bottom: 24px;
}

.file-list {
  margin-top: 24px;
}

.empty-state {
  padding: 48px 0;
  text-align: center;
}
</style>
