import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HeaderFooter } from './components/Layout/HeaderFooter'
import './index.css'

const rootElement = document.getElementById('root')
if (!rootElement) throw new Error('Failed to find the root element')

createRoot(rootElement).render(
  <StrictMode>
    <HeaderFooter>
      <div tag="body" className="w-full max-w-md bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8 text-center relative z-10 border border-white/20">
        <div className="mb-6">
          <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-600 rounded-full mx-auto mb-4 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">T</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Добро пожаловать!
          </h1>
          <p className="text-gray-600">
            Tailwind CSS успешно подключен к вашему проекту
          </p>
        </div>

        <div className="space-y-4">
          <button className="w-full bg-gradient-to-r from-orange-500 to-red-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-orange-600 hover:to-red-700 transition-all duration-200 transform hover:scale-105 shadow-lg">
            Начать работу
          </button>

          <div className="flex flex-wrap gap-2 justify-center">
            <div className="bg-green-100 text-green-800 py-2 px-4 rounded-lg text-sm font-medium">
              ✅ Vite
            </div>
            <div className="bg-blue-100 text-blue-800 py-2 px-4 rounded-lg text-sm font-medium">
              ✅ React
            </div>
            <div className="bg-purple-100 text-purple-800 py-2 px-4 rounded-lg text-sm font-medium">
              ✅ Tailwind
            </div>
          </div>
        </div>

        <div className="mt-6 text-xs text-gray-500">
          Готово к разработке! 🚀
        </div>
      </div>
    </HeaderFooter>
  </StrictMode>
)
