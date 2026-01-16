import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface Message {
  time: string;
  status: 'success' | 'error' | 'info';
  message: string;
}

export const useHistoryStore = defineStore('history', () => {
  // State
  const messages = ref<Message[]>([]);
  const maxMessages = 100;

  // Actions
  function addLog(status: 'success' | 'error' | 'info', message: string) {
    const time = new Date().toLocaleTimeString();
    messages.value.unshift({ time, status, message });
    
    // 只保留最近的消息
    if (messages.value.length > maxMessages) {
      messages.value = messages.value.slice(0, maxMessages);
    }
  }

  function clearLogs() {
    messages.value = [];
  }

  return {
    // State
    messages,
    // Actions
    addLog,
    clearLogs,
  };
});
