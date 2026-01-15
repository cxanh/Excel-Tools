<template>
  <div class="delete-empty-row-plugin">
    <!-- 插件标题和描述 -->
    <div class="plugin-header">
      <h2>删除 Excel 空白内容</h2>
      <p>删除 Excel 空白内容（空白工作表、空白行列等）</p>
    </div>

    <!-- 帮助文档插槽 -->
    <template #help-content>
      <div class="help-documentation">
        <h1>删除 Excel 空白内容</h1>

        <h2>功能介绍</h2>
        <p>该插件用于批量删除 Excel 文档中的空白内容，支持以下功能：</p>
        <ul>
          <li>删除空白工作表</li>
          <li>删除空白行</li>
          <li>删除空白列</li>
          <li>支持选择特定工作表进行处理</li>
          <li>可同时删除多种空白内容</li>
        </ul>

        <h2>操作步骤</h2>
        <ol>
          <li>
            <strong>上传文件</strong>：点击"选择 Excel 文件"按钮，选择要处理的
            Excel 文件
          </li>
          <li>
            <strong>选择工作表</strong
            >：可选，指定要处理的工作表，默认处理所有工作表
          </li>
          <li>
            <strong>选择删除类型</strong>：
            <ul>
              <li>删除空白工作表：删除完全空白的工作表</li>
              <li>删除空白行：删除所有单元格都为空的行</li>
              <li>删除空白列：删除所有单元格都为空的列</li>
            </ul>
          </li>
          <li><strong>执行删除</strong>：点击"开始删除"按钮，执行删除操作</li>
          <li><strong>查看结果</strong>：删除完成后，查看删除统计结果</li>
          <li>
            <strong>下载文件</strong
            >：点击"下载处理后的文件"按钮，下载处理后的文件
          </li>
        </ol>

        <h2>使用示例</h2>
        <h3>示例1：清理空白工作表</h3>
        <p>删除 Excel 文件中所有完全空白的工作表</p>
        <ul>
          <li>选择删除类型：删除空白工作表</li>
        </ul>

        <h3>示例2：清理空白行列</h3>
        <p>删除所有工作表中的空白行和空白列</p>
        <ul>
          <li>选择删除类型：删除空白行、删除空白列</li>
        </ul>

        <h3>示例3：选择性清理</h3>
        <p>只在特定工作表中删除空白行</p>
        <ul>
          <li>选择工作表：Sheet1, Sheet3</li>
          <li>选择删除类型：删除空白行</li>
        </ul>

        <h2>注意事项</h2>
        <ul>
          <li>支持 .xlsx 和 .xls 格式的 Excel 文件</li>
          <li>单个文件大小限制为 10MB</li>
          <li>空白行/列指的是所有单元格都为空的行/列</li>
          <li>删除操作不可逆，请在操作前备份原始文件</li>
          <li>处理大型文件可能需要较长时间，请耐心等待</li>
        </ul>

        <h2>常见问题</h2>
        <h3>Q: 为什么有些看起来空白的行/列没有被删除？</h3>
        <p>A: 可能的原因：</p>
        <ul>
          <li>行/列中可能存在不可见字符或空格</li>
          <li>行/列中可能存在公式返回空值的情况</li>
          <li>行/列中可能存在格式设置但无实际内容</li>
        </ul>

        <h3>Q: 如何判断一个工作表是否被认为是空白的？</h3>
        <p>A: 空白工作表是指没有任何数据、格式和对象的工作表</p>

        <h3>Q: 可以撤销删除操作吗？</h3>
        <p>A: 当前版本不支持撤销操作，请在删除前备份原始文件</p>
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

    <!-- 删除配置区域 -->
    <a-card v-if="selectedFile" title="删除配置" class="config-card">
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

      <!-- 选择要删除的空白内容类型 -->
      <div class="config-section">
        <a-alert
          type="info"
          show-icon
          message="删除类型说明"
          description="您可以选择多种删除类型，系统将按照您的选择执行相应的删除操作。"
          style="margin-bottom: 16px"
        />
        <a-form-item label="删除类型" required>
          <a-checkbox-group
            v-model:value="deleteOptions"
            :status="deleteOptions.length === 0 && 'warning'"
          >
            <div class="checkbox-item">
              <a-checkbox
                value="delete_empty_sheets"
                :tooltip="{ title: '删除完全空白的工作表' }"
              >
                <a-icon type="file-excel" /> 删除空白工作表
              </a-checkbox>
              <div class="checkbox-description">
                删除没有任何内容、格式和对象的工作表
              </div>
            </div>
            <div class="checkbox-item">
              <a-checkbox
                value="delete_empty_rows"
                :tooltip="{ title: '删除所有单元格都为空的行' }"
              >
                <a-icon type="minus-square" /> 删除空白行
              </a-checkbox>
              <div class="checkbox-description">删除所有单元格都为空的行</div>
            </div>
            <div class="checkbox-item">
              <a-checkbox
                value="delete_empty_cols"
                :tooltip="{ title: '删除所有单元格都为空的列' }"
              >
                <a-icon type="minus-square" /> 删除空白列
              </a-checkbox>
              <div class="checkbox-description">删除所有单元格都为空的列</div>
            </div>
          </a-checkbox-group>
          <div v-if="deleteOptions.length === 0" class="error-text">
            请至少选择一种删除类型
          </div>
        </a-form-item>
      </div>

      <!-- 执行删除按钮 -->
      <div class="action-section">
        <a-button
          type="primary"
          :loading="isDeleting"
          @click="handleDelete"
          :disabled="!canDelete"
        >
          <DeleteOutlined /> 开始删除
        </a-button>
      </div>
    </a-card>

    <!-- 删除结果区域 -->
    <a-card v-if="deleteResult" title="删除结果" class="result-card">
      <div class="result-content">
        <!-- 结果统计 -->
        <div class="result-stats">
          <a-statistic
            title="已删除空白工作表"
            :value="deleteResult.deleted_sheets.length"
          />
          <a-statistic title="已删除空白行" :value="totalDeletedRows" />
          <a-statistic title="已删除空白列" :value="totalDeletedCols" />
        </div>

        <!-- 详细结果 -->
        <div class="result-details">
          <!-- 已删除工作表 -->
          <div
            v-if="deleteResult.deleted_sheets.length > 0"
            class="detail-section"
          >
            <h3>已删除的空白工作表：</h3>
            <a-tag
              v-for="sheet in deleteResult.deleted_sheets"
              :key="sheet"
              color="red"
              style="margin-right: 8px; margin-bottom: 8px"
            >
              {{ sheet }}
            </a-tag>
          </div>

          <!-- 工作表详细删除情况 -->
          <div
            v-if="
              Object.keys(deleteResult.deleted_rows).length > 0 ||
              Object.keys(deleteResult.deleted_cols).length > 0
            "
            class="detail-section"
          >
            <h3>工作表详细删除情况：</h3>
            <a-table
              :columns="resultColumns"
              :data-source="generateSheetResults"
              bordered
              :pagination="false"
            >
              <!-- 动态渲染列 -->
            </a-table>
          </div>
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
import { UploadOutlined, DeleteOutlined } from "@ant-design/icons-vue";
import { usePyodide } from "@/utils/py";

// Pyodide 实例
const pyodide = usePyodide();

// 文件相关状态
const fileList = ref([]);
const selectedFile = ref(null);
const isLoading = ref(false);
const isDeleting = ref(false);
const isDownloading = ref(false);

// 工作表信息
const availableSheets = ref([]);
const selectedSheets = ref([]);

// 删除选项
const deleteOptions = ref([]);

// 删除结果
const deleteResult = ref(null);
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

// 解析 Excel 文件，获取工作表信息
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
  } catch (error) {
    console.error("解析文件失败：", error);
    throw error;
  }
};

// 检查是否可以开始删除
const canDelete = computed(() => {
  return selectedFile.value && deleteOptions.value.length > 0;
});

// 开始删除空白内容
const handleDelete = async () => {
  if (!canDelete.value) {
    message.warning("请选择要删除的空白内容类型！");
    return;
  }

  isDeleting.value = true;

  try {
    // 准备删除选项
    const options = {
      sheet_names: selectedSheets.value,
      delete_empty_sheets: deleteOptions.value.includes("delete_empty_sheets"),
      delete_empty_rows: deleteOptions.value.includes("delete_empty_rows"),
      delete_empty_cols: deleteOptions.value.includes("delete_empty_cols"),
    };

    // 初始化 Pyodide
    await pyodide.init();

    // 读取 Python 代码
    const pythonCode = await fetch(
      "/src/plugins/delete-empty-row/worker.py",
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

result = delete_empty_content(file_data, options)
print(json.dumps(result, ensure_ascii=False))
    `;

    // 执行代码
    const execResult = await pyodide.runPython(execCode);
    const result = JSON.parse(execResult);

    if (result.success) {
      // 保存处理结果
      deleteResult.value = result.data.results;
      processedFileData.value = result.data.file_data;
      message.success("删除完成！");
    } else {
      message.error("删除失败：" + result.error);
    }
  } catch (error) {
    console.error("删除失败：", error);
    message.error("删除失败：" + error.message);
  } finally {
    isDeleting.value = false;
  }
};

// 计算总删除行数
const totalDeletedRows = computed(() => {
  if (!deleteResult.value) return 0;

  const rows = deleteResult.value.deleted_rows;
  return Object.values(rows).reduce((total, count) => total + count, 0);
});

// 计算总删除列数
const totalDeletedCols = computed(() => {
  if (!deleteResult.value) return 0;

  const cols = deleteResult.value.deleted_cols;
  return Object.values(cols).reduce((total, count) => total + count, 0);
});

// 生成工作表删除结果数据
const generateSheetResults = computed(() => {
  if (!deleteResult.value) return [];

  const results = [];
  const deletedRows = deleteResult.value.deleted_rows;
  const deletedCols = deleteResult.value.deleted_cols;

  // 获取所有涉及的工作表名称
  const sheetNames = new Set([
    ...Object.keys(deletedRows),
    ...Object.keys(deletedCols),
  ]);

  sheetNames.forEach((sheetName) => {
    results.push({
      key: sheetName,
      sheet_name: sheetName,
      deleted_rows: deletedRows[sheetName] || 0,
      deleted_cols: deletedCols[sheetName] || 0,
    });
  });

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
    title: "删除空白行数量",
    dataIndex: "deleted_rows",
    key: "deleted_rows",
  },
  {
    title: "删除空白列数量",
    dataIndex: "deleted_cols",
    key: "deleted_cols",
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
    const newFileName = `${nameWithoutExt}_cleaned.xlsx`;

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
.delete-empty-row-plugin {
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

.action-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.result-content {
  padding: 16px 0;
}

.result-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h3 {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

/* 优化后的复选框样式 */
.checkbox-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.checkbox-item:hover {
  background-color: #fafafa;
  border-color: #165dff;
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.1);
}

.checkbox-description {
  font-size: 12px;
  color: #666;
  margin-left: 24px;
  margin-top: 4px;
}

.error-text {
  color: #ff4d4f;
  font-size: 12px;
  margin-top: 4px;
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
  .delete-empty-row-plugin {
    padding: 12px;
  }

  .plugin-header h2 {
    font-size: 20px;
  }

  .result-stats {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
