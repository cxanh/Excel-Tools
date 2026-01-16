import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSettingsStore = defineStore('settings', () => {
  // State
  const currentView = ref('file');
  const isConnected = ref(false);
  const currentProgress = ref(0);
  const progressMessage = ref('');

  // Actions
  function setCurrentView(view: string) {
    currentView.value = view;
  }

  function setConnected(connected: boolean) {
    isConnected.value = connected;
  }

  function setProgress(progress: number, message: string = '') {
    currentProgress.value = progress;
    progressMessage.value = message;
  }

  function clearProgress() {
    currentProgress.value = 0;
    progressMessage.value = '';
  }

  return {
    // State
    currentView,
    isConnected,
    currentProgress,
    progressMessage,
    // Actions
    setCurrentView,
    setConnected,
    setProgress,
    clearProgress,
  };
});
