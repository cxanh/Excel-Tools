<template>
  <div class="remove-empty-row">
    <PluginTemplate
      plugin-title="删除 Excel 空白内容"
      info-message="批量删除 Excel 文件中的空白工作表、空白行和空白列，提升数据处理效率"
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

    <!-- 步骤1：设置处理规则 -->
    <div v-if="currentStep === 1" class="step-content">
      <h3>空白内容删除设置</h3>
      <a-form layout="vertical">
        <a-form-item label="处理内容">
          <a-checkbox-group v-model:value="settings.contentToRemove">
            <a-checkbox value="emptySheets">删除空白工作表</a-checkbox>
            <a-checkbox value="emptyRows">删除空白行</a-checkbox>
            <a-checkbox value="emptyColumns">删除空白列</a-checkbox>
          </a-checkbox-group>
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

        <!-- 空白行设置 -->
        <a-collapse v-if="settings.contentToRemove.includes('emptyRows')">
          <a-collapse-panel key="rowSettings" header="空白行设置">
            <a-form-item label="空白行定义">
              <a-radio-group v-model:value="settings.emptyRowDefinition">
                <a-radio value="all">所有单元格为空</a-radio>
                <a-radio value="data">数据列为空（忽略格式列）</a-radio>
              </a-radio-group>
            </a-form-item>

            <a-form-item label="保留选项">
              <a-checkbox v-model:checked="settings.keepHeaderRow"
                >保留表头行</a-checkbox
              >
            </a-form-item>
          </a-collapse-panel>
        </a-collapse>

        <!-- 空白列设置 -->
        <a-collapse v-if="settings.contentToRemove.includes('emptyColumns')">
          <a-collapse-panel key="columnSettings" header="空白列设置">
            <a-form-item label="空白列定义">
              <a-radio-group v-model:value="settings.emptyColumnDefinition">
                <a-radio value="all">所有单元格为空</a-radio>
                <a-radio value="data">数据行为空（忽略格式行）</a-radio>
              </a-radio-group>
            </a-form-item>

            <a-form-item label="保留选项">
              <a-checkbox v-model:checked="settings.keepHeaderColumn"
                >保留表头列</a-checkbox
              >
            </a-form-item>
          </a-collapse-panel>
        </a-collapse>
      </a-form>
    </div>

    <!-- 步骤2：设置其它选项 -->
    <div v-if="currentStep === 2" class="step-content">
      <h3>其他选项设置</h3>
      <a-form layout="vertical">
        <a-form-item label="处理选项">
          <a-checkbox v-model:checked="settings.ignoreHiddenSheets"
            >忽略隐藏工作表</a-checkbox
          >
          <a-checkbox v-model:checked="settings.ignoreFilteredRows"
            >忽略已筛选行</a-checkbox
          >
        </a-form-item>

        <a-form-item label="日志记录">
          <a-checkbox v-model:checked="settings.enableDetailedLogs"
            >启用详细日志</a-checkbox
          >
        </a-form-item>
      </a-form>
    </div>

    <!-- 步骤3：设置输出目录 -->
    <div v-if="currentStep === 3" class="step-content">
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

        <a-form-item label="文件名设置">
          <a-radio-group v-model:value="settings.filenameMode">
            <a-radio value="append">在原文件名后添加后缀</a-radio>
            <a-radio value="custom">使用自定义文件名</a-radio>
          </a-radio-group>

          <a-input
            v-if="settings.filenameMode === 'append'"
            v-model:value="settings.filenameSuffix"
            placeholder="请输入后缀（例如：_处理后）"
            style="margin-top: 12px"
          />

          <a-input
            v-if="settings.filenameMode === 'custom'"
            v-model:value="settings.customFilename"
            placeholder="请输入自定义文件名（不包含扩展名）"
            style="margin-top: 12px"
          />
        </a-form-item>
      </a-form>
    </div>

    <!-- 步骤4：开始处理 -->
    <div v-if="currentStep === 4" class="step-content">
      <h3>处理确认</h3>
      <div class="processing-summary">
        <p>
          即将处理 <strong>{{ files.value.length }}</strong> 个文件：
        </p>
        <ul>
          <li v-for="file in files.value" :key="file.key">{{ file.name }}</li>
        </ul>

        <div class="settings-summary">
          <h4>处理设置：</h4>
          <p><strong>处理内容：</strong>{{ getContentToRemoveText() }}</p>
          <p><strong>工作表选项：</strong>{{ getSheetOptionText() }}</p>

          <template v-if="settings.value.contentToRemove.includes('emptyRows')">
            <p>
              <strong>空白行定义：</strong>{{ getEmptyRowDefinitionText() }}
            </p>
            <p>
              <strong>行保留选项：</strong
              >{{
                settings.value.keepHeaderRow ? "保留表头行" : "不保留表头行"
              }}
            </p>
          </template>

          <template
            v-if="settings.value.contentToRemove.includes('emptyColumns')"
          >
            <p>
              <strong>空白列定义：</strong>{{ getEmptyColumnDefinitionText() }}
            </p>
            <p>
              <strong>列保留选项：</strong
              >{{
                settings.value.keepHeaderColumn ? "保留表头列" : "不保留表头列"
              }}
            </p>
          </template>

          <p><strong>输出位置：</strong>{{ getOutputLocationText() }}</p>
        </div>

        <a-button
          type="primary"
          size="large"
          @click="processFiles"
          :disabled="isProcessing.value"
        >
          {{ isProcessing.value ? "处理中..." : "开始处理" }}
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

// 删除空白内容设置
const settings = ref({
  contentToRemove: ["emptyRows"], // emptySheets, emptyRows, emptyColumns
  sheetOption: "all", // all, active, selected
  selectedSheets: "",
  emptyRowDefinition: "all", // all, data
  keepHeaderRow: true,
  emptyColumnDefinition: "all", // all, data
  keepHeaderColumn: true,
  ignoreHiddenSheets: true,
  ignoreFilteredRows: true,
  enableDetailedLogs: true,
  outputLocation: "same", // same, custom
  customOutputDir: "",
  filenameMode: "append", // append, custom
  filenameSuffix: "_处理后",
  customFilename: "",
});

// 获取工作表选项文本
const getSheetOptionText = () => {
  const options = {
    all: "处理所有工作表",
    active: "只处理当前工作表",
    selected: `指定工作表：${settings.value.selectedSheets}`,
  };
  return options[settings.value.sheetOption] || "处理所有工作表";
};

// 获取空白行定义文本
const getEmptyRowDefinitionText = () => {
  const definitions = {
    all: "所有单元格为空",
    data: "数据列为空（忽略格式列）",
  };
  return definitions[settings.value.emptyRowDefinition] || "所有单元格为空";
};

// 获取空白列定义文本
const getEmptyColumnDefinitionText = () => {
  const definitions = {
    all: "所有单元格为空",
    data: "数据行为空（忽略格式行）",
  };
  return definitions[settings.value.emptyColumnDefinition] || "所有单元格为空";
};

// 获取处理内容文本
const getContentToRemoveText = () => {
  const contentMap = {
    emptySheets: "空白工作表",
    emptyRows: "空白行",
    emptyColumns: "空白列",
  };
  return settings.value.contentToRemove
    .map((item) => contentMap[item])
    .join(", ");
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
  const response = await fetch("/plugins/remove-empty-row/worker.py");
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
    for (let i = 0; i < files.value.length; i++) {
      const fileItem = files.value[i];
      logs.value.push(`正在处理文件：${fileItem.name}`);
      logs.value.push(`设置参数：${JSON.stringify(settings.value)}`);

      // 传递设置参数给Python脚本
      const result = await runPy(script, {
        type: "single",
        file: fileItem.file,
        fileName: fileItem.name,
        settings: settings.value,
      });
      progress.value = 30 + Math.round(((i + 1) / files.value.length) * 50);

      logs.value.push(`${fileItem.name} 处理完成！`);
      logs.value.push(...result.logs);

      // 下载处理后的文件
      const blob = new Blob([result.buffer], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${fileItem.name.replace(".xlsx", "").replace(".xls", "")}_处理后.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    }

    logs.value.push("所有文件处理完成！");
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
.remove-empty-row {
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
