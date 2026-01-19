<template>
  <div id="app">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">
        <h1>📊 Excel 工具箱</h1>
        <p>轻松处理 Excel 文件</p>
      </div>
      
      <nav class="nav-menu">
        <div 
          v-for="item in menuItems" 
          :key="item.id"
          :class="['nav-item', { active: settingsStore.currentView === item.id }]"
          @click="settingsStore.setCurrentView(item.id)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </div>
      </nav>
      
      <div class="sidebar-footer">
        <div class="connection-status" :class="{ connected: settingsStore.isConnected }">
          <span class="status-dot"></span>
          <span>{{ settingsStore.isConnected ? '后端已连接' : '后端未连接' }}</span>
        </div>
        
        <Tooltip text="打开帮助文档 (F1)" position="top">
          <button 
            class="help-btn" 
            @click="showHelpModal = true"
          >
            <span class="help-icon">❓</span>
            <span>帮助</span>
          </button>
        </Tooltip>
      </div>
    </aside>
    
    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 当前文件信息栏 -->
      <CurrentFileBar 
        @save-file="saveFile"
        @close-file="closeFile"
      />
      
      <!-- 进度条 -->
      <div v-if="settingsStore.currentProgress > 0" class="progress-overlay">
        <div class="progress-card">
          <h3>处理中...</h3>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: settingsStore.currentProgress + '%' }">
              {{ settingsStore.currentProgress }}%
            </div>
          </div>
          <p class="progress-message">{{ settingsStore.progressMessage }}</p>
        </div>
      </div>

      <!-- 文件管理视图 -->
      <div v-if="settingsStore.currentView === 'file'" class="view-container">
        <h2 class="view-title">📁 文件管理</h2>
        
        <div class="file-section">
          <!-- 文件选择按钮 -->
          <div class="file-select-buttons" style="margin-bottom: 16px;">
            <Tooltip text="使用系统文件选择器浏览文件" position="bottom">
              <button 
                @click="selectFileWithDialog" 
                :disabled="fileStore.isLoading" 
                class="btn btn-primary"
                style="width: 100%;"
              >
                📂 浏览文件
              </button>
            </Tooltip>
          </div>
          
          <!-- 拖拽上传区域 -->
          <FileDropzone
            title="拖拽 Excel 文件到这里"
            description="支持 .xlsx, .xls, .csv 格式，或点击浏览文件"
            accept=".xlsx,.xls,.csv"
            :disabled="fileStore.isLoading"
            @file-selected="handleFileDropped"
            @file-error="handleFileError"
            @file-cleared="handleFileCleared"
          />
          
          <!-- 操作按钮 -->
          <div class="file-actions">
            <Tooltip text="加载 Excel 文件 (Ctrl+O)" position="bottom">
              <button 
                @click="loadFile" 
                :disabled="fileStore.isLoading || !fileStore.filePath" 
                class="btn btn-primary"
              >
                {{ fileStore.isLoading ? '加载中...' : '📂 加载文件' }}
              </button>
            </Tooltip>
            <Tooltip text="关闭当前文件 (Ctrl+W)" position="bottom">
              <button 
                @click="closeFile" 
                :disabled="fileStore.isLoading || !fileStore.loadedFile" 
                class="btn btn-secondary"
              >
                ❌ 关闭文件
              </button>
            </Tooltip>
          </div>
          
          <div v-if="fileStore.loadedFile" class="file-info-card">
            <h3>📄 已加载文件</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">文件名</span>
                <span class="value">{{ fileStore.loadedFile.file_name }}</span>
              </div>
              <div class="info-item">
                <span class="label">格式</span>
                <span class="value">{{ fileStore.loadedFile.file_format?.toUpperCase() || 'XLSX' }}</span>
              </div>
              <div class="info-item">
                <span class="label">大小</span>
                <span class="value">{{ formatFileSize(fileStore.loadedFile.file_size) }}</span>
              </div>
              <div class="info-item">
                <span class="label">工作表</span>
                <span class="value">{{ fileStore.loadedFile.sheet_count }} 个</span>
              </div>
            </div>
            
            <div class="sheets-list">
              <h4>工作表列表</h4>
              <div v-for="(sheet, index) in fileStore.loadedFile.sheets" :key="index" class="sheet-card">
                <span class="sheet-name">{{ sheet.name }}</span>
                <span class="sheet-info">{{ sheet.max_row }} 行 × {{ sheet.max_column }} 列</span>
                <span :class="['sheet-badge', sheet.visible ? 'visible' : 'hidden']">
                  {{ sheet.visible ? '✓ 可见' : '✗ 隐藏' }}
                </span>
              </div>
            </div>
            
            <div class="action-buttons">
              <Tooltip text="保存文件并创建备份 (Ctrl+S)" position="top">
                <button 
                  @click="saveFile" 
                  :disabled="fileStore.isLoading" 
                  class="btn btn-success"
                >
                  💾 保存文件
                </button>
              </Tooltip>
            </div>
          </div>
          
          <!-- 最近文件列表 -->
          <RecentFilesList 
            v-if="!fileStore.loadedFile"
            @file-selected="handleRecentFileSelected"
            style="margin-top: 24px;"
          />
        </div>
      </div>

      <!-- 内容处理视图 -->
      <div v-if="settingsStore.currentView === 'content'" class="view-container">
        <h2 class="view-title">✏️ 内容处理</h2>
        
        <div v-if="!fileStore.loadedFile" class="empty-state">
          <div class="empty-icon">📂</div>
          <p>请先在"文件管理"中加载一个 Excel 文件</p>
          <button 
            @click="settingsStore.setCurrentView('file')" 
            class="btn btn-primary"
            style="margin-top: 16px;"
          >
            前往文件管理
          </button>
        </div>
        
        <div v-else class="content-section">
          <!-- 显示当前文件信息 -->
          <div class="current-file-info">
            <h3>📄 当前文件</h3>
            <div class="info-row">
              <span class="label">文件名：</span>
              <span class="value">{{ fileStore.loadedFile.file_name }}</span>
            </div>
            <div class="info-row">
              <span class="label">工作表：</span>
              <span class="value">{{ fileStore.loadedFile.sheet_count }} 个</span>
            </div>
          </div>
          
          <div class="operations-grid">
          <div class="operation-card">
            <div class="card-header">
              <h3>🗑️ 删除空白行</h3>
              <Tooltip text="删除所有单元格均为空的行" position="left">
                <button 
                  @click="removeBlankRows" 
                  :disabled="fileStore.isLoading" 
                  class="btn btn-primary"
                >
                  执行操作
                </button>
              </Tooltip>
            </div>
            <p class="description">删除工作表中所有单元格均为空的行</p>
          </div>
          
          <div class="operation-card">
            <div class="card-header">
              <h3>🧹 清除空白单元格</h3>
              <Tooltip text="清除空白单元格但保留结构" position="left">
                <button 
                  @click="clearBlankCells" 
                  :disabled="fileStore.isLoading" 
                  class="btn btn-primary"
                >
                  执行操作
                </button>
              </Tooltip>
            </div>
            <p class="description">清除空白单元格内容，但保留工作表结构</p>
          </div>
          
          <div class="operation-card">
            <div class="card-header">
              <h3>🔢 删除公式</h3>
              <Tooltip text="将公式替换为计算结果" position="left">
                <button 
                  @click="removeFormulas" 
                  :disabled="fileStore.isLoading" 
                  class="btn btn-primary"
                >
                  执行操作
                </button>
              </Tooltip>
            </div>
            <p class="description">将公式替换为计算结果值，保持格式不变</p>
          </div>
          
          <div class="operation-card">
            <div class="card-header">
              <h3>🔄 删除重复行</h3>
              <Tooltip text="删除完全重复的数据行" position="left">
                <button 
                  @click="removeDuplicateRows" 
                  :disabled="fileStore.isLoading" 
                  class="btn btn-primary"
                >
                  执行操作
                </button>
              </Tooltip>
            </div>
            <p class="description">删除完全重复的数据行，保留第一次出现的行</p>
          </div>
          
          <div class="operation-card full-width">
            <div class="card-header">
              <h3>🔍 替换内容</h3>
            </div>
            <p class="description">按规则查找并替换单元格内容</p>
            <div class="replace-form">
              <div class="form-row">
                <input 
                  v-model="replaceFind" 
                  placeholder="查找内容" 
                  class="form-input"
                />
                <input 
                  v-model="replaceWith" 
                  placeholder="替换为" 
                  class="form-input"
                />
              </div>
              <div class="form-row">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="replaceCaseSensitive" />
                  <span>区分大小写</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="replaceUseRegex" />
                  <span>使用正则表达式</span>
                </label>
                <Tooltip text="查找并替换单元格内容" position="top">
                  <button 
                    @click="replaceContent" 
                    :disabled="fileStore.isLoading || !replaceFind" 
                    class="btn btn-primary"
                  >
                    执行替换
                  </button>
                </Tooltip>
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>
      
      <!-- 图像处理视图 -->
      <div v-if="settingsStore.currentView === 'image'" class="view-container">
        <h2 class="view-title">🖼️ 图像处理</h2>
        
        <div v-if="!fileStore.loadedFile" class="empty-state">
          <div class="empty-icon">📂</div>
          <p>请先在"文件管理"中加载一个 Excel 文件</p>
        </div>
        
        <div v-else class="content-section">
          <div class="operation-card">
            <div class="card-header">
              <h3>📤 提取图片</h3>
            </div>
            <p class="description">从 Excel 文件中提取所有嵌入的图片</p>
            <div class="form-row">
              <input 
                v-model="extractOutputDir" 
                placeholder="输出目录（例如：C:\output）" 
                class="form-input"
              />
              <button @click="extractImages" :disabled="fileStore.isLoading || !extractOutputDir" class="btn btn-primary">
                提取图片
              </button>
            </div>
          </div>
          
          <div class="operation-card full-width">
            <div class="card-header">
              <h3>💧 添加水印</h3>
            </div>
            <p class="description">为 Excel 中的图片添加文字或图片水印</p>
            <div class="watermark-form">
              <div class="form-row">
                <select v-model="watermarkType" class="form-input">
                  <option value="text">文字水印</option>
                  <option value="image">图片水印</option>
                </select>
                <select v-model="watermarkPosition" class="form-input">
                  <option value="center">居中</option>
                  <option value="top-left">左上</option>
                  <option value="top-right">右上</option>
                  <option value="bottom-left">左下</option>
                  <option value="bottom-right">右下</option>
                </select>
              </div>
              <div class="form-row" v-if="watermarkType === 'text'">
                <input 
                  v-model="watermarkText" 
                  placeholder="水印文字" 
                  class="form-input"
                />
                <input 
                  v-model="watermarkOpacity" 
                  type="number" 
                  min="0" 
                  max="100" 
                  placeholder="透明度 (0-100)" 
                  class="form-input"
                  style="max-width: 150px;"
                />
              </div>
              <div class="form-row" v-if="watermarkType === 'image'">
                <input 
                  v-model="watermarkImagePath" 
                  placeholder="水印图片路径" 
                  class="form-input"
                />
              </div>
              <div class="form-row">
                <button @click="addWatermark" :disabled="fileStore.isLoading || !canAddWatermark" class="btn btn-primary">
                  添加水印
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 工作表管理视图 -->
      <div v-if="settingsStore.currentView === 'sheet'" class="view-container">
        <h2 class="view-title">📄 工作表管理</h2>
        
        <div v-if="!fileStore.loadedFile" class="empty-state">
          <div class="empty-icon">📂</div>
          <p>请先在"文件管理"中加载一个 Excel 文件</p>
        </div>
        
        <div v-else class="content-section">
          <div class="operation-card">
            <div class="card-header">
              <h3>➕ 插入工作表</h3>
            </div>
            <p class="description">在指定位置插入新的工作表</p>
            <div class="form-row">
              <input 
                v-model="newSheetName" 
                placeholder="工作表名称" 
                class="form-input"
              />
              <input 
                v-model="insertPosition" 
                type="number" 
                min="0" 
                placeholder="插入位置 (0=开头)" 
                class="form-input"
                style="max-width: 150px;"
              />
              <button @click="insertSheet" :disabled="fileStore.isLoading || !newSheetName" class="btn btn-primary">
                插入
              </button>
            </div>
          </div>
          
          <div class="operation-card">
            <div class="card-header">
              <h3>❌ 删除工作表</h3>
            </div>
            <p class="description">删除指定的工作表</p>
            <div class="form-row">
              <select v-model="deleteSheetName" class="form-input">
                <option value="">选择工作表</option>
                <option v-for="sheet in fileStore.loadedFile.sheets" :key="sheet.name" :value="sheet.name">
                  {{ sheet.name }}
                </option>
              </select>
              <button @click="deleteSheet" :disabled="fileStore.isLoading || !deleteSheetName" class="btn btn-danger">
                删除
              </button>
            </div>
          </div>
          
          <div class="operation-card">
            <div class="card-header">
              <h3>✏️ 重命名工作表</h3>
            </div>
            <p class="description">修改工作表名称</p>
            <div class="form-row">
              <select v-model="renameSheetOldName" class="form-input">
                <option value="">选择工作表</option>
                <option v-for="sheet in fileStore.loadedFile.sheets" :key="sheet.name" :value="sheet.name">
                  {{ sheet.name }}
                </option>
              </select>
              <input 
                v-model="renameSheetNewName" 
                placeholder="新名称" 
                class="form-input"
              />
              <button @click="renameSheet" :disabled="fileStore.isLoading || !renameSheetOldName || !renameSheetNewName" class="btn btn-primary">
                重命名
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 合并拆分视图 -->
      <div v-if="settingsStore.currentView === 'merge'" class="view-container">
        <h2 class="view-title">🔗 合并拆分</h2>
        
        <div class="content-section">
          <div class="operation-card full-width">
            <div class="card-header">
              <h3>🔗 合并 Excel 文件</h3>
            </div>
            <p class="description">将多个 Excel 文件合并为一个文件</p>
            <div class="form-row">
              <input 
                v-model="mergeInputFiles" 
                placeholder="输入文件路径（用逗号分隔）" 
                class="form-input"
              />
            </div>
            <div class="form-row">
              <input 
                v-model="mergeOutputFile" 
                placeholder="输出文件路径" 
                class="form-input"
              />
              <select v-model="mergeMode" class="form-input" style="max-width: 200px;">
                <option value="append">追加到同一工作表</option>
                <option value="separate">保留独立工作表</option>
              </select>
              <button @click="mergeExcelFiles" :disabled="fileStore.isLoading || !mergeInputFiles || !mergeOutputFile" class="btn btn-primary">
                合并
              </button>
            </div>
          </div>
          
          <div class="operation-card full-width">
            <div class="card-header">
              <h3>✂️ 拆分 Excel 文件</h3>
            </div>
            <p class="description">按指定行数拆分 Excel 文件</p>
            <div class="form-row">
              <input 
                v-model="splitInputFile" 
                placeholder="输入文件路径" 
                class="form-input"
              />
              <input 
                v-model="splitRowsPerFile" 
                type="number" 
                min="1" 
                placeholder="每个文件行数" 
                class="form-input"
                style="max-width: 150px;"
              />
            </div>
            <div class="form-row">
              <input 
                v-model="splitOutputDir" 
                placeholder="输出目录" 
                class="form-input"
              />
              <button @click="splitExcelFile" :disabled="fileStore.isLoading || !splitInputFile || !splitRowsPerFile || !splitOutputDir" class="btn btn-primary">
                拆分
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 格式转换视图 -->
      <div v-if="settingsStore.currentView === 'convert'" class="view-container">
        <h2 class="view-title">🔄 格式转换</h2>
        
        <div v-if="!fileStore.loadedFile" class="empty-state">
          <div class="empty-icon">📂</div>
          <p>请先在"文件管理"中加载一个 Excel 文件</p>
        </div>
        
        <div v-else class="content-section">
          <div class="operation-card">
            <div class="card-header">
              <h3>📄 转换为 PDF</h3>
            </div>
            <p class="description">将 Excel 文件转换为 PDF 格式</p>
            <div class="form-row">
              <input 
                v-model="pdfOutputPath" 
                placeholder="输出 PDF 路径" 
                class="form-input"
              />
              <select v-model="pdfSheetRange" class="form-input" style="max-width: 150px;">
                <option value="all">所有工作表</option>
                <option value="current">当前工作表</option>
              </select>
              <button @click="convertToPdf" :disabled="fileStore.isLoading || !pdfOutputPath" class="btn btn-primary">
                转换
              </button>
            </div>
          </div>
          
          <div class="operation-card">
            <div class="card-header">
              <h3>📊 转换为 CSV</h3>
            </div>
            <p class="description">将 Excel 文件转换为 CSV 格式</p>
            <div class="form-row">
              <input 
                v-model="csvOutputDir" 
                placeholder="输出目录" 
                class="form-input"
              />
              <select v-model="csvEncoding" class="form-input" style="max-width: 120px;">
                <option value="utf-8">UTF-8</option>
                <option value="gbk">GBK</option>
                <option value="gb2312">GB2312</option>
              </select>
              <button @click="convertToCsv" :disabled="fileStore.isLoading || !csvOutputDir" class="btn btn-primary">
                转换
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 批量操作视图 -->
      <div v-if="settingsStore.currentView === 'batch'" class="view-container">
        <h2 class="view-title">📦 批量操作</h2>
        
        <div class="content-section">
          <!-- 文件选择 -->
          <div class="operation-card full-width">
            <div class="card-header">
              <h3>1. 选择文件</h3>
            </div>
            <p class="description">选择要批量处理的 Excel 文件</p>
            <div class="form-row">
              <button @click="selectBatchFiles" class="btn btn-secondary">
                📂 浏览文件
              </button>
              <button @click="clearBatchFiles" :disabled="batchFiles.length === 0" class="btn btn-secondary">
                清除列表
              </button>
            </div>
            <div v-if="batchFiles.length > 0" class="batch-files-list">
              <div class="batch-files-header">
                已选择 {{ batchFiles.length }} 个文件
              </div>
              <div class="batch-files-items">
                <div v-for="(file, index) in batchFiles" :key="index" class="batch-file-item">
                  <span class="file-icon">📄</span>
                  <span class="file-path">{{ file }}</span>
                  <button @click="removeBatchFile(index)" class="remove-btn">✕</button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 操作选择 -->
          <div class="operation-card full-width">
            <div class="card-header">
              <h3>2. 选择操作</h3>
            </div>
            <p class="description">选择要对所有文件执行的操作</p>
            <div class="form-row">
              <select v-model="batchOperation" class="form-input">
                <option value="">请选择操作</option>
                <optgroup label="内容处理">
                  <option value="remove_blank_rows">删除空白行</option>
                  <option value="clear_blank_cells">清除空白单元格</option>
                  <option value="remove_formulas">删除公式</option>
                  <option value="remove_duplicate_rows">删除重复行</option>
                </optgroup>
                <optgroup label="工作表管理">
                  <option value="insert_sheet">插入工作表</option>
                </optgroup>
              </select>
            </div>
            
            <!-- 操作参数配置 -->
            <div v-if="batchOperation === 'insert_sheet'" class="operation-params">
              <h4>参数配置</h4>
              <div class="form-row">
                <input 
                  v-model="batchOperationParams.sheet_name" 
                  placeholder="工作表名称（可选）" 
                  class="form-input"
                />
                <input 
                  v-model.number="batchOperationParams.position" 
                  type="number" 
                  min="0" 
                  placeholder="插入位置（0=开头）" 
                  class="form-input"
                  style="max-width: 200px;"
                />
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="batch-actions">
            <button 
              @click="startBatchProcessing" 
              :disabled="!canStartBatch || batchStore.isProcessing"
              class="btn btn-primary btn-large"
            >
              开始批量处理
            </button>
          </div>
        </div>
      </div>
      
      <!-- 消息日志视图 -->
      <div v-if="settingsStore.currentView === 'logs'" class="view-container">
        <h2 class="view-title">📋 操作日志</h2>
        
        <div class="logs-section">
          <div class="logs-header">
            <span>共 {{ historyStore.messages.length }} 条消息</span>
            <button @click="historyStore.clearLogs()" class="btn btn-secondary btn-sm">清空日志</button>
          </div>
          
          <div class="logs-list">
            <div v-for="(msg, index) in historyStore.messages" :key="index" :class="['log-item', msg.status]">
              <span class="log-time">{{ msg.time }}</span>
              <span :class="['log-status', msg.status]">{{ getStatusText(msg.status) }}</span>
              <span class="log-message">{{ msg.message }}</span>
            </div>
            
            <div v-if="historyStore.messages.length === 0" class="empty-logs">
              <p>暂无操作日志</p>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 欢迎向导 -->
    <WelcomeGuide 
      :visible="showWelcomeGuide" 
      @close="showWelcomeGuide = false"
      @finish="handleGuideFinish"
    />
    
    <!-- 帮助文档 -->
    <HelpModal 
      :visible="showHelpModal" 
      @close="showHelpModal = false"
    />
    
    <!-- 确认对话框 -->
    <ConfirmDialog
      v-model:visible="showConfirmDialog"
      :type="confirmDialogOptions.type"
      :title="confirmDialogOptions.title"
      :message="confirmDialogOptions.message"
      :detail="confirmDialogOptions.detail"
      :confirm-text="confirmDialogOptions.confirmText"
      :cancel-text="confirmDialogOptions.cancelText"
      @confirm="confirmDialogOptions.onConfirm"
    />
    
    <!-- 错误提示 -->
    <ErrorToast
      v-model:visible="showErrorToast"
      :type="errorToastOptions.type"
      :title="errorToastOptions.title"
      :message="errorToastOptions.message"
      :detail="errorToastOptions.detail"
    />
    
    <!-- 批量处理进度 -->
    <BatchProgress 
      v-if="batchStore.isProcessing && batchStore.currentTask"
      :task="batchStore.currentTask"
      @cancel="cancelBatchProcessing"
    />
    
    <!-- 批量处理结果摘要 -->
    <BatchSummary 
      v-if="showBatchSummary && batchStore.currentTask"
      :task="batchStore.currentTask"
      @close="closeBatchSummary"
    />
    
    <!-- 全局拖拽区域 -->
    <GlobalDropzone @file-dropped="handleGlobalFileDrop" />
  </div>
</template>


<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useFileStore } from './stores/fileStore';
import { useHistoryStore } from './stores/historyStore';
import { useSettingsStore } from './stores/settingsStore';
import { useRecentFilesStore } from './stores/recentFilesStore';
import { useBatchStore } from './stores/batchStore';
import Tooltip from './components/Tooltip.vue';
import FileDropzone from './components/FileDropzone.vue';
import GlobalDropzone from './components/GlobalDropzone.vue';
import CurrentFileBar from './components/CurrentFileBar.vue';
import WelcomeGuide from './components/WelcomeGuide.vue';
import HelpModal from './components/HelpModal.vue';
import ConfirmDialog from './components/ConfirmDialog.vue';
import RecentFilesList from './components/RecentFilesList.vue';
import ErrorToast from './components/ErrorToast.vue';
import BatchProgress from './components/BatchProgress.vue';
import BatchSummary from './components/BatchSummary.vue';

// 使用 Pinia stores
const fileStore = useFileStore();
const historyStore = useHistoryStore();
const settingsStore = useSettingsStore();
const recentFilesStore = useRecentFilesStore();
const batchStore = useBatchStore();

// 帮助系统状态
const showWelcomeGuide = ref(false);
const showHelpModal = ref(false);

// 确认对话框状态
const showConfirmDialog = ref(false);
const confirmDialogOptions = ref({
  type: 'warning' as 'warning' | 'danger' | 'info' | 'question',
  title: '',
  message: '',
  detail: '',
  confirmText: '确定',
  cancelText: '取消',
  onConfirm: () => {}
});

// 错误提示状态
const showErrorToast = ref(false);
const errorToastOptions = ref({
  type: 'error' as 'error' | 'warning' | 'success' | 'info',
  title: '',
  message: '',
  detail: ''
});

// 菜单项
const menuItems = [
  { id: 'file', icon: '📁', label: '文件管理' },
  { id: 'content', icon: '✏️', label: '内容处理' },
  { id: 'image', icon: '🖼️', label: '图像处理' },
  { id: 'sheet', icon: '📄', label: '工作表管理' },
  { id: 'merge', icon: '🔗', label: '合并拆分' },
  { id: 'convert', icon: '🔄', label: '格式转换' },
  { id: 'batch', icon: '📦', label: '批量操作' },
  { id: 'logs', icon: '📋', label: '操作日志' },
];

// 本地状态（表单输入）
const replaceFind = ref('');
const replaceWith = ref('');
const replaceCaseSensitive = ref(false);
const replaceUseRegex = ref(false);

const extractOutputDir = ref('');
const watermarkType = ref('text');
const watermarkPosition = ref('center');
const watermarkText = ref('');
const watermarkOpacity = ref(50);
const watermarkImagePath = ref('');

const newSheetName = ref('');
const insertPosition = ref(0);
const deleteSheetName = ref('');
const renameSheetOldName = ref('');
const renameSheetNewName = ref('');

// 批量处理状态
const batchFiles = ref<string[]>([]);
const batchOperation = ref('');
const batchOperationParams = ref<Record<string, any>>({});
const showBatchSummary = ref(false);
// const insertPosition = ref(0);
// const deleteSheetName = ref('');
// const renameSheetOldName = ref('');
// const renameSheetNewName = ref('');

const mergeInputFiles = ref('');
const mergeOutputFile = ref('');
const mergeMode = ref('append');
const splitInputFile = ref('');
const splitRowsPerFile = ref(1000);
const splitOutputDir = ref('');

const pdfOutputPath = ref('');
const pdfSheetRange = ref('all');
const csvOutputDir = ref('');
const csvEncoding = ref('utf-8');

/**
 * 计算属性：是否可以添加水印
 */
const canAddWatermark = computed(() => {
  if (watermarkType.value === 'text') {
    return watermarkText.value.trim() !== '';
  } else {
    return watermarkImagePath.value.trim() !== '';
  }
});

/**
 * 获取状态文本
 */
function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    'success': '✓ 成功',
    'error': '✗ 错误',
    'info': 'ℹ 信息',
  };
  return statusMap[status] || status;
}

/**
 * 处理全局文件拖拽
 */
function handleGlobalFileDrop(file: File) {
  // 验证文件类型
  const validExtensions = ['.xlsx', '.xls', '.csv']
  const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!validExtensions.includes(fileExt)) {
    historyStore.addLog('error', `不支持的文件格式: ${fileExt}`)
    return
  }
  
  // 获取文件路径
  const filePath = (file as any).path || file.name
  fileStore.setFilePath(filePath)
  
  historyStore.addLog('info', `已拖入文件: ${file.name}`)
  
  // 自动切换到文件管理视图
  settingsStore.setCurrentView('file')
  
  // 自动加载文件
  setTimeout(() => {
    loadFile()
  }, 300)
}

/**
 * 处理拖拽文件
 */
function handleFileDropped(fileInfo: any) {
  fileStore.setFilePath(fileInfo.path);
  historyStore.addLog('info', `已选择文件: ${fileInfo.name} (${formatFileSize(fileInfo.size)})`);
  
  // 自动加载文件
  loadFile();
}

/**
 * 处理文件错误
 */
function handleFileError(error: any) {
  historyStore.addLog('error', error.message);
}

/**
 * 处理文件清除
 */
function handleFileCleared() {
  fileStore.setFilePath('');
  historyStore.addLog('info', '已清除选择的文件');
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

/**
 * 使用原生文件对话框选择文件
 */
async function selectFileWithDialog() {
  try {
    const result = await window.dialogAPI.openFile();
    if (!result.canceled && result.filePaths.length > 0) {
      const filePath = result.filePaths[0];
      fileStore.setFilePath(filePath);
      historyStore.addLog('info', `已选择文件: ${filePath}`);
      
      // 自动加载文件
      loadFile();
    }
  } catch (error) {
    console.error('打开文件对话框失败:', error);
    showError('打开失败', '无法打开文件选择对话框');
  }
}

/**
 * 处理最近文件选择
 */
function handleRecentFileSelected(file: any) {
  fileStore.setFilePath(file.path);
  historyStore.addLog('info', `正在打开最近文件: ${file.name}`);
  loadFile();
}

/**
 * 显示确认对话框
 */
function showConfirm(options: {
  type?: 'warning' | 'danger' | 'info' | 'question'
  title: string
  message: string
  detail?: string
  confirmText?: string
  cancelText?: string
}): Promise<boolean> {
  return new Promise((resolve) => {
    confirmDialogOptions.value = {
      type: options.type || 'warning',
      title: options.title,
      message: options.message,
      detail: options.detail || '',
      confirmText: options.confirmText || '确定',
      cancelText: options.cancelText || '取消',
      onConfirm: () => {
        showConfirmDialog.value = false;
        resolve(true);
      }
    };
    showConfirmDialog.value = true;
    
    // 设置一个标志来处理取消
    const originalValue = showConfirmDialog.value;
    setTimeout(() => {
      if (!showConfirmDialog.value && originalValue) {
        resolve(false);
      }
    }, 100);
  });
}

/**
 * 显示错误提示
 */
function showError(title: string, message: string, detail?: string) {
  errorToastOptions.value = {
    type: 'error',
    title,
    message,
    detail: detail || ''
  };
  showErrorToast.value = true;
}

/**
 * 显示成功提示
 */
function showSuccess(title: string, message: string, detail?: string) {
  errorToastOptions.value = {
    type: 'success',
    title,
    message,
    detail: detail || ''
  };
  showErrorToast.value = true;
}

/**
 * 显示警告提示
 */
function showWarning(title: string, message: string, detail?: string) {
  errorToastOptions.value = {
    type: 'warning',
    title,
    message,
    detail: detail || ''
  };
  showErrorToast.value = true;
}

/**
 * 显示信息提示
 */
function showInfo(title: string, message: string, detail?: string) {
  errorToastOptions.value = {
    type: 'info',
    title,
    message,
    detail: detail || ''
  };
  showErrorToast.value = true;
}

/**
 * 加载文件
 */
function loadFile() {
  if (!fileStore.filePath) {
    historyStore.addLog('error', '请输入文件路径');
    return;
  }
  
  fileStore.setLoading(true);
  fileStore.setLoadedFile(null);
  historyStore.addLog('info', `正在加载文件: ${fileStore.filePath}`);
  
  window.pythonBridge.sendCommand({
    action: 'load_file',
    params: {
      file_path: fileStore.filePath
    }
  });
}

/**
 * 关闭文件
 */
async function closeFile() {
  // 显示确认对话框
  const confirmed = await showConfirm({
    type: 'warning',
    title: '确认关闭文件',
    message: '确定要关闭当前文件吗？',
    detail: '请确保已保存所有更改',
    confirmText: '关闭',
    cancelText: '取消'
  });
  
  if (!confirmed) {
    historyStore.addLog('info', '已取消关闭操作');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', '正在关闭文件...');
  
  window.pythonBridge.sendCommand({
    action: 'close_file',
    params: {}
  });
}

/**
 * 保存文件
 */
function saveFile() {
  if (!fileStore.loadedFile) {
    historyStore.addLog('error', '没有加载的文件');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', '正在保存文件...');
  
  window.pythonBridge.sendCommand({
    action: 'save_file',
    params: {
      file_path: fileStore.loadedFile.file_path,
      overwrite: true,
      create_backup: true
    }
  });
}

/**
 * 删除空白行
 */
function removeBlankRows() {
  fileStore.setLoading(true);
  historyStore.addLog('info', '正在删除空白行...');
  
  window.pythonBridge.sendCommand({
    action: 'remove_blank_rows',
    params: {}
  });
}

/**
 * 清除空白单元格
 */
function clearBlankCells() {
  fileStore.setLoading(true);
  historyStore.addLog('info', '正在清除空白单元格...');
  
  window.pythonBridge.sendCommand({
    action: 'clear_blank_cells',
    params: {}
  });
}

/**
 * 删除公式
 */
function removeFormulas() {
  fileStore.setLoading(true);
  historyStore.addLog('info', '正在删除公式...');
  
  window.pythonBridge.sendCommand({
    action: 'remove_formulas',
    params: {}
  });
}

/**
 * 删除重复行
 */
function removeDuplicateRows() {
  fileStore.setLoading(true);
  historyStore.addLog('info', '正在删除重复行...');
  
  window.pythonBridge.sendCommand({
    action: 'remove_duplicate_rows',
    params: {}
  });
}

/**
 * 替换内容
 */
function replaceContent() {
  if (!replaceFind.value) {
    historyStore.addLog('error', '请输入查找内容');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', `正在替换内容: "${replaceFind.value}" → "${replaceWith.value}"`);
  
  window.pythonBridge.sendCommand({
    action: 'replace_content',
    params: {
      find_text: replaceFind.value,
      replace_text: replaceWith.value,
      case_sensitive: replaceCaseSensitive.value,
      use_regex: replaceUseRegex.value
    }
  });
}

/**
 * 提取图片
 */
function extractImages() {
  if (!extractOutputDir.value) {
    historyStore.addLog('error', '请输入输出目录');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', `正在提取图片到: ${extractOutputDir.value}`);
  
  window.pythonBridge.sendCommand({
    action: 'extract_images',
    params: {
      output_dir: extractOutputDir.value
    }
  });
}

/**
 * 添加水印
 */
function addWatermark() {
  if (watermarkType.value === 'text' && !watermarkText.value) {
    historyStore.addLog('error', '请输入水印文字');
    return;
  }
  
  if (watermarkType.value === 'image' && !watermarkImagePath.value) {
    historyStore.addLog('error', '请输入水印图片路径');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', `正在添加${watermarkType.value === 'text' ? '文字' : '图片'}水印...`);
  
  const action = watermarkType.value === 'text' ? 'add_text_watermark' : 'add_image_watermark';
  const params: any = {
    position: watermarkPosition.value
  };
  
  if (watermarkType.value === 'text') {
    params.text = watermarkText.value;
    params.opacity = watermarkOpacity.value / 100;
  } else {
    params.watermark_image = watermarkImagePath.value;
    params.opacity = watermarkOpacity.value / 100;
  }
  
  window.pythonBridge.sendCommand({
    action,
    params
  });
}

/**
 * 插入工作表
 */
function insertSheet() {
  if (!newSheetName.value) {
    historyStore.addLog('error', '请输入工作表名称');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', `正在插入工作表: ${newSheetName.value}`);
  
  window.pythonBridge.sendCommand({
    action: 'insert_sheet',
    params: {
      sheet_name: newSheetName.value,
      position: insertPosition.value
    }
  });
}

/**
 * 删除工作表
 */
async function deleteSheet() {
  if (!deleteSheetName.value) {
    showError('输入错误', '请选择要删除的工作表');
    return;
  }
  
  // 显示确认对话框
  const confirmed = await showConfirm({
    type: 'danger',
    title: '确认删除工作表',
    message: `确定要删除工作表"${deleteSheetName.value}"吗？`,
    detail: '此操作无法撤销，工作表中的所有数据将被永久删除',
    confirmText: '删除',
    cancelText: '取消'
  });
  
  if (!confirmed) {
    historyStore.addLog('info', '已取消删除操作');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', `正在删除工作表: ${deleteSheetName.value}`);
  
  window.pythonBridge.sendCommand({
    action: 'delete_sheet',
    params: {
      sheet_name: deleteSheetName.value
    }
  });
}

/**
 * 重命名工作表
 */
function renameSheet() {
  if (!renameSheetOldName.value || !renameSheetNewName.value) {
    historyStore.addLog('error', '请选择工作表并输入新名称');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', `正在重命名工作表: ${renameSheetOldName.value} → ${renameSheetNewName.value}`);
  
  window.pythonBridge.sendCommand({
    action: 'rename_sheet',
    params: {
      old_name: renameSheetOldName.value,
      new_name: renameSheetNewName.value
    }
  });
}

/**
 * 合并 Excel 文件
 */
function mergeExcelFiles() {
  if (!mergeInputFiles.value || !mergeOutputFile.value) {
    historyStore.addLog('error', '请输入文件路径');
    return;
  }
  
  const inputFiles = mergeInputFiles.value.split(',').map(f => f.trim());
  
  fileStore.setLoading(true);
  historyStore.addLog('info', `正在合并 ${inputFiles.length} 个文件...`);
  
  window.pythonBridge.sendCommand({
    action: 'merge_excel_files',
    params: {
      input_files: inputFiles,
      output_file: mergeOutputFile.value,
      mode: mergeMode.value
    }
  });
}

/**
 * 拆分 Excel 文件
 */
function splitExcelFile() {
  if (!splitInputFile.value || !splitRowsPerFile.value || !splitOutputDir.value) {
    historyStore.addLog('error', '请填写所有必填项');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', `正在拆分文件，每个文件 ${splitRowsPerFile.value} 行...`);
  
  window.pythonBridge.sendCommand({
    action: 'split_excel_file',
    params: {
      input_file: splitInputFile.value,
      rows_per_file: parseInt(splitRowsPerFile.value.toString()),
      output_dir: splitOutputDir.value
    }
  });
}

/**
 * 转换为 PDF
 */
function convertToPdf() {
  if (!pdfOutputPath.value) {
    historyStore.addLog('error', '请输入输出 PDF 路径');
    return;
  }
  
  if (!fileStore.loadedFile) {
    historyStore.addLog('error', '没有加载的文件');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', '正在转换为 PDF...');
  
  window.pythonBridge.sendCommand({
    action: 'excel_to_pdf',
    params: {
      input_file: fileStore.loadedFile.file_path,
      output_file: pdfOutputPath.value,
      sheet_range: pdfSheetRange.value
    }
  });
}

/**
 * 转换为 CSV
 */
function convertToCsv() {
  if (!csvOutputDir.value) {
    historyStore.addLog('error', '请输入输出目录');
    return;
  }
  
  if (!fileStore.loadedFile) {
    historyStore.addLog('error', '没有加载的文件');
    return;
  }
  
  fileStore.setLoading(true);
  historyStore.addLog('info', '正在转换为 CSV...');
  
  window.pythonBridge.sendCommand({
    action: 'excel_to_csv',
    params: {
      input_file: fileStore.loadedFile.file_path,
      output_dir: csvOutputDir.value,
      encoding: csvEncoding.value
    }
  });
}

/**
 * 处理 Python 后端消息
 */
function handlePythonMessage(message: any) {
  console.log('Received from Python:', message);
  
  if (message.type === 'startup') {
    settingsStore.setConnected(true);
    historyStore.addLog('success', '后端连接成功');
    fileStore.setLoading(false);
    showSuccess('连接成功', 'Python 后端已成功连接');
  } else if (message.type === 'result') {
    fileStore.setLoading(false);
    settingsStore.clearProgress();
    
    if (message.status === 'success') {
      historyStore.addLog('success', message.message);
      
      // 如果是文件加载成功，保存文件信息并添加到最近列表
      if (message.data && message.data.file_name) {
        fileStore.setLoadedFile(message.data);
        
        // 添加到最近文件列表
        recentFilesStore.addRecentFile({
          path: message.data.file_path,
          name: message.data.file_name,
          lastOpened: Date.now(),
          size: message.data.file_size,
          format: message.data.file_format
        });
        
        showSuccess('加载成功', `文件 ${message.data.file_name} 已成功加载`);
      } 
      // 如果操作返回了更新的文件信息，更新 store
      else if (message.data && message.data.file_info) {
        fileStore.setLoadedFile(message.data.file_info);
        showSuccess('操作成功', message.message);
      }
      else {
        // 其他成功操作
        showSuccess('操作成功', message.message);
      }
      
      // 如果是关闭文件，清除文件信息
      if (message.message === '文件已关闭' || message.message === '没有打开的文件') {
        fileStore.clearFile();
      }
    } else {
      historyStore.addLog('error', message.message);
      
      // 显示错误提示
      showError(
        '操作失败',
        message.message,
        message.suggested_action || undefined
      );
      
      if (message.suggested_action) {
        historyStore.addLog('info', `建议: ${message.suggested_action}`);
      }
    }
  } else if (message.type === 'progress') {
    settingsStore.setProgress(message.progress, message.message);
  } else if (message.type === 'batch_progress') {
    // 批量处理进度更新
    if (message.data) {
      batchStore.updateProgress(
        message.progress,
        message.data.current_file || '',
        message.data.current_file_index || 0,
        message.data.total_files || 0
      );
    }
  } else if (message.type === 'result' && (message.status === 'success' || message.status === 'partial_success') && message.data && message.data.results) {
    // 批量处理完成
    if (batchStore.currentTask) {
      // 添加所有结果
      message.data.results.forEach((result: any) => {
        batchStore.addResult(result);
      });
      
      batchStore.completeBatchTask();
      
      // 显示结果摘要
      showBatchSummary.value = true;
      
      // 记录日志
      historyStore.addLog(
        message.status === 'success' ? 'success' : 'info',
        message.message
      );
    }
  }
}

/**
 * 检查是否首次使用
 */
function checkFirstTimeUser() {
  const hasSeenGuide = localStorage.getItem('hasSeenWelcomeGuide');
  if (!hasSeenGuide) {
    showWelcomeGuide.value = true;
  }
}

/**
 * 完成欢迎向导
 */
function handleGuideFinish(dontShowAgain: boolean) {
  if (dontShowAgain) {
    localStorage.setItem('hasSeenWelcomeGuide', 'true');
  }
  showWelcomeGuide.value = false;
}

/**
 * 键盘快捷键处理
 */
function handleKeyboard(event: KeyboardEvent) {
  // F1 - 打开帮助
  if (event.key === 'F1') {
    event.preventDefault();
    showHelpModal.value = true;
    return;
  }
  
  // Esc - 关闭对话框
  if (event.key === 'Escape') {
    showWelcomeGuide.value = false;
    showHelpModal.value = false;
    return;
  }
  
  // Ctrl 组合键
  if (event.ctrlKey || event.metaKey) {
    switch (event.key.toLowerCase()) {
      case 'o': // Ctrl+O - 打开文件
        event.preventDefault();
        settingsStore.setCurrentView('file');
        break;
      case 's': // Ctrl+S - 保存文件
        event.preventDefault();
        if (fileStore.loadedFile) {
          saveFile();
        }
        break;
      case 'w': // Ctrl+W - 关闭文件
        event.preventDefault();
        if (fileStore.loadedFile) {
          closeFile();
        }
        break;
      case 'l': // Ctrl+L - 查看日志
        event.preventDefault();
        settingsStore.setCurrentView('logs');
        break;
      case '1': // Ctrl+1 - 文件管理
        event.preventDefault();
        settingsStore.setCurrentView('file');
        break;
      case '2': // Ctrl+2 - 内容处理
        event.preventDefault();
        settingsStore.setCurrentView('content');
        break;
      case '3': // Ctrl+3 - 图像处理
        event.preventDefault();
        settingsStore.setCurrentView('image');
        break;
      case '4': // Ctrl+4 - 工作表管理
        event.preventDefault();
        settingsStore.setCurrentView('sheet');
        break;
      case '5': // Ctrl+5 - 合并拆分
        event.preventDefault();
        settingsStore.setCurrentView('merge');
        break;
      case '6': // Ctrl+6 - 格式转换
        event.preventDefault();
        settingsStore.setCurrentView('convert');
        break;
      case '7': // Ctrl+7 - 操作日志
        event.preventDefault();
        settingsStore.setCurrentView('logs');
        break;
    }
  }
}

/**
 * 批量处理相关函数
 */

// 计算属性：是否可以开始批量处理
const canStartBatch = computed(() => {
  return batchFiles.value.length > 0 && batchOperation.value !== '';
});

// 选择批量文件
async function selectBatchFiles() {
  try {
    const result = await window.dialogAPI.openFiles();
    if (!result.canceled && result.filePaths.length > 0) {
      batchFiles.value = [...batchFiles.value, ...result.filePaths];
      historyStore.addLog('info', `已选择 ${result.filePaths.length} 个文件`);
    }
  } catch (error) {
    console.error('选择文件失败:', error);
    showError('选择失败', '无法打开文件选择对话框');
  }
}

// 清除批量文件列表
function clearBatchFiles() {
  batchFiles.value = [];
  historyStore.addLog('info', '已清除文件列表');
}

// 移除单个批量文件
function removeBatchFile(index: number) {
  batchFiles.value.splice(index, 1);
}

// 开始批量处理
function startBatchProcessing() {
  if (!canStartBatch.value) {
    showError('参数错误', '请选择文件和操作');
    return;
  }
  
  // 创建批量任务
  const task = {
    id: Date.now().toString(),
    name: `批量${getOperationName(batchOperation.value)}`,
    files: [...batchFiles.value],
    operation: batchOperation.value,
    params: { ...batchOperationParams.value },
    status: 'running' as const,
    progress: 0,
    currentFile: '',
    currentFileIndex: 0,
    totalFiles: batchFiles.value.length,
    results: [],
    startTime: Date.now(),
  };
  
  batchStore.startBatchTask(task);
  
  historyStore.addLog('info', `开始批量处理 ${batchFiles.value.length} 个文件...`);
  
  // 发送批量处理命令
  window.pythonBridge.sendCommand({
    action: 'batch_process',
    params: {
      files: batchFiles.value,
      operation: batchOperation.value,
      operation_params: batchOperationParams.value,
      save_files: true,
    },
  });
}

// 取消批量处理
function cancelBatchProcessing() {
  window.pythonBridge.sendCommand({
    action: 'cancel_batch',
    params: {},
  });
  
  batchStore.cancelBatchTask();
  historyStore.addLog('info', '已取消批量处理');
}

// 关闭批量摘要
function closeBatchSummary() {
  showBatchSummary.value = false;
  batchStore.clearCurrentTask();
}

// 获取操作名称
function getOperationName(operation: string): string {
  const names: Record<string, string> = {
    'remove_blank_rows': '删除空白行',
    'clear_blank_cells': '清除空白单元格',
    'remove_formulas': '删除公式',
    'remove_duplicate_rows': '删除重复行',
    'insert_sheet': '插入工作表',
  };
  return names[operation] || operation;
}

/**
 * 组件挂载时设置消息监听
 */
onMounted(() => {
  window.pythonBridge.onMessage(handlePythonMessage);
  historyStore.addLog('info', '应用已启动，等待后端连接...');
  
  // 检查首次使用
  checkFirstTimeUser();
  
  // 加载批量处理模板
  batchStore.loadTemplates();
  
  // 添加键盘快捷键监听
  window.addEventListener('keydown', handleKeyboard);
});

/**
 * 组件卸载时清理监听器
 */
onUnmounted(() => {
  window.pythonBridge.removeMessageListener();
  window.removeEventListener('keydown', handleKeyboard);
});
</script>


<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  display: flex;
  height: 100vh;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #f5f7fa;
  color: #2c3e50;
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #ffffff 0%, #f8f9fb 100%);
  border-right: 1px solid #e1e4e8;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.03);
}

.logo {
  padding: 30px 20px;
  border-bottom: 1px solid #e1e4e8;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.logo h1 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 5px;
}

.logo p {
  font-size: 13px;
  opacity: 0.9;
}

.nav-menu {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  margin: 4px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  color: #5a6c7d;
}

.nav-item:hover {
  background: #f0f3f7;
  color: #667eea;
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  color: #667eea;
  font-weight: 500;
}

.nav-icon {
  font-size: 20px;
  margin-right: 12px;
}

.nav-label {
  font-size: 14px;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #e1e4e8;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.connection-status {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #8b95a1;
  padding: 10px;
  border-radius: 8px;
  background: #f8f9fb;
}

.connection-status.connected {
  color: #10b981;
  background: #10b98110;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #8b95a1;
  margin-right: 8px;
  animation: pulse 2s infinite;
}

.connection-status.connected .status-dot {
  background: #10b981;
}

.help-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.help-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.help-icon {
  font-size: 16px;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 主内容区 */
.main-content {
  flex: 1;
  overflow-y: auto;
  position: relative;
}

.view-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px;
}

.view-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 30px;
  color: #1a202c;
}

/* 进度覆盖层 */
.progress-overlay {
  position: fixed;
  top: 0;
  left: 260px;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.progress-card {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  min-width: 400px;
  text-align: center;
}

.progress-card h3 {
  margin-bottom: 20px;
  color: #667eea;
  font-size: 20px;
}

.progress-bar {
  background: #e1e4e8;
  border-radius: 12px;
  height: 32px;
  overflow: hidden;
  margin-bottom: 15px;
}

.progress-fill {
  background: linear-gradient(90deg, #667eea, #764ba2);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  transition: width 0.3s ease;
}

.progress-message {
  color: #5a6c7d;
  font-size: 14px;
}

/* 文件管理 */
.file-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.file-select-buttons {
  display: flex;
  gap: 12px;
}

.file-select-buttons .btn {
  flex: 1;
}

.file-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  justify-content: center;
}

.input-group {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.file-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e1e4e8;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s;
}

.file-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #f0f3f7;
  color: #5a6c7d;
}

.btn-secondary:hover:not(:disabled) {
  background: #e1e4e8;
}

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

/* 文件信息卡片 */
.file-info-card {
  background: linear-gradient(135deg, #f8f9fb 0%, #ffffff 100%);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid #e1e4e8;
}

.file-info-card h3 {
  font-size: 18px;
  margin-bottom: 20px;
  color: #1a202c;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item .label {
  font-size: 12px;
  color: #8b95a1;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item .value {
  font-size: 16px;
  color: #1a202c;
  font-weight: 500;
}

.sheets-list {
  margin: 25px 0;
}

.sheets-list h4 {
  font-size: 14px;
  color: #5a6c7d;
  margin-bottom: 12px;
  font-weight: 500;
}

.sheet-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 1px solid #e1e4e8;
}

.sheet-name {
  font-weight: 500;
  color: #1a202c;
  min-width: 120px;
}

.sheet-info {
  color: #8b95a1;
  font-size: 13px;
  flex: 1;
}

.sheet-badge {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.sheet-badge.visible {
  background: #10b98115;
  color: #10b981;
}

.sheet-badge.hidden {
  background: #8b95a115;
  color: #8b95a1;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

/* 内容处理 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #8b95a1;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state p {
  font-size: 16px;
}

.current-file-info {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e1e4e8;
}

.current-file-info h3 {
  font-size: 16px;
  color: #1a202c;
  margin: 0 0 12px 0;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-size: 14px;
  color: #8b95a1;
  font-weight: 500;
}

.info-row .value {
  font-size: 14px;
  color: #1a202c;
  font-weight: 600;
}

.operations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.operation-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #e1e4e8;
  transition: all 0.2s;
}

.operation-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.operation-card.full-width {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-header h3 {
  font-size: 16px;
  color: #1a202c;
}

.description {
  color: #8b95a1;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.replace-form {
  margin-top: 16px;
}

.watermark-form {
  margin-top: 16px;
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}

.form-input {
  flex: 1;
  padding: 10px 14px;
  border: 2px solid #e1e4e8;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #5a6c7d;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* 日志 */
.logs-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e1e4e8;
}

.logs-header span {
  font-size: 14px;
  color: #5a6c7d;
  font-weight: 500;
}

.logs-list {
  max-height: 600px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f8f9fb;
  border-left: 3px solid transparent;
}

.log-item.success {
  border-left-color: #10b981;
  background: #10b98108;
}

.log-item.error {
  border-left-color: #ef4444;
  background: #ef444408;
}

.log-item.info {
  border-left-color: #3b82f6;
  background: #3b82f608;
}

.log-time {
  color: #8b95a1;
  font-size: 12px;
  min-width: 80px;
  font-family: 'Courier New', monospace;
}

.log-status {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  min-width: 70px;
  text-align: center;
}

.log-status.success {
  background: #10b98120;
  color: #10b981;
}

.log-status.error {
  background: #ef444420;
  color: #ef4444;
}

.log-status.info {
  background: #3b82f620;
  color: #3b82f6;
}

.log-message {
  flex: 1;
  color: #2c3e50;
  font-size: 14px;
}

.empty-logs {
  text-align: center;
  padding: 60px 20px;
  color: #8b95a1;
}

.empty-logs p {
  font-size: 15px;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* 批量操作 */
.batch-files-list {
  margin-top: 16px;
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  overflow: hidden;
}

.batch-files-header {
  padding: 12px 16px;
  background: #f8f9fb;
  border-bottom: 1px solid #e1e4e8;
  font-weight: 500;
  color: #1a202c;
  font-size: 14px;
}

.batch-files-items {
  max-height: 300px;
  overflow-y: auto;
}

.batch-file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #e1e4e8;
  transition: background 0.2s;
}

.batch-file-item:last-child {
  border-bottom: none;
}

.batch-file-item:hover {
  background: #f8f9fb;
}

.file-icon {
  font-size: 18px;
}

.file-path {
  flex: 1;
  color: #1a202c;
  font-size: 13px;
  word-break: break-all;
}

.remove-btn {
  background: none;
  border: none;
  color: #8b95a1;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: #ef4444;
}

.operation-params {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fb;
  border-radius: 8px;
}

.operation-params h4 {
  margin: 0 0 12px 0;
  color: #1a202c;
  font-size: 14px;
  font-weight: 500;
}

.batch-actions {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.btn-large {
  padding: 14px 32px;
  font-size: 16px;
}

</style>
