#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Помощник для получения и управления сессионными данными для Mobile Stresser

Этот файл содержит инструкции и утилиты для получения актуальных
сессионных данных, которые необходимы для работы Mobile Stresser.
"""

import json
import os
from datetime import datetime

class SessionHelper:
    """Помощник для работы с сессионными данными"""
    
    def __init__(self):
        self.session_file = "current_session.json"
    
    def save_session(self, session_data):
        """
        Сохраняет сессионные данные в файл
        
        Args:
            session_data (dict): Сессионные данные
        """
        try:
            # Добавляем метку времени
            session_data['saved_at'] = datetime.now().isoformat()
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Сессионные данные сохранены в {self.session_file}")
            return True
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
            return False
    
    def load_session(self):
        """
        Загружает сессионные данные из файла
        
        Returns:
            dict: Сессионные данные или None если файл не найден
        """
        try:
            if not os.path.exists(self.session_file):
                print(f"⚠️ Файл {self.session_file} не найден")
                return None
            
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            print(f"✅ Сессионные данные загружены из {self.session_file}")
            
            # Проверяем возраст сессии
            if 'saved_at' in session_data:
                saved_time = datetime.fromisoformat(session_data['saved_at'])
                age = datetime.now() - saved_time
                print(f"📅 Возраст сессии: {age}")
                
                if age.total_seconds() > 3600:  # 1 час
                    print("⚠️ Сессия может быть устаревшей (старше 1 часа)")
            
            return session_data
        except Exception as e:
            print(f"❌ Ошибка при загрузке: {e}")
            return None
    
    def create_session_template(self):
        """Создает шаблон для сессионных данных"""
        template = {
            "session_key": "ПОМЕСТИТЕ_СЮДА_ВАШИ_SESSION_KEY",
            "session_id": "ПОМЕСТИТЕ_СЮДА_ВАШИ_SESSION_ID",
            "refid": "ВАШИ_REF_ID",
            "imei": "ВАШИ_IMEI",
            "userid": "ВАШИ_USER_ID",
            "customerno": "ВАШИ_CUSTOMER_NO",
            "status": "ALLOWED",
            "userlocale": "ru",
            "userphonenumber": "+996XXXXXXXXX",
            "userotpdelivery": "sms",
            "customerindcorp": "C",
            "username": "ваш_логин",
            "userbranch": "001",
            "useremail": "ваш_email@gmail.com",
            "isuseractive": "true",
            "isuserreadonly": "false",
            "iscustomerreadonly": "false",
            "lastpasswordchangetimestamp": "Mon May 26 2025 10:27:16 GMT+0600 (Kyrgyzstan Time)",
            "isjointaccount": "false",
            "istrusted": "false",
            "ismaker": "true",
            "ischecker": "true"
        }
        
        template_file = "session_template.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Шаблон создан: {template_file}")
        print("📝 Заполните шаблон вашими данными и переименуйте в current_session.json")
        
        return template_file

def print_instructions():
    """Выводит инструкции по получению сессионных данных"""
    print("=" * 60)
    print("📋 ИНСТРУКЦИИ ПО ПОЛУЧЕНИЮ СЕССИОННЫХ ДАННЫХ")
    print("=" * 60)
    print()
    print("1. 🔐 АВТОРИЗАЦИЯ В СИСТЕМЕ:")
    print("   - Войдите в мобильное приложение или веб-интерфейс")
    print("   - Выполните полную авторизацию с логином и паролем")
    print("   - Подтвердите авторизацию через SMS/OTP если требуется")
    print()
    print("2. 🔍 ПОЛУЧЕНИЕ СЕССИОННЫХ ДАННЫХ:")
    print("   Вариант A - Через браузер (Web-версия):")
    print("   - Откройте инструменты разработчика (F12)")
    print("   - Перейдите на вкладку Network")
    print("   - Выполните любой запрос в системе")
    print("   - Найдите заголовки запроса и скопируйте:")
    print("     * session_key")
    print("     * session_id")
    print("     * userid")
    print("     * другие параметры пользователя")
    print()
    print("   Вариант B - Через логи приложения:")
    print("   - Включите отладку в мобильном приложении")
    print("   - Найдите в логах успешные gRPC запросы")
    print("   - Скопируйте метаданные запросов")
    print()
    print("   Вариант C - Через базу данных сессий:")
    print("   - Подключитесь к базе данных сессий")
    print("   - Найдите активную сессию для вашего пользователя")
    print("   - Скопируйте session_key и session_id")
    print()
    print("3. 💾 СОХРАНЕНИЕ ДАННЫХ:")
    print("   - Используйте SessionHelper для сохранения данных")
    print("   - Или создайте файл current_session.json вручную")
    print("   - Убедитесь, что все обязательные поля заполнены")
    print()
    print("4. ✅ ПРОВЕРКА:")
    print("   - Запустите mobile_stresser.py с новыми данными")
    print("   - Убедитесь, что тесты проходят успешно")
    print()
    print("⚠️ ВАЖНО:")
    print("   - Сессии имеют ограниченное время жизни")
    print("   - Обновляйте данные регулярно")
    print("   - Не делитесь сессионными данными")
    print()
    print("=" * 60)

def main():
    """Главная функция помощника"""
    print("🔧 Session Helper для Mobile Stresser")
    print()
    
    helper = SessionHelper()
    
    while True:
        print("\nВыберите действие:")
        print("1. 📋 Показать инструкции")
        print("2. 📝 Создать шаблон сессии")
        print("3. 💾 Загрузить текущую сессию")
        print("4. ✅ Проверить сессию")
        print("5. 🚪 Выход")
        
        choice = input("\nВведите номер (1-5): ").strip()
        
        if choice == '1':
            print_instructions()
        elif choice == '2':
            helper.create_session_template()
        elif choice == '3':
            session = helper.load_session()
            if session:
                print("Загруженная сессия:")
                # Скрываем чувствительные данные
                safe_session = session.copy()
                if 'session_key' in safe_session:
                    safe_session['session_key'] = safe_session['session_key'][:10] + "..."
                if 'session_id' in safe_session:
                    safe_session['session_id'] = safe_session['session_id'][:10] + "..."
                print(json.dumps(safe_session, indent=2, ensure_ascii=False))
        elif choice == '4':
            session = helper.load_session()
            if session:
                # Простая проверка обязательных полей
                required = ['session_key', 'session_id', 'userid']
                missing = [field for field in required if field not in session or not session[field]]
                
                if missing:
                    print(f"❌ Отсутствуют обязательные поля: {missing}")
                else:
                    print("✅ Все обязательные поля присутствуют")
                    
                    # Проверка длины ключей
                    if len(session['session_key']) < 20:
                        print("⚠️ session_key кажется слишком коротким")
                    if len(session['session_id']) < 20:
                        print("⚠️ session_id кажется слишком коротким")
        elif choice == '5':
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main() 