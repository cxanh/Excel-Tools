<template>
  <a-config-provider :theme="customTheme">
    <div id="app">
      <router-view />
    </div>
  </a-config-provider>
</template>

<script setup lang="ts">
// 配置主题
const customTheme = {
  token: {
    colorPrimary: '#165DFF',
    borderRadius: 4,
  },
}
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
