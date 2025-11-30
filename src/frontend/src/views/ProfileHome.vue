<template>
  <PageContainer>
    <template #header>
      <AppTopBar />
    </template>
  <ProfileInfo :user="user" />

    <!-- 已发布与 我的互动 同行 -->
    <div class="grid">
      <div class="col left">
        <SectionCard title="已发布内容">
          <template #actions>
            <button class="link" @click.prevent="viewAllPublished">查看全部</button>
          </template>
          <template #content>
            <div class="posts">
              <PostItem
                v-for="p in published.slice(0, 2)"
                :key="p.id"
                :post="p"
                :showStats="false"
              />
              <p v-if="!published || published.length === 0" class="empty">暂无已发布内容</p>
            </div>
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
  </PageContainer>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
 import PageContainer from '@/components/ui/PageContainer.vue'
 import SectionTitle from '@/components/ui/SectionTitle.vue'
 import AppTopBar from '@/components/ui/AppTopBar.vue'
import SectionCard from '@/components/SectionCard.vue'
import ProfileInfo from '@/components/ProfileInfo.vue'
import InteractionStat from '@/components/InteractionStat.vue'
import ControlPanel from '@/components/ControlPanel.vue'
import PostItem from '@/components/PostItem.vue'
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
  router.push('/profile/posts')
}

const onNavigate = (to) => {
  router.push(to)
}
</script>

<style scoped>
.profile-home { /* wrapped by PageContainer */ }
.title { font-size: 1.4rem; margin-bottom: 0.75rem }
.grid { display: grid; grid-template-columns: 1fr; gap: 1rem; margin-top: 1rem }
.col { display: flex; flex-direction: column; gap: 1rem }
.posts { list-style: none; padding: 0; margin: 0 }
.post { padding: 0.5rem 0; border-bottom: 1px dashed rgba(0,0,0,0.04) }
.post-title { font-weight: 600 }
.post-meta { font-size: 0.85rem; color: var(--color-muted) }
.interactions { display: flex; flex-wrap: wrap }
.hint { color: var(--color-muted); font-size: 0.85rem; margin-top: 0.5rem }
.link { background: none; border: none; color: var(--color-accent); cursor: pointer }

@media (min-width: 1024px) {
  .grid { grid-template-columns: 1fr 1fr }
}
</style>
