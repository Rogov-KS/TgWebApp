import { useModal, ModalType } from '../../../shared/lib/contexts/ModalContext';
import { ProfileIcon } from '../../../features/auth/ui/ProfileIcon';
import { ThemeDropdown } from '../../../shared/ui';

export function Header() {
  const { openModal } = useModal();

  const handleLeaderboardClick = () => {
    openModal(ModalType.LEADERBOARD);
  };

  return (
    <div className="gradient-primary border-b border-slate-300 dark:border-white/20 relative z-20">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div>
            <h1 className="text-slate-800 dark:text-white text-xl font-bold">Snake Game</h1>
            <p className="text-slate-600 dark:text-gray-300 text-xs">Telegram Web App</p>
          </div>

          {/* Заголовок с иконкой профиля и кнопкой лидерборда */}
          <div className="flex justify-between items-center mb-5">
            <h2 className="text-slate-800 dark:text-white m-0">
              Snake Game
            </h2>

            <div className="flex items-center gap-3">
              {/* Кнопка лидерборда */}
              <button
                onClick={handleLeaderboardClick}
                className="text-slate-800 dark:text-white border-slate-300 dark:border-white/20 hover:bg-slate-100 dark:hover:bg-white/10"
              >
                🏆 Лидеры
              </button>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-3">
            {/* Theme Dropdown */}
            <ThemeDropdown />

            {/* Profile Icon - всегда в самой правой части */}
            <ProfileIcon onGuestPlay={() => {}} />
          </div>
        </div>
      </div>
    </div>
  );
}
