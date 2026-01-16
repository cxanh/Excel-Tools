<template>
  <a-layout class="main-layout">
    <!-- 左侧导航栏 -->
    <a-layout-sider 
      v-model:collapsed="collapsed" 
      collapsible
      :width="260"
      class="sidebar"
    >
      <div class="logo">
        <div class="logo-icon">
          <FileExcelOutlined v-if="!collapsed" />
          <span v-if="!collapsed" class="logo-text">Excel工具箱</span>
          <FileExcelOutlined v-else />
        </div>
      </div>
      
      <a-menu
        theme="light"
        mode="inline"
        :selected-keys="[selectedKey]"
        @select="handleMenuSelect"
        class="sidebar-menu"
      >
        <a-menu-item key="home" class="menu-item">
          <template #icon>
            <HomeOutlined />
          </template>
          <span>仪表盘</span>
        </a-menu-item>
        
        <a-menu-divider v-if="plugins.length > 0" />
        
        <a-menu-item-group v-if="plugins.length > 0" title="功能模块">
          <a-menu-item 
            v-for="plugin in plugins" 
            :key="plugin.metadata.key"
            class="menu-item"
          >
            <template #icon>
              <ToolOutlined />
            </template>
            <span>{{ plugin.metadata.name }}</span>
          </a-menu-item>
        </a-menu-item-group>
      </a-menu>
    </a-layout-sider>
    
    <!-- 右侧内容区 -->
    <a-layout class="content-layout">
      <!-- 顶部标题栏 -->
      <a-layout-header class="header">
        <div class="header-content">
          <div class="header-left">
            <a-button 
              v-if="selectedKey !== 'home'" 
              type="text" 
              class="back-btn"
              @click="handleBack"
            >
              <LeftOutlined />
              返回
            </a-button>
            <h1 class="page-title">{{ pageTitle }}</h1>
          </div>
          <div class="header-actions">
            <a-badge :count="plugins.length" :overflow-count="99">
              <a-button type="text" class="header-btn">
                <AppstoreOutlined />
              </a-button>
            </a-badge>
            <a-button type="text" class="header-btn">
              <BellOutlined />
            </a-button>
            <a-button type="text" class="header-btn">
              <SettingOutlined />
            </a-button>
          </div>
        </div>
      </a-layout-header>
      
      <!-- 主内容区 -->
      <a-layout-content class="main-content">
        <router-view v-if="selectedKey !== 'home'" />
        
        <!-- 仪表盘首页 -->
        <div v-else class="dashboard">
          <!-- 欢迎卡片 -->
          <div class="welcome-card glass-card">
            <div class="welcome-content">
              <h2 class="welcome-title">
                <RocketOutlined class="welcome-icon" />
                欢迎使用 Excel 工具箱
              </h2>
              <p class="welcome-subtitle">强大的 Excel 文件处理工具集，让数据处理更简单高效</p>
              <div class="tech-stack">
                <a-tag color="blue" class="tech-tag">
                  <ThunderboltOutlined /> Electron 27
                </a-tag>
                <a-tag color="green" class="tech-tag">
                  <CodeOutlined /> Vue 3
                </a-tag>
                <a-tag color="orange" class="tech-tag">
                  <FireOutlined /> Vite 5
                </a-tag>
                <a-tag color="purple" class="tech-tag">
                  <BgColorsOutlined /> Ant Design Vue 4
                </a-tag>
                <a-tag color="cyan" class="tech-tag">
                  <ApiOutlined /> Pyodide 0.24
                </a-tag>
              </div>
            </div>
          </div>

          <!-- 统计卡片行 -->
          <div class="stats-row">
            <div class="stat-card glass-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <AppstoreOutlined />
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ plugins.length }}</div>
                <div class="stat-label">可用工具</div>
              </div>
            </div>
            
            <div class="stat-card glass-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <FileExcelOutlined />
              </div>
              <div class="stat-content">
                <div class="stat-value">0</div>
                <div class="stat-label">处理文件</div>
              </div>
            </div>
            
            <div class="stat-card glass-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <ClockCircleOutlined />
              </div>
              <div class="stat-content">
                <div class="stat-value">0s</div>
                <div class="stat-label">节省时间</div>
              </div>
            </div>
            
            <div class="stat-card glass-card">
              <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <CheckCircleOutlined />
              </div>
              <div class="stat-content">
                <div class="stat-value">100%</div>
                <div class="stat-label">成功率</div>
              </div>
            </div>
          </div>

          <!-- 主要内容区域 -->
          <div class="dashboard-grid">
            <!-- 热门工具 -->
            <div class="dashboard-section glass-card">
              <div class="section-header">
                <h3 class="section-title">
                  <FireOutlined class="section-icon" />
                  热门工具
                </h3>
              </div>
              <div class="tools-grid">
                <div 
                  v-for="plugin in popularPlugins" 
                  :key="plugin.metadata.key"
                  class="tool-card"
                  @click="handleMenuSelect({ key: plugin.metadata.key })"
                >
                  <div class="tool-icon">
                    <ToolOutlined />
                  </div>
                  <div class="tool-info">
                    <div class="tool-name">{{ plugin.metadata.name }}</div>
                    <div class="tool-desc">{{ plugin.metadata.description }}</div>
                  </div>
                  <RightOutlined class="tool-arrow" />
                </div>
              </div>
            </div>

            <!-- 最近文件 -->
            <div class="dashboard-section glass-card">
              <div class="section-header">
                <h3 class="section-title">
                  <ClockCircleOutlined class="section-icon" />
                  最近文件
                </h3>
              </div>
              <div class="recent-files">
                <a-empty 
                  description="暂无处理记录"
                  :image="emptyImage"
                >
                  <template #description>
                    <span class="empty-text">开始使用工具处理 Excel 文件</span>
                  </template>
                </a-empty>
              </div>
            </div>

            <!-- 系统状态 -->
            <div class="dashboard-section glass-card">
              <div class="section-header">
                <h3 class="section-title">
                  <DashboardOutlined class="section-icon" />
                  系统状态
                </h3>
              </div>
              <div class="system-status">
                <div class="status-item">
                  <div class="status-label">
                    <CheckCircleOutlined class="status-icon success" />
                    Pyodide 环境
                  </div>
                  <a-tag color="success">运行中</a-tag>
                </div>
                <div class="status-item">
                  <div class="status-label">
                    <CheckCircleOutlined class="status-icon success" />
                    插件系统
                  </div>
                  <a-tag color="success">已就绪</a-tag>
                </div>
                <div class="status-item">
                  <div class="status-label">
                    <CheckCircleOutlined class="status-icon success" />
                    文件处理器
                  </div>
                  <a-tag color="success">正常</a-tag>
                </div>
                <div class="status-item">
                  <div class="status-label">
                    <InfoCircleOutlined class="status-icon info" />
                    内存使用
                  </div>
                  <a-progress :percent="35" size="small" :show-info="false" />
                </div>
              </div>
            </div>

            <!-- 快速开始 -->
            <div class="dashboard-section glass-card quick-start">
              <div class="section-header">
                <h3 class="section-title">
                  <BulbOutlined class="section-icon" />
                  快速开始
                </h3>
              </div>
              <div class="quick-actions">
                <div class="quick-action-item">
                  <div class="action-number">1</div>
                  <div class="action-content">
                    <div class="action-title">选择工具</div>
                    <div class="action-desc">从左侧菜单选择需要的功能</div>
                  </div>
                </div>
                <div class="quick-action-item">
                  <div class="action-number">2</div>
                  <div class="action-content">
                    <div class="action-title">上传文件</div>
                    <div class="action-desc">拖拽或点击上传 Excel 文件</div>
                  </div>
                </div>
                <div class="quick-action-item">
                  <div class="action-number">3</div>
                  <div class="action-content">
                    <div class="action-title">处理下载</div>
                    <div class="action-desc">等待处理完成并下载结果</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </a-layout-content>
      
      <!-- 底部 -->
      <a-layout-footer class="footer">
        <div class="footer-content">
          <span>Excel工具箱 ©2026</span>
          <span class="footer-divider">|</span>
          <span>基于 Electron + Vue 3 + Pyodide 构建</span>
        </div>
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { pluginManager } from '@/utils/plugin-manager'
import type { PluginInstance } from '@/utils/plugin-manager'
import { Empty } from 'ant-design-vue'
import {
  HomeOutlined,
  FileExcelOutlined,
  ToolOutlined,
  AppstoreOutlined,
  BellOutlined,
  SettingOutlined,
  RocketOutlined,
  ThunderboltOutlined,
  CodeOutlined,
  FireOutlined,
  BgColorsOutlined,
  ApiOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  DashboardOutlined,
  InfoCircleOutlined,
  BulbOutlined,
  RightOutlined,
  LeftOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()

const collapsed = ref(false)
const selectedKey = ref('home')
const plugins = ref<PluginInstance[]>([])
const emptyImage = Empty.PRESENTED_IMAGE_SIMPLE

const pageTitle = computed(() => {
  if (selectedKey.value === 'home') {
    return '仪表盘'
  }
  
  const plugin = plugins.value.find(p => p.metadata.key === selectedKey.value)
  return plugin ? plugin.metadata.name : '未知页面'
})

const popularPlugins = computed(() => {
  // 返回前6个插件作为热门工具
  return plugins.value.slice(0, 6)
})

function handleMenuSelect({ key }: { key: string }) {
  selectedKey.value = key
  
  if (key === 'home') {
    router.push('/')
  } else {
    router.push(`/plugin/${key}`)
  }
}

function handleBack() {
  selectedKey.value = 'home'
  router.push('/')
}

onMounted(() => {
  // 加载插件列表
  plugins.value = pluginManager.getPlugins()
  console.log(`Home组件已挂载，发现 ${plugins.value.length} 个插件`)
  
  // 根据当前路由设置选中的菜单项
  const currentPath = route.path
  if (currentPath === '/' || currentPath === '') {
    selectedKey.value = 'home'
  } else if (currentPath.startsWith('/plugin/')) {
    const pluginKey = currentPath.replace('/plugin/', '')
    selectedKey.value = pluginKey
  } else {
    selectedKey.value = 'home'
  }
})
</script>

<style scoped>
/* 主布局 */
.main-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
}

.main-layout::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 40% 20%, rgba(59, 130, 246, 0.08) 0%, transparent 50%);
  pointer-events: none;
}

/* 侧边栏 */
.sidebar {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(16px) saturate(180%);
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.04);
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  color: #6366f1;
  font-weight: 600;
}

.logo-text {
  font-size: 18px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-menu {
  background: transparent !important;
  border-right: none !important;
}

.sidebar-menu :deep(.ant-menu-item),
.sidebar-menu :deep(.ant-menu-submenu-title) {
  border-radius: 8px;
  margin: 4px 8px;
  transition: all 0.3s ease;
  color: #64748b;
}

.sidebar-menu :deep(.ant-menu-item:hover) {
  background: rgba(99, 102, 241, 0.08) !important;
  color: #6366f1;
}

.sidebar-menu :deep(.ant-menu-item-selected) {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
  color: #6366f1;
  font-weight: 500;
}

.sidebar-menu :deep(.ant-menu-item-group-title) {
  color: #94a3b8;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding-left: 24px;
  font-weight: 600;
}

/* 内容布局 */
.content-layout {
  background: transparent;
  position: relative;
  z-index: 1;
}

/* 头部 */
.header {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(16px) saturate(180%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 0 32px;
  height: 64px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.back-btn {
  color: #64748b !important;
  font-size: 14px;
  height: 36px;
  padding: 0 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.back-btn:hover {
  background: rgba(99, 102, 241, 0.1) !important;
  color: #6366f1 !important;
  border-color: rgba(99, 102, 241, 0.3);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-btn {
  color: #64748b !important;
  font-size: 18px;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.header-btn:hover {
  background: rgba(99, 102, 241, 0.1) !important;
  color: #6366f1 !important;
}

/* 主内容区 */
.main-content {
  margin: 24px;
  padding: 0;
  overflow-y: auto;
  max-height: calc(100vh - 64px - 48px - 48px);
}

/* 仪表盘 */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 玻璃态卡片 */
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: rgba(99, 102, 241, 0.2);
}

/* 欢迎卡片 */
.welcome-card {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.welcome-content {
  text-align: center;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.welcome-icon {
  font-size: 36px;
  color: #6366f1;
}

.welcome-subtitle {
  font-size: 16px;
  color: #64748b;
  margin: 0 0 24px 0;
}

.tech-stack {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tech-tag {
  font-size: 14px;
  padding: 6px 16px;
  border-radius: 20px;
  border: none;
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 统计卡片行 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

/* 仪表盘网格 */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.dashboard-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  font-size: 20px;
  color: #6366f1;
}

/* 工具网格 */
.tools-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tool-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tool-card:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(99, 102, 241, 0.3);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
}

.tool-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #6366f1;
  flex-shrink: 0;
}

.tool-info {
  flex: 1;
}

.tool-name {
  font-size: 15px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 4px;
}

.tool-desc {
  font-size: 13px;
  color: #64748b;
}

.tool-arrow {
  color: #94a3b8;
  font-size: 14px;
}

/* 最近文件 */
.recent-files {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-text {
  color: #94a3b8;
}

/* 系统状态 */
.system-status {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.status-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1e293b;
  font-size: 14px;
}

.status-icon {
  font-size: 16px;
}

.status-icon.success {
  color: #52c41a;
}

.status-icon.info {
  color: #1890ff;
}

/* 快速开始 */
.quick-start {
  grid-column: 1 / -1;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.quick-action-item {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.quick-action-item:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08);
}

.action-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.action-desc {
  font-size: 13px;
  color: #64748b;
}

/* 底部 */
.footer {
  background: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(16px);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  padding: 16px 32px;
  text-align: center;
}

.footer-content {
  color: #64748b;
  font-size: 14px;
}

.footer-divider {
  margin: 0 12px;
  color: #cbd5e1;
}

/* 响应式 */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 滚动条样式 */
.main-content::-webkit-scrollbar {
  width: 8px;
}

.main-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.03);
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* Ant Design 组件样式覆盖 */
:deep(.ant-empty-description) {
  color: #94a3b8;
}

:deep(.ant-progress-bg) {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}

:deep(.ant-tag) {
  border: none;
}

:deep(.ant-layout-sider-trigger) {
  background: rgba(255, 255, 255, 0.9) !important;
  color: #64748b !important;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}
</style>
