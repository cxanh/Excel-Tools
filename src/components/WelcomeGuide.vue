<template>
  <transition name="guide-fade">
    <div v-if="visible" class="guide-overlay" @click.self="close">
      <div class="guide-modal">
        <button class="close-btn" @click="close">✕</button>
        
        <div class="guide-content">
          <!-- Step 1 -->
          <div v-if="currentStep === 0" class="guide-step">
            <div class="guide-icon">👋</div>
            <h2>欢迎使用 Excel 工具箱</h2>
            <p>这是一个功能强大的 Excel 文件处理工具，让我们快速了解如何使用它。</p>
            <div class="features-grid">
              <div class="feature-item">
                <span class="feature-icon">📁</span>
                <span>文件管理</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">✏️</span>
                <span>内容处理</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🖼️</span>
                <span>图像处理</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🔗</span>
                <span>合并拆分</span>
              </div>
            </div>
          </div>
          
          <!-- Step 2 -->
          <div v-if="currentStep === 1" class="guide-step">
            <div class="guide-icon">📂</div>
            <h2>第一步：加载文件</h2>
            <p>在"文件管理"页面，输入 Excel 文件路径并点击"加载文件"按钮。</p>
            <div class="example-box">
              <code>C:\Documents\data.xlsx</code>
            </div>
            <p class="tip">💡 提示：支持 .xlsx、.xlsm 和 .xls 格式</p>
          </div>
          
          <!-- Step 3 -->
          <div v-if="currentStep === 2" class="guide-step">
            <div class="guide-icon">⚙️</div>
            <h2>第二步：选择功能</h2>
            <p>使用左侧导航栏切换到不同的功能模块：</p>
            <ul class="feature-list">
              <li><strong>内容处理</strong> - 删除空白行、公式、重复行等</li>
              <li><strong>图像处理</strong> - 提取图片、添加水印</li>
              <li><strong>工作表管理</strong> - 插入、删除、重命名工作表</li>
              <li><strong>合并拆分</strong> - 合并或拆分多个文件</li>
              <li><strong>格式转换</strong> - 转换为 PDF 或 CSV</li>
            </ul>
          </div>
          
          <!-- Step 4 -->
          <div v-if="currentStep === 3" class="guide-step">
            <div class="guide-icon">💾</div>
            <h2>第三步：保存结果</h2>
            <p>处理完成后，返回"文件管理"页面点击"保存文件"。</p>
            <p class="tip">✅ 自动备份：每次保存前会自动创建备份，保留最近 5 个版本</p>
          </div>
          
          <!-- Step 5 -->
          <div v-if="currentStep === 4" class="guide-step">
            <div class="guide-icon">🎉</div>
            <h2>开始使用吧！</h2>
            <p>您已经了解了基本操作流程。</p>
            <div class="shortcuts-box">
              <h3>快捷键提示</h3>
              <div class="shortcut-item">
                <kbd>Ctrl</kbd> + <kbd>O</kbd>
                <span>打开文件</span>
              </div>
              <div class="shortcut-item">
                <kbd>Ctrl</kbd> + <kbd>S</kbd>
                <span>保存文件</span>
              </div>
              <div class="shortcut-item">
                <kbd>F1</kbd>
                <span>打开帮助</span>
              </div>
            </div>
            <label class="checkbox-label">
              <input type="checkbox" v-model="dontShowAgain" />
              <span>不再显示此向导</span>
            </label>
          </div>
        </div>
        
        <div class="guide-footer">
          <div class="step-indicators">
            <span 
              v-for="i in totalSteps" 
              :key="i" 
              :class="['step-dot', { active: currentStep === i - 1 }]"
            ></span>
          </div>
          <div class="guide-actions">
            <button v-if="currentStep > 0" @click="prevStep" class="btn btn-secondary">
              上一步
            </button>
            <button v-if="currentStep < totalSteps - 1" @click="nextStep" class="btn btn-primary">
              下一步
            </button>
            <button v-else @click="finish" class="btn btn-success">
              开始使用
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Props {
  visible: boolean;
}

interface Emits {
  (e: 'close'): void;
  (e: 'finish', dontShowAgain: boolean): void;
}

defineProps<Props>();
const emit = defineEmits<Emits>();

const currentStep = ref(0);
const totalSteps = 5;
const dontShowAgain = ref(false);

function nextStep() {
  if (currentStep.value < totalSteps - 1) {
    currentStep.value++;
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

function close() {
  emit('close');
}

function finish() {
  emit('finish', dontShowAgain.value);
}
</script>

<style scoped>
.guide-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.guide-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  display: flex;
  flex-direction: column;
}

.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 36px;
  height: 36px;
  border: none;
  background: #f0f3f7;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}

.close-btn:hover {
  background: #e1e4e8;
  transform: rotate(90deg);
}

.guide-content {
  flex: 1;
  padding: 60px 50px 40px;
  overflow-y: auto;
}

.guide-step {
  text-align: center;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.guide-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.guide-step h2 {
  font-size: 28px;
  color: #1a202c;
  margin-bottom: 16px;
}

.guide-step p {
  font-size: 16px;
  color: #5a6c7d;
  line-height: 1.6;
  margin-bottom: 20px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 30px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fb 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #e1e4e8;
}

.feature-icon {
  font-size: 32px;
}

.feature-item span:last-child {
  font-size: 14px;
  color: #5a6c7d;
  font-weight: 500;
}

.example-box {
  background: #f8f9fb;
  border: 2px dashed #e1e4e8;
  border-radius: 8px;
  padding: 16px;
  margin: 20px 0;
}

.example-box code {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #667eea;
}

.tip {
  font-size: 14px !important;
  color: #667eea !important;
  background: #667eea10;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 3px solid #667eea;
  text-align: left;
}

.feature-list {
  text-align: left;
  list-style: none;
  padding: 0;
  margin: 20px 0;
}

.feature-list li {
  padding: 12px 16px;
  margin-bottom: 8px;
  background: #f8f9fb;
  border-radius: 8px;
  font-size: 15px;
  color: #2c3e50;
}

.feature-list strong {
  color: #667eea;
}

.shortcuts-box {
  background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
  border-radius: 12px;
  padding: 24px;
  margin: 24px 0;
}

.shortcuts-box h3 {
  font-size: 16px;
  color: #1a202c;
  margin-bottom: 16px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  font-size: 14px;
  color: #5a6c7d;
}

.shortcut-item kbd {
  background: white;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  font-family: 'Segoe UI', sans-serif;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #5a6c7d;
  cursor: pointer;
  margin-top: 20px;
  justify-content: center;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.guide-footer {
  padding: 24px 50px;
  border-top: 1px solid #e1e4e8;
  background: #f8f9fb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-indicators {
  display: flex;
  gap: 8px;
}

.step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e1e4e8;
  transition: all 0.3s;
}

.step-dot.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 24px;
  border-radius: 5px;
}

.guide-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: white;
  color: #5a6c7d;
  border: 1px solid #e1e4e8;
}

.btn-secondary:hover {
  background: #f8f9fb;
}

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-success:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.guide-fade-enter-active,
.guide-fade-leave-active {
  transition: opacity 0.3s ease;
}

.guide-fade-enter-from,
.guide-fade-leave-to {
  opacity: 0;
}

.guide-fade-enter-active .guide-modal,
.guide-fade-leave-active .guide-modal {
  transition: transform 0.3s ease;
}

.guide-fade-enter-from .guide-modal,
.guide-fade-leave-to .guide-modal {
  transform: scale(0.9);
}
</style>
