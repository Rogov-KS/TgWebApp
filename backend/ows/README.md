# OAuth2 Integrations

Модуль для интеграции с внешними сервисами через OAuth2 авторизацию.

## Структура

```
oauth2_integrations/
├── __init__.py              # Основные экспорты
├── base.py                  # Базовые классы
├── google/                  # Google интеграции
│   ├── __init__.py
│   └── drive.py            # Google Drive интеграция
└── yandex/                 # Yandex интеграции
    ├── __init__.py
    └── disk.py             # Yandex.Disk интеграция
```

## Использование

### Базовые классы

```python
from backend.ows.auth_integrations import CloudFile, CloudIntegration

# CloudFile - информация о файле в облачном хранилище
file = CloudFile(
    name="document.pdf",
    id="12345",
    size=1024,
    mime_type="application/pdf",
    modified_time="2024-01-01T12:00:00Z",
    download_url="https://example.com/download"
)

# CloudIntegration - базовый класс для интеграций
class MyCloudIntegration(CloudIntegration):
    async def get_files(self, access_token: str) -> List[CloudFile]:
        # Реализация получения файлов
        pass
```

### Google Drive интеграция

```python
from backend.ows.auth_integrations import GoogleDriveIntegration

drive = GoogleDriveIntegration()
files = await drive.get_files(access_token)
```

### Yandex.Disk интеграция

```python
from backend.ows.auth_integrations import YandexDiskIntegration

disk = YandexDiskIntegration()
files = await disk.get_files(access_token)
```

## Интеграция с OAuth2 провайдерами

OAuth2 провайдеры теперь используют эти интеграции для получения файлов из облачных хранилищ:

- `GoogleOAuth2Provider` использует `GoogleDriveIntegration`
- `YandexOAuth2Provider` использует `YandexDiskIntegration`

Это позволяет:
1. Разделить логику авторизации и работы с файлами
2. Легко добавлять новые интеграции
3. Переиспользовать код между разными частями приложения
4. Упростить тестирование
