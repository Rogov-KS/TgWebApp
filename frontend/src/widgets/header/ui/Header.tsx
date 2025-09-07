import { useModal } from '../../../contexts/ModalContext';
import { ModalType } from '../../../contexts/ModalContext';
import { ProfileIcon } from '../../../features/auth/ui/ProfileIcon';

export function Header() {
  const { openModal } = useModal();

  const handleLeaderboardClick = () => {
    openModal(ModalType.LEADERBOARD);
  };

  return (
    <header className="bg-black/20 backdrop-blur-sm border-b border-white/10 relative z-20">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div>
            <h1 className="text-white text-xl font-bold">Snake Game</h1>
            <p className="text-gray-300 text-xs">Telegram Web App</p>
          </div>

          {/* Navigation */}
          <div className="hidden lg:flex items-center gap-10">
            <a href="#" className="text-gray-200 hover:text-white transition-colors text-sm">
              Играть
            </a>
            <button
              onClick={handleLeaderboardClick}
              className="text-gray-200 hover:text-white transition-colors text-sm"
            >
              Рейтинг
            </button>
            <a href="#" className="text-gray-200 hover:text-white transition-colors text-sm">
              О нас
            </a>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-4">
            {/* Profile Icon - всегда в самой правой части */}
            <ProfileIcon onGuestPlay={() => {}} />
          </div>
        </div>
      </div>
    </header>
  );
}
