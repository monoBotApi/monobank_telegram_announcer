import requests
import time
from datetime import datetime

# Конфигурация
WEBHOOK_URL = "https://api.monobank.ua/..."
TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_IDS = ["610552091", "6401174198"]  # Список ID администраторов
CHECK_EVERY = 5  # Проверка каждые 5 секунд

last_processed_id = None

def send_to_telegram(message):
    """Отправка сообщения двум администраторам в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            response = requests.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }, timeout=5)
            
            # Логируем ответ от Telegram API
            if response.status_code == 200:
                print(f"✅ Сообщение успешно отправлено в чат {chat_id}")
            else:
                print(f"❌ Ошибка при отправке в Telegram (чат {chat_id}): {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Ошибка отправки в Telegram (чат {chat_id}): {e}")

def check_new_transactions():
    global last_processed_id
    
    try:
        # Получаем последнюю транзакцию
        response = requests.get(WEBHOOK_URL, timeout=10)
        response.raise_for_status()
        
        tx = response.json()
        print(f"Получены данные транзакции: {tx}")  # Логируем транзакцию
        
        if not tx or 'data' not in tx or 'statementItem' not in tx['data']:
            print("Ошибка: нет данных транзакции или отсутствует 'id' в ответе")
            return False
        
        # Извлекаем данные из 'statementItem'
        statement_item = tx['data']['statementItem']
        
        # Если это новая транзакция
        if last_processed_id != statement_item['id']:
            last_processed_id = statement_item['id']
            print(f"Новая транзакция с ID {statement_item['id']}")  # Логируем, что транзакция новая
            return statement_item
        else:
            print(f"Транзакция с ID {statement_item['id']} уже обработана")
            
    except Exception as e:
        print(f"Ошибка при проверке транзакции: {e}")
    
    return False

def format_message(tx):
    """Форматируем красивое сообщение"""
    amount = tx['amount'] / 100  # Переводим в гривны
    time_str = datetime.fromtimestamp(tx['time']).strftime('%d.%m.%Y %H:%M')
    
    return (
        f"💸 <b>Новый платеж в Monobank!</b>\n\n"
        f"⏰ <b>Время:</b> {time_str}\n"
        f"💰 <b>Сумма:</b> {amount:.2f} UAH\n"
        f"📌 <b>Описание:</b> {tx.get('description', 'нет описания')}\n"
        f"🔢 <b>MCC:</b> {tx.get('mcc', 'не указан')}"
    )

if __name__ == "__main__":
    print("🔍 Начинаю мониторинг платежей...")
    print(f"⏱ Проверка каждые {CHECK_EVERY} секунд")
    
    try:
        while True:
            tx = check_new_transactions()
            if tx:
                message = format_message(tx)
                send_to_telegram(message)
                print(f"✅ Отправлено уведомление о платеже {tx['id']}")
            
            time.sleep(CHECK_EVERY)
            
    except KeyboardInterrupt:
        print("\n🛑 Мониторинг остановлен")
