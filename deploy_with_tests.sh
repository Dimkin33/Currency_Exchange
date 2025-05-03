#!/bin/bash

# Переменные
APP_DIR="/proect_currency"  # Путь к директории развертывания
BRANCH="main"  # Ветка для деплоя
REPO_URL="git@github.com:your-username/your-repo.git"  # URL вашего репозитория

# Функция для вывода сообщений
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Начало деплоя с тестами"

# 1. Установка rye, если он не установлен
if ! command -v rye &> /dev/null; then
    log "Установка rye..."
    curl -sSf https://rye-up.com/get | bash
    export PATH="$HOME/.rye/bin:$PATH"  # Добавляем rye в PATH
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
rye sync --dev  # Устанавливаем dev-зависимости для тестов

# 4. Запуск тестов
log "Запуск тестов..."
if ! rye run test; then
    log "Тесты не прошли. Деплой остановлен."
    exit 1
fi

# 5. Сборка проекта
log "Сборка проекта..."
rye build

# 6. Запуск приложения
log "Запуск приложения..."
rye run start

log "Деплой завершен!"