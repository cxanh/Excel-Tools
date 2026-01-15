<template>
  <div class="merge-excel">
    <PluginTemplate
      plugin-title="合并Excel文件"
      info-message="批量合并多个Excel文件的内容到一个文件中，支持相同格式的Excel文件合并"
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

    <!-- 步骤2：设置处理规则 -->
    <div v-if="currentStep === 1" class="step-content">
      <h3>合并设置</h3>
      <a-form layout="vertical">
        <a-form-item label="合并方式">
          <a-radio-group v-model:value="settings.mergeMode">
            <a-radio value="append">追加到同一工作表</a-radio>
            <a-radio value="separate">保留原工作表</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item label="输出文件名称">
          <a-input
            v-model:value="settings.outputFileName"
            placeholder="请输入合并后的文件名"
          />
        </a-form-item>

        <a-form-item label="工作表选项">
          <a-radio-group v-model:value="settings.sheetOption">
            <a-radio value="all">处理所有工作表</a-radio>
            <a-radio value="active">只处理当前工作表</a-radio>
            <a-radio value="selected">指定工作表（用逗号分隔）</a-radio>
          </a-radio-group>

          <a-input
            v-if="settings.sheetOption === 'selected'"
            v-model:value="settings.selectedSheets"
            placeholder="请输入工作表名称，用逗号分隔"
            style="margin-top: 12px"
          />
        </a-form-item>

        <a-form-item label="合并选项">
          <a-checkbox v-model:checked="settings.includeHeaders"
            >包含表头（仅追加模式有效）</a-checkbox
          >
          <a-checkbox v-model:checked="settings.skipEmptyRows"
            >跳过空行</a-checkbox
          >
          <a-checkbox v-model:checked="settings.enableDetailedLogs"
            >启用详细日志</a-checkbox
          >
        </a-form-item>
      </a-form>
    </div>

    <!-- 步骤3：设置输出目录 -->
    <div v-if="currentStep === 2" class="step-content">
      <h3>输出目录设置</h3>
      <a-form layout="vertical">
        <a-form-item label="输出位置">
          <a-radio-group v-model:value="settings.outputLocation">
            <a-radio value="same">与源文件相同目录</a-radio>
            <a-radio value="custom">自定义目录</a-radio>
          </a-radio-group>

          <div
            v-if="settings.outputLocation === 'custom'"
            style="margin-top: 12px"
          >
            <a-button type="default" @click="handleSelectOutputDir">
              选择输出目录
            </a-button>
            <span
              v-if="settings.customOutputDir"
              style="margin-left: 12px; color: #666"
            >
              {{ settings.customOutputDir }}
            </span>
          </div>
        </a-form-item>
      </a-form>
    </div>

    <!-- 步骤4：开始处理 -->
    <div v-if="currentStep === 3" class="step-content">
      <h3>处理确认</h3>
      <div class="processing-summary">
        <p>
          即将合并 <strong>{{ files.value.length }}</strong> 个文件：
        </p>
        <ul>
          <li v-for="file in files.value" :key="file.key">{{ file.name }}</li>
        </ul>

        <div class="settings-summary">
          <h4>处理设置：</h4>
          <p><strong>合并方式：</strong>{{ getMergeModeText() }}</p>
          <p><strong>输出文件名：</strong>{{ settings.outputFileName }}</p>
          <p><strong>工作表选项：</strong>{{ getSheetOptionText() }}</p>
          <p>
            <strong>包含表头：</strong
            >{{ settings.includeHeaders ? "是" : "否" }}
          </p>
          <p>
            <strong>跳过空行：</strong
            >{{ settings.skipEmptyRows ? "是" : "否" }}
          </p>
          <p><strong>输出位置：</strong>{{ getOutputLocationText() }}</p>
        </div>

        <a-button
          type="primary"
          size="large"
          @click="processFiles"
          :disabled="isProcessing.value"
        >
          {{ isProcessing.value ? "处理中..." : "开始合并" }}
        </a-button>
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
import { ref, nextTick } from "vue";
import PluginTemplate from "@/components/PluginTemplate.vue";
import { runPy } from "@/utils/py";

const pluginTemplate = ref(null);
const currentStep = ref(0);
const files = ref([]);
const isProcessing = ref(false);
const progress = ref(0);
const logs = ref([]);
const fileInput = ref(null);

// 合并Excel设置
const settings = ref({
  mergeMode: "append", // append: 追加到同一工作表, separate: 保留原工作表
  outputFileName: "合并结果.xlsx",
  includeHeaders: true,
  skipEmptyRows: true,
  sheetOption: "all", // all, active, selected
  selectedSheets: "",
  enableDetailedLogs: true,
  outputLocation: "same", // same, custom
  customOutputDir: "",
  filenameMode: "custom", // custom (because merge always needs custom filename)
});

// 获取合并方式文本
const getMergeModeText = () => {
  const modes = {
    append: "追加到同一工作表",
    separate: "保留原工作表",
  };
  return modes[settings.value.mergeMode] || "追加到同一工作表";
};

// 获取工作表选项文本
const getSheetOptionText = () => {
  const options = {
    all: "处理所有工作表",
    active: "只处理当前工作表",
    selected: `指定工作表：${settings.value.selectedSheets}`,
  };
  return options[settings.value.sheetOption] || "处理所有工作表";
};

// 获取输出位置文本
const getOutputLocationText = () => {
  if (settings.value.outputLocation === "same") {
    return "与源文件相同目录";
  } else {
    return settings.value.customOutputDir || "未选择输出目录";
  }
};

// 选择输出目录
const handleSelectOutputDir = () => {
  logs.value.push("选择输出目录功能开发中...");
};

// 读取 Python 脚本
const getPythonScript = async () => {
  const response = await fetch("/plugins/merge-excel/worker.py");
  return response.text();
};

// 添加文件
const handleAddFile = () => {
  fileInput.value?.click();
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
    // 进入步骤1：设置处理规则
    if (files.value.length === 0) {
      logs.value.push("请先添加需要合并的Excel文件");
      return;
    }
    currentStep.value = 1;
    logs.value.push("进入设置处理规则步骤...");
  } else if (currentStep.value === 1) {
    // 进入步骤2：设置其他选项
    currentStep.value = 2;
    logs.value.push("进入设置其他选项步骤...");
  } else if (currentStep.value === 2) {
    // 进入步骤3：设置输出目录
    currentStep.value = 3;
    logs.value.push("进入设置输出目录步骤...");
  } else if (currentStep.value === 3) {
    // 进入步骤4：开始处理
    currentStep.value = 4;
    await processFiles();
  }
};

// 删除文件
const handleRemoveFile = (key) => {
  files.value = files.value.filter((file) => file.key !== key);
};

// 文件选择变化
const handleFileChange = (e) => {
  const selectedFiles = Array.from(e.target.files);
  if (selectedFiles.length > 0) {
    selectedFiles.forEach((file, index) => {
      const fileItem = {
        key: `${file.name}-${Date.now()}-${index}`,
        index: files.value.length + index + 1,
        name: file.name,
        path: file.name, // 浏览器环境下无法获取完整路径
        extension: file.name.split(".").pop(),
        createTime: new Date(file.lastModified).toLocaleString(),
        modifyTime: new Date(file.lastModified).toLocaleString(),
        file: file,
      };
      files.value.push(fileItem);
    });

    // 清空 input，允许重复上传
    e.target.value = "";

    // 更新插件模板的文件列表
    nextTick(() => {
      if (pluginTemplate.value) {
        pluginTemplate.value.files = files.value;
      }
    });
  }
};

// 处理文件
const processFiles = async () => {
  if (files.value.length === 0) return;

  isProcessing.value = true;
  logs.value = ["开始处理文件..."];
  progress.value = 10;

  try {
    const script = await getPythonScript();
    progress.value = 30;

    // 依次处理每个文件
    const filesToProcess = {};
    for (let i = 0; i < files.value.length; i++) {
      const fileItem = files.value[i];
      // 读取文件内容
      const reader = new FileReader();
      const fileContent = await new Promise((resolve) => {
        reader.onload = (e) => resolve(e.target.result);
        reader.readAsArrayBuffer(fileItem.file);
      });
      filesToProcess[fileItem.name] = new Uint8Array(fileContent);
      progress.value = 30 + Math.round(((i + 1) / files.value.length) * 20);
    }

    // 调用Python脚本处理
    logs.value.push("开始合并Excel文件...");
    logs.value.push(`设置参数：${JSON.stringify(settings.value)}`);
    const result = await runPy(script, {
      type: "multiple",
      files: filesToProcess,
      settings: settings.value,
    });
    progress.value = 80;

    if (result.success) {
      logs.value.push("文件合并完成！");
      logs.value.push(...result.logs);

      // 下载处理后的文件
      const blob = new Blob([result.buffer], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = settings.outputFileName || "合并结果.xlsx";
      a.click();
      URL.revokeObjectURL(url);
    } else {
      logs.value.push(`合并失败：${result.error}`);
    }

    progress.value = 100;
  } catch (error) {
    logs.value.push(`错误：${error.message}`);
    console.error("Processing error:", error);
  } finally {
    isProcessing.value = false;
  }
};
</script>

<style scoped>
.merge-excel {
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
</style>
