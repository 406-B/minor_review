

import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
<<<<<<< HEAD
import router from './router/index.js'
=======
import router from '@/router'
>>>>>>> origin/dev

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
