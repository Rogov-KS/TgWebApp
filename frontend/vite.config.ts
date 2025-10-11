import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import fs from 'fs'

// Функция для загрузки .env файлов в нужном порядке
function loadCustomEnv(mode: string) {
  const envDir = path.resolve(__dirname, '../configs/envs')
  const envFiles = [
    path.join(envDir, '.env-base'),        // Базовый файл
    path.join(envDir, `.env-${mode}`),     // Режим-специфичный файл
    path.join(envDir, '.env.local'),       // Локальные переопределения
  ]

  let env: Record<string, string> = {}

  // Загружаем файлы в порядке приоритета
  for (const envFile of envFiles) {
    if (fs.existsSync(envFile)) {
      const fileContent = fs.readFileSync(envFile, 'utf-8')
      const lines = fileContent.split('\n')

      for (const line of lines) {
        const trimmedLine = line.trim()
        if (trimmedLine && !trimmedLine.startsWith('#')) {
          const [key, ...valueParts] = trimmedLine.split('=')
          if (key && valueParts.length > 0) {
            const value = valueParts.join('=').trim()
            env[key.trim()] = value
          }
        }
      }
    }
  }

  return env
}

// Функция для создания define объекта
function createDefineObject(env: Record<string, string>) {
  return Object.keys(env).reduce((acc, key) => {
    if (key.startsWith('VITE_')) {
      acc[`import.meta.env.${key}`] = JSON.stringify(env[key])
    }
    return acc
  }, {} as Record<string, string>)
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Загружаем кастомные .env файлы
  const customEnv = loadCustomEnv(mode)

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '~': path.resolve(__dirname, '.'),
      },
    },
    envDir: '../configs/envs',
    define: createDefineObject(customEnv),
    server: {
      allowedHosts: "all", // Разрешить все хосты для ngrok
    },
  }
})
