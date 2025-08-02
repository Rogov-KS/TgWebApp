cd frontend


if [ -f "../.env" ]; then
    # Получаем переменную из .env
    export VITE_NGROK_FRONTEND_URL_SH=$(grep "^VITE_NGROK_FRONTEND_URL=" ../.env | cut -d'=' -f2 | sed 's|^https://||')
    echo "Найдена переменная VITE_NGROK_FRONTEND_URL: $VITE_NGROK_FRONTEND_URL_SH"

    # Обновляем vite.config.ts с новым значением
    if [ ! -z "$VITE_NGROK_FRONTEND_URL_SH" ]; then
        sed -i "s/allowedHosts: \[.*\]/allowedHosts: [\"$VITE_NGROK_FRONTEND_URL_SH\"]/" vite.config.ts
        echo "Обновлен vite.config.ts с новым allowedHosts: $VITE_NGROK_FRONTEND_URL_SH"
    fi
else
    echo "Файл .env не найден в корне проекта"
fi

clear

npm run dev
