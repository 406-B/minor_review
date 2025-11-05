<template>
  <div class="profile-info">
    <div class="avatar-area">
      <img class="avatar" :src="avatarSrc" alt="avatar" />
    </div>
    <div class="meta">
      <h2 class="name">{{ userDisplayName }}</h2>
        <ul class="meta-list">
          <li v-if="user.created"><strong>注册时间：</strong>{{ formatDate(user.created) }}</li>
        </ul>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  user: { type: Object, default: () => ({}) }
})


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
.meta-list { margin: 0.5rem 0 0; padding-left: 1rem; }
.todo { color: #999; margin-top: 0.5rem; }
.name { margin: 0; }
.bio { margin: 0.25rem 0; color: #555 }
.actions { margin-top: 0.75rem }
</style>
