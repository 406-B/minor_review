<template>
	<div class="sidebar-vertical">
		<div class="sidebar-search">
			<el-input
				v-model="searchText"
				placeholder="搜索菜品/标签/价格"
				size="small"
				@keyup.enter="goSearch"
				clearable
				class="search-input"
			>
				<template #append>
					  <el-button icon="el-icon-search" @click="goSearch" size="small">搜索</el-button>
				</template>
			</el-input>
		</div>
		<el-menu
			:default-active="activeCanteen"
			class="canteen-sidebar-menu"
			@select="handleSelect"
			background-color="orange"
			text-color="#fff"
			active-text-color="#ffd04b"
		>
			<el-menu-item
				v-for="canteen in canteens"
				:key="String(canteen.id)"
				:index="String(canteen.id)"
			>
				{{ canteen.name }}
			</el-menu-item>
		</el-menu>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const props = defineProps({
	canteens: {
		type: Array,
		required: true
	},
	activeCanteen: {
		type: String,
		required: true
	}
})
const emit = defineEmits(['update:active-canteen'])
const router = useRouter()
const searchText = ref('')

function handleSelect(key) {
	emit('update:active-canteen', String(key))
}
function goSearch() {
	if (searchText.value.trim()) {
		router.push({ name: 'DishSearch', query: { q: searchText.value.trim() } })
		searchText.value = ''
	} else {
		router.push({ name: 'DishSearch' })
	}
}
</script>

<style scoped>
.sidebar-vertical {
	display: flex;
	flex-direction: column;
	height: 100vh;
	width: 220px;
	min-width: 200px;
	max-width: 260px;
	background: orange;
	box-shadow: 2px 0 16px #e0e0e0aa;
}
.sidebar-search {
	padding: 16px 12px 8px 12px;
	background: orange;
}
.search-input {
	width: 100%;
}
.canteen-sidebar-menu {
	border-right: none;
	background: orange;
	flex: 1 1 auto;
	height: auto;
	min-height: 0;
	width: 100%;
	box-shadow: none;
	overflow-y: auto;
}
</style>
