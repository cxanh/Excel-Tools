import { createApp } from 'vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import router from './router'
import { installErrorHandler } from './utils/error-handler'
import { initializePlugins } from './plugins'
import { initPyodide } from './utils/py'

const app = createApp(App)

// 安装全局错误处理器
installErrorHandler(app)

// 配置Ant Design Vue
app.use(Antd)
app.use(router)

// 初始化应用
async function initializeApp() {
  try {
    console.log('=== 开始初始化应用 ===')
    
    // 初始化Pyodide环境
    console.log('1/3 正在初始化Pyodide环境...')
    await initPyodide()
    console.log('✓ Pyodide环境初始化完成')

    // 初始化插件
    console.log('2/3 正在初始化插件系统...')
    await initializePlugins()
    console.log('✓ 插件系统初始化完成')

    // 挂载应用
    console.log('3/3 正在挂载应用...')
    app.mount('#app')
    console.log('✓ 应用启动完成')
    console.log('=== 应用初始化成功 ===')
  } catch (error) {
    console.error('❌ 应用初始化失败:', error)
    console.error('错误详情:', error instanceof Error ? error.stack : error)
    // 即使初始化失败，也挂载应用以显示错误信息
    app.mount('#app')
  }
}

initializeApp()
