<template>
  <div class="delete-formula">
    <PluginTemplate
      plugin-title="删除Excel公式"
      info-message="删除Excel中的公式，只保留计算后的值"
      :current-step="currentStep"
      @add-file="handleAddFile"
      @import-folder="handleImportFromFolder"
      @more-action="handleMoreAction"
      @next-step="handleNextStep"
      @remove-file="handleRemoveFile"
      ref="pluginTemplate"
    />

    <!-- 文件上传组件 -->
    <div style="display: none">
      <input
        ref="fileInput"
        type="file"
        accept=".xlsx,.xls"
        multiple
        @change="handleFileChange"
      />
    </div>

    <!-- 步骤1：上传文件 -->
    <div v-if="currentStep === 1" class="step-content">
      <h3>上传Excel文件</h3>
      <a-upload-dragger
        name="file"
        :multiple="true"
        :show-upload-list="false"
        accept=".xlsx,.xls"
        :before-upload="handleUpload"
      >
        <p class="ant-upload-drag-icon">
          <a-icon type="file-excel" style="font-size: 48px; color: #52c41a" />
        </p>
        <p class="ant-upload-text">点击或拖拽Excel文件到此处上传</p>
        <p class="ant-upload-hint">支持 .xlsx, .xls 格式文件</p>
      </a-upload-dragger>

      <!-- 已上传文件列表 -->
      <div v-if="files.length > 0" style="margin-top: 16px">
        <h4>已上传文件 ({{ files.length }})</h4>
        <a-list
          bordered
          :data-source="files"
          :pagination="{ pageSize: 5 }"
          size="small"
        >
          <template #renderItem="{ item, index }">
            <a-list-item>
              <span>{{ index + 1 }}. {{ item.name }}</span>
              <a-button
                type="link"
                danger
                size="small"
                @click="handleRemoveFile(index)"
              >
                删除
              </a-button>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </div>

    <!-- 步骤2：设置 -->
    <div v-if="currentStep === 2" class="step-content">
      <h3>删除公式设置</h3>
      <a-form layout="vertical">
        <a-form-item label="工作表选择">
          <a-radio-group v-model:value="settings.sheetOption">
            <a-radio value="all">处理所有工作表</a-radio>
            <a-radio value="specific">只处理指定工作表</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item
          label="指定工作表名称（多个用逗号分隔）"
          v-if="settings.sheetOption === 'specific'"
        >
          <a-input
            v-model:value="settings.specificSheets"
            placeholder="例如：Sheet1,Sheet2"
            style="max-width: 400px"
          />
          <div style="margin-top: 8px; color: #666; font-size: 12px">
            不区分大小写，支持部分匹配（例如：Sheet* 匹配所有以 Sheet
            开头的工作表）
          </div>
        </a-form-item>

        <a-form-item label="处理选项">
          <a-checkbox-group v-model:value="settings.processOptions">
            <a-checkbox value="formula">删除公式（保留计算值）</a-checkbox>
            <a-checkbox value="arrayFormula"
              >删除数组公式（保留计算值）</a-checkbox
            >
            <a-checkbox value="blankCells">忽略空白单元格</a-checkbox>
          </a-checkbox-group>
        </a-form-item>

        <a-form-item label="数据区域">
          <a-radio-group v-model:value="settings.rangeOption">
            <a-radio value="all">处理整个工作表</a-radio>
            <a-radio value="used">只处理已使用区域</a-radio>
            <a-radio value="specific">处理指定区域</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item
          label="指定区域范围"
          v-if="settings.rangeOption === 'specific'"
        >
          <a-input
            v-model:value="settings.specificRange"
            placeholder="例如：A1:C10"
            style="max-width: 200px"
          />
          <div style="margin-top: 8px; color: #666; font-size: 12px">
            支持单个区域或多个区域用逗号分隔
          </div>
        </a-form-item>
      </a-form>
    </div>

    <!-- 步骤3：预览和确认 -->
    <div v-if="currentStep === 3" class="step-content">
      <h3>预览和确认</h3>
      <a-alert
        message="处理前预览"
        description="以下是您选择的文件和设置，点击开始处理后将执行公式删除操作"
        type="info"
        show-icon
        style="margin-bottom: 20px"
      />

      <div class="settings-summary">
        <h4>文件列表 ({{ files.length }})</h4>
        <a-list
          bordered
          :data-source="files"
          :pagination="{ pageSize: 5 }"
          size="small"
          style="margin-bottom: 20px"
        >
          <template #renderItem="{ item, index }">
            <a-list-item>
              <span>{{ index + 1 }}. {{ item.name }}</span>
            </a-list-item>
          </template>
        </a-list>

        <h4>处理设置</h4>
        <a-descriptions bordered column="{1}" size="small">
          <a-descriptions-item label="工作表选择">
            {{
              settings.sheetOption === "all"
                ? "所有工作表"
                : `指定工作表: ${settings.specificSheets}`
            }}
          </a-descriptions-item>
          <a-descriptions-item label="处理选项">
            <span v-if="settings.processOptions.includes('formula')">公式</span>
            <span v-if="settings.processOptions.includes('arrayFormula')"
              >，数组公式</span
            >
            <span v-if="settings.processOptions.includes('blankCells')"
              >，忽略空白单元格</span
            >
          </a-descriptions-item>
          <a-descriptions-item label="数据区域">
            {{
              settings.rangeOption === "all"
                ? "整个工作表"
                : settings.rangeOption === "used"
                  ? "已使用区域"
                  : `指定区域: ${settings.specificRange}`
            }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </div>

    <!-- 处理进度 -->
    <a-progress
      v-if="progress > 0 && progress < 100"
      :percent="progress"
      style="margin: 16px 0"
    ></a-progress>

    <!-- 处理日志 -->
    <div v-if="logs.length > 0" style="margin: 16px 0">
      <h3>处理日志</h3>
      <a-list bordered :data-source="logs" size="small">
        <template #renderItem="{ item }">
          <a-list-item>{{ item }}</a-list-item>
        </template>
      </a-list>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import PluginTemplate from "@/components/PluginTemplate.vue";
import { runPy } from "@/utils/py";

const pluginTemplate = ref(null);
const currentStep = ref(0);
const files = ref([]);
const isProcessing = ref(false);
const progress = ref(0);
const logs = ref([]);
const fileInput = ref(null);

// 设置
const settings = ref({
  sheetOption: "all", // 'all' 或 'specific'
  specificSheets: "",
  processOptions: ["formula", "arrayFormula", "blankCells"], // 'formula', 'arrayFormula', 'blankCells'
  rangeOption: "used", // 'all', 'used', 'specific'
  specificRange: "",
});

// 读取 Python 脚本
const getPythonScript = async () => {
  const response = await fetch("/plugins/delete-formula/worker.py");
  return response.text();
};

// 添加文件
const handleAddFile = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// 从文件夹导入
const handleImportFromFolder = () => {
  logs.value.push("从文件夹导入功能开发中...");
};

// 更多操作
const handleMoreAction = (key) => {
  switch (key) {
    case "paste":
      logs.value.push("从剪贴板读取功能开发中...");
      break;
    case "clear":
      files.value = [];
      break;
  }
};

// 下一步
const handleNextStep = async () => {
  if (currentStep.value === 0) {
    // 进入步骤1：上传文件
    currentStep.value = 1;
    logs.value.push("进入上传文件步骤...");
  } else if (currentStep.value === 1) {
    // 进入步骤2：设置
    if (files.length === 0) {
      logs.value.push("请先上传文件");
      return;
    }
    currentStep.value = 2;
    logs.value.push("进入设置步骤...");
  } else if (currentStep.value === 2) {
    // 进入步骤3：预览和确认
    currentStep.value = 3;
    logs.value.push("进入预览和确认步骤...");
  } else if (currentStep.value === 3) {
    // 开始处理
    await processFiles();
  }
};

// 删除文件
const handleRemoveFile = (index) => {
  files.value.splice(index, 1);
};

// 文件选择变化
const handleFileChange = (e) => {
  const selectedFiles = Array.from(e.target.files);
  if (selectedFiles.length > 0) {
    files.value = [...files.value, ...selectedFiles];
  }
  e.target.value = ""; // 清空 input
};

// 文件上传
const handleUpload = (file) => {
  files.value.push(file);
  return false; // 阻止默认上传
};

// 处理文件
const processFiles = async () => {
  if (files.length === 0) return;

  isProcessing.value = true;
  logs.value = ["开始处理文件..."];
  progress.value = 10;

  try {
    const script = await getPythonScript();
    progress.value = 30;

    logs.value.push(`处理文件数量: ${files.length} 个`);
    logs.value.push(`设置参数: ${JSON.stringify(settings.value)}`);

    // 处理每个文件
    for (let i = 0; i < files.length; i++) {
      const file = files.value[i];
      const fileIndex = i + 1;

      logs.value.push(
        `开始处理文件 ${fileIndex}/${files.length}: ${file.name}`,
      );

      // 读取文件内容
      const reader = new FileReader();
      const fileContent = await new Promise((resolve) => {
        reader.onload = (e) => resolve(e.target.result);
        reader.readAsArrayBuffer(file);
      });

      // 更新进度
      progress.value = 40 + Math.round((i / files.length) * 40);

      // 构建处理数据对象
      const processingData = {
        file: new Uint8Array(fileContent),
        fileName: file.name,
        settings: settings.value,
      };

      // 调用Python脚本处理
      const result = await runPy(script, processingData);

      if (result.success) {
        logs.value.push(`文件 ${fileIndex}/${files.length} 处理成功`);
        logs.value.push(`删除了 ${result.deletedCount} 个公式`);

        // 生成下载链接
        if (result.buffer) {
          const blob = new Blob([result.buffer], {
            type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          });
          const url = URL.createObjectURL(blob);

          // 创建下载链接
          const link = document.createElement("a");
          link.href = url;
          link.download = `处理后_${file.name}`;
          document.body.appendChild(link);
          link.click();

          // 清理
          document.body.removeChild(link);
          URL.revokeObjectURL(url);

          logs.value.push(`文件已下载: 处理后_${file.name}`);
        }
      } else {
        logs.value.push(
          `文件 ${fileIndex}/${files.length} 处理失败: ${result.error}`,
        );
      }
    }

    progress.value = 100;
    logs.value.push("所有文件处理完成！");
  } catch (error) {
    logs.value.push(`处理错误: ${error.message}`);
    console.error("Processing error:", error);
  } finally {
    isProcessing.value = false;
  }
};
</script>

<style scoped>
.delete-formula {
  background: #f5f5f5;
  min-height: calc(100vh - 120px);
  padding: 0;
}

.step-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.settings-summary {
  background: #fafafa;
  padding: 16px;
  border-radius: 8px;
  margin-top: 16px;
}

.settings-summary h4 {
  margin-bottom: 12px;
  color: #333;
  font-size: 14px;
  font-weight: 500;
}
</style>
