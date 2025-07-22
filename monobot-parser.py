import requests
import time

# === Конфигурация ===
TELEGRAM_TOKEN = '7855786308:AAHCGrPtUNQnLV_SFxXE-KIxoXySIKfy2D_Q'
TELEGRAM_CHAT_ID = '7404701653'
MONOBANK_TOKEN = 'uYFqQI0R26vwsS-C-Ip8s-N5okQUs6xTn7E7n83Nxz3M'


# === Получение ID счёта (карты) ===
def get_account_id():
    headers = {"X-Token": MONOBANK_TOKEN}
    r = requests.get("https://api.monobank.ua/personal/client-info", headers=headers)
    data = r.json()
    return data["accounts"][0]["id"]

# === Отправка в Telegram ===
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

# === Основной цикл ===
def run_monitoring():
    account_id = get_account_id()
    last_txn_time = 0

    while True:
        try:
            url = f"https://api.monobank.ua/personal/statement/{account_id}/{last_txn_time}"
            headers = {"X-Token": MONOBANK_TOKEN}
            response = requests.get(url, headers=headers)
            data = response.json()

            if isinstance(data, list):
                for txn in data:
                    if txn["time"] > last_txn_time:
                        last_txn_time = txn["time"]
                        amount = txn["amount"] / 100
                        description = txn.get("description", "Без описания")
                        message = f"💸 {description}\nСумма: {amount} грн"
                        send_to_telegram(message)

        except Exception as e:
            print("Ошибка:", e)

        time.sleep(60)

if __name__ == '__main__':
    run_monitoring()

