<template>
  <div class="replace-content">
    <PluginTemplate
      plugin-title="按规则修改内容"
      info-message="用于批量在 Excel 文档中查找并替换/删除指定内容，支持多种匹配规则"
      :current-step="currentStep"
      @add-file="handleAddFile"
      @import-folder="handleImportFromFolder"
      @more-action="handleMoreAction"
      @next-step="handleNextStep"
      @prev-step="handlePrevStep"
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

    <!-- 步骤1：设置处理规则 - 替换规则 -->
    <div v-if="currentStep === 1" class="step-content">
      <h3>替换规则设置</h3>
      <a-form layout="vertical">
        <div class="replacement-rules">
          <a-button
            type="primary"
            icon="plus"
            @click="addReplacementRule"
            style="margin-bottom: 16px"
          >
            添加替换规则
          </a-button>

          <a-list :data-source="replacementRules || []" bordered size="small">
            <template #renderItem="{ item, index }">
              <a-list-item>
                <div class="rule-item">
                  <div class="rule-index">{{ index + 1 }}</div>
                  <div class="rule-content">
                    <a-form-item label="查找内容" required>
                      <a-input
                        v-model:value="item.findText"
                        placeholder="请输入要查找的内容"
                        style="margin-right: 8px; width: 200px"
                      />
                    </a-form-item>

                    <a-form-item label="替换为" required>
                      <a-input
                        v-model:value="item.replaceText"
                        placeholder="请输入替换后的内容（留空表示删除）"
                        style="margin-right: 8px; width: 200px"
                      />
                    </a-form-item>

                    <a-form-item label="匹配模式">
                      <a-radio-group
                        v-model:value="item.matchMode"
                        button-style="solid"
                      >
                        <a-radio-button value="normal">普通</a-radio-button>
                        <a-radio-button value="regex"
                          >正则表达式</a-radio-button
                        >
                      </a-radio-group>
                    </a-form-item>
                  </div>

                  <a-button
                    type="text"
                    danger
                    @click="removeReplacementRule(index)"
                  >
                    删除
                  </a-button>
                </div>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </a-form>
    </div>

    <!-- 步骤2：设置其他选项 -->
    <div v-if="currentStep === 2" class="step-content">
      <h3>高级设置</h3>
      <a-form layout="vertical">
        <a-form-item label="匹配选项">
          <a-checkbox v-model:checked="settings.caseSensitive"
            >区分大小写</a-checkbox
          >
          <a-checkbox v-model:checked="settings.matchEntireCell"
            >匹配整个单元格</a-checkbox
          >
          <a-checkbox v-model:checked="settings.ignoreHiddenCells"
            >忽略隐藏单元格</a-checkbox
          >
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

        <a-form-item label="处理范围">
          <a-radio-group v-model:value="settings.rangeOption">
            <a-radio value="all">整个工作表</a-radio>
            <a-radio value="data">仅数据区域</a-radio>
            <a-radio value="custom">自定义范围</a-radio>
          </a-radio-group>

          <a-input
            v-if="settings.rangeOption === 'custom'"
            v-model:value="settings.customRange"
            placeholder="请输入单元格范围（例如：A1:D100）"
            style="margin-top: 12px"
          />
        </a-form-item>

        <a-form-item label="其他选项">
          <a-checkbox v-model:checked="settings.enableDetailedLogs"
            >启用详细日志</a-checkbox
          >
          <a-checkbox v-model:checked="settings.backupOriginal"
            >创建源文件备份</a-checkbox
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
          即将处理 <strong>{{ (files || []).length }}</strong> 个文件：
        </p>
        <ul>
          <li v-for="file in files || []" :key="file.key">{{ file.name }}</li>
        </ul>

        <div class="settings-summary">
          <h4>替换规则：</h4>
          <ul class="rule-summary">
            <li v-for="(rule, index) in replacementRules || []" :key="index">
              {{ index + 1 }}. 查找: "{{ rule.findText }}" → 替换为: "{{
                rule.replaceText || "（删除）"
              }}" ({{ rule.matchMode === "regex" ? "正则" : "普通" }})
            </li>
          </ul>

          <h4>高级设置：</h4>
          <p><strong>匹配选项：</strong>{{ getMatchOptionsText() }}</p>
          <p><strong>工作表选项：</strong>{{ getSheetOptionText() }}</p>
          <p><strong>处理范围：</strong>{{ getRangeOptionText() }}</p>
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

    <!-- 步骤5：处理结果 -->
    <div v-if="currentStep === 5" class="step-content step-result">
      <!-- 处理完成提示 -->
      <div class="success-banner">
        <div class="success-icon">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="32" fill="#f0f9eb" />
            <path
              d="M20 32L28 40L44 24"
              stroke="#52c41a"
              stroke-width="4"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
        <div class="success-info">
          <h2>处理完成</h2>
          <p>从 {{ files?.length || 0 }} 项任务中，耗时约 0 秒</p>
          <p>
            成功
            {{
              (processedFiles?.filter((f) => f.status === "success") || [])
                .length
            }}
            项， 失败
            {{
              (processedFiles?.filter((f) => f.status === "error") || []).length
            }}
            项
          </p>
        </div>
      </div>

      <!-- 日志区域 -->
      <div class="logs-container">
        <a-collapse v-model:activeKey="activeLogKey" ghost>
          <a-collapse-panel key="1" header="查看详细日志" :show-arrow="false">
            <div class="logs-content">
              <div v-for="(log, index) in logs" :key="index" class="log-item">
                {{ log }}
              </div>
            </div>
          </a-collapse-panel>
        </a-collapse>
      </div>

      <!-- 处理结果折叠面板 -->
      <a-collapse
        v-model:activeKey="resultPanels"
        ghost
        style="margin-top: 16px"
      >
        <!-- 处理结果 -->
        <a-collapse-panel
          key="result"
          header="处理结果"
          style="margin-bottom: 12px"
        >
          <div class="processing-results">
            <div class="result-item">
              <span class="result-label">输出目录：</span>
              <span class="result-value">{{
                settings.outputLocation === "same"
                  ? "与源文件相同目录"
                  : settings.customOutputDir || "未设置"
              }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">规则名称：</span>
              <span class="result-value">替换规则</span>
            </div>
          </div>
        </a-collapse-panel>

        <!-- 处理结果表格 -->
        <a-collapse-panel
          key="details"
          header="处理结果"
          style="margin-bottom: 12px"
        >
          <div class="result-table-container">
            <a-table
              :columns="resultColumns"
              :data-source="processedFiles || []"
              :pagination="false"
              bordered
              size="small"
              :scroll="{ x: 800 }"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'status'">
                  <a-tag
                    :color="record.status === 'success' ? 'green' : 'red'"
                    style="margin: 0"
                  >
                    {{ record.status === "success" ? "处理成功" : "处理失败" }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'action'">
                  <a-button
                    v-if="record.status === 'success' && record.downloadUrl"
                    type="link"
                    size="small"
                    @click="handleDownload(record)"
                    style="padding: 0; color: #165dff"
                  >
                    下载
                  </a-button>
                </template>
                <template v-else-if="column.key === 'path'">
                  <span class="file-path">{{ record.downloadName }}</span>
                </template>
              </template>
            </a-table>
          </div>
        </a-collapse-panel>
      </a-collapse>

      <!-- 操作按钮 -->
      <div class="result-actions">
        <a-button type="default" @click="handlePrevStep">
          <a-icon type="left" /> 上一步
        </a-button>
        <a-button type="primary" @click="restartProcess"> 直接处理 </a-button>
      </div>
    </div>

    <!-- 处理日志（其他步骤） -->
    <div v-if="currentStep !== 5 && logs.length > 0" style="margin: 16px 0">
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
import { ref, nextTick, computed } from "vue";
import { useRouter } from "vue-router";
import PluginTemplate from "@/components/PluginTemplate.vue";
import { runPy } from "@/utils/py";

const router = useRouter();

const pluginTemplate = ref(null);
const currentStep = ref(0);
const files = ref([]);
const replacementRules = ref([
  { findText: "", replaceText: "", matchMode: "normal" },
]);
const isProcessing = ref(false);
const progress = ref(0);
const logs = ref([]);
const fileInput = ref(null);

// 处理结果相关变量
const processedFiles = ref([]);
const totalReplacements = ref(0);
const activeLogKey = ref(["1"]);
const resultPanels = ref(["result", "details"]);

// 处理结果表格列配置
const resultColumns = [
  { title: "序号", dataIndex: "index", key: "index", width: 80 },
  { title: "处理的文件名", dataIndex: "name", key: "name" },
  { title: "状态", dataIndex: "status", key: "status", width: 100 },
  {
    title: "替换次数",
    dataIndex: "replacements",
    key: "replacements",
    width: 120,
  },
  {
    title: "处理耗时 (秒)",
    dataIndex: "time",
    key: "time",
    width: 120,
    customRender: () => "0.09",
  },
  { title: "处理后的路径", dataIndex: "downloadName", key: "path", width: 200 },
  {
    title: "操作",
    dataIndex: "action",
    key: "action",
    width: 100,
    fixed: "right",
  },
];

// 高级设置
const settings = ref({
  caseSensitive: false,
  matchEntireCell: false,
  ignoreHiddenCells: true,
  sheetOption: "all",
  selectedSheets: "",
  rangeOption: "all",
  customRange: "",
  enableDetailedLogs: true,
  backupOriginal: false,
  outputLocation: "same",
  customOutputDir: "",
  filenameMode: "append",
  filenameSuffix: "_处理后",
});

// 读取 Python 脚本
const getPythonScript = async () => {
  const response = await fetch("/plugins/replace-content/worker.py");
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
      logs.value.push("请先添加需要处理的Excel文件");
      return;
    }
    currentStep.value = 1;
    logs.value.push("进入设置处理规则步骤...");
  } else if (currentStep.value === 1) {
    // 进入步骤2：设置其他选项
    if (
      replacementRules.value.length === 0 ||
      replacementRules.value.some((rule) => !rule.findText)
    ) {
      logs.value.push("请确保所有替换规则都已填写完整");
      return;
    }
    currentStep.value = 2;
    logs.value.push("进入设置其他选项步骤...");
  } else if (currentStep.value === 2) {
    // 进入步骤3：设置输出目录
    currentStep.value = 3;
    logs.value.push("进入设置输出目录步骤...");
  } else if (currentStep.value === 3) {
    // 进入步骤4：开始处理 - 验证输出目录设置
    if (settings.outputLocation === "custom" && !settings.customOutputDir) {
      logs.value.push('请选择输出目录或切换为"与源文件相同目录"');
      return;
    }
    currentStep.value = 4;
    logs.value.push("进入开始处理步骤...");
  } else if (currentStep.value === 4) {
    // 进入步骤5：处理结果 - 实际处理文件
    await processFiles();
    currentStep.value = 5;
    logs.value.push("进入处理结果步骤...");
  }
};

// 上一步
const handlePrevStep = () => {
  if (currentStep.value === 1) {
    // 返回步骤0：文件选择
    currentStep.value = 0;
    logs.value.push("返回文件选择步骤...");
  } else if (currentStep.value === 2) {
    // 返回步骤1：设置处理规则
    currentStep.value = 1;
    logs.value.push("返回设置处理规则步骤...");
  } else if (currentStep.value === 3) {
    // 返回步骤2：设置其他选项
    currentStep.value = 2;
    logs.value.push("返回设置其他选项步骤...");
  } else if (currentStep.value === 4) {
    // 返回步骤3：设置输出目录
    currentStep.value = 3;
    logs.value.push("返回设置输出目录步骤...");
  } else if (currentStep.value === 5) {
    // 返回步骤4：处理步骤
    currentStep.value = 4;
    logs.value.push("返回处理步骤...");
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

// 添加替换规则
const addReplacementRule = () => {
  replacementRules.value.push({
    findText: "",
    replaceText: "",
    matchMode: "normal",
  });
};

// 删除替换规则
const removeReplacementRule = (index) => {
  if (replacementRules.value.length > 1) {
    replacementRules.value.splice(index, 1);
  } else {
    logs.value.push("至少需要保留一条替换规则");
  }
};

// 获取匹配选项文本
const getMatchOptionsText = () => {
  const options = [];
  if (settings.caseSensitive) options.push("区分大小写");
  if (settings.matchEntireCell) options.push("匹配整个单元格");
  if (settings.ignoreHiddenCells) options.push("忽略隐藏单元格");
  return options.length > 0 ? options.join(", ") : "默认";
};

// 获取工作表选项文本
const getSheetOptionText = () => {
  const options = {
    all: "处理所有工作表",
    active: "只处理当前工作表",
    selected: `指定工作表：${settings.selectedSheets}`,
  };
  return options[settings.sheetOption] || "处理所有工作表";
};

// 获取处理范围文本
const getRangeOptionText = () => {
  if (settings.rangeOption === "custom") {
    return `自定义范围：${settings.customRange}`;
  }
  const ranges = {
    all: "整个工作表",
    data: "仅数据区域",
  };
  return ranges[settings.rangeOption] || "整个工作表";
};

// 获取输出位置文本
const getOutputLocationText = () => {
  if (settings.outputLocation === "same") {
    return "与源文件相同目录";
  } else {
    return settings.customOutputDir || "未选择输出目录";
  }
};

// 选择输出目录
const handleSelectOutputDir = () => {
  // 在Electron环境中，可以使用dialog.showOpenDialog来选择目录
  // 在浏览器环境中，我们使用模拟数据
  // 以下是浏览器环境的模拟实现
  const mockDir = "C:\\ExcelFiles\\Output";
  settings.customOutputDir = mockDir;
  logs.value.push(`已选择输出目录：${mockDir}`);
};

// 处理文件
const processFiles = async () => {
  if (files.value.length === 0) return;

  isProcessing.value = true;
  logs.value = ["开始处理文件..."];
  progress.value = 10;
  processedFiles.value = [];
  totalReplacements.value = 0;

  try {
    // 显示 Pyodide 加载遮罩层
    if (pluginTemplate.value) {
      pluginTemplate.value.pyodideLoading = true;
    }

    const script = await getPythonScript();
    progress.value = 30;

    logs.value.push(`替换规则数量：${replacementRules.value.length}`);
    replacementRules.value.forEach((rule, index) => {
      logs.value.push(
        `规则 ${index + 1}: 查找"${rule.findText}" → 替换为"${rule.replaceText || "（删除）"}" (${rule.matchMode === "regex" ? "正则" : "普通"})`,
      );
    });
    logs.value.push(`高级设置：${JSON.stringify(settings)}`);

    // 依次处理每个文件
    for (let i = 0; i < files.value.length; i++) {
      const fileItem = files.value[i];
      logs.value.push(`正在处理文件：${fileItem.name}`);

      // 将File对象转换为Uint8Array
      const fileBuffer = await fileItem.file.arrayBuffer();
      const fileUint8Array = new Uint8Array(fileBuffer);

      // 构建统一格式的输入数据
      const processingData = {
        type: "single",
        file: fileUint8Array,
        fileName: fileItem.name,
        settings: {
          ...settings,
          replacementRules: replacementRules.value,
        },
      };

      const result = await runPy(script, processingData);
      progress.value = 30 + Math.round(((i + 1) / files.value.length) * 50);

      logs.value.push(`${fileItem.name} 处理完成！`);
      logs.value.push(...result.logs);

      // 处理结果统计
      let replacements = 0;
      if (result.details?.statistics) {
        replacements = result.details.statistics.totalReplacements || 0;
        totalReplacements.value += replacements;

        logs.value.push("文件处理统计:");
        logs.value.push(
          `  - 工作表数: ${result.details.statistics.totalSheets}`,
        );
        logs.value.push(
          `  - 处理单元格数: ${result.details.statistics.totalCells}`,
        );
        logs.value.push(
          `  - 替换次数: ${result.details.statistics.totalReplacements}`,
        );
        logs.value.push(
          `  - 有效规则数: ${result.details.statistics.validRules}`,
        );
      }

      // 准备下载URL
      let downloadUrl = null;
      let downloadName = fileItem.name;
      if (result.success && result.buffer) {
        const blob = new Blob([result.buffer], {
          type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        });
        downloadUrl = URL.createObjectURL(blob);

        if (settings.filenameMode === "append") {
          const [name, ext] = downloadName.split(".");
          downloadName = `${name}${settings.filenameSuffix}.${ext}`;
        } else if (
          settings.filenameMode === "custom" &&
          settings.customFilename
        ) {
          const ext = downloadName.split(".").pop();
          downloadName = `${settings.customFilename}.${ext}`;
        }
      } else {
        logs.value.push(`警告: 无法处理 ${fileItem.name}，可能处理失败`);
      }

      // 添加到处理结果列表
      processedFiles.value.push({
        key: fileItem.key,
        index: i + 1,
        name: fileItem.name,
        originalName: fileItem.name,
        downloadName: downloadName,
        downloadUrl: downloadUrl,
        status: result.success ? "success" : "error",
        replacements: replacements,
        error: result.error || null,
      });
    }

    logs.value.push("所有文件处理完成！");
    logs.value.push(`总替换次数：${totalReplacements.value} 次`);
    progress.value = 100;
  } catch (error) {
    logs.value.push(`错误：${error.message}`);
    console.error("Processing error:", error);
  } finally {
    isProcessing.value = false;
    // 隐藏 Pyodide 加载遮罩层
    if (pluginTemplate.value) {
      pluginTemplate.value.pyodideLoading = false;
    }
  }
};

// 下载单个文件
const handleDownload = (file) => {
  if (!file.downloadUrl) {
    logs.value.push(`无法下载文件 ${file.name}：没有有效的下载链接`);
    return;
  }

  const a = document.createElement("a");
  a.href = file.downloadUrl;
  a.download = file.downloadName;
  a.click();
  logs.value.push(`正在下载文件：${file.downloadName}`);
};

// 下载全部结果
const handleDownloadAll = () => {
  let successCount = 0;
  processedFiles.value.forEach((file) => {
    if (file.downloadUrl) {
      handleDownload(file);
      successCount++;
    }
  });

  logs.value.push(`开始下载全部文件：共 ${successCount} 个文件`);
};

// 返回主界面
const navigateBack = () => {
  // 清理资源
  processedFiles.value.forEach((file) => {
    if (file.downloadUrl) {
      URL.revokeObjectURL(file.downloadUrl);
    }
  });

  // 重置状态
  currentStep.value = 0;
  files.value = [];
  logs.value = [];
  processedFiles.value = [];
  totalReplacements.value = 0;

  // 导航到主界面
  router.push("/");
};

// 重新处理
const restartProcess = () => {
  // 清理资源
  processedFiles.value.forEach((file) => {
    if (file.downloadUrl) {
      URL.revokeObjectURL(file.downloadUrl);
    }
  });

  // 重置处理状态，返回步骤1
  currentStep.value = 0;
  isProcessing.value = false;
  progress.value = 0;
  logs.value = [];
  processedFiles.value = [];
  totalReplacements.value = 0;

  logs.value.push("准备重新处理文件...");
};
</script>

<style scoped>
.replace-content {
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

.replacement-rules {
  margin-bottom: 20px;
}

.rule-item {
  display: flex;
  align-items: center;
  width: 100%;
}

.rule-index {
  width: 32px;
  height: 32px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  margin-right: 12px;
}

.rule-content {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.rule-content .ant-form-item {
  margin-bottom: 8px;
}

.rule-summary {
  padding-left: 20px;
  margin: 8px 0;
}

.rule-summary li {
  margin-bottom: 4px;
  font-size: 13px;
}

/* 处理结果样式 */
.step-result {
  padding: 0;
}

/* 处理完成提示 */
.success-banner {
  display: flex;
  align-items: center;
  background: #f0f9eb;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.success-icon {
  margin-right: 20px;
}

.success-info h2 {
  margin: 0 0 8px 0;
  color: #389e0d;
  font-size: 20px;
}

.success-info p {
  margin: 0;
  color: #52c41a;
  font-size: 14px;
}

/* 日志区域 */
.logs-container {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
  margin-bottom: 16px;
}

.logs-content {
  background: #ffffff;
  padding: 16px;
  max-height: 200px;
  overflow-y: auto;
  font-family: monospace;
  white-space: pre-wrap;
  border-radius: 0 0 8px 8px;
}

.log-item {
  margin-bottom: 4px;
  font-size: 12px;
  color: #389e0d;
}

/* 处理结果折叠面板 */
.processing-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #fafafa;
  padding: 16px;
  border-radius: 8px;
}

.result-item {
  display: flex;
  align-items: center;
}

.result-label {
  font-weight: 500;
  width: 100px;
  color: #666;
  font-size: 14px;
}

.result-value {
  color: #333;
  font-size: 14px;
  flex: 1;
}

.result-value.success {
  color: #52c41a;
}

.result-value.error {
  color: #f5222d;
}

/* 处理结果表格 */
.result-table-container {
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
}

.file-path {
  font-size: 12px;
  color: #165dff;
}

/* 操作按钮 */
.result-actions {
  display: flex;
  justify-content: flex-start;
  gap: 12px;
  margin: 16px;
  padding: 16px 0;
  border-top: 1px solid #f0f0f0;
}

/* 折叠面板样式 */
:deep(.ant-collapse) {
  background: transparent;
  border: none;
}

:deep(.ant-collapse-item) {
  background: #ffffff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}

:deep(.ant-collapse-header) {
  background: #fafafa;
  font-weight: 500;
  padding: 12px 16px;
}

:deep(.ant-collapse-content-box) {
  padding: 16px;
}
</style>
