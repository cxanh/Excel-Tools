import { defineStore } from 'pinia';

export interface BatchResult {
  file: string;
  file_name: string;
  status: 'success' | 'error';
  message: string;
  duration: number;
}

export interface BatchTask {
  id: string;
  name: string;
  files: string[];
  operation: string;
  params: Record<string, any>;
  status: 'pending' | 'running' | 'completed' | 'cancelled';
  progress: number;
  currentFile: string;
  currentFileIndex: number;
  totalFiles: number;
  results: BatchResult[];
  startTime?: number;
  endTime?: number;
}

export interface TaskTemplate {
  id: string;
  name: string;
  description: string;
  operation: string;
  params: Record<string, any>;
  createdAt: number;
  updatedAt: number;
}

export const useBatchStore = defineStore('batch', {
  state: () => ({
    currentTask: null as BatchTask | null,
    templates: [] as TaskTemplate[],
    isProcessing: false,
  }),
  
  actions: {
    startBatchTask(task: BatchTask) {
      this.currentTask = task;
      this.isProcessing = true;
    },
    
    updateProgress(progress: number, currentFile: string, currentFileIndex: number, totalFiles: number) {
      if (this.currentTask) {
        this.currentTask.progress = progress;
        this.currentTask.currentFile = currentFile;
        this.currentTask.currentFileIndex = currentFileIndex;
        this.currentTask.totalFiles = totalFiles;
      }
    },
    
    addResult(result: BatchResult) {
      if (this.currentTask) {
        this.currentTask.results.push(result);
      }
    },
    
    completeBatchTask() {
      if (this.currentTask) {
        this.currentTask.status = 'completed';
        this.currentTask.endTime = Date.now();
      }
      this.isProcessing = false;
    },
    
    cancelBatchTask() {
      if (this.currentTask) {
        this.currentTask.status = 'cancelled';
        this.currentTask.endTime = Date.now();
      }
      this.isProcessing = false;
    },
    
    clearCurrentTask() {
      this.currentTask = null;
      this.isProcessing = false;
    },
    
    // 模板管理
    saveTemplate(template: TaskTemplate) {
      const existingIndex = this.templates.findIndex(t => t.id === template.id);
      if (existingIndex >= 0) {
        this.templates[existingIndex] = template;
      } else {
        this.templates.push(template);
      }
      this._saveTemplatesToStorage();
    },
    
    loadTemplates() {
      const stored = localStorage.getItem('batchTaskTemplates');
      if (stored) {
        try {
          this.templates = JSON.parse(stored);
        } catch (e) {
          console.error('Failed to load templates:', e);
          this.templates = [];
        }
      }
    },
    
    deleteTemplate(id: string) {
      this.templates = this.templates.filter(t => t.id !== id);
      this._saveTemplatesToStorage();
    },
    
    getTemplate(id: string): TaskTemplate | undefined {
      return this.templates.find(t => t.id === id);
    },
    
    _saveTemplatesToStorage() {
      localStorage.setItem('batchTaskTemplates', JSON.stringify(this.templates));
    },
  },
});
