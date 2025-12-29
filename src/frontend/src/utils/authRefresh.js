/**
 * 刷新与登录态相关的依赖项。
 * 会读取 localStorage 中的 `jwt` 并派发全局事件 `auth:changed`，
 * detail: { isAuthed: boolean }
 */
export function refreshAuthDependent() {
  const isAuthed = !!(typeof localStorage !== 'undefined' && localStorage.getItem('jwt'))
  try {
    window.dispatchEvent(new CustomEvent('auth:changed', { detail: { isAuthed } }))
  } catch (e) {
    // 浏览器不支持 CustomEvent 的极端情况
    const ev = document.createEvent('Event')
    ev.initEvent('auth:changed', true, true)
    ev.detail = { isAuthed }
    window.dispatchEvent(ev)
  }
  return isAuthed
}

export default refreshAuthDependent
