import * as real from './client';
import * as mock from './mock_client';

function shouldUseMock(): boolean {
  try {
    const qs = new URLSearchParams(window.location.search);
    if (qs.has('mock') || qs.has('mockAuth')) return true;
  } catch {}
  try {
    if ((import.meta as any)?.env?.VITE_ENABLE_MOCKS === 'true') return true;
    if ((import.meta as any)?.env?.VITE_MOCK_AUTH === 'true') return true;
  } catch {}
  return false;
}

const useMock = shouldUseMock();

export const authAPI = useMock ? mock.authAPI : real.authAPI;
export const gameAPI = useMock ? mock.gameAPI : real.gameAPI;
export const leaderboardAPI = useMock ? mock.leaderboardAPI : real.leaderboardAPI;
export const googleOAuthAPI = useMock ? mock.googleOAuthAPI : real.googleOAuthAPI;
export const yandexOAuthAPI = useMock ? mock.yandexOAuthAPI : real.yandexOAuthAPI;
export { getBaseURL } from './client';
