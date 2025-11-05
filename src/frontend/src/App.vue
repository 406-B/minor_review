<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
function goCommunity() { router.push({ name: 'CommunityHome' }) }
function goHome() { router.push({ path: '/' }) }
function goProfile() { router.push({ path: '/profile' }) }
</script>

<template>
  <div id="app-root">
    <nav class="top-nav">
      <router-link to="/">点评社区</router-link>
      <router-link to="/profile">个人主页</router-link>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>


<style scoped>
/* kept some legacy styles harmlessly; main UI is handled in components */
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}

.top-nav { display:flex; gap:1rem; padding:0.75rem 1rem; background:#fafafa; border-bottom:1px solid rgba(0,0,0,0.04) }
.top-nav a { color:#2b8aef; text-decoration:none }
#app-root { min-height: 100vh }
</style>
