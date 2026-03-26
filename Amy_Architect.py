import os
import subprocess
from datetime import datetime

# Настройки имен файлов
CONFIG_FILE = "Amy_config.json.txt"
INSIGHTS_FILE = "Amy_insights.md.txt"
INDEX_FILE = "Index.md.txt"
MEMORY_FILE = "Memory.txt"
CHATLOG_FILE = "Amy_chatlog.txt"
PROMPT_OUTPUT = "Rehydration_Prompt.txt"

CHAT_TAIL_SIZE = 5000 

def update_archives():
    """Переносит данные из чатлога в память и обновляет индекс."""
    if not os.path.exists(CHATLOG_FILE) or os.path.getsize(CHATLOG_FILE) == 0:
        print("[INFO] Чатлог пуст, архивация не требуется.")
        return

    with open(CHATLOG_FILE, "r", encoding="utf-8") as f:
        new_content = f.read().strip()

    if not new_content:
        return

    timestamp = datetime.now().strftime("%d.%m.%y %H:%M")
    
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n\n--- SESSION {timestamp} ---\n{new_content}")

    if not os.path.exists(INDEX_FILE) or os.path.getsize(INDEX_FILE) == 0:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write("| Дата | Суть | Ссылка |\n| :--- | :--- | :--- |\n")

    with open(INDEX_FILE, "a", encoding="utf-8") as f:
        f.write(f"| {timestamp} | New dialogue session | [Memory] |\n")
    print("[OK] Архивы обновлены.")

def run_git_commands():
    """Синхронизация с GitHub (максимальная совместимость со старыми версиями Python)."""
    try:
        # Убрали text=True, теперь работаем с байтами
        result = subprocess.run(["git", "status", "--porcelain"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Декодируем байты в строку вручную
        status = result.stdout.decode('utf-8').strip()

        if not status:
            print("[GIT] Изменений не обнаружено.")
            return

        print("[GIT] Синхронизация...")
        subprocess.run(["git", "add", "."], check=True)
        commit_msg = "Auto-sync: " + datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[GIT] Успешно отправлено на GitHub.")
    except Exception as e:
        print(f"[GIT ERROR] Ошибка: {e}")
def build_prompt():
    """Сборка промпта для новой сессии."""
    prompt_parts = ["### CORE CONFIGURATION\n"]
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            prompt_parts.append(f.read())
    
    prompt_parts.append("\n### GITHUB REPO: https://github.com/EugeneShevoldaev/glass-origami")
    
    if os.path.exists(CHATLOG_FILE):
        with open(CHATLOG_FILE, "r", encoding="utf-8") as f:
            tail = f.read()[-CHAT_TAIL_SIZE:]
            prompt_parts.append(f"\n### RECENT CONTEXT\n...{tail}")

    with open(PROMPT_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(prompt_parts))
    print(f"[OK] Промпт готов: {PROMPT_OUTPUT}")

if __name__ == "__main__":
    print("--- AMY ARCHITECT: REHYDRATION SYSTEM ---")
    update_archives()
    build_prompt()
    run_git_commands()
    print("--- Ready to start a new session ---")