#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."
# Проверка наличия .env файла


# === Конфигурация ===
BRANCH="main"
REPO_URL="https://github.com/Dimkin33/test.git"

# === Функция логирования ===
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# === Начало ===
log "🚀 Начало деплоя"

# Проверка наличия .env файла
if [ ! -f .env ]; then
    log "❌ Файл .env не найден по пути $(pwd)/.env. Завершение работы."
    exit 1
fi

# 1. Установка rye
if ! command -v rye &> /dev/null; then
    log "📦 Установка rye..."
    curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION=--yes bash || { log "❌ Ошибка установки rye"; exit 1; }
    echo 'source "$HOME/.rye/env"' >> ~/.profile
    source "$HOME/.rye/env"
fi

# 2. Клонирование или обновление репозитория
log "📤 Обновление репозитория..."
git fetch origin
git reset --hard "origin/$BRANCH" || { log "❌ Не удалось обновить код"; exit 1; }



# 5. Установка зависимостей
log "📦 Установка зависимостей через rye..."
rye sync || { log "❌ Ошибка при установке зависимостей"; exit 1; }

# # 6. Установка PYTHONPATH (важно!)
# export PYTHONPATH=src

# 7. Сборка
log "🔨 Сборка проекта..."
rye build || { log "❌ Сборка завершилась с ошибкой"; exit 1; }

# 8. Инициализация базы
log "🛠️ Инициализация базы данных..."
rye run init-db || { log "❌ Ошибка инициализации базы"; exit 1; }

# 9. Запуск
log "🚀 Запуск приложения в фоне..."
#nohup rye run start > app.log 2>&1 &
rye run start 

log "✅ Деплой завершён успешно!"
