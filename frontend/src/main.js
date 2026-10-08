import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入你的路由配置
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import DataVVue3 from '@kjgl77/datav-vue3'

const app = createApp(App)
app.use(router) // 激活路由！非常重要
app.use(ElementPlus)
app.use(DataVVue3)
app.mount('#app')