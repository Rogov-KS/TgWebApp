import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type Theme = 'light' | 'dark' | 'system';

interface ThemeState {
  currentTheme: Theme;
  isDark: boolean;
}

// Функция для определения системной темы
const getSystemTheme = (): boolean => {
  if (typeof window !== 'undefined') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  return false;
};

// Функция для получения сохраненной темы из localStorage
const getStoredTheme = (): Theme => {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('theme');
    if (stored && ['light', 'dark', 'system'].includes(stored)) {
      return stored as Theme;
    }
  }
  return 'system';
};

// Функция для определения, должна ли тема быть темной
const shouldBeDark = (theme: Theme): boolean => {
  if (theme === 'system') {
    return getSystemTheme();
  }
  return theme === 'dark';
};

const initialState: ThemeState = {
  currentTheme: getStoredTheme(),
  isDark: shouldBeDark(getStoredTheme()),
};

const themeSlice = createSlice({
  name: 'theme',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<Theme>) => {
      state.currentTheme = action.payload;
      state.isDark = shouldBeDark(action.payload);

      // Сохраняем в localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('theme', action.payload);

        // Применяем класс к document
        const root = document.documentElement;
        if (state.isDark) {
          root.classList.add('dark');
        } else {
          root.classList.remove('dark');
        }
      }
    },
    toggleTheme: (state) => {
      const newTheme = state.isDark ? 'light' : 'dark';
      state.currentTheme = newTheme;
      state.isDark = !state.isDark;

      // Сохраняем в localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('theme', newTheme);

        // Применяем класс к document
        const root = document.documentElement;
        if (state.isDark) {
          root.classList.add('dark');
        } else {
          root.classList.remove('dark');
        }
      }
    },
    initializeTheme: (state) => {
      // Инициализация темы при загрузке приложения
      const root = document.documentElement;
      if (state.isDark) {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    },
  },
});

export const { setTheme, toggleTheme, initializeTheme } = themeSlice.actions;
export default themeSlice.reducer;
