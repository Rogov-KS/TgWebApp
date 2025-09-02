# TgSnakeWebApp


## Как запустить приложение?

Есть два способа:

0. Теперь есть docker compose так что подойдёт команда `docker compose down && clear && docker compose up --build`

1. Просто запустить `start_scripts/start_all_with_ngrok.sh`, находясь в корне (в папке `TgWebApp`)

2. Более многоступенчатый:

    - Сначала запустить `ngrok start --all`
    - Потом обновить переменные `VITE_NGROK_FRONTEND_URL` и `VITE_NGROK_BACKEND_URL` в соотвествии с выходом ngrok (порт 8000 для бекенда, а порт 5173 для фронтенда)
    - А затем уже запустить `start_scripts/start_app.sh`, находясь в корне (в папке `TgWebApp`)
