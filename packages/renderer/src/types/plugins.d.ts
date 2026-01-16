// Type declarations for plugin imports

// Vue component imports
declare module '@plugins/*/index.vue' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Manifest JSON imports
declare module '@plugins/*/manifest.json' {
  interface PluginManifest {
    key: string
    name: string
    version: string
    description: string
    author: string
    category: string
    icon: string
    dependencies: string[]
    permissions: string[]
  }
  const manifest: PluginManifest
  export default manifest
}

// Python worker script imports
declare module '@plugins/*/worker.py?raw' {
  const content: string
  export default content
}
