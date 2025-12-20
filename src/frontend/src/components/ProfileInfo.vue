<template>
  <div class="profile-info">
    <div class="avatar-area">
      <img class="avatar" :src="avatarSrc" alt="avatar" />
    </div>
    <div class="meta">
      <div class="header-row">
        <h2 class="name">{{ userDisplayName }}</h2>
        <button class="edit-btn" @click="handleEdit">编辑资料</button>
      </div>
      <ul class="meta-list">
        <li v-if="user.created"><strong>注册时间：</strong>{{ formatDate(user.created) }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  user: { type: Object, default: () => ({}) }
})

const router = useRouter()

const userDisplayName = computed(() => props.user.nickname || props.user.name || '匿名用户')

const avatarSrc = computed(() => {
  if (props.user && props.user.avatar) return props.user.avatar
  try { return new URL('../assets/logo.svg', import.meta.url).href } catch (e) { return '' }
})

function formatDate(iso) {
  try {
    const d = new Date(iso)
    return d.toLocaleString()
  } catch (e) { return iso }
}

const handleEdit = () => {
  router.push('/profile/edit')
}
</script>

<style scoped>
.profile-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  border: 1px solid rgba(0,0,0,0.06);
  padding: 1rem;
  border-radius: 8px;
  background: #fff;
}
.avatar { width: 72px; height: 72px; border-radius: 8px; object-fit: cover; }
.meta { flex: 1; }
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.name { margin: 0; }
.edit-btn {
  padding: 0.4rem 1rem;
  background-color: var(--color-accent);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}
.edit-btn:hover {
  background-color: var(--brand-700);
}
.meta-list { margin: 0.5rem 0 0; padding-left: 1rem; }
.bio { margin: 0.25rem 0; color: #555 }
.actions { margin-top: 0.75rem }
</style>
