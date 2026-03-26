import os
import json
import subprocess
from datetime import datetime

# Настройки имен файлов (с учетом двойных расширений Windows)
CONFIG_FILE = "Amy_config.json.txt"
INSIGHTS_FILE = "Amy_insights.md.txt"
INDEX_FILE = "Index.md.txt"
MEMORY_FILE = "Memory.txt"
CHATLOG_FILE = "Amy_chatlog.txt"
PROMPT_OUTPUT = "Rehydration_Prompt.txt"

# Хвост чатлога для промпта (в символах)
CHAT_TAIL_SIZE = 5000 

def run_git_commands():
    """Автоматизирует отправку изменений на GitHub."""
    try:
        print("[GIT] Синхронизация с репозиторием...")
        subprocess.run(["git", "add", "."], check=True)
        commit_msg = f"Auto-sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[GIT] Успешно отправлено на GitHub.")
    except Exception as e:
        print(f"[GIT ERROR] Не удалось выполнить push: {e}")

def update_archives():
    """Переносит данные из чатлога в память и обновляет индекс."""
    if not os.path.exists(CHATLOG_FILE) or os.path.getsize(CHATLOG_FILE) == 0:
        return "Нет новых данных для архивации."

    with open(CHATLOG_FILE, "r", encoding="utf-8") as f:
        new_content = f.read().strip()

    if not new_content:
        return

    timestamp = datetime.now().strftime("%d.%m.%y %H:%M")
    
    # 1. Добавляем в Memory
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n\n--- SESSION {timestamp} ---\n{new_content}")

    # 2. Добавляем краткую запись в Index (таблица Markdown)
    # Если файл пустой, создаем заголовок таблицы
    if os.path.getsize(INDEX_FILE) == 0:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write("| Дата | Суть | Ссылка в Memory |\n| :--- | :--- | :--- |\n")

    with open(INDEX_FILE, "a", encoding="utf-8") as f:
        f.write(f"| {timestamp} | New dialogue session | [See Memory] |\n")

def build_prompt():
    """Собирает финальный промпт для новой сессии."""
    prompt_parts = []
    
    # Загрузка конфига
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config_data = f.read()
            prompt_parts.append(f"### CORE CONFIGURATION\n{config_data}\n")
    
    # Добавление ссылок на Гит (берем из конфига если есть, или пишем вручную)
    prompt_parts.append("\n### EXTERNAL KNOWLEDGE BASE (GITHUB)")
    prompt_parts.append("- Repository: https://github.com/EugeneShevoldaev/glass-origami")
    prompt_parts.append(f"- Insights: https://raw.githubusercontent.com/EugeneShevoldaev/glass-origami/main/{INSIGHTS_FILE}")
    
    # Срез чатлога (последние 5000 символов)
    if os.path.exists(CHATLOG_FILE):
        with open(CHATLOG_FILE, "r", encoding="utf-8") as f:
            chat_content = f.read()
            tail = chat_content[-CHAT_TAIL_SIZE:]
            prompt_parts.append(f"\n### RECENT CONTEXT (OPERATIONAL MEMORY)\n...{tail}")

    final_prompt = "\n".join(prompt_parts)
    
    with open(PROMPT_OUTPUT, "w", encoding="utf-8") as f:
        f.write(final_prompt)
    
    print(f"[OK] Промпт собран в {PROMPT_OUTPUT}")

if __name__ == "__main__":
    print("--- AMY ARCHITECT: REHYDRATION SYSTEM ---")
    update_archives()
    build_prompt()
    run_git_commands()
    print("--- Ready to start a new session ---")