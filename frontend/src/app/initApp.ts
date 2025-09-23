import { setupTelegramMock } from '../shared/lib/utils/tg_helper/telegram_mock';
import { IsInTMA, clearTelegramMock } from '../shared/lib/utils/tg_helper/telegram_wrapper';
import {
    themeParams,
    miniApp,
    initData,
    init as initSDK
} from '@telegram-apps/sdk'

export const initApp = (): void => {
    const urlParams = new URLSearchParams(window.location.search);
    const isTelegramParamTrue = (urlParams.get('telegram') === 'true');

    // пытаемся удалить окружение Telegram если оно вдруг осталось
    clearTelegramMock();

    if (isTelegramParamTrue) {
        setupTelegramMock();
    } else if (IsInTMA()) {
        try {
            initSDK();

            miniApp.mount();
            themeParams.mount();
            initData.restore();
        } catch (error) {
            console.error('Error initializing SDK', error);
        }
    }
};
