<template>
  <div class="profile-home">
    <h1 class="title">个人主页</h1>

  <!-- 我的资料（最上方） -->
  <ProfileInfo :user="user" />

    <!-- 已发布与 我的互动 同行 -->
    <div class="grid">
      <div class="col left">
        <SectionCard title="已发布内容">
          <template #actions>
            <button class="link" @click.prevent="viewAllPublished">查看全部 <!-- TODO: 跳转到已发布列表 --></button>
          </template>
          <template #content>
            <ul class="posts">
              <li v-for="(p, idx) in published.slice(0,2)" :key="p.id" class="post">
                <div class="post-title">{{ p.title }}</div>
                <div class="post-meta">{{ p.createdAt }} <!-- TODO: 使用后端时间字段并格式化 --> </div>
              </li>
              <li v-if="!published || published.length === 0" class="empty">暂无已发布内容</li>
            </ul>
          </template>
        </SectionCard>
      </div>

      <div class="col right">
        <SectionCard title="我的互动">
          <template #content>
            <div class="interactions">
              <InteractionStat
                v-for="(it, i) in interactions"
                :key="i"
                :name="it.name"
                :count="it.count"
                :to="it.to"
                @navigate="onNavigate"
              />
            </div>
            <p class="hint"><!-- TODO: 后续替换为真实互动内容 --> 示例数据仅用于演示</p>
          </template>
        </SectionCard>
      </div>
    </div>

    <!-- 控制组件板块（在底部） -->
    <ControlPanel />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import SectionCard from '@/components/SectionCard.vue'
import ProfileInfo from '@/components/ProfileInfo.vue'
import InteractionStat from '@/components/InteractionStat.vue'
import ControlPanel from '@/components/ControlPanel.vue'
import { getProfileSections } from '@/api/profile'

const published = ref([])
const interactions = ref([])
const user = ref({})

const load = async () => {
  try {
    const res = await getProfileSections()
  published.value = res.published || []
  interactions.value = res.interactions || []
  user.value = res.user || {}
  } catch (e) {
    console.error('加载个人主页数据失败', e)
  }
}

onMounted(load)

const viewAllPublished = () => {
  // TODO: 使用 vue-router 跳转到已发布内容列表
  console.log('viewAllPublished TODO')
}

const onNavigate = (to) => {
  // TODO: 路由跳转或父组件处理
  console.log('navigate to', to)
}
</script>

<style scoped>
.profile-home { padding: 1rem; }
.title { font-size: 1.4rem; margin-bottom: 0.75rem }
.grid { display: grid; grid-template-columns: 1fr; gap: 1rem; margin-top: 1rem }
.col { display: flex; flex-direction: column; gap: 1rem }
.posts { list-style: none; padding: 0; margin: 0 }
.post { padding: 0.5rem 0; border-bottom: 1px dashed rgba(0,0,0,0.04) }
.post-title { font-weight: 600 }
.post-meta { font-size: 0.85rem; color: #666 }
.interactions { display: flex; flex-wrap: wrap }
.hint { color: #888; font-size: 0.85rem; margin-top: 0.5rem }
.link { background: none; border: none; color: #2b8aef; cursor: pointer }

@media (min-width: 1024px) {
  .grid { grid-template-columns: 1fr 1fr }
}
</style>
