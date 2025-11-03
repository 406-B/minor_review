<template>
  <div id="app">
    <header class="site-header">
      <div class="top-breadcrumb">
        <nav>
          <a @click.prevent="goHome">首页</a>
          <a @click.prevent="goCommunity">点评社区</a>
          <a @click.prevent="goProfile">个人主页</a>
        </nav>
      </div>

      
    </header>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
function goCommunity() { router.push({ name: 'CommunityHome' }) }
function goHome() { router.push({ path: '/' }) }
function goProfile() { router.push({ path: '/' }) }
</script>

<style scoped>
.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #fff;
  border-bottom: 1px solid #eee;
}
.top-breadcrumb {
  padding: 10px 20px;
  font-size: 14px;
  color: #666;
  max-width: 1200px;
  margin: 0 auto;
}
.top-breadcrumb nav { display:flex; gap:12px; align-items:center }
.top-breadcrumb nav a { color: #409eff; cursor: pointer }
.header-main { display:flex; justify-content:space-between; align-items:center; padding:8px 20px }
.logo { width:48px; height:48px }
.nav-links { list-style:none; display:flex; gap:12px; margin:0; padding:0 }
.nav-links li { cursor:pointer; color:#333; padding:6px 10px; border-radius:4px }
.nav-links li.active { background:#eef6ff; color:#409eff }
.user-area { color:#666 }
main { padding: 20px; padding-top: 84px }

/* ensure header inner content isn't squeezed by any left side navigation */
.site-header, .top-breadcrumb, .header-main { box-sizing: border-box }
</style>
