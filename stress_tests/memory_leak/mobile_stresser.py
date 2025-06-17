import grpc
import os
import sys
import json
import time
import uuid
from datetime import datetime

# Добавляем путь к директории, где находится протофайл
sys.path.append(os.path.abspath("C:\\project_kicb\\stress_tests\\memory_leak"))

from protofile_pb2_grpc import WebAccountApiStub
from protofile_pb2 import WebAccountsRequest

class MobileStresser:
    def __init__(self, session_data=None):
        """
        Инициализация с возможностью передачи сессионных данных
        
        Args:
            session_data (dict): Словарь с сессионными данными
        """
        print("Создаем подключение к серверу...")
        
        # Сессионные данные по умолчанию (АКТУАЛЬНЫЕ из JS кода!)
        self.default_session_data = {
            'sessionKey': '2x6tKgoGDy1h9UV649qESQ',  # ✅ Из рабочего JS кода
            'sessionId': '4R9fQdPKecpMslFeZ9vIVb',   # ✅ Из рабочего JS кода
            'device-type': 'ios',
            'x-real-ip': '138.199.55.230',
            'user-agent': '{"ua": {"device": "iPhone 15 Pro", "osVersion": "18.0.1"}, "imei": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1", "deviceName": "", "deviceType": "ios", "macAddress": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1"}',
            'user-agent-c': '18.0.1; iPhone 15 Pro',
            'app-type': 'I'
        }
        
        # Используем переданные сессионные данные или данные по умолчанию
        self.session_data = session_data if session_data else self.default_session_data
        
        # Выводим информацию о сессионных данных
        if not session_data:
            print("✅ Используются актуальные сессионные данные из JS кода")
            print(f"📋 sessionKey: {self.session_data['sessionKey'][:10]}...")
            print(f"📋 sessionId: {self.session_data['sessionId'][:10]}...")
        else:
            print("🔑 Используются пользовательские сессионные данные")
        
        try:
            self.channel = grpc.secure_channel(
                'newibanktest.kicb.net:443', 
                grpc.ssl_channel_credentials()
            )
            print("✅ Канал создан успешно")
            
            self.stub = WebAccountApiStub(self.channel)
            print("✅ Stub создан успешно")
            
            # Проверяем подключение
            print("Проверяем подключение к серверу...")
            try:
                state = self.channel.get_state()
                print(f"Состояние канала: {state}")
            except Exception as e:
                print(f"⚠️ Ошибка при проверке состояния канала: {e}")
                
        except Exception as e:
            print(f"❌ Ошибка при создании подключения: {e}")
            raise
        
        self.endpoints = [
            'GET_ACCOUNTS',
            'GET_LOANS', 
            'GET_DEPOSITS'
        ]
    
    def generate_ref_id(self):
        """Генерирует новый refId для каждого запроса"""
        return str(uuid.uuid4())
    
    def update_session_data(self, new_session_data):
        """
        Обновляет сессионные данные
        
        Args:
            new_session_data (dict): Новые сессионные данные
        """
        self.session_data.update(new_session_data)
        print(f"✅ Обновлены сессионные данные: {list(new_session_data.keys())}")
    
    def get_metadata(self):
        """Возвращает метадату с сессионными данными в формате как в JS коде"""
        
        # Генерируем новый refId для каждого запроса
        ref_id = self.generate_ref_id()
        
        # Формируем метадату в том же формате, что и в JS коде
        metadata = [
            ('sessionkey', self.session_data.get('sessionKey', '')),
            ('sessionid', self.session_data.get('sessionId', '')),
            ('device-type', self.session_data.get('device-type', 'ios')),
            ('refid', ref_id),
            ('x-real-ip', self.session_data.get('x-real-ip', '138.199.55.230')),
            ('user-agent', self.session_data.get('user-agent', '{"ua": {"device": "iPhone 15 Pro", "osVersion": "18.0.1"}, "imei": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1", "deviceName": "", "deviceType": "ios", "macAddress": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1"}')),
            ('user-agent-c', self.session_data.get('user-agent-c', '18.0.1; iPhone 15 Pro')),
            ('app-type', self.session_data.get('app-type', 'I'))
        ]
        
        print(f"🔄 Сгенерирован новый refId: {ref_id}")
        
        return tuple(metadata)
    
    def validate_session(self):
        """
        Проверяет валидность сессии перед выполнением запросов
        """
        print("\n🔍 Проверка валидности сессии...")
        
        # Проверяем обязательные поля
        required_fields = ['sessionKey', 'sessionId']
        for field in required_fields:
            if field not in self.session_data or not self.session_data[field]:
                print(f"❌ Отсутствует обязательное поле: {field}")
                return False
        
        # Проверяем длину session ключей
        session_key = self.session_data['sessionKey']
        session_id = self.session_data['sessionId']
        
        if len(session_key) < 20:
            print(f"❌ sessionKey слишком короткий: {len(session_key)} символов")
            return False
            
        if len(session_id) < 20:
            print(f"❌ sessionId слишком короткий: {len(session_id)} символов")
            return False
        
        print("✅ Базовая проверка сессии пройдена")
        return True
        
    def test_endpoint(self, endpoint_name):
        """Выполняет запрос к endpoint"""
        print(f"\n--- Тестирование {endpoint_name} ---")
        
        try:
            print("1. Получаем метадату...")
            metadata = self.get_metadata()
            print(f"✅ Метадата готова ({len(metadata)} полей)")
            
            # Показываем ключевые поля сессии для диагностики
            print(f"   sessionKey: {self.session_data['sessionKey'][:10]}...")
            print(f"   sessionId: {self.session_data['sessionId'][:10]}...")
            print(f"   device-type: {self.session_data.get('device-type', 'ios')}")
            
            print("2. Подготавливаем данные запроса...")
            # Используем пустой объект как в JS коде
            request_data = {}
            print(f"✅ Данные запроса: {request_data}")
            
            print("3. Создаем объект запроса...")
            request = WebAccountsRequest(
                code=endpoint_name,
                data=json.dumps(request_data)
            )
            print(f"✅ Запрос создан - код: {request.code}")
            
            print("4. Отправляем запрос на сервер...")
            print(f"   Сервер: newibanktest.kicb.net:443")
            print(f"   Метод: makeWebAccount")
            print(f"   Endpoint: {endpoint_name}")
            print(f"   Время: {datetime.now().strftime('%H:%M:%S')}")
            
            start_time = time.time()
            response = self.stub.makeWebAccount(request, metadata=metadata)
            end_time = time.time()
            
            print("5. Получили ответ от сервера!")
            print(f"   Время отклика: {(end_time - start_time):.2f}с")
            print(f"   Success: {response.success}")
            
            if response.success:
                print(f"✅ {endpoint_name}: Успешно")
                if hasattr(response, 'data') and response.data:
                    print(f"   Данные получены: {len(response.data)} символов")
                    # Попробуем распарсить данные
                    try:
                        parsed_data = json.loads(response.data)
                        if isinstance(parsed_data, dict) and 'result' in parsed_data:
                            result = parsed_data['result']
                            if isinstance(result, list):
                                print(f"   Найдено записей: {len(result)}")
                            elif isinstance(result, dict):
                                print(f"   Получен объект с ключами: {list(result.keys())}")
                    except:
                        pass
                return True
            else:
                error_code = response.error.code if response.error else "UNKNOWN_ERROR"
                print(f"❌ {endpoint_name}: Ошибка - {error_code}")
                
                if response.error:
                    print(f"   Код ошибки: {response.error.code}")
                    if hasattr(response.error, 'message'):
                        print(f"   Сообщение: {response.error.message}")
                    if hasattr(response.error, 'details'):
                        print(f"   Детали: {response.error.details}")
                
                # Специальная обработка ошибок сессии
                if error_code == "INVALID_SESSION_KEY":
                    print("🔄 РЕКОМЕНДАЦИЯ: Обновите sessionKey!")
                    print("   Получите новый sessionKey через авторизацию")
                elif error_code == "SESSION_EXPIRED":
                    print("🔄 РЕКОМЕНДАЦИЯ: Сессия истекла, требуется повторная авторизация")
                elif error_code == "INVALID_SESSION_ID":
                    print("🔄 РЕКОМЕНДАЦИЯ: Обновите sessionId!")
                    
                return False
            
        except grpc.RpcError as e:
            print(f"❌ gRPC ошибка:")
            print(f"   Код: {e.code()}")
            print(f"   Детали: {e.details()}")
            
            # Специальная обработка gRPC ошибок
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                print("🔄 РЕКОМЕНДАЦИЯ: Проблема с аутентификацией")
            elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
                print("🔄 РЕКОМЕНДАЦИЯ: Недостаточно прав доступа")
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                print("🔄 РЕКОМЕНДАЦИЯ: Сервер недоступен")
                
            return False
        except Exception as e:
            print(f"❌ Общая ошибка: {type(e).__name__}")
            print(f"   Сообщение: {str(e)}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False

    def run_tests(self):
        """Запускает тесты для всех endpoints"""
        print("=== НАЧАЛО ТЕСТИРОВАНИЯ ===")
        print(f"Будем тестировать {len(self.endpoints)} endpoints")
        
        # Проверяем сессию перед началом тестов
        if not self.validate_session():
            print("❌ Проверка сессии не пройдена. Остановка тестирования.")
            return
        
        success_count = 0
        total_count = len(self.endpoints)
        
        for i, endpoint in enumerate(self.endpoints, 1):
            print(f"\n[{i}/{total_count}] Тестирование {endpoint}")
            if self.test_endpoint(endpoint):
                success_count += 1
        
        print(f"\n=== РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ===")
        print(f"Успешно: {success_count}/{total_count}")
        print(f"Неудачно: {total_count - success_count}/{total_count}")
        
        if success_count == 0:
            print("\n❌ ВСЕ ТЕСТЫ НЕУСПЕШНЫ!")
            print("🔄 Возможные причины:")
            print("   1. Устаревший sessionKey")
            print("   2. Истекшая sessionId")
            print("   3. Проблемы с заголовками")
            print("   4. Проблемы с сервером")
            print("\n💡 Решение: Обновите сессионные данные из рабочего браузера!")
        elif success_count == total_count:
            print("\n🎉 ВСЕ ТЕСТЫ УСПЕШНЫ!")
            print("✅ Соединение работает корректно")
            print("✅ Сессионные данные актуальны")
        else:
            print(f"\n⚠️ ЧАСТИЧНЫЙ УСПЕХ: {success_count}/{total_count}")
            print("🔍 Некоторые endpoints могут требовать дополнительных прав")
        
        print("=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===")

    def close(self):
        """Закрывает соединение"""
        print("Закрываем подключение...")
        if hasattr(self, 'channel'):
            self.channel.close()
            print("✅ Подключение закрыто")

if __name__ == "__main__":
    print("🚀 Запуск Mobile Stresser")
    print("=" * 50)
    
    # Пытаемся загрузить сессионные данные из файла
    session_data = None
    session_file = "current_session.json"
    
    if os.path.exists(session_file):
        try:
            print(f"📁 Найден файл с сессионными данными: {session_file}")
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            print("✅ Сессионные данные загружены из файла")
            
            # Проверяем возраст сессии
            if 'saved_at' in session_data:
                from datetime import datetime  
                saved_time = datetime.fromisoformat(session_data['saved_at'])
                age = datetime.now() - saved_time
                print(f"📅 Возраст сессии: {age}")
                
                if age.total_seconds() > 3600:  # 1 час
                    print("⚠️ Сессия может быть устаревшей (старше 1 часа)")
                    
        except Exception as e:
            print(f"❌ Ошибка при загрузке сессионных данных: {e}")
            print("Будут использованы данные по умолчанию")
            session_data = None
    else:
        print(f"📋 Файл {session_file} не найден")
        print("✅ Используются актуальные данные из JS кода")
    
    # Создаем экземпляр MobileStresser
    if session_data:
        print("🔑 Используются сессионные данные из файла")
        mobile_stresser = MobileStresser(session_data=session_data)
    else:
        print("📋 Используются сессионные данные из рабочего JS кода")
        mobile_stresser = MobileStresser()
    
    try:
        mobile_stresser.run_tests()
        
    except KeyboardInterrupt:
        print("\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        mobile_stresser.close()
        print("\n👋 Работа завершена")
