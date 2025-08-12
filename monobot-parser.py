import os
import requests
import time

# === Конфигурация ===
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
MONOBANK_TOKEN = os.environ.get('MONOBANK_TOKEN')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not MONOBANK_TOKEN:
    raise RuntimeError("Missing required environment variables: TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, MONOBANK_TOKEN")


# === Получение ID счёта (карты) ===


    # Проверка, есть ли ключ 'accounts'
def get_account_id():
    headers = {"X-Token": MONOBANK_TOKEN}
    try:
        response = requests.get(
            "https://api.monobank.ua/personal/client-info",
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as error:
        print("Не удалось получить информацию о клиенте Monobank:", error)
        return None

    if "accounts" not in data or not data["accounts"]:
        print("❌ Ошибка: ключ 'accounts' отсутствует или пуст. Ответ без подробностей по безопасности.")
        return None

    return data["accounts"][0]["id"]
# === Отправка в Telegram ===
def send_to_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
    except Exception as error:
        print("Не удалось отправить сообщение в Telegram:", error)

# === Основной цикл ===
def run_monitoring():
    account_id = get_account_id()
    if not account_id:
        # Не удалось получить аккаунт, повторим позже
        time.sleep(30)
        account_id = get_account_id()
        if not account_id:
            raise RuntimeError("Не удалось получить ID счёта Monobank. Проверьте токен и доступность API.")

    last_txn_time = 0
    last_txn_id = None

    while True:
        try:
            url = f"https://api.monobank.ua/personal/statement/{account_id}/{last_txn_time}"
            headers = {"X-Token": MONOBANK_TOKEN}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and data:
                # Сортируем по времени (и по id для детерминированности) от старых к новым
                data.sort(key=lambda t: (t.get("time", 0), str(t.get("id", ""))))

                for txn in data:
                    txn_time = txn.get("time", 0)
                    txn_id = txn.get("id")

                    should_process = (
                        txn_time > last_txn_time or
                        (txn_time == last_txn_time and txn_id is not None and txn_id != last_txn_id)
                    )

                    if should_process:
                        amount = txn.get("amount", 0) / 100
                        description = txn.get("description", "Без описания")
                        message = f"💸 {description}\nСумма: {amount} грн"
                        send_to_telegram(message)

                        # Обновляем маркеры
                        last_txn_time = txn_time
                        last_txn_id = txn_id

        except Exception as e:
            print("Ошибка во время опроса Monobank:", e)

        time.sleep(60)

if __name__ == '__main__':
    run_monitoring()

