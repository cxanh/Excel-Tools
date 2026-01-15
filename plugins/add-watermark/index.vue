<template>
  <div class="plugin-container">
    <!-- 插件模板 -->
    <plugin-template
      ref="pluginTemplate"
      :plugin-title="pluginTitle"
      :current-step="currentStep"
      @add-file="handleAddFile"
      @import-folder="handleImportFromFolder"
      @more-action="handleMoreAction"
      @next-step="handleNextStep"
      @prev-step="handlePrevStep"
      @remove-file="handleRemoveFile"
    />

    <!-- 处理步骤内容 -->
    <div v-if="currentStep === 0" class="step-content">
      <!-- 这一步由 PluginTemplate 组件负责 -->
    </div>

    <!-- 步骤1：设置水印 -->
    <div v-else-if="currentStep === 1" class="step-content">
      <h3 class="step-title">设置水印</h3>
      <a-divider />

      <a-card title="水印内容" class="setting-card">
        <a-form layout="vertical">
          <a-form-item label="水印文字">
            <a-input
              v-model:value="settings.watermark.text"
              placeholder="请输入水印文字"
              size="large"
            />
          </a-form-item>
        </a-form>
      </a-card>

      <a-card title="水印样式" class="setting-card">
        <a-form layout="vertical">
          <a-row :gutter="[16, 16]">
            <a-col :span="8">
              <a-form-item label="字体">
                <a-select
                  v-model:value="settings.watermark.fontName"
                  style="width: 100%"
                >
                  <a-select-option value="Arial">Arial</a-select-option>
                  <a-select-option value="SimSun">宋体</a-select-option>
                  <a-select-option value="SimHei">黑体</a-select-option>
                  <a-select-option value="KaiTi">楷体</a-select-option>
                  <a-select-option value="Microsoft YaHei">微软雅黑</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="字体大小">
                <a-input-number
                  v-model:value="settings.watermark.fontSize"
                  :min="8"
                  :max="120"
                  :step="1"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="旋转角度">
                <a-slider
                  v-model:value="settings.watermark.rotation"
                  :min="-180"
                  :max="180"
                  :step="1"
                />
                <div class="slider-value">{{ settings.watermark.rotation }}°</div>
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="[16, 16]">
            <a-col :span="8">
              <a-form-item label="透明度">
                <a-slider
                  v-model:value="settings.watermark.opacity"
                  :min="0"
                  :max="1"
                  :step="0.05"
                />
                <div class="slider-value">{{ (settings.watermark.opacity * 100).toFixed(0) }}%</div>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="文字颜色">
                <div class="color-picker-container">
                  <input
                    type="color"
                    v-model="settings.watermark.color"
                    class="color-picker"
                  />
                  <span class="color-value">{{ settings.watermark.color }}</span>
                </div>
              </a-form-item>
            </a-col>
          </a-row>
        </a-form>
      </a-card>

      <a-card title="工作表选择" class="setting-card">
        <a-form layout="vertical">
          <a-form-item label="选择工作表">
            <a-select
              v-model:value="settings.sheetNames"
              mode="multiple"
              placeholder="选择要处理的工作表，默认处理所有工作表"
              style="width: 100%"
            >
              <a-select-option value="*">所有工作表</a-select-option>
              <a-select-option
                v-for="sheet in availableSheets"
                :key="sheet"
                :value="sheet"
              >
                {{ sheet }}
              </a-select-option>
            </a-select>
          </a-form-item>
          <a-button type="primary" @click="getSheets">获取工作表列表</a-button>
        </a-form>
      </a-card>
    </div>

    <!-- 步骤2：设置其它选项 -->
    <div v-else-if="currentStep === 2" class="step-content">
      <!-- 预留步骤 -->
      <h3 class="step-title">设置其它选项</h3>
      <a-divider />
      <p class="placeholder-text">此步骤暂无配置项</p>
    </div>

    <!-- 步骤3：设置输出目录 -->
    <div v-else-if="currentStep === 3" class="step-content">
      <!-- 预留步骤 -->
      <h3 class="step-title">设置输出目录</h3>
      <a-divider />
      <p class="placeholder-text">处理完成后将自动下载文件</p>
    </div>

    <!-- 步骤4：开始处理 -->
    <div v-else-if="currentStep === 4" class="step-content">
      <h3 class="step-title">开始处理</h3>
      <a-divider />

      <!-- 处理日志 -->
      <a-card title="处理日志" class="log-card">
        <div class="log-container">
          <div v-for="(log, index) in logs" :key="index" class="log-item">
            {{ log }}
          </div>
        </div>
      </a-card>

      <!-- 开始处理按钮 -->
      <div class="start-process-container">
        <a-button
          type="primary"
          size="large"
          icon="play-circle"
          @click="startProcess"
          :disabled="isProcessing"
        >
          <template #icon>
            <a-spin v-if="isProcessing" />
            <play-circle-outlined v-else />
          </template>
          {{ isProcessing ? '处理中...' : '开始处理' }}
        </a-button>
      </div>
    </div>

    <!-- 处理状态 -->
    <a-modal
      v-model:open="showResultModal"
      title="处理结果"
      @ok="showResultModal = false"
    >
      <div v-if="processResult.success" class="success-result">
        <a-result
          status="success"
          title="处理成功"
          sub-title="所有文件已成功处理完成"
        >
          <template #extra>
            <a-button type="primary" @click="showResultModal = false">
              确定
            </a-button>
          </template>
        </a-result>
      </div>
      <div v-else class="error-result">
        <a-result
          status="error"
          title="处理失败"
          :sub-title="processResult.error || '处理过程中发生错误'"
        >
          <template #extra>
            <a-button type="primary" @click="showResultModal = false">
              确定
            </a-button>
          </template>
        </a-result>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { PlayCircleOutlined } from '@ant-design/icons-vue';
import PluginTemplate from '@/components/PluginTemplate.vue';
import { runPy } from '@/utils/py';
import { getPythonScript } from '@/utils/plugin';

const router = useRouter();
const pluginTitle = '添加 Excel 文字水印';

// 插件模板引用
const pluginTemplate = ref(null);

// 处理步骤
const currentStep = ref(0);
const maxStep = 4;

// 处理状态
const isProcessing = ref(false);
const logs = ref([]);
const processResult = ref({ success: false, error: null });
const showResultModal = ref(false);

// 可用工作表列表
const availableSheets = ref([]);

// 插件设置
const settings = reactive({
  watermark: {
    text: "水印",
    fontName: "Arial",
    fontSize: 36,
    color: "#000000",
    opacity: 0.3,
    rotation: -45
  },
  sheetNames: ['*']
});

// 获取工作表列表
const getSheets = async () => {
  if (!pluginTemplate.value || pluginTemplate.value.files.length === 0) {
    return;
  }
  
  try {
    // 获取第一个文件
    const firstFile = pluginTemplate.value.files[0];
    
    // 读取文件内容
    const fileBuffer = await firstFile.file.arrayBuffer();
    const fileUint8Array = new Uint8Array(fileBuffer);
    
    // 获取工作表的Python代码
    const getSheetsCode = `
import io
from openpyxl import load_workbook

def process(input_data):
    file = input_data["file"]
    wb = load_workbook(io.BytesIO(file))
    return {
        'success': True,
        'sheetNames': wb.sheetnames
    }
`;
    
    // 调用Python脚本
    const result = await runPy(getSheetsCode, {
      type: "single",
      file: fileUint8Array,
      fileName: firstFile.name,
      settings: {}
    });
    
    if (result.success && result.sheetNames) {
      availableSheets.value = result.sheetNames;
    }
  } catch (error) {
    console.error('获取工作表列表失败:', error);
  }
};

// 处理文件选择
const handleAddFile = async (files) => {
  // 处理文件添加
  console.log('添加文件:', files);
};

// 从文件夹导入
const handleImportFromFolder = () => {
  console.log('从文件夹导入');
};

// 更多操作
const handleMoreAction = (action) => {
  console.log('更多操作:', action);
  if (action === 'paste') {
    // 从剪贴板读取
  } else if (action === 'clear') {
    // 清空列表
  }
};

// 下一步
const handleNextStep = () => {
  if (currentStep.value < maxStep) {
    currentStep.value++;
  }
};

// 上一步
const handlePrevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
};

// 删除文件
const handleRemoveFile = (key) => {
  console.log('删除文件:', key);
};

// 开始处理
const startProcess = async () => {
  if (!pluginTemplate.value || pluginTemplate.value.files.length === 0) {
    return;
  }
  
  isProcessing.value = true;
  logs.value = ['开始处理文件...'];
  
  try {
    // 获取Python脚本
    const script = await getPythonScript('add-watermark');
    if (!script) {
      logs.value.push('获取Python脚本失败');
      return;
    }
    
    // 遍历处理所有文件
    const files = pluginTemplate.value.files;
    for (let i = 0; i < files.length; i++) {
      const fileItem = files[i];
      logs.value.push(`正在处理文件：${fileItem.name}`);
      
      // 将File对象转换为Uint8Array
      const fileBuffer = await fileItem.file.arrayBuffer();
      const fileUint8Array = new Uint8Array(fileBuffer);
      
      // 调用Python脚本处理
      const result = await runPy(script, {
        type: "single",
        file: fileUint8Array,
        fileName: fileItem.name,
        settings: settings
      });
      
      logs.value.push(`${fileItem.name} 处理完成！`);
      logs.value.push(...result.logs);
      
      // 下载处理后的文件
      if (result.success && result.buffer) {
        const blob = new Blob([result.buffer], {
          type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileItem.name.replace('.xlsx', '').replace('.xls', '')}_处理后.xlsx`;
        a.click();
        URL.revokeObjectURL(url);
      }
    }
    
    logs.value.push('所有文件处理完成！');
    processResult.value = { success: true, error: null };
    showResultModal.value = true;
  } catch (error) {
    logs.value.push(`处理错误: ${error.message}`);
    processResult.value = { success: false, error: error.message };
    showResultModal.value = true;
  } finally {
    isProcessing.value = false;
  }
};

// 初始化
onMounted(() => {
  // 初始化设置
  console.log('插件初始化');
});
</script>

<style scoped>
.plugin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.step-content {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.step-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin-bottom: 20px;
}

.setting-card {
  margin-bottom: 20px;
}

.color-picker-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-picker {
  width: 50px;
  height: 36px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
}

.color-value {
  font-family: monospace;
  color: #666;
}

.slider-value {
  text-align: center;
  color: #666;
  margin-top: 5px;
  font-size: 12px;
}

.log-card {
  height: 400px;
  overflow: hidden;
}

.log-container {
  height: 330px;
  overflow-y: auto;
  padding: 10px;
  background-color: #fafafa;
  border-radius: 4px;
}

.log-item {
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.start-process-container {
  text-align: center;
  margin-top: 30px;
}

.placeholder-text {
  color: #999;
  text-align: center;
  padding: 50px 0;
}

.success-result,
.error-result {
  text-align: center;
}
</style>
