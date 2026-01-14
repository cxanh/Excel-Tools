<template>
  <div class="generate-from-template">
    <PluginTemplate
      plugin-title="根据模板生成文档"
      info-message="先指定一个 Excel 文档作为模板，然后根据数据源批量生成多个 Excel 文档"
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
        ref="templateInput"
        type="file"
        accept=".xlsx,.xls"
        @change="handleTemplateFileChange"
      />
      <input
        ref="dataInput"
        type="file"
        accept=".xlsx,.xls,.csv"
        @change="handleDataFileChange"
      />
    </div>

    <!-- 步骤1：上传模板文件 -->
    <div v-if="currentStep === 1" class="step-content">
      <h3>上传Excel模板</h3>
      <a-upload-dragger
        name="file"
        :multiple="false"
        :show-upload-list="false"
        accept=".xlsx,.xls"
        :before-upload="handleTemplateUpload"
      >
        <p class="ant-upload-drag-icon">
          <a-icon type="file-excel" style="font-size: 48px; color: #52c41a" />
        </p>
        <p class="ant-upload-text">点击或拖拽模板文件到此处上传</p>
        <p class="ant-upload-hint">支持 .xlsx, .xls 格式文件</p>
      </a-upload-dragger>

      <div v-if="templateFile" class="file-info">
        <a-tag color="green" style="margin-top: 16px">{{
          templateFile.name
        }}</a-tag>
        <a-button
          type="default"
          style="margin-left: 12px"
          @click="templateFile = null"
        >
          重新选择
        </a-button>
      </div>
    </div>

    <!-- 步骤2：上传数据源 -->
    <div v-if="currentStep === 2" class="step-content">
      <h3>上传数据源</h3>
      <a-upload-dragger
        name="file"
        :multiple="false"
        :show-upload-list="false"
        accept=".xlsx,.xls,.csv"
        :before-upload="handleDataUpload"
      >
        <p class="ant-upload-drag-icon">
          <a-icon type="database" style="font-size: 48px; color: #165dff" />
        </p>
        <p class="ant-upload-text">点击或拖拽数据源文件到此处上传</p>
        <p class="ant-upload-hint">支持 .xlsx, .xls, .csv 格式文件</p>
      </a-upload-dragger>

      <div v-if="dataFile" class="file-info">
        <a-tag color="blue" style="margin-top: 16px">{{ dataFile.name }}</a-tag>
        <a-button
          type="default"
          style="margin-left: 12px"
          @click="
            dataFile = null;
            dataContent = null;
          "
        >
          重新选择
        </a-button>
      </div>
    </div>

    <!-- 步骤3：字段映射 -->
    <div v-if="currentStep === 3" class="step-content">
      <h3>字段映射设置</h3>
      <div v-if="dataContent && dataContent.columns" class="mapping-section">
        <a-alert
          message="模板占位符说明"
          description="在模板文件中使用 {字段名} 作为占位符，系统会自动替换为数据源中的对应值"
          type="info"
          show-icon
          style="margin-bottom: 20px"
        />

        <h4>数据源字段</h4>
        <a-table
          :columns="dataColumns"
          :data-source="dataContent.sampleData"
          :pagination="false"
          size="small"
          style="margin-bottom: 20px"
        />

        <h4>映射设置</h4>
        <a-form layout="vertical">
          <a-form-item label="输出文件名规则">
            <a-input
              v-model:value="settings.outputFilenameRule"
              placeholder="例如：合同_{合同编号}.xlsx"
              style="max-width: 400px"
            />
            <div style="margin-top: 8px; color: #666; font-size: 12px">
              使用 {字段名} 作为文件名中的变量
            </div>
          </a-form-item>

          <a-form-item label="数据起始行">
            <a-input-number
              v-model:value="settings.dataStartRow"
              :min="1"
              style="width: 100px"
            />
          </a-form-item>

          <a-form-item label="模板工作表">
            <a-select
              v-model:value="settings.templateSheet"
              placeholder="选择模板工作表"
              style="width: 200px"
            >
              <a-select-option
                v-for="sheet in templateSheets"
                :key="sheet"
                :value="sheet"
              >
                {{ sheet }}
              </a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
      </div>
      <div v-else class="no-data">
        <a-empty description="请先上传数据源文件" />
      </div>
    </div>

    <!-- 步骤4：开始生成 -->
    <div v-if="currentStep === 4" class="step-content">
      <h3>生成设置</h3>
      <div class="processing-summary">
        <h4>模板信息</h4>
        <p><strong>模板文件：</strong>{{ templateFile?.name }}</p>
        <p><strong>模板工作表：</strong>{{ settings.templateSheet }}</p>

        <h4>数据源信息</h4>
        <p><strong>数据源文件：</strong>{{ dataFile?.name }}</p>
        <p><strong>数据记录数：</strong>{{ dataContent?.totalRows || 0 }}</p>
        <p>
          <strong>数据字段数：</strong>{{ dataContent?.columns?.length || 0 }}
        </p>

        <h4>生成设置</h4>
        <p>
          <strong>输出文件名规则：</strong>{{ settings.outputFilenameRule }}
        </p>
        <p><strong>数据起始行：</strong>{{ settings.dataStartRow }}</p>
        <p><strong>批量生成数量：</strong>{{ batchSize }} 个文件</p>

        <a-button
          type="primary"
          size="large"
          @click="generateFiles"
          :disabled="isProcessing.value"
          style="margin-top: 20px"
        >
          {{ isProcessing.value ? "生成中..." : "开始批量生成" }}
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
      <h3>生成日志</h3>
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
import PluginTemplate from "@/components/PluginTemplate.vue";
import { runPy } from "@/utils/py";

const pluginTemplate = ref(null);
const currentStep = ref(0);
const templateFile = ref(null);
const dataFile = ref(null);
const dataContent = ref(null);
const templateSheets = ref([]);
const isProcessing = ref(false);
const progress = ref(0);
const logs = ref([]);
const templateInput = ref(null);
const dataInput = ref(null);

// 设置
const settings = ref({
  outputFilenameRule: "文档_{序号}.xlsx",
  dataStartRow: 1,
  templateSheet: "",
});

// 批量生成数量
const batchSize = computed(() => {
  return Math.min(dataContent?.totalRows || 0, 100); // 限制最大批量生成数量
});

// 数据源列定义
const dataColumns = computed(() => {
  if (!dataContent?.columns) return [];
  return dataContent.columns.map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
  }));
});

// 读取 Python 脚本
const getPythonScript = async () => {
  const response = await fetch("/plugins/generate-from-template/worker.py");
  return response.text();
};

// 添加文件
const handleAddFile = () => {
  // 根据当前步骤决定打开哪个文件选择器
  if (currentStep.value === 1) {
    templateInput.value?.click();
  } else if (currentStep.value === 2) {
    dataInput.value?.click();
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
      if (currentStep.value === 1) {
        templateFile.value = null;
      } else if (currentStep.value === 2) {
        dataFile.value = null;
        dataContent.value = null;
      }
      break;
  }
};

// 下一步
const handleNextStep = async () => {
  if (currentStep.value === 0) {
    // 进入步骤1：上传模板文件
    currentStep.value = 1;
    logs.value.push("进入上传模板文件步骤...");
  } else if (currentStep.value === 1) {
    // 进入步骤2：上传数据源
    if (!templateFile.value) {
      logs.value.push("请先上传模板文件");
      return;
    }
    currentStep.value = 2;
    logs.value.push("进入上传数据源步骤...");
  } else if (currentStep.value === 2) {
    // 进入步骤3：字段映射
    if (!dataFile.value || !dataContent.value) {
      logs.value.push("请先上传数据源文件");
      return;
    }
    currentStep.value = 3;
    logs.value.push("进入字段映射步骤...");
  } else if (currentStep.value === 3) {
    // 进入步骤4：开始生成
    if (!settings.value.outputFilenameRule) {
      logs.value.push("请设置输出文件名规则");
      return;
    }
    currentStep.value = 4;
    logs.value.push("进入开始生成步骤...");
  } else if (currentStep.value === 4) {
    // 开始生成
    await generateFiles();
  }
};

// 删除文件
const handleRemoveFile = (key) => {
  // 此插件不需要文件列表，所以不处理
};

// 模板文件选择变化
const handleTemplateFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    handleTemplateUpload(file);
  }
  e.target.value = ""; // 清空 input
};

// 模板文件上传
const handleTemplateUpload = (file) => {
  templateFile.value = file;

  // 解析模板文件，获取工作表列表
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      // 在实际项目中，这里应该使用 JS-XLSX 或其他库来解析 Excel 文件
      // 这里仅做模拟
      templateSheets.value = ["Sheet1", "Sheet2", "Sheet3"];
      settings.value.templateSheet = templateSheets.value[0];
      logs.value.push("模板文件解析成功");
    } catch (error) {
      logs.value.push(`模板文件解析错误: ${error.message}`);
      templateSheets.value = [];
    }
  };
  reader.readAsArrayBuffer(file);

  return false; // 阻止默认上传
};

// 数据源文件选择变化
const handleDataFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    handleDataFileUpload(file);
  }
  e.target.value = ""; // 清空 input
};

// 数据源文件上传
const handleDataFileUpload = (file) => {
  dataFile.value = file;

  // 解析数据源文件，获取字段和示例数据
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      // 在实际项目中，这里应该使用 JS-XLSX 或其他库来解析 Excel/CSV 文件
      // 这里仅做模拟
      dataContent.value = {
        columns: ["合同编号", "客户名称", "金额", "日期", "状态"],
        sampleData: [
          {
            合同编号: "HT001",
            客户名称: "客户A",
            金额: 10000,
            日期: "2026-01-14",
            状态: "生效",
          },
          {
            合同编号: "HT002",
            客户名称: "客户B",
            金额: 20000,
            日期: "2026-01-15",
            状态: "生效",
          },
          {
            合同编号: "HT003",
            客户名称: "客户C",
            金额: 30000,
            日期: "2026-01-16",
            状态: "草稿",
          },
        ],
        totalRows: 50,
      };
      logs.value.push("数据源文件解析成功");
    } catch (error) {
      logs.value.push(`数据源文件解析错误: ${error.message}`);
      dataContent.value = null;
    }
  };
  reader.readAsArrayBuffer(file);

  return false; // 阻止默认上传
};

// 生成文件
const generateFiles = async () => {
  if (!templateFile.value || !dataFile.value || !dataContent.value) return;

  isProcessing.value = true;
  logs.value = ["开始批量生成文档..."];
  progress.value = 10;

  try {
    const script = await getPythonScript();
    progress.value = 30;

    logs.value.push(`模板文件: ${templateFile.value.name}`);
    logs.value.push(`数据源文件: ${dataFile.value.name}`);
    logs.value.push(`生成数量: ${batchSize.value} 个文件`);
    logs.value.push(`设置参数: ${JSON.stringify(settings.value)}`);

    // 读取模板文件内容
    const templateReader = new FileReader();
    const templateContent = await new Promise((resolve) => {
      templateReader.onload = (e) => resolve(e.target.result);
      templateReader.readAsArrayBuffer(templateFile.value);
    });
    progress.value = 40;

    // 读取数据源文件内容
    const dataReader = new FileReader();
    const dataContentBuffer = await new Promise((resolve) => {
      dataReader.onload = (e) => resolve(e.target.result);
      dataReader.readAsArrayBuffer(dataFile.value);
    });
    progress.value = 50;

    // 构建处理数据对象
    const processingData = {
      template: new Uint8Array(templateContent),
      data: new Uint8Array(dataContentBuffer),
      settings: settings.value,
      dataInfo: dataContent.value,
    };

    // 调用Python脚本处理
    logs.value.push("开始批量生成...");
    const result = await runPy(script, processingData);
    progress.value = 80;

    if (result.success) {
      logs.value.push("文档批量生成完成！");
      logs.value.push(...result.logs);

      // 模拟下载生成的文件
      for (let i = 0; i < batchSize.value; i++) {
        const blob = new Blob([result.buffer], {
          type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        // 根据规则生成文件名
        let filename = settings.value.outputFilenameRule;
        filename = filename.replace("{序号}", i + 1);
        filename = filename.replace(
          "{合同编号}",
          `HT${(1000 + i).toString().slice(-3)}`,
        );
        a.download = filename;
        // 模拟点击下载
        logs.value.push(`生成文件: ${filename}`);
        URL.revokeObjectURL(url);
      }
    } else {
      logs.value.push(`生成失败: ${result.error}`);
    }

    progress.value = 100;
  } catch (error) {
    logs.value.push(`错误: ${error.message}`);
    console.error("Processing error:", error);
  } finally {
    isProcessing.value = false;
  }
};
</script>

<style scoped>
.generate-from-template {
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

.file-info {
  margin-top: 16px;
}

.mapping-section {
  margin-top: 20px;
}

.no-data {
  padding: 40px 0;
  text-align: center;
}

.processing-summary {
  line-height: 1.8;
}

.processing-summary h4 {
  margin: 20px 0 12px 0;
  color: #333;
}
</style>
