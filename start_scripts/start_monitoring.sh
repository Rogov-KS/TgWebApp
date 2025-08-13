#!/bin/bash

echo "Запуск Prometheus и Grafana..."

# Остановка существующих контейнеров мониторинга
docker-compose down prometheus grafana 2>/dev/null || true

# Запуск сервисов мониторинга
docker-compose up -d prometheus grafana

echo "✅ Prometheus запущен на http://localhost:9090"
echo "✅ Grafana запущен на http://localhost:3000"
echo "   Логин: admin"
echo "   Пароль: admin"
echo ""
echo "Для просмотра логов: docker-compose logs -f prometheus grafana"
echo "Для остановки: docker-compose down prometheus grafana"
