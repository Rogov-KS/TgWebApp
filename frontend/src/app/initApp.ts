import { setupTelegramMock } from '../shared/lib/utils/tg_helper/telegram_mock';
import { IsInTMA } from '../shared/lib/utils/tg_helper/telegram_wrapper';
import {
    init as initSDK
} from '@telegram-apps/sdk';

export const initApp = (): void => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('telegram') === 'true') {
        setupTelegramMock();
    }

    if (IsInTMA()) {
        initSDK();
    }

};
