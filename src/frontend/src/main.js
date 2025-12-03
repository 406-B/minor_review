

import './assets/main.css'
import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus, { ElMessage, ElLoading } from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router/index.js'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
// 暴露全局路由引用（用于个别组件的延迟跳转场景）
window.appRouter = router

// 全局消息封装
window.$message = {
	success: (msg) => ElMessage({ type: 'success', message: msg }),
	error: (msg) => ElMessage({ type: 'error', message: msg }),
	info: (msg) => ElMessage({ type: 'info', message: msg }),
	warning: (msg) => ElMessage({ type: 'warning', message: msg }),
}

// 路由加载指示（轻量 Loading 遮罩）
let loadingInstance = null
router.beforeEach((to, from, next) => {
	if (!loadingInstance) {
		loadingInstance = ElLoading.service({ fullscreen: true, text: '页面加载中...' })
	}
	next()
})
router.afterEach(() => {
	if (loadingInstance) {
		loadingInstance.close()
		loadingInstance = null
	}
})

app.mount('#app')
