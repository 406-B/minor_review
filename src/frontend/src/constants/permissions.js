// 受限路由与权限常量（仅前端 UX 层使用，后端仍做最终鉴权）
export const PROTECTED_PATHS = [
  '/community',
  '/community/create',
]

// 若后续有角色控制，可在此扩展：
// export const ROLE_PERMISSIONS = { admin: ['*'], user: ['/profile', '/community'] };

export function isProtectedPath(path) {
  // 简单判定：以受限前缀开头即受限
  return PROTECTED_PATHS.some(p => path === p || path.startsWith(p + '/'))
}
