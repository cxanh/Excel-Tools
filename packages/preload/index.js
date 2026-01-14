const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  getPlugins: () => ipcRenderer.invoke("get-plugins"),
});
