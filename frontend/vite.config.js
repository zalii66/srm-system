import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  // loadEnv 会按优先级加载以下文件：
  // 1. .env.[mode].local (最高优先级，git忽略)
  // 2. .env.local (git忽略)
  // 3. .env.[mode]
  // 4. .env (最低优先级)
  // 第三个参数 '' 表示加载所有环境变量（包括 VITE_ 前缀的）
  const env = loadEnv(mode, process.cwd(), '')
  
  // 获取环境变量（支持 VITE_ 前缀）
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://127.0.0.1:8001'
  const devPort = env.VITE_DEV_PORT || '3000'
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    server: {
      host: '0.0.0.0',  // 监听所有网络接口
      port: parseInt(devPort, 10),
      proxy: {
        // API代理：处理 /api 路径
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
          // 如果路径已经包含 /v1，直接转发；否则添加 /v1
          rewrite: path => {
            if (path.startsWith('/api/v1/')) {
              // 路径已经是 /api/v1/...，直接转发（不重写）
              return path
            } else if (path.startsWith('/api/')) {
              // 路径是 /api/...，重写为 /api/v1/...
              return path.replace(/^\/api/, '/api/v1')
            }
            return path
          }
        },
        // 文件服务代理：处理 /uploads 路径（文件服务不在 /api/v1 下）
        '/uploads': {
          target: proxyTarget,
          changeOrigin: true,
          // 文件路径直接转发，不重写
          rewrite: path => path
        }
      }
    }
  }
})
