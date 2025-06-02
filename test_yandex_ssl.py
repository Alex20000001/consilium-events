import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Email настройки для SSL
SMTP_SERVER = 'smtp.yandex.ru'
SMTP_PORT = 465  # SSL порт
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'consilium-events@yandex.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'consilium-events@yandex.com')

print("Пробуем SSL подключение к Яндексу...")
print(f"Server: {SMTP_SERVER}:{SMTP_PORT}")
print(f"Username: {SMTP_USERNAME}")
print()

if not SMTP_PASSWORD:
    print("ОШИБКА: Пароль не установлен!")
    exit(1)

try:
    # Создаем SSL контекст
    context = ssl.create_default_context()
    
    print("Подключаемся через SSL...")
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context)
    
    print("Авторизуемся...")
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    
    print("Создаем письмо...")
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "Тест SSL - Consilium Events"
    
    body = "Тест отправки через SSL порт 465"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    print("Отправляем...")
    server.send_message(msg)
    server.quit()
    
    print("\nУСПЕШНО! Письмо отправлено!")
    print("Используйте порт 465 в настройках")
    
except Exception as e:
    print(f"\nОШИБКА: {e}")