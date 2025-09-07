import { useModal, ModalType } from '../../../shared/lib/contexts/ModalContext';
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

          {/* Заголовок с иконкой профиля и кнопкой лидерборда */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h2 style={{ color: '#FFFFFF', margin: 0 }}>
              Snake Game
            </h2>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
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
          <div className="flex items-center">
            {/* Profile Icon - всегда в самой правой части */}
            <ProfileIcon onGuestPlay={() => {}} />
          </div>
        </div>
      </div>
    </header>
  );
}
