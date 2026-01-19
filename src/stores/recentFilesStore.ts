import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface RecentFile {
  path: string
  name: string
  lastOpened: number
  size?: number
  format?: string
}

export const useRecentFilesStore = defineStore('recentFiles', () => {
  const MAX_RECENT_FILES = 10
  
  // 从 localStorage 恢复最近文件列表
  const savedRecentFiles = localStorage.getItem('excel-toolkit-recent-files')
  const recentFiles = ref<RecentFile[]>(
    savedRecentFiles ? JSON.parse(savedRecentFiles) : []
  )
  
  /**
   * 添加文件到最近列表
   */
  function addRecentFile(file: RecentFile) {
    // 移除已存在的相同路径文件
    recentFiles.value = recentFiles.value.filter(f => f.path !== file.path)
    
    // 添加到列表开头
    recentFiles.value.unshift({
      ...file,
      lastOpened: Date.now()
    })
    
    // 限制列表长度
    if (recentFiles.value.length > MAX_RECENT_FILES) {
      recentFiles.value = recentFiles.value.slice(0, MAX_RECENT_FILES)
    }
    
    // 保存到 localStorage
    saveToLocalStorage()
  }
  
  /**
   * 从最近列表中移除文件
   */
  function removeRecentFile(path: string) {
    recentFiles.value = recentFiles.value.filter(f => f.path !== path)
    saveToLocalStorage()
  }
  
  /**
   * 清空最近列表
   */
  function clearRecentFiles() {
    recentFiles.value = []
    localStorage.removeItem('excel-toolkit-recent-files')
  }
  
  /**
   * 保存到 localStorage
   */
  function saveToLocalStorage() {
    localStorage.setItem('excel-toolkit-recent-files', JSON.stringify(recentFiles.value))
  }
  
  /**
   * 格式化时间
   */
  function formatTime(timestamp: number): string {
    const now = Date.now()
    const diff = now - timestamp
    
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes} 分钟前`
    if (hours < 24) return `${hours} 小时前`
    if (days < 7) return `${days} 天前`
    
    const date = new Date(timestamp)
    return date.toLocaleDateString('zh-CN')
  }
  
  return {
    recentFiles,
    addRecentFile,
    removeRecentFile,
    clearRecentFiles,
    formatTime
  }
})
