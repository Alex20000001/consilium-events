import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Email настройки
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.yandex.ru')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'consilium-events@yandex.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'consilium-events@yandex.com')

print("Настройки email:")
print(f"SMTP Server: {SMTP_SERVER}")
print(f"SMTP Port: {SMTP_PORT}")
print(f"Username: {SMTP_USERNAME}")
print(f"Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'НЕ УСТАНОВЛЕН'}")
print(f"Recipient: {RECIPIENT_EMAIL}")
print()

if not SMTP_PASSWORD:
    print("ОШИБКА: Пароль SMTP не установлен в .env файле!")
    print("Добавьте строку SMTP_PASSWORD=ваш-пароль-приложения в .env")
    exit(1)

try:
    print("Подключаемся к серверу...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    
    print("Авторизуемся...")
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    
    print("Создаем письмо...")
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "Тест отправки с Consilium Events"
    
    body = "Это тестовое письмо от сайта Consilium Events.\n\nЕсли вы получили это письмо, значит настройки email работают правильно!\n\n---\nConsilium Events"
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    print("Отправляем письмо...")
    server.send_message(msg)
    server.quit()
    
    print(f"\nУспешно! Письмо отправлено на {RECIPIENT_EMAIL}!")
    print("Проверьте папку Входящие и Спам")
    
except smtplib.SMTPAuthenticationError:
    print("\nОШИБКА: Неверный логин или пароль!")
    print("Проверьте:")
    print("1. Правильность email в SMTP_USERNAME")
    print("2. Используете ли вы пароль приложения (не обычный пароль от почты)")
    
except Exception as e:
    print(f"\nОШИБКА: {e}")
    print("\nВозможные причины:")
    print("1. Неверные настройки SMTP сервера")
    print("2. Проблемы с интернет-соединением")
    print("3. Блокировка со стороны почтового сервера")