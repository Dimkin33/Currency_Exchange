#!/bin/bash

# === Конфигурация ===
APP_DIR="proect_currency"
BRANCH="main"
REPO_URL="https://github.com/Dimkin33/test.git"

# === Функция логирования ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# === Начало ===
log "🚀 Начало деплоя"

# 1. Установка rye
if ! command -v rye &> /dev/null; then
    log "📦 Установка rye..."
    curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION=--yes bash || { log "❌ Ошибка установки rye"; exit 1; }
    echo 'source "$HOME/.rye/env"' >> ~/.profile
    source "$HOME/.rye/env"
fi

# 2. Клонирование или обновление репозитория
if [ ! -d "$APP_DIR" ]; then
    log "📥 Клонирование репозитория..."
    git clone --branch $BRANCH "$REPO_URL" "$APP_DIR" || { log "❌ Не удалось клонировать репозиторий"; exit 1; }
else
    log "📤 Обновление репозитория..."
    cd "$APP_DIR" || { log "❌ Не удалось перейти в $APP_DIR"; exit 1; }
    git fetch origin
    git reset --hard "origin/$BRANCH" || { log "❌ Не удалось обновить код"; exit 1; }
    cd ..
fi

# 3. Смена директории в проект
cd "$APP_DIR" || { log "❌ Директория $APP_DIR не найдена"; exit 1; }

# 4. Копирование переменных окружения
log "📄 Копирование .env файлов..."
cp -f ../.env .env
cp -f ../.env.test .env.test

# 5. Установка зависимостей
log "📦 Установка зависимостей через rye..."
rye sync || { log "❌ Ошибка при установке зависимостей"; exit 1; }

# 6. Установка PYTHONPATH (важно!)
export PYTHONPATH=src

# 7. Сборка
log "🔨 Сборка проекта..."
rye build || { log "❌ Сборка завершилась с ошибкой"; exit 1; }

# 8. Инициализация базы
log "🛠️ Инициализация базы данных..."
rye run init-db || { log "❌ Ошибка инициализации базы"; exit 1; }

# 9. Запуск
log "🚀 Запуск приложения в фоне..."
nohup rye run start > app.log 2>&1 &

log "✅ Приложение запущено в фоне. Логи записываются в app.log"

log "✅ Деплой завершён успешно!"
