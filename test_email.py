Consilium Events
"""
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    print("Отправляем письмо...")
    server.send_message(msg)
    server.quit()
    
    print(f"\n✓ Письмо успешно отправлено на {RECIPIENT_EMAIL}!")
    print("Проверьте папку 'Входящие' и 'Спам'")
    
except smtplib.SMTPAuthenticationError:
    print("\n✗ ОШИБКА: Неверный логин или пароль!")
    print("Проверьте:")
    print("1. Правильность email в SMTP_USERNAME")
    print("2. Используете ли вы пароль приложения (не обычный пароль от почты)")
    
except Exception as e:
    print(f"\n✗ ОШИБКА: {e}")
    print("\nВозможные причины:")
    print("1. Неверные настройки SMTP сервера")
    print("2. Проблемы с интернет-соединением")
    print("3. Блокировка со стороны почтового сервера")