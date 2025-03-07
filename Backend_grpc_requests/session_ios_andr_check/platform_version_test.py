import pytest
import json
from .request_to_validate import test_ios_versions
from .request_to_validate_android import test_android_versions

@pytest.mark.skip(reason="Временно отключено")
def test_all_platforms():
    print("=== Тестирование версий Android ===")
    test_android_versions()
    
    print("\n=== Тестирование версий iOS ===")
    test_ios_versions()
    
    # Объединяем результаты
    try:
        with open('android_version_test_results.json', 'r') as f:
            android_results = json.load(f)
        
        with open('ios_version_test_results.json', 'r') as f:
            ios_results = json.load(f)
            
        combined_results = {
            'android': android_results,
            'ios': ios_results
        }
        
        # Сохраняем общие результаты
        with open('platform_version_test_results.json', 'w') as f:
            json.dump(combined_results, f, indent=2)
            
        print("\n=== Общие результаты тестирования ===")
        print(f"Android рабочие версии: {len(android_results['working_versions'])}")
        print(f"Android нерабочие версии: {len(android_results['failed_versions'])}")
        print(f"iOS рабочие версии: {len(ios_results['working_versions'])}")
        print(f"iOS нерабочие версии: {len(ios_results['failed_versions'])}")
        
    except FileNotFoundError as e:
        print(f"Ошибка при чтении результатов: {e}")

if __name__ == '__main__':
    test_all_platforms() 