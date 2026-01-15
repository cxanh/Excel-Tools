<template>
  <div class="replace-content-plugin">
    <!-- 插件标题和描述 -->
    <div class="plugin-header">
      <h2>按规则修改 Excel 内容</h2>
      <p>用于批量在 Excel 文档中查找并替换/删除指定内容</p>
    </div>

    <!-- 帮助文档插槽 -->
    <template #help-content>
      <div class="help-documentation">
        <h1>按规则修改 Excel 内容</h1>

        <h2>功能介绍</h2>
        <p>
          该插件用于批量在 Excel 文档中查找并替换或删除指定内容，支持以下功能：
        </p>
        <ul>
          <li>精确匹配或正则表达式匹配</li>
          <li>区分大小写选项</li>
          <li>支持删除指定内容</li>
          <li>可选择特定列进行处理</li>
          <li>多规则并行处理</li>
        </ul>

        <h2>操作步骤</h2>
        <ol>
          <li>
            <strong>上传文件</strong>：点击"选择 Excel 文件"按钮，选择要处理的
            Excel 文件
          </li>
          <li>
            <strong>配置替换规则</strong>：
            <ul>
              <li>点击"添加替换规则"按钮，添加一条新的替换规则</li>
              <li>输入"查找内容"：要查找的文本或正则表达式</li>
              <li>
                输入"替换为"：替换后的文本（如果选择了"删除内容"，则此选项无效）
              </li>
              <li>选择"匹配类型"：精确匹配或正则表达式</li>
              <li>选择"区分大小写"：是否区分大小写</li>
              <li>选择"删除内容"：是否直接删除查找的内容</li>
              <li>选择"处理列"：可选，指定要处理的列</li>
            </ul>
          </li>
          <li><strong>执行修改</strong>：点击"开始修改"按钮，执行替换操作</li>
          <li><strong>查看结果</strong>：修改完成后，查看修改统计结果</li>
          <li>
            <strong>下载文件</strong
            >：点击"下载处理后的文件"按钮，下载修改后的文件
          </li>
        </ol>

        <h2>使用示例</h2>
        <h3>示例1：替换文本</h3>
        <p>将所有"旧公司"替换为"新公司"</p>
        <ul>
          <li>查找内容：旧公司</li>
          <li>替换为：新公司</li>
          <li>匹配类型：精确匹配</li>
          <li>区分大小写：否</li>
          <li>删除内容：否</li>
        </ul>

        <h3>示例2：使用正则表达式</h3>
        <p>将所有手机号码格式统一为xxx-xxxx-xxxx</p>
        <ul>
          <li>查找内容：(\d{3})(\d{4})(\d{4})</li>
          <li>替换为：$1-$2-$3</li>
          <li>匹配类型：正则表达式</li>
          <li>区分大小写：否</li>
        </ul>

        <h3>示例3：删除内容</h3>
        <p>删除所有括号及括号内的内容</p>
        <ul>
          <li>查找内容：\(.*?\)</li>
          <li>匹配类型：正则表达式</li>
          <li>区分大小写：否</li>
          <li>删除内容：是</li>
        </ul>

        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>单个文件大小限制为 10MB</li>
          <li>正则表达式使用 Python 正则语法</li>
          <li>处理大型文件可能需要较长时间，请耐心等待</li>
          <li>建议先在小文件上测试规则，确保规则正确后再处理大型文件</li>
        </ul>

        <h2>常见问题</h2>
        <h3>Q: 为什么有些内容没有被替换？</h3>
        <p>A: 可能的原因：</p>
        <ul>
          <li>匹配类型设置不正确</li>
          <li>区分大小写选项设置不正确</li>
          <li>正则表达式语法错误</li>
          <li>内容存在不可见字符</li>
        </ul>

        <h3>Q: 如何处理多个工作表？</h3>
        <p>
          A: 系统默认处理所有工作表，您也可以在"选择工作表"中指定要处理的工作表
        </p>

        <h3>Q: 如何撤销修改？</h3>
        <p>A: 当前版本不支持撤销操作，请在修改前备份原始文件</p>
      </div>
    </template>

    <!-- 文件上传区域 -->
    <a-card title="上传文件" class="upload-card">
      <div class="upload-area">
        <a-upload
          v-model:file-list="fileList"
          :before-upload="handleBeforeUpload"
          :custom-request="handleUpload"
          :show-upload-list="true"
          accept=".xlsx,.xls"
        >
          <a-button type="primary">
            <UploadOutlined /> 选择 Excel 文件
          </a-button>
          <div class="upload-hint">支持 .xlsx, .xls 格式文件</div>
        </a-upload>
      </div>
    </a-card>

    <!-- 修改配置区域 -->
    <a-card v-if="selectedFile" title="修改配置" class="config-card">
      <!-- 选择要处理的工作表 -->
      <div class="config-section">
        <a-form-item label="选择工作表">
          <a-select
            v-model:value="selectedSheets"
            mode="multiple"
            placeholder="选择要处理的工作表"
            style="width: 100%"
          >
            <a-select-option
              v-for="sheet in availableSheets"
              :key="sheet"
              :value="sheet"
            >
              {{ sheet }}
            </a-select-option>
          </a-select>
          <div class="hint-text">留空则处理所有工作表</div>
        </a-form-item>
      </div>

      <!-- 替换规则配置 -->
      <div class="config-section">
        <a-alert
          type="info"
          show-icon
          message="替换规则说明"
          description="您可以添加多条替换规则，系统将按顺序执行。每条规则可以设置查找内容、替换为、匹配类型等选项。"
          style="margin-bottom: 16px"
        />
        <a-form-item label="替换规则">
          <div class="rules-container">
            <div
              v-for="(rule, index) in replaceRules"
              :key="index"
              class="rule-item"
            >
              <a-card
                size="small"
                title="规则 {{ index + 1 }}"
                :bordered="true"
              >
                <div class="rule-content">
                  <a-row :gutter="16">
                    <a-col :span="12">
                      <a-form-item label="查找内容" required>
                        <a-input
                          v-model:value="rule.find"
                          placeholder="输入要查找的内容（必填）"
                          style="width: 100%"
                          :status="!rule.find && 'warning'"
                        >
                          <template #addonAfter>
                            <a-tooltip title="支持正则表达式">
                              <a-icon
                                :type="
                                  rule.match_type === 'regex'
                                    ? 'code'
                                    : 'file-text'
                                "
                              />
                            </a-tooltip>
                          </template>
                        </a-input>
                        <div v-if="!rule.find" class="error-text">
                          请输入要查找的内容
                        </div>
                      </a-form-item>
                    </a-col>
                    <a-col :span="12">
                      <a-form-item label="替换为">
                        <a-input
                          v-model:value="rule.replace"
                          placeholder="输入替换后的内容（删除模式下无需填写）"
                          :disabled="rule.delete"
                          style="width: 100%"
                        >
                          <template #addonAfter>
                            <a-tooltip
                              :title="
                                rule.delete
                                  ? '已启用删除模式，替换内容无效'
                                  : '替换后的内容'
                              "
                            >
                              <a-icon
                                :type="
                                  rule.delete ? 'close-circle' : 'check-circle'
                                "
                              />
                            </a-tooltip>
                          </template>
                        </a-input>
                      </a-form-item>
                    </a-col>
                  </a-row>

                  <a-row :gutter="16">
                    <a-col :span="8">
                      <a-form-item label="匹配类型">
                        <a-select
                          v-model:value="rule.match_type"
                          style="width: 100%"
                          :status="!rule.match_type && 'warning'"
                        >
                          <a-select-option value="exact">
                            <a-icon type="check-circle" /> 精确匹配
                          </a-select-option>
                          <a-select-option value="regex">
                            <a-icon type="code" /> 正则表达式
                          </a-select-option>
                        </a-select>
                      </a-form-item>
                    </a-col>
                    <a-col :span="8">
                      <a-form-item label="区分大小写">
                        <div class="flex-space">
                          <a-checkbox v-model:checked="rule.case_sensitive" />
                          <span class="checkbox-label">是否区分大小写</span>
                        </div>
                      </a-form-item>
                    </a-col>
                    <a-col :span="8">
                      <a-form-item label="删除内容">
                        <div class="flex-space">
                          <a-checkbox v-model:checked="rule.delete" />
                          <span class="checkbox-label">直接删除查找内容</span>
                        </div>
                      </a-form-item>
                    </a-col>
                  </a-row>

                  <a-row :gutter="16">
                    <a-col :span="24">
                      <a-form-item label="处理列（可选）">
                        <a-select
                          v-model:value="rule.columns"
                          mode="multiple"
                          placeholder="选择要处理的列，留空则处理所有列"
                          style="width: 100%"
                        >
                          <a-select-option
                            v-for="col in availableColumns"
                            :key="col.index"
                            :value="col.index"
                          >
                            {{ col.name }} ({{ col.index + 1 }})
                          </a-select-option>
                        </a-select>
                        <div class="hint-text">留空则处理所有列</div>
                      </a-form-item>
                    </a-col>
                  </a-row>

                  <div class="rule-actions">
                    <a-button
                      type="danger"
                      size="small"
                      @click="removeRule(index)"
                      :disabled="replaceRules.length <= 1"
                      :tooltip="{
                        title:
                          replaceRules.length <= 1
                            ? '至少需要保留一条规则'
                            : '删除此规则',
                      }"
                    >
                      <a-icon type="delete" /> 删除规则
                    </a-button>
                  </div>
                </div>
              </a-card>
            </div>
          </div>

          <div class="add-rule-section">
            <a-button
              type="dashed"
              @click="addRule"
              style="width: 100%"
              icon="plus"
              :tooltip="{ title: '添加一条新的替换规则' }"
            >
              添加替换规则
            </a-button>
          </div>
        </a-form-item>
      </div>

      <!-- 执行修改按钮 -->
      <div class="action-section">
        <a-button
          type="primary"
          :loading="isReplacing"
          @click="handleReplace"
          :disabled="!canReplace"
        >
          <EditOutlined /> 开始修改
        </a-button>
      </div>
    </a-card>

    <!-- 修改结果区域 -->
    <a-card v-if="replaceResult" title="修改结果" class="result-card">
      <div class="result-content">
        <!-- 结果统计 -->
        <div class="result-stats">
          <a-statistic
            title="总修改单元格数"
            :value="replaceResult.total_replaced"
          />
        </div>

        <!-- 详细结果 -->
        <div class="result-details">
          <h3>工作表修改情况：</h3>
          <a-table
            :columns="resultColumns"
            :data-source="sheetResults"
            bordered
          >
            <!-- 动态渲染列 -->
          </a-table>
        </div>

        <!-- 下载处理后的文件 -->
        <div class="download-section">
          <a-button
            type="primary"
            :loading="isDownloading"
            @click="handleDownload"
            icon="download"
          >
            下载处理后的文件
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- 加载状态 -->
    <a-spin v-if="isLoading" tip="正在处理...">
      <div class="loading-placeholder"></div>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { message } from "ant-design-vue";
import { UploadOutlined, EditOutlined } from "@ant-design/icons-vue";
import { usePyodide } from "@/utils/py";

// Pyodide 实例
const pyodide = usePyodide();

// 文件相关状态
const fileList = ref([]);
const selectedFile = ref(null);
const isLoading = ref(false);
const isReplacing = ref(false);
const isDownloading = ref(false);

// 工作表信息
const availableSheets = ref([]);
const selectedSheets = ref([]);
const availableColumns = ref([]);

// 替换规则
const replaceRules = ref([
  {
    find: "",
    replace: "",
    match_type: "exact",
    case_sensitive: false,
    columns: [],
    delete: false,
  },
]);

// 替换结果
const replaceResult = ref(null);
const processedFileData = ref(null);

// 处理文件上传前的验证
const handleBeforeUpload = (file) => {
  const isExcel =
    file.type ===
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
    file.type === "application/vnd.ms-excel";
  const isLt10M = file.size / 1024 / 1024 < 10;

  if (!isExcel) {
    message.error("请上传 Excel 文件！");
    return false;
  }
  if (!isLt10M) {
    message.error("文件大小不能超过 10MB！");
    return false;
  }

  return false; // 阻止自动上传，使用自定义上传
};

// 处理文件上传
const handleUpload = async (options) => {
  const file = options.file;
  isLoading.value = true;

  try {
    // 读取文件内容
    const arrayBuffer = await file.arrayBuffer();
    const fileData = new Uint8Array(arrayBuffer);

    // 存储选中的文件
    selectedFile.value = {
      name: file.name,
      data: fileData,
    };

    // 解析 Excel 文件，获取工作表信息
    await parseExcelFile(fileData);

    message.success("文件上传成功！");
  } catch (error) {
    message.error("文件上传失败：" + error.message);
  } finally {
    isLoading.value = false;
  }
};

// 解析 Excel 文件，获取工作表和列信息
const parseExcelFile = async (fileData) => {
  try {
    // 初始化 Pyodide
    await pyodide.init();

    // 获取工作表名称
    const getSheetsCode = `
import sys
import os
from openpyxl import load_workbook
from io import BytesIO

file_data = bytes.fromhex('${Array.from(fileData)
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")}')
workbook = load_workbook(filename=BytesIO(file_data))
print(','.join(workbook.sheetnames))
    `;

    // 执行代码获取工作表名称
    const sheetsResult = await pyodide.runPython(getSheetsCode);
    availableSheets.value = sheetsResult.split(",");

    // 获取第一个工作表的列信息
    if (availableSheets.value.length > 0) {
      const getColumnsCode = `
import sys
import os
from openpyxl import load_workbook
from io import BytesIO

file_data = bytes.fromhex('${Array.from(fileData)
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("")}')
workbook = load_workbook(filename=BytesIO(file_data))
sheet = workbook[workbook.sheetnames[0]]
header = []
for col in range(1, sheet.max_column + 1):
    cell_value = sheet.cell(row=1, column=col).value
    header.append(cell_value or f'列{col}')
print(','.join(header))
      `;

      const columnsResult = await pyodide.runPython(getColumnsCode);
      const columnNames = columnsResult.split(",");
      availableColumns.value = columnNames.map((name, index) => ({
        index,
        name,
      }));
    }
  } catch (error) {
    console.error("解析文件失败：", error);
    throw error;
  }
};

// 添加替换规则
const addRule = () => {
  replaceRules.value.push({
    find: "",
    replace: "",
    match_type: "exact",
    case_sensitive: false,
    columns: [],
    delete: false,
  });
};

// 删除替换规则
const removeRule = (index) => {
  if (replaceRules.value.length > 1) {
    replaceRules.value.splice(index, 1);
  } else {
    message.warning("至少需要保留一个替换规则！");
  }
};

// 检查是否可以开始替换
const canReplace = computed(() => {
  if (!selectedFile.value) return false;

  // 检查是否有有效的替换规则
  for (const rule of replaceRules.value) {
    if (rule.find.trim()) {
      return true;
    }
  }

  return false;
});

// 开始替换内容
const handleReplace = async () => {
  if (!canReplace.value) {
    message.warning("请至少添加一个有效的替换规则！");
    return;
  }

  isReplacing.value = true;

  try {
    // 准备替换选项
    const options = {
      sheet_names: selectedSheets.value,
      replace_rules: replaceRules.value,
    };

    // 初始化 Pyodide
    await pyodide.init();

    // 读取 Python 代码
    const pythonCode = await fetch(
      "/src/plugins/replace-content/worker.py",
    ).then((res) => res.text());

    // 构建执行代码
    const execCode = `
${pythonCode}

import sys
import json

file_data = bytes.fromhex('${Array.from(selectedFile.value.data)
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")}')
options = ${JSON.stringify(options)}

result = replace_content_in_excel(file_data, options)
print(json.dumps(result, ensure_ascii=False))
    `;

    // 执行代码
    const execResult = await pyodide.runPython(execCode);
    const result = JSON.parse(execResult);

    if (result.success) {
      // 保存处理结果
      replaceResult.value = result.data.results;
      processedFileData.value = result.data.file_data;
      message.success("修改完成！");
    } else {
      message.error("修改失败：" + result.error);
    }
  } catch (error) {
    console.error("修改失败：", error);
    message.error("修改失败：" + error.message);
  } finally {
    isReplacing.value = false;
  }
};

// 生成工作表结果数据
const sheetResults = computed(() => {
  if (!replaceResult.value) return [];

  const results = [];
  const sheetResults = replaceResult.value.sheet_results;

  for (const [sheetName, result] of Object.entries(sheetResults)) {
    results.push({
      key: sheetName,
      sheet_name: sheetName,
      replaced_count: result.replaced_count,
    });
  }

  return results;
});

// 结果表格列配置
const resultColumns = [
  {
    title: "工作表名称",
    dataIndex: "sheet_name",
    key: "sheet_name",
  },
  {
    title: "修改单元格数",
    dataIndex: "replaced_count",
    key: "replaced_count",
  },
];

// 下载处理后的文件
const handleDownload = () => {
  if (!processedFileData.value) return;

  isDownloading.value = true;

  try {
    // 将十六进制字符串转换为二进制数据
    const binaryData = new Uint8Array(
      processedFileData.value
        .match(/.{1,2}/g)
        .map((byte) => parseInt(byte, 16)),
    );

    // 创建下载链接
    const blob = new Blob([binaryData], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);

    // 设置文件名
    const originalName = selectedFile.value.name;
    const nameWithoutExt = originalName.substring(
      0,
      originalName.lastIndexOf("."),
    );
    const newFileName = `${nameWithoutExt}_replaced.xlsx`;

    link.setAttribute("href", url);
    link.setAttribute("download", newFileName);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    message.success("文件下载成功！");
  } catch (error) {
    console.error("下载失败：", error);
    message.error("文件下载失败：" + error.message);
  } finally {
    isDownloading.value = false;
  }
};
</script>

<style scoped>
.replace-content-plugin {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.plugin-header {
  text-align: center;
  margin-bottom: 24px;
}

.plugin-header h2 {
  color: #165dff;
  margin-bottom: 8px;
}

.plugin-header p {
  color: #666;
  margin: 0;
}

.upload-card,
.config-card,
.result-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.upload-hint {
  margin-top: 12px;
  color: #999;
  font-size: 14px;
}

.config-section {
  margin-bottom: 20px;
}

.hint-text {
  margin-top: 4px;
  color: #999;
  font-size: 12px;
}

.rules-container {
  margin-bottom: 16px;
  max-height: 600px;
  overflow-y: auto;
}

.rule-item {
  margin-bottom: 16px;
}

.rule-content {
  padding: 8px 0;
}

.rule-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.add-rule-section {
  margin-top: 16px;
}

.error-text {
  color: #ff4d4f;
  font-size: 12px;
  margin-top: 4px;
}

.checkbox-label {
  font-size: 14px;
  color: #333;
  margin-left: 4px;
}

.flex-space {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.result-content {
  padding: 16px 0;
}

.result-stats {
  margin-bottom: 24px;
  text-align: center;
}

.result-details {
  margin-bottom: 20px;
}

.result-details h3 {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.download-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.loading-placeholder {
  height: 400px;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .replace-content-plugin {
    padding: 12px;
  }

  .plugin-header h2 {
    font-size: 20px;
  }
}
</style>
