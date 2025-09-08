import { GamePage } from '../../game';

export function HomePage() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700 dark:from-blue-600 dark:via-blue-700 dark:to-blue-800">
      <div className="flex-1 flex items-center justify-center p-4 relative">
        <GamePage />
      </div>
    </div>
  );
}
