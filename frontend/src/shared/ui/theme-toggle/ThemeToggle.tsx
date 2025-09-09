import { useAppDispatch, useAppSelector } from '../../../app/store/hooks';
import { toggleTheme } from '../../../app/store/themeSlice';
import './ThemeToggle.css';

export function ThemeToggle() {
  const dispatch = useAppDispatch();
  const { isDark } = useAppSelector((state) => state.theme);

  const handleToggle = () => {
    dispatch(toggleTheme());
  };

  return (
    <button
      onClick={handleToggle}
      className="theme-toggle"
      aria-label={
        isDark ? 'Переключить на светлую тему' : 'Переключить на темную тему'
      }
      title={
        isDark ? 'Переключить на светлую тему' : 'Переключить на темную тему'
      }
    >
      <div className="theme-toggle-icon">
        {isDark ? (
          // Иконка солнца для светлой темы
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="5" />
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
          </svg>
        ) : (
          // Иконка луны для темной темы
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
          </svg>
        )}
      </div>
    </button>
  );
}
