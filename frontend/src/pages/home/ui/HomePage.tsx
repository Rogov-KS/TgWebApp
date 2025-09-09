import { GamePage } from '../../game';

export function HomePage() {
  return (
    <div className="min-h-screen flex flex-col gradient-primary">
      <div className="flex-1 flex items-center justify-center p-4 relative">
        <GamePage />
      </div>
    </div>
  );
}
