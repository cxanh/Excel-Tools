import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import PluginContainer from "../views/PluginContainer.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: Home,
  },
  {
    path: "/plugin/:key",
    name: "plugin",
    component: PluginContainer,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
