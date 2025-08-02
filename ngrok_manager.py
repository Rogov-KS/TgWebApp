#!/usr/bin/env python3
"""
Ngrok Manager - утилита для автоматического управления ngrok туннелями
"""

import requests
import json
import time
import os
import sys
from typing import Dict, List, Optional

class NgrokManager:
    def __init__(self, api_url: str = "http://localhost:4040"):
        self.api_url = api_url
        self.session = requests.Session()

    def is_ngrok_running(self) -> bool:
        """Проверяет, запущен ли ngrok"""
        try:
            response = self.session.get(f"{self.api_url}/api/tunnels")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_tunnels(self) -> List[Dict]:
        """Получает список всех туннелей"""
        try:
            response = self.session.get(f"{self.api_url}/api/tunnels")
            if response.status_code == 200:
                data = response.json()
                return data.get("tunnels", [])
            return []
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения туннелей: {e}")
            return []

    def get_tunnel_by_port(self, port: int) -> Optional[Dict]:
        """Получает туннель по порту"""
        tunnels = self.get_tunnels()
        for tunnel in tunnels:
            if tunnel.get("config", {}).get("addr") == f"localhost:{port}":
                return tunnel
        return None

    def get_tunnel_url(self, port: int) -> Optional[str]:
        """Получает URL туннеля по порту"""
        tunnel = self.get_tunnel_by_port(port)
        return tunnel.get("public_url") if tunnel else None

    def create_tunnel(self, port: int, name: str = None) -> Optional[Dict]:
        """Создает новый туннель"""
        try:
            payload = {
                "addr": f"localhost:{port}"
            }
            if name:
                payload["name"] = name

            response = self.session.post(
                f"{self.api_url}/api/tunnels",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 201:
                return response.json()
            else:
                print(f"Ошибка создания туннеля: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка создания туннеля: {e}")
            return None

    def delete_tunnel(self, name: str) -> bool:
        """Удаляет туннель по имени"""
        try:
            response = self.session.delete(f"{self.api_url}/api/tunnels/{name}")
            return response.status_code == 204
        except requests.exceptions.RequestException as e:
            print(f"Ошибка удаления туннеля: {e}")
            return False

    def wait_for_ngrok(self, timeout: int = 30) -> bool:
        """Ожидает готовности ngrok API"""
        print("Ожидание готовности ngrok API...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.is_ngrok_running():
                print("Ngrok API готов")
                return True
            time.sleep(1)

        print("Таймаут ожидания ngrok API")
        return False

    def setup_tunnels(self, backend_port: int = 8000, frontend_port: int = 5173) -> Dict[str, str]:
        """Настраивает туннели для backend и frontend"""
        tunnels = {}

        # Создаем туннель для backend
        print(f"Создание туннеля для backend (порт {backend_port})...")
        backend_tunnel = self.create_tunnel(backend_port, "backend")
        if backend_tunnel:
            tunnels["backend"] = backend_tunnel.get("public_url")
            print(f"Backend туннель создан: {tunnels['backend']}")

        # Создаем туннель для frontend
        print(f"Создание туннеля для frontend (порт {frontend_port})...")
        frontend_tunnel = self.create_tunnel(frontend_port, "frontend")
        if frontend_tunnel:
            tunnels["frontend"] = frontend_tunnel.get("public_url")
            print(f"Frontend туннель создан: {tunnels['frontend']}")

        return tunnels

    def update_env_file(self, tunnels: Dict[str, str]):
        """Обновляет .env файл с URL туннелей"""
        env_content = ""

        if "frontend" in tunnels:
            env_content += f"VITE_NGROK_FRONTEND_URL={tunnels['frontend']}\n"

        if "backend" in tunnels:
            env_content += f"VITE_NGROK_BACKEND_URL={tunnels['backend']}\n"

        if env_content:
            with open(".env", "w") as f:
                f.write(env_content)
            print("Файл .env обновлен")

    def print_status(self):
        """Выводит статус всех туннелей"""
        tunnels = self.get_tunnels()

        if not tunnels:
            print("Активных туннелей не найдено")
            return

        print("Активные туннели:")
        for tunnel in tunnels:
            name = tunnel.get("name", "unnamed")
            public_url = tunnel.get("public_url", "N/A")
            addr = tunnel.get("config", {}).get("addr", "N/A")
            print(f"  {name}: {public_url} -> {addr}")

def main():
    manager = NgrokManager()

    if len(sys.argv) < 2:
        print("Использование:")
        print("  python ngrok_manager.py status          - показать статус туннелей")
        print("  python ngrok_manager.py setup           - настроить туннели")
        print("  python ngrok_manager.py get <port>      - получить URL туннеля по порту")
        print("  python ngrok_manager.py create <port>   - создать туннель для порта")
        return

    command = sys.argv[1]

    if command == "status":
        if not manager.is_ngrok_running():
            print("Ngrok не запущен")
            return
        manager.print_status()

    elif command == "setup":
        if not manager.wait_for_ngrok():
            print("Не удалось подключиться к ngrok API")
            return

        tunnels = manager.setup_tunnels()
        if tunnels:
            manager.update_env_file(tunnels)
            print("\nНастройка завершена:")
            for name, url in tunnels.items():
                print(f"  {name}: {url}")

    elif command == "get" and len(sys.argv) > 2:
        port = int(sys.argv[2])
        url = manager.get_tunnel_url(port)
        if url:
            print(f"URL для порта {port}: {url}")
        else:
            print(f"Туннель для порта {port} не найден")

    elif command == "create" and len(sys.argv) > 2:
        port = int(sys.argv[2])
        name = sys.argv[3] if len(sys.argv) > 3 else None

        if not manager.wait_for_ngrok():
            print("Не удалось подключиться к ngrok API")
            return

        tunnel = manager.create_tunnel(port, name)
        if tunnel:
            print(f"Туннель создан: {tunnel.get('public_url')}")
        else:
            print("Ошибка создания туннеля")

    else:
        print("Неизвестная команда")

if __name__ == "__main__":
    main()