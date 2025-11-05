<!-- TODO：互动信息部分仍存在问题，需要前后端进行修改 -->

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
                <div class="post-meta">{{ p.createdAt }}</div>
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
            <p v-if="loading" class="hint">加载中...</p>
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
import { useRouter } from 'vue-router'
import SectionCard from '@/components/SectionCard.vue'
import ProfileInfo from '@/components/ProfileInfo.vue'
import InteractionStat from '@/components/InteractionStat.vue'
import ControlPanel from '@/components/ControlPanel.vue'
import { getProfileSections } from '@/api/profile'
import { getMyPosts, getUserStats } from '@/api/community'

const router = useRouter()
const published = ref([])
const interactions = ref([])
const user = ref({})
const loading = ref(false)

const load = async () => {
  loading.value = true
  try {
    // 获取个人资料和基础数据
    const res = await getProfileSections()
    user.value = res.user || {}
    
    // 获取用户统计信息
    let receivedCommentsCount = 0
    try {
      const stats = await getUserStats()
      
      // 获取我的帖子列表以统计收到的评论数
      try {
        const postsRes = await getMyPosts(1, 100) // 获取更多帖子以准确统计
        if (postsRes.code === 200 && postsRes.data) {
          // 计算所有帖子收到的评论总数
          receivedCommentsCount = (postsRes.data.posts || []).reduce((sum, post) => {
            return sum + (post.comments_count || 0)
          }, 0)
          
          // 设置已发布内容列表（只显示前5条）
          published.value = (postsRes.data.posts || []).slice(0, 5).map(post => ({
            id: post.id,
            title: post.subject || '无标题', // 直接使用 subject 字段
            createdAt: formatTime(post.created_at)
          }))
        }
      } catch (err) {
        console.error('获取我的帖子失败:', err)
      }
      
      // 设置交互统计数据
      interactions.value = [
        { name: '我点赞的帖子', count: stats.liked_posts_count || 0, to: '/community' },
        { name: '我收到的评论', count: receivedCommentsCount, to: '/community' },
        { name: '我发布的评论', count: stats.commented_posts_count || 0, to: '/community' }
      ]
    } catch (err) {
      console.error('获取用户统计失败:', err)
      // 使用默认值
      interactions.value = [
        { name: '我点赞的帖子', count: 0, to: '/community' },
        { name: '我收到的评论', count: 0, to: '/community' },
        { name: '我发布的评论', count: 0, to: '/community' }
      ]
      published.value = res.published || []
    }
  } catch (e) {
    console.error('加载个人主页数据失败', e)
  } finally {
    loading.value = false
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
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
