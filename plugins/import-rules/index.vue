<template>
  <div class="import-rules">
    <PluginTemplate
      plugin-title="导入规则修改内容"
      info-message="当不同的 Excel 文档有不同的修改规则时，可以通过导入规则文件进行批量修改"
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
      <input
        ref="rulesInput"
        type="file"
        accept=".json"
        @change="handleRulesFileChange"
      />
    </div>

    <!-- 步骤1：上传Excel文件 -->
    <div v-if="currentStep === 1" class="step-content">
      <h3>上传Excel文件</h3>
      <a-upload-dragger
        name="file"
        :multiple="true"
        :show-upload-list="false"
        accept=".xlsx,.xls"
        :before-upload="handleDragUpload"
      >
        <p class="ant-upload-drag-icon">
          <a-icon type="inbox" style="font-size: 48px; color: #165dff" />
        </p>
        <p class="ant-upload-text">点击或拖拽文件到此处上传</p>
        <p class="ant-upload-hint">支持上传多个Excel文件</p>
      </a-upload-dragger>
    </div>

    <!-- 步骤2：上传规则文件 -->
    <div v-if="currentStep === 2" class="step-content">
      <h3>上传规则文件</h3>
      <div class="rules-upload-section">
        <a-upload
          :show-upload-list="false"
          :before-upload="handleRulesFileUpload"
          accept=".json"
        >
          <div class="rules-upload">
            <div v-if="!rulesFile" style="padding: 24px; text-align: center">
              <a-icon
                type="file-text"
                style="font-size: 48px; color: #165dff"
              ></a-icon>
              <p style="margin: 16px 0">点击上传规则文件</p>
              <a-button type="primary">选择JSON文件</a-button>
              <div style="margin: 16px 0; color: #999; font-size: 12px">
                <div style="margin-bottom: 8px">规则文件格式示例：</div>
                <pre
                  style="
                    background: #f5f5f5;
                    padding: 8px;
                    text-align: left;
                    font-size: 11px;
                    overflow-x: auto;
                  "
                >
{
  "rules": [
    {
      "findText": "旧内容",
      "replaceText": "新内容",
      "matchMode": "normal"
    }
  ],
  "settings": {
    "caseSensitive": false,
    "matchEntireCell": false
  }
}
                </pre>
              </div>
            </div>
            <div v-else style="padding: 24px; text-align: center">
              <a-icon
                type="check-circle"
                style="font-size: 48px; color: #52c41a"
              ></a-icon>
              <p style="margin: 16px 0">规则文件已上传</p>
              <a-tag color="green">{{ rulesFile.name }}</a-tag>
              <a-button
                type="default"
                style="margin-left: 12px"
                @click="
                  rulesFile = null;
                  rulesContent = null;
                "
              >
                重新选择
              </a-button>
            </div>
          </div>
        </a-upload>
      </div>
    </div>

    <!-- 步骤3：规则预览 -->
    <div v-if="currentStep === 3" class="step-content">
      <h3>规则预览</h3>
      <div v-if="rulesContent && rulesContent.rules" class="rules-preview">
        <h4>替换规则</h4>
        <a-list
          :data-source="rulesContent.rules"
          bordered
          size="small"
          style="margin-bottom: 20px"
        >
          <template #renderItem="{ item, index }">
            <a-list-item>
              <div class="rule-item">
                <div class="rule-index">{{ index + 1 }}</div>
                <div class="rule-content">
                  <p><strong>查找:</strong> "{{ item.findText }}"</p>
                  <p>
                    <strong>替换为:</strong> "{{
                      item.replaceText || "（删除）"
                    }}"
                  </p>
                  <p>
                    <strong>匹配模式:</strong>
                    {{ item.matchMode === "regex" ? "正则表达式" : "普通文本" }}
                  </p>
                </div>
              </div>
            </a-list-item>
          </template>
        </a-list>

        <h4>高级设置</h4>
        <div class="settings-preview">
          <a-descriptions bordered column="2">
            <a-descriptions-item label="区分大小写">
              {{ rulesContent.settings?.caseSensitive ? "是" : "否" }}
            </a-descriptions-item>
            <a-descriptions-item label="匹配整个单元格">
              {{ rulesContent.settings?.matchEntireCell ? "是" : "否" }}
            </a-descriptions-item>
            <a-descriptions-item label="忽略隐藏单元格">
              {{ rulesContent.settings?.ignoreHiddenCells ? "是" : "否" }}
            </a-descriptions-item>
            <a-descriptions-item label="处理范围">
              {{ getRangeOptionText() }}
            </a-descriptions-item>
          </a-descriptions>
        </div>
      </div>
      <div v-else class="no-rules">
        <a-empty description="未加载规则内容" />
      </div>
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
          <p>
            <strong>替换规则数量：</strong
            >{{ rulesContent?.rules?.length || 0 }}
          </p>
          <p><strong>规则文件：</strong>{{ rulesFile?.name || "未选择" }}</p>
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
const rulesFile = ref(null);
const rulesContent = ref(null);
const isProcessing = ref(false);
const progress = ref(0);
const logs = ref([]);
const fileInput = ref(null);
const rulesInput = ref(null);

// 处理范围选项
const rangeOption = ref("all");
const customRange = ref("");

// 获取处理范围文本
const getRangeOptionText = () => {
  if (rulesContent?.settings?.rangeOption === "custom") {
    return `自定义范围：${rulesContent.settings.customRange}`;
  }
  const ranges = {
    all: "整个工作表",
    data: "仅数据区域",
    custom: "自定义范围",
  };
  return ranges[rulesContent?.settings?.rangeOption || "all"] || "整个工作表";
};

// 读取 Python 脚本
const getPythonScript = async () => {
  const response = await fetch("/plugins/import-rules/worker.py");
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
    // 进入步骤1：上传Excel文件
    currentStep.value = 1;
    logs.value.push("进入上传Excel文件步骤...");
  } else if (currentStep.value === 1) {
    // 进入步骤2：上传规则文件
    if (files.value.length === 0) {
      logs.value.push("请先添加需要处理的Excel文件");
      return;
    }
    currentStep.value = 2;
    logs.value.push("进入上传规则文件步骤...");
  } else if (currentStep.value === 2) {
    // 进入步骤3：规则预览
    if (
      !rulesContent ||
      !rulesContent.rules ||
      rulesContent.rules.length === 0
    ) {
      logs.value.push("请先上传有效的规则文件");
      return;
    }
    currentStep.value = 3;
    logs.value.push("进入规则预览步骤...");
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
        path: file.name,
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

// 拖拽上传
const handleDragUpload = (file) => {
  const fileItem = {
    key: `${file.name}-${Date.now()}`,
    index: files.value.length + 1,
    name: file.name,
    path: file.name,
    extension: file.name.split(".").pop(),
    createTime: new Date(file.lastModified).toLocaleString(),
    modifyTime: new Date(file.lastModified).toLocaleString(),
    file: file,
  };
  files.value.push(fileItem);

  // 更新插件模板的文件列表
  nextTick(() => {
    if (pluginTemplate.value) {
      pluginTemplate.value.files = files.value;
    }
  });

  return false; // 阻止默认上传
};

// 规则文件选择变化
const handleRulesFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    handleRulesFileUpload(file);
  }
  e.target.value = ""; // 清空 input
};

// 规则文件上传
const handleRulesFileUpload = (file) => {
  rulesFile.value = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const content = JSON.parse(e.target.result);
      rulesContent.value = content;
      logs.value.push("规则文件解析成功");
    } catch (error) {
      logs.value.push(`规则文件解析错误: ${error.message}`);
      rulesContent.value = null;
      rulesFile.value = null;
    }
  };
  reader.readAsText(file);
  return false; // 阻止默认上传
};

// 处理文件
const processFiles = async () => {
  if (files.value.length === 0 || !rulesContent || !rulesContent.rules) return;

  isProcessing.value = true;
  logs.value = ["开始处理文件..."];
  progress.value = 10;

  try {
    const script = await getPythonScript();
    progress.value = 30;

    logs.value.push(`规则数量：${rulesContent.rules.length}`);
    logs.value.push(`设置参数：${JSON.stringify(rulesContent.settings || {})}`);

    // 依次处理每个文件
    for (let i = 0; i < files.value.length; i++) {
      const fileItem = files.value[i];
      logs.value.push(`正在处理文件：${fileItem.name}`);

      // 构建统一格式的输入数据
      const processingData = {
        type: "single",
        file: fileItem.file,
        fileName: fileItem.name,
        settings: {
          ...(rulesContent.settings || {}),
          replacementRules: rulesContent.rules,
        },
      };

      const result = await runPy(script, processingData);
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
.import-rules {
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

.rules-upload-section {
  max-width: 600px;
}

.rules-upload {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  transition: all 0.3s;
  cursor: pointer;
  min-height: 200px;
  background: #fafafa;
}

.rules-upload:hover {
  border-color: #165dff;
  background: #f0f7ff;
}

.rules-preview {
  margin-top: 20px;
}

.rule-item {
  display: flex;
  align-items: flex-start;
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
  flex-shrink: 0;
}

.rule-content {
  flex: 1;
}

.rule-content p {
  margin: 4px 0;
}

.settings-preview {
  margin-top: 20px;
}

.no-rules {
  padding: 40px 0;
  text-align: center;
}
</style>
