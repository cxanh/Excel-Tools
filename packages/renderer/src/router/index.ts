import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { pluginManager } from '@/utils/plugin-manager'
import { h } from 'vue'
import Home from '@/views/Home.vue'

// 基础路由
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: Home
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHashHistory(),
  routes
})

/**
 * 动态注册插件路由
 */
export function registerPluginRoute(pluginKey: string, component: any, workerScript: string): void {
  const route: RouteRecordRaw = {
    path: `/plugin/${pluginKey}`,
    name: `Plugin_${pluginKey}`,
    component: {
      render() {
        return h(component, { workerScript })
      }
    }
  }

  router.addRoute(route)
  console.log(`路由已注册: /plugin/${pluginKey}`)
}

/**
 * 初始化插件路由
 */
export async function initializePluginRoutes(): Promise<void> {
  const plugins = pluginManager.getPlugins()
  
  for (const plugin of plugins) {
    registerPluginRoute(plugin.metadata.key, plugin.component, plugin.worker)
  }
}

export default router
