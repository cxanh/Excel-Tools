<template>
  <PluginLayout
    title="Excel合并"
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
      <!-- 步骤 0: 选择待处理文件-->
      <div v-if="currentStep === 0" class="step-content">
        <a-alert
          message="功能说明"
          description="合并多个Excel文件为一个文件。可以选择将所有工作表合并到一个工作表，或保留各自的工作表结构。"
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
          <a-alert
            v-if="files.length < 2"
            message="请至少选择2个文件进行合并"
            type="warning"
            show-icon
            style="margin-top: 12px"
          />
        </div>

        <div v-else class="empty-state">
          <a-empty description="请拖放文件到此处或点击上方添加文件按钮" />
        </div>
      </div>

      <!-- 步骤 1: 选择合并模式 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-card title="合并模式配置" :bordered="false">
          <a-form layout="vertical">
            <a-form-item label="合并模式">
              <a-radio-group v-model:value="mergeMode" button-style="solid">
                <a-radio-button value="sheets">保留工作表</a-radio-button>
                <a-radio-button value="single">合并到单个工作表</a-radio-button>
              </a-radio-group>
            </a-form-item>
            <a-alert
              v-if="mergeMode === 'sheets'"
              message="保留工作表模式"
              description="将所有文件的工作表复制到一个新文件中，保留原有的工作表名称和结构。"
              type="info"
              show-icon
              style="margin-top: 12px"
            />
            <a-alert
              v-else
              message="合并到单个工作表模式"
              description="将所有文件的所有工作表的数据合并到一个工作表中，按文件顺序依次追加。"
              type="info"
              show-icon
              style="margin-top: 12px"
            />
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 2: 设置导出选项 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-card title="导出选项" :bordered="false">
          <a-form layout="vertical">
            <a-form-item label="输出文件名">
              <a-input
                v-model:value="exportOptions.fileName"
                placeholder="例如：merged.xlsx"
              />
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 3: 设置输出目录 -->
      <div v-if="currentStep === 3" class="step-content">
        <a-card title="输出目录" :bordered="false">
          <a-form layout="vertical">
            <a-form-item label="保存位置">
              <a-input
                v-model:value="outputPath"
                placeholder="选择输出目录"
                readonly
              >
                <template #addonAfter>
                  <a-button @click="selectOutputPath">
                    <FolderOpenOutlined />浏览
                  </a-button>
                </template>
              </a-input>
            </a-form-item>
            <a-form-item>
              <a-checkbox v-model:checked="autoOpen"
                >处理完成后自动打开输出目录</a-checkbox
              >
            </a-form-item>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤 4: 开始处理-->
      <div v-if="currentStep === 4" class="step-content">
        <a-result
          :status="processing ? 'info' : result ? 'success' : 'info'"
          :title="
            processing ? '正在合并...' : result ? '合并完成！' : '准备开始合并'
          "
          :sub-title="
            processing
              ? '正在处理文件...'
              : result
                ? '文件已成功合并'
                : '点击下方开始处理按钮'
          "
        >
          <template #icon>
            <LoadingOutlined
              v-if="processing"
              spin
              style="font-size: 48px; color: #6366f1"
            />
          </template>
          <template #extra>
            <a-progress
              v-if="processing"
              :percent="progress"
              :stroke-color="{ '0%': '#6366f1', '100%': '#8b5cf6' }"
              style="max-width: 500px; margin: 0 auto"
            />
            <a-space v-if="result && result.success" style="margin-top: 16px">
              <a-button type="primary" @click="handleDownload(result)"
                ><DownloadOutlined />下载</a-button
              >
            </a-space>
          </template>
        </a-result>

        <div v-if="result" class="results-list">
          <a-card size="small">
            <template #title>
              <a-space>
                <CheckCircleOutlined
                  v-if="result.success"
                  style="color: #52c41a"
                />
                <CloseCircleOutlined v-else style="color: #ff4d4f" />
                <span>合并结果</span>
              </a-space>
            </template>
            <div v-if="result.success && result.statistics">
              <a-descriptions :column="2" size="small">
                <a-descriptions-item label="合并文件数">{{
                  result.statistics.filesProcessed
                }}</a-descriptions-item>
                <a-descriptions-item label="总工作表数">{{
                  result.statistics.totalSheets
                }}</a-descriptions-item>
                <a-descriptions-item label="总行数">{{
                  result.statistics.totalRows
                }}</a-descriptions-item>
                <a-descriptions-item label="合并模式">{{
                  result.statistics.mergeMode
                }}</a-descriptions-item>
                <a-descriptions-item label="处理时间"
                  >{{ result.statistics.processingTime }}ms</a-descriptions-item
                >
              </a-descriptions>
            </div>
            <a-alert
              v-if="!result.success"
              :message="result.error"
              type="error"
              show-icon
            />
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
  FileExcelOutlined,
  FolderOpenOutlined,
  LoadingOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from "@ant-design/icons-vue";
import PluginLayout from "@/components/PluginLayout.vue";
import FileUpload from "@/components/FileUpload.vue";
import { downloadResult, type ProcessResult } from "@/utils/file-service";
import { runPy } from "@/utils/py";

const props = defineProps<{ workerScript?: string }>();

const files = ref<File[]>([]);
const mergeMode = ref<"sheets" | "single">("sheets");
const exportOptions = ref({ fileName: "merged.xlsx" });
const outputPath = ref("");
const autoOpen = ref(true);
const processing = ref(false);
const progress = ref(0);
const result = ref<ProcessResult | null>(null);
const fileUploadRef = ref();
const layoutRef = ref();

const fileColumns = [
  { title: "序号", key: "index", width: 80 },
  { title: "名称", key: "name" },
  { title: "大小", key: "size", width: 120 },
  { title: "类型", key: "type", width: 100 },
  { title: "创建时间", key: "createTime", width: 180 },
  { title: "修改时间", key: "modifyTime", width: 180 },
  { title: "操作", key: "actions", width: 100 },
];

const canProceed = computed(() => {
  const step = layoutRef.value?.currentStep || 0;
  if (step === 0) return files.value.length >= 2;
  if (step === 3) return outputPath.value !== "";
  return true;
});

function handleFileChange(newFiles: File[]) {
  files.value = newFiles;
}

function handleAddFiles() {
  fileUploadRef.value?.openFileDialog();
}

function handleImportFromFolder() {
  message.info("从文件夹导入功能开发中...");
}

function handleClearAll() {
  files.value = [];
  result.value = null;
  if (fileUploadRef.value) fileUploadRef.value.clear();
}

function removeFile(index: number) {
  files.value.splice(index, 1);
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

function formatDate(timestamp: number): string {
  return new Date(timestamp).toLocaleString("zh-CN");
}

function selectOutputPath() {
  outputPath.value = "C:\\Users\\Desktop\\Output";
  message.success("已选择输出目录");
}

function handleStepChange(step: number) {
  console.log("Step changed to:", step);
}

function handleNext() {
  const step = layoutRef.value?.currentStep || 0;
  if (step === 3) handleProcess();
}

async function handleProcess() {
  if (!props.workerScript) {
    message.error("插件配置错误");
    return;
  }

  processing.value = true;
  progress.value = 0;
  result.value = null;

  try {
    const fileBuffers = [];
    for (let i = 0; i < files.value.length; i++) {
      const file = files.value[i];
      const buffer = await file.arrayBuffer();
      fileBuffers.push({ name: file.name, data: buffer });
      progress.value = Math.round(((i + 1) / files.value.length) * 50);
    }

    const input = {
      files: fileBuffers,
      params: { mergeMode: mergeMode.value },
    };

    const pyResult = await runPy(props.workerScript, input);
    progress.value = 100;

    result.value = {
      success: pyResult.success,
      fileName: exportOptions.value.fileName,
      buffer: pyResult.buffer,
      logs: pyResult.logs,
      statistics: pyResult.details?.statistics,
      error: pyResult.error,
    };

    if (pyResult.success) {
      message.success("合并完成！");
    } else {
      message.error("合并失败: " + pyResult.error);
    }
  } catch (error) {
    message.error("处理失败: " + (error as Error).message);
    result.value = {
      success: false,
      fileName: exportOptions.value.fileName,
      logs: [],
      error: (error as Error).message,
    };
  } finally {
    processing.value = false;
  }
}

async function handleDownload(result: ProcessResult) {
  try {
    await downloadResult(result, exportOptions.value.fileName);
    message.success("文件已保存");
  } catch (error) {
    message.error("下载失败: " + (error as Error).message);
  }
}
</script>

<style scoped>
.step-content {
  max-width: 1200px;
  margin: 0 auto;
}
.upload-area {
  margin-bottom: 24px;
}
.file-list {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}
.empty-state {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 8px;
}
.results-list {
  margin-top: 24px;
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
}
</style>
