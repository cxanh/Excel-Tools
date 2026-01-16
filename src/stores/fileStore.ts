import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface FileInfo {
  file_path: string;
  file_name: string;
  file_format: string;
  file_size: number;
  sheet_count: number;
  sheets: Array<{
    name: string;
    max_row: number;
    max_column: number;
    visible: boolean;
  }>;
}

export const useFileStore = defineStore('file', () => {
  // 从 localStorage 恢复状态
  const savedFilePath = localStorage.getItem('excel-toolkit-file-path');
  const savedLoadedFile = localStorage.getItem('excel-toolkit-loaded-file');

  // State
  const filePath = ref(savedFilePath || '');
  const loadedFile = ref<FileInfo | null>(
    savedLoadedFile ? JSON.parse(savedLoadedFile) : null
  );
  const isLoading = ref(false);

  // Computed
  const hasLoadedFile = computed(() => loadedFile.value !== null);
  const fileName = computed(() => loadedFile.value?.file_name || '');
  const sheetNames = computed(() => loadedFile.value?.sheets.map(s => s.name) || []);

  // Actions
  function setFilePath(path: string) {
    filePath.value = path;
    // 持久化到 localStorage
    if (path) {
      localStorage.setItem('excel-toolkit-file-path', path);
    } else {
      localStorage.removeItem('excel-toolkit-file-path');
    }
  }

  function setLoadedFile(file: FileInfo | null) {
    loadedFile.value = file;
    // 持久化到 localStorage
    if (file) {
      localStorage.setItem('excel-toolkit-loaded-file', JSON.stringify(file));
    } else {
      localStorage.removeItem('excel-toolkit-loaded-file');
    }
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading;
  }

  function clearFile() {
    filePath.value = '';
    loadedFile.value = null;
    // 清除 localStorage
    localStorage.removeItem('excel-toolkit-file-path');
    localStorage.removeItem('excel-toolkit-loaded-file');
  }

  return {
    // State
    filePath,
    loadedFile,
    isLoading,
    // Computed
    hasLoadedFile,
    fileName,
    sheetNames,
    // Actions
    setFilePath,
    setLoadedFile,
    setLoading,
    clearFile,
  };
});
