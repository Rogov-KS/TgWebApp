import { useModal, ModalType } from '../../../shared/lib/contexts/ModalContext';
import { ProfileIcon } from '../../../features/auth/ui/ProfileIcon';
import { ThemeToggle } from '../../../shared/ui';

export function Header() {
  const { openModal } = useModal();

  const handleLeaderboardClick = () => {
    openModal(ModalType.LEADERBOARD);
  };

  return (
    <div className="bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700 dark:from-blue-600 dark:via-blue-700 dark:to-blue-800 border-b border-white/10 dark:border-white/20 relative z-20">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div>
            <h1 className="text-white text-xl font-bold">Snake Game</h1>
            <p className="text-gray-300 text-xs">Telegram Web App</p>
          </div>

          {/* Заголовок с иконкой профиля и кнопкой лидерборда */}
          <div className="flex justify-between items-center mb-5">
            <h2 className="text-white m-0">
              Snake Game
            </h2>

            <div className="flex items-center gap-3">
              {/* Кнопка лидерборда */}
              <button
                onClick={handleLeaderboardClick}
                className="text-white border-white/20 hover:bg-white/10"
              >
                🏆 Лидеры
              </button>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-3">
            {/* Theme Toggle */}
            <ThemeToggle />

            {/* Profile Icon - всегда в самой правой части */}
            <ProfileIcon onGuestPlay={() => {}} />
          </div>
        </div>
      </div>
    </div>
  );
}
