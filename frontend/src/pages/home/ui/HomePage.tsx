import { GamePage } from '../../game';
import { Header } from '../../../widgets/header';
import { Footer } from '../../../widgets/footer';

export function HomePage() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700">
      <Header />

      <main className="flex-1 flex items-center justify-center p-4 relative">
        <GamePage />
      </main>

      <Footer />
    </div>
  );
}
