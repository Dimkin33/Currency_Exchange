#!/bin/bash

# Переменные
APP_DIR="proect_currency"  # Путь к директории развертывания
BRANCH="main"  # Ветка для деплоя
REPO_URL="https://github.com/Dimkin33/test.git"  # URL вашего репозитория

# Функция для вывода сообщений
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Начало деплоя"

# 1. Установка rye, если он не установлен
if ! command -v rye &> /dev/null; then
    log "Установка rye..."
    curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION=--yes bash
    export PATH="$HOME/.rye/bin:$PATH"  # Добавляем rye в PATH
    echo 'source "$HOME/.rye/env"' >> ~/.profile
    source "$HOME/.rye/env"

fi

# 2. Клонирование или обновление репозитория
if [ ! -d "$APP_DIR" ]; then
    log "Клонирование репозитория..."
    git clone $REPO_URL $APP_DIR
else
    log "Обновление репозитория..."
    cd $APP_DIR
    git fetch origin
    git reset --hard origin/$BRANCH
fi

# 3. Установка зависимостей через rye
log "Установка зависимостей через rye..."
cd $APP_DIR
rye sync

# 4. Сборка проекта
log "Сборка проекта..."
rye build

# 4.5 Инициализация базы данных
log " Инициализация базы данных"
rye run init-db


# 5. Запуск приложения
log "Запуск приложения..."
rye run start

log "Деплой завершен!"