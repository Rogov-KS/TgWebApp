#!/bin/bash

# Проверяем, был ли PYTHONPATH экспортирован
if [ -z "${PYTHONPATH:-}" ]; then
    export PYTHONPATH=$(pwd)
fi

# Проверяем, содержится ли текущий путь в PYTHONPATH
if [[ ":$PYTHONPATH:" != *":$(pwd):"* ]]; then
    export PYTHONPATH=$PYTHONPATH:$(pwd)
fi

source .venv/bin/activate

clear

uvicorn backend.main:app --reload
# python3 backend/main.py
# python3 backend/test_main.py
