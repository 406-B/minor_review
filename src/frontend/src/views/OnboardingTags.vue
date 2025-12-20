<template>
	<PageContainer>
		<template #header><AppTopBar /></template>
		<div class="wrap">
			<h2 class="title">选择你的口味偏好</h2>
			<p class="subtitle">建议至少选择 3 个，用于个性化推荐；也可跳过</p>

			<div class="tools">
				<el-input v-model="keyword" placeholder="搜索标签..." clearable style="max-width: 260px" />
				<div class="spacer" />
				<el-button link type="primary" @click="clearAll" :disabled="selected.size===0">清空选择</el-button>
			</div>

			<div class="tag-grid">
				<el-check-tag
					v-for="t in filteredTags" :key="t.id"
					:checked="selected.has(t.id)"
					@change="() => toggle(t.id)"
					class="tag-item"
				>{{ t.name }}</el-check-tag>
			</div>

			<div class="actions">
				<el-button @click="skip" :disabled="saving">跳过</el-button>
				<el-button type="primary" @click="save" :disabled="selected.size===0" :loading="saving">
					保存偏好（{{ selected.size }}）
				</el-button>
			</div>
		</div>
	</PageContainer>
  
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTags } from '@/utils/api/listApi'
import { setPreferenceTags } from '@/api/profile'
import PageContainer from '@/components/ui/PageContainer.vue'
import AppTopBar from '@/components/ui/AppTopBar.vue'

const router = useRouter()
const tags = ref([])
const keyword = ref('')
const selected = ref(new Set())
const saving = ref(false)

const filteredTags = computed(() => {
	const k = keyword.value.trim().toLowerCase()
	if (!k) return tags.value
	return tags.value.filter(t => String(t.name).toLowerCase().includes(k))
})

const toggle = (id) => {
	const s = selected.value
	if (s.has(id)) s.delete(id)
	else s.add(id)
	// 触发更新
	selected.value = new Set(s)
}

const clearAll = () => { selected.value = new Set() }

const loadTags = async () => {
	try {
		const res = await getTags()
		tags.value = res?.data ?? res ?? []
	} catch (e) {
		window.$message?.error?.('加载标签失败')
	}
}

const save = async () => {
	saving.value = true
	try {
		await setPreferenceTags([...selected.value])
		window.$message?.success?.('偏好已保存')
		router.push('/profile')
	} catch (e) {
		window.$message?.error?.(e?.message || '保存失败')
	} finally {
		saving.value = false
	}
}

const skip = () => {
	router.push('/profile')
}

onMounted(loadTags)
</script>

<style scoped>
.wrap { max-width: 960px; margin: 0 auto; padding: 8px 0 }
.title { margin: 8px 0 4px; }
.subtitle { color: var(--color-muted); margin-bottom: 16px; }
.tools { display: flex; align-items: center; gap: 12px; margin-bottom: 12px }
.spacer { flex: 1 }
.tag-grid { display: flex; flex-wrap: wrap; gap: 8px; padding: 8px 0 }
.tag-item { padding: 8px 12px; border-radius: 6px; }
.actions { margin-top: 16px; display: flex; gap: 8px }
</style>
