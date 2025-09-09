import { useState, useRef, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../../app/store/hooks';
import { setTheme, Theme } from '../../../app/store/themeSlice';
import './ThemeDropdown.css';

const themeOptions = [
  { value: 'light' as Theme, label: 'Светлая', icon: '☀️' },
  { value: 'dark' as Theme, label: 'Темная', icon: '🌙' },
  { value: 'system' as Theme, label: 'Системная', icon: '💻' },
];

export function ThemeDropdown() {
  const dispatch = useAppDispatch();
  const { currentTheme } = useAppSelector((state) => state.theme);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Закрытие dropdown при клике вне его
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleThemeSelect = (theme: Theme) => {
    dispatch(setTheme(theme));
    setIsOpen(false);

    // Логируем информацию о выбранной теме
    if (theme === 'system') {
      const systemIsDark = window.matchMedia(
        '(prefers-color-scheme: dark)'
      ).matches;
      console.log('🎨 Выбрана системная тема:', {
        theme: theme,
        systemTheme: systemIsDark ? 'dark' : 'light',
        appliedTheme: systemIsDark ? 'Темная' : 'Светлая',
        timestamp: new Date().toLocaleTimeString(),
      });
    } else {
      console.log('🎨 Выбрана тема:', {
        theme,
        appliedTheme: theme === 'dark' ? 'Темная' : 'Светлая',
        timestamp: new Date().toLocaleTimeString(),
      });
    }
  };

  const currentOption = themeOptions.find(
    (option) => option.value === currentTheme
  );

  return (
    <div className="theme-dropdown" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="theme-dropdown-trigger"
        aria-label="Выбрать тему"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <div className="theme-dropdown-icon">{currentOption?.icon}</div>
        <div className="theme-dropdown-arrow">
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          >
            <polyline points="6,9 12,15 18,9" />
          </svg>
        </div>
      </button>

      {isOpen && (
        <div className="theme-dropdown-menu">
          {themeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => handleThemeSelect(option.value)}
              className={`theme-dropdown-item ${
                currentTheme === option.value
                  ? 'theme-dropdown-item-active'
                  : ''
              }`}
            >
              <span className="theme-dropdown-item-icon">{option.icon}</span>
              <span className="theme-dropdown-item-label">{option.label}</span>
              {currentTheme === option.value && (
                <span className="theme-dropdown-item-check">✓</span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
