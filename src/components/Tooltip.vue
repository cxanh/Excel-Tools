<template>
  <transition name="modal-fade">
    <div v-if="visible" class="modal-overlay" @click.self="close">
      <div class="modal-content">
        <div class="modal-header">
          <h2>📚 帮助文档</h2>
          <button class="close-btn" @click="close">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="tabs">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              :class="['tab-btn', { active: activeTab === tab.id }]"
              @click="activeTab = tab.id"
            >
              {{ tab.icon }} {{ tab.label }}
            </button>
          </div>
          
          <div class="tab-content">
            <!-- 快捷键 -->
            <div v-if="activeTab === 'shortcuts'" class="shortcuts-section">
              <h3>⌨️ 键盘快捷键</h3>
              <div class="shortcuts-list">
                <div class="shortcut-group">
                  <h4>文件操作</h4>
                  <div class="shortcut-row">
                    <div class="keys">
                      <kbd>Ctrl</kbd> + <kbd>O</kbd>
                    </div>
                    <span>打开文件</span>
                  </div>
                  <div class="shortcut-row">
                    <div class="keys">
                      <kbd>Ctrl</kbd> + <kbd>S</kbd>
                    </div>
                    <span>保存文件</span>
                  </div>
                  <div class="shortcut-row">
                    <div class="keys">
                      <kbd>Ctrl</kbd> + <kbd>W</kbd>
                    </div>
                    <span>关闭文件</span>
                  </div>
                </div>
                
                <div class="shortcut-group">
                  <h4>导航</h4>
                  <div class="shortcut-row">
                    <div class="keys">
                      <kbd>Ctrl</kbd> + <kbd>1-7</kbd>
                    </div>
                    <span>切换到对应功能页面</span>
                  </div>
                  <div class="shortcut-row">
                    <div class="keys">
                      <kbd>F1</kbd>
                    </div>
                    <span>打开帮助</span>
                  </div>
                </div>
                
                <div class="shortcut-group">
                  <h4>其他</h4>
                  <div class="shortcut-row">
                    <div class="keys">
                      <kbd>Ctrl</kbd> + <kbd>L</kbd>
                    </div>
                    <span>查看日志</span>
                  </div>
                  <div class="shortcut-row">
                    <div class="keys">
                      <kbd>Esc</kbd>
                    </div>
                    <span>关闭对话框</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 功能说明 -->
            <div v-if="activeTab === 'features'" class="features-section">
              <h3>🎯 功能说明</h3>
              
              <div class="feature-doc">
                <h4>📁 文件管理</h4>
                <p>加载、保存和管理 Excel 文件。</p>
                <ul>
                  <li>支持 .xlsx、.xlsm、.xls 格式</li>
                  <li>自动备份功能，保留最近 5 个版本</li>
                  <li>显示文件详细信息和工作表列表</li>
                </ul>
              </div>
              
              <div class="feature-doc">
                <h4>✏️ 内容处理</h4>
                <p>对 Excel 内容进行各种处理操作。</p>
                <ul>
                  <li><strong>删除空白行</strong>：删除所有单元格均为空的行</li>
                  <li><strong>清除空白单元格</strong>：清除空白单元格内容，保留结构</li>
                  <li><strong>删除公式</strong>：将公式替换为计算结果值</li>
                  <li><strong>删除重复行</strong>：删除完全重复的数据行</li>
                  <li><strong>替换内容</strong>：支持普通文本和正则表达式替换</li>
                </ul>
              </div>
              
              <div class="feature-doc">
                <h4>🖼️ 图像处理</h4>
                <p>处理 Excel 中的嵌入图片。</p>
                <ul>
                  <li><strong>提取图片</strong>：从 Excel 中提取所有图片</li>
                  <li><strong>添加水印</strong>：支持文字和图片水印，可调整位置和透明度</li>
                </ul>
              </div>
              
              <div class="feature-doc">
                <h4>📄 工作表管理</h4>
                <p>管理 Excel 工作表。</p>
                <ul>
                  <li><strong>插入工作表</strong>：在指定位置插入新工作表</li>
                  <li><strong>删除工作表</strong>：删除指定工作表（至少保留一个）</li>
                  <li><strong>重命名工作表</strong>：修改工作表名称</li>
                </ul>
              </div>
              
              <div class="feature-doc">
                <h4>🔗 合并拆分</h4>
                <p>合并或拆分多个 Excel 文件。</p>
                <ul>
                  <li><strong>合并文件</strong>：支持追加到同一工作表或保留独立工作表</li>
                  <li><strong>拆分文件</strong>：按指定行数拆分大文件</li>
                </ul>
              </div>
              
              <div class="feature-doc">
                <h4>🔄 格式转换</h4>
                <p>转换 Excel 文件格式。</p>
                <ul>
                  <li><strong>转换为 PDF</strong>：支持转换所有或当前工作表</li>
                  <li><strong>转换为 CSV</strong>：每个工作表生成独立 CSV 文件</li>
                </ul>
              </div>
            </div>
            
            <!-- 常见问题 -->
            <div v-if="activeTab === 'faq'" class="faq-section">
              <h3>❓ 常见问题</h3>
              
              <div class="faq-item">
                <h4>Q: 为什么提示"文件正在被其他程序使用"？</h4>
                <p>A: 请先关闭 Excel 或其他正在使用该文件的程序，然后重试。</p>
              </div>
              
              <div class="faq-item">
                <h4>Q: 如何恢复误操作的文件？</h4>
                <p>A: 每次保存前会自动创建备份，备份文件位于原文件目录的 .backup 子目录中。</p>
              </div>
              
              <div class="faq-item">
                <h4>Q: 支持哪些 Excel 格式？</h4>
                <p>A: 支持 .xlsx（Excel 2007+）、.xlsm（带宏）和 .xls（Excel 97-2003）格式。</p>
              </div>
              
              <div class="faq-item">
                <h4>Q: 处理大文件时为什么很慢？</h4>
                <p>A: 大文件（超过 10000 行）处理需要较长时间，请耐心等待。应用会显示实时进度。</p>
              </div>
              
              <div class="faq-item">
                <h4>Q: 如何使用正则表达式替换？</h4>
                <p>A: 在替换内容功能中，勾选"使用正则表达式"选项，然后输入正则表达式模式。例如：<code>\d+</code> 匹配所有数字。</p>
              </div>
              
              <div class="faq-item">
                <h4>Q: PDF 转换功能不可用怎么办？</h4>
                <p>A: Windows 系统会自动使用 Excel COM 组件。如果失败，请确保已安装 Microsoft Excel 或 LibreOffice。</p>
              </div>
            </div>
            
            <!-- 关于 -->
            <div v-if="activeTab === 'about'" class="about-section">
              <h3>ℹ️ 关于</h3>
              <div class="about-content">
                <div class="app-info">
                  <div class="app-icon">📊</div>
                  <h4>Excel 工具箱</h4>
                  <p class="version">版本 1.0.0</p>
                  <p class="description">
                    一个功能强大的 Excel 文件处理工具，提供文件管理、内容处理、图像处理、
                    工作表管理、合并拆分和格式转换等功能。
                  </p>
                </div>
                
                <div class="tech-stack">
                  <h5>技术栈</h5>
                  <div class="tech-tags">
                    <span class="tech-tag">Electron 28.0.0</span>
                    <span class="tech-tag">Vue.js 3.4.0</span>
                    <span class="tech-tag">Python 3.9+</span>
                    <span class="tech-tag">TypeScript 5.3.0</span>
                  </div>
                </div>
                
                <div class="links">
                  <h5>相关链接</h5>
                  <a href="#" class="link-item">📖 完整文档</a>
                  <a href="#" class="link-item">🐛 报告问题</a>
                  <a href="#" class="link-item">💡 功能建议</a>
                </div>
              </div>
            </div>
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
}

defineProps<Props>();
const emit = defineEmits<Emits>();

const activeTab = ref('shortcuts');

const tabs = [
  { id: 'shortcuts', icon: '⌨️', label: '快捷键' },
  { id: 'features', icon: '🎯', label: '功能说明' },
  { id: 'faq', icon: '❓', label: '常见问题' },
  { id: 'about', icon: 'ℹ️', label: '关于' },
];

function close() {
  emit('close');
}
</script>

<style scoped>
.modal-overlay {
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

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 24px 30px;
  border-bottom: 1px solid #e1e4e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h2 {
  font-size: 24px;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  font-size: 18px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.modal-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tabs {
  display: flex;
  gap: 4px;
  padding: 16px 20px 0;
  background: #f8f9fb;
  border-bottom: 1px solid #e1e4e8;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: 8px 8px 0 0;
  font-size: 14px;
  font-weight: 500;
  color: #5a6c7d;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.tab-btn.active {
  background: white;
  color: #667eea;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
}

.tab-content h3 {
  font-size: 20px;
  color: #1a202c;
  margin-bottom: 24px;
}

/* 快捷键 */
.shortcuts-list {
  display: grid;
  gap: 24px;
}

.shortcut-group h4 {
  font-size: 16px;
  color: #667eea;
  margin-bottom: 12px;
}

.shortcut-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fb;
  border-radius: 8px;
  margin-bottom: 8px;
}

.keys {
  display: flex;
  gap: 6px;
  align-items: center;
}

.keys kbd {
  background: white;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
  padding: 4px 10px;
  font-size: 13px;
  font-family: 'Segoe UI', sans-serif;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  min-width: 32px;
  text-align: center;
}

.shortcut-row span {
  color: #5a6c7d;
  font-size: 14px;
}

/* 功能说明 */
.features-section {
  display: grid;
  gap: 20px;
}

.feature-doc {
  padding: 20px;
  background: #f8f9fb;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.feature-doc h4 {
  font-size: 16px;
  color: #1a202c;
  margin-bottom: 8px;
}

.feature-doc p {
  color: #5a6c7d;
  font-size: 14px;
  margin-bottom: 12px;
}

.feature-doc ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-doc li {
  padding: 6px 0;
  color: #2c3e50;
  font-size: 14px;
  padding-left: 20px;
  position: relative;
}

.feature-doc li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: #667eea;
  font-weight: bold;
}

.feature-doc strong {
  color: #667eea;
}

/* 常见问题 */
.faq-section {
  display: grid;
  gap: 16px;
}

.faq-item {
  padding: 20px;
  background: #f8f9fb;
  border-radius: 12px;
  border-left: 4px solid #10b981;
}

.faq-item h4 {
  font-size: 15px;
  color: #1a202c;
  margin-bottom: 8px;
}

.faq-item p {
  color: #5a6c7d;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.faq-item code {
  background: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #667eea;
}

/* 关于 */
.about-content {
  display: grid;
  gap: 24px;
}

.app-info {
  text-align: center;
  padding: 30px;
  background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
  border-radius: 12px;
}

.app-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.app-info h4 {
  font-size: 24px;
  color: #1a202c;
  margin-bottom: 8px;
}

.version {
  color: #8b95a1;
  font-size: 14px;
  margin-bottom: 16px;
}

.description {
  color: #5a6c7d;
  font-size: 14px;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
}

.tech-stack,
.links {
  padding: 20px;
  background: #f8f9fb;
  border-radius: 12px;
}

.tech-stack h5,
.links h5 {
  font-size: 14px;
  color: #1a202c;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tech-tag {
  padding: 6px 12px;
  background: white;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  font-size: 13px;
  color: #5a6c7d;
}

.links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.link-item {
  padding: 10px 16px;
  background: white;
  border-radius: 8px;
  color: #667eea;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}

.link-item:hover {
  background: #667eea;
  color: white;
  transform: translateX(4px);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-content,
.modal-fade-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-fade-enter-from .modal-content,
.modal-fade-leave-to .modal-content {
  transform: scale(0.9);
}

/* 滚动条 */
.tab-content::-webkit-scrollbar {
  width: 8px;
}

.tab-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.tab-content::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
}

.tab-content::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}
</style>
