#!/usr/bin/env python3
"""
Скрипт для генерации хеша пароля администратора
"""

from werkzeug.security import generate_password_hash
import getpass

def main():
    print("Генератор хеша пароля для Consilium")
    print("-" * 40)
    
    password = getpass.getpass("Введите пароль администратора: ")
    confirm = getpass.getpass("Подтвердите пароль: ")
    
    if password != confirm:
        print("❌ Пароли не совпадают!")
        return
    
    if len(password) < 8:
        print("⚠️  Предупреждение: пароль слишком короткий (рекомендуется минимум 8 символов)")
    
    password_hash = generate_password_hash(password)
    
    print("\n✅ Хеш пароля успешно сгенерирован!")
    print("\nДобавьте эту строку в ваш .env файл:")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    
    print("\n📝 Также вы можете использовать эти переменные окружения:")
    print(f"export ADMIN_PASSWORD_HASH='{password_hash}'")

if __name__ == "__main__":
    main()