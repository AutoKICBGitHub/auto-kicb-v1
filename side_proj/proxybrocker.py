#!/usr/bin/env python3

import requests
import json
import os
from typing import List, Dict
import time
import re

class ProxyBroker:
    def __init__(self):
        self.working_proxies = []
        self.proxy_sources = [
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all',
            'https://api.proxyscrape.com/v2/?request=get&protocol=socks5&timeout=5000&country=all',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt', 
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
            'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list',
            'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt'
        ]
        
    def fetch_from_api_sources(self) -> List[str]:
        """Собираем прокси из API источников"""
        all_proxies = []
        
        for source in self.proxy_sources:
            try:
                print(f"Парсим: {source}")
                response = requests.get(source, timeout=15)
                if response.status_code == 200:
                    content = response.text.strip()
                    # Ищем IP:PORT паттерны
                    proxy_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]+\b'
                    found_proxies = re.findall(proxy_pattern, content)
                    all_proxies.extend(found_proxies)
                    print(f"Найдено {len(found_proxies)} прокси")
                else:
                    print(f"Ошибка {response.status_code}")
            except Exception as e:
                print(f"Ошибка парсинга {source}: {e}")
        
        # Убираем дубликаты
        unique_proxies = list(set(all_proxies))
        print(f"Всего уникальных прокси: {len(unique_proxies)}")
        return unique_proxies
    
    def fetch_from_geonode_api(self) -> List[str]:
        """Парсим с GeoNode API"""
        proxies = []
        try:
            url = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc'
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                proxy_list = data.get('data', [])
                for proxy in proxy_list:
                    proxy_string = f"{proxy['ip']}:{proxy['port']}"
                    proxies.append(proxy_string)
                print(f"GeoNode: найдено {len(proxies)} прокси")
        except Exception as e:
            print(f"Ошибка GeoNode API: {e}")
        return proxies
    
    def fetch_from_proxylist_plus(self) -> List[str]:
        """Парсим с proxylist.plus"""
        proxies = []
        try:
            for country in ['US', 'CA', 'GB', 'DE', 'FR']:
                url = f'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{country}'
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    proxy_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]+\b'
                    found = re.findall(proxy_pattern, response.text)
                    proxies.extend(found)
            print(f"ProxyList+: найдено {len(proxies)} прокси")
        except Exception as e:
            print(f"Ошибка ProxyList+: {e}")
        return proxies
    
    def get_test_proxies(self) -> List[str]:
        """Получаем тестовые прокси для проверки"""
        test_proxies = [
            # Популярные публичные прокси (могут работать)
            '8.8.8.8:8080',
            '1.1.1.1:8080', 
            '208.67.222.222:8080',
            '8.8.4.4:8080',
            
            # Squid прокси по умолчанию
            '127.0.0.1:3128',
            '127.0.0.1:8080',
            'localhost:3128',
            'localhost:8080',
            
            # Популярные порты
            '185.199.109.153:8080',
            '185.199.108.153:8080',
            '140.82.112.3:8080',
            '140.82.113.3:8080'
        ]
        return test_proxies
    
    def parse_all_sources(self) -> List[str]:
        """Парсим все источники"""
        all_proxies = []
        
        print("=== ПАРСИНГ ПРОКСИ ===")
        
        # Добавляем тестовые прокси первыми
        test_proxies = self.get_test_proxies()
        all_proxies.extend(test_proxies)
        print(f"Добавлены тестовые прокси: {len(test_proxies)}")
        
        # API источники
        api_proxies = self.fetch_from_api_sources()
        all_proxies.extend(api_proxies)
        
        # GeoNode API
        geonode_proxies = self.fetch_from_geonode_api()
        all_proxies.extend(geonode_proxies)
        
        # ProxyList+
        proxylist_proxies = self.fetch_from_proxylist_plus()
        all_proxies.extend(proxylist_proxies)
        
        # Убираем дубликаты и фильтруем
        unique_proxies = list(set(all_proxies))
        good_ports = [80, 8080, 3128, 8888, 1080, 9999, 8000, 8081, 9090]
        filtered_proxies = []
        other_proxies = []
        
        for proxy in unique_proxies:
            if ':' in proxy and '.' in proxy:
                try:
                    ip, port = proxy.split(':')
                    port_num = int(port)
                    if 1 <= port_num <= 65535:
                        # Приоритет для популярных портов
                        if port_num in good_ports:
                            filtered_proxies.append(proxy)
                        else:
                            other_proxies.append(proxy)
                except:
                    continue
        
        # Сначала популярные порты, потом остальные
        final_list = filtered_proxies + other_proxies
        print(f"Финальный список: {len(final_list)} прокси (приоритетных: {len(filtered_proxies)})")
        return final_list
    

    
    def test_proxy(self, proxy_string: str) -> bool:
        """Тестируем прокси"""
        # Пробуем несколько типов подключения
        test_urls = [
            'http://httpbin.org/ip',
            'https://httpbin.org/ip', 
            'http://ipinfo.io/ip',
            'https://api.ipify.org'
        ]
        
        # HTTP прокси
        for url in test_urls:
            try:
                proxies = {
                    'http': f'http://{proxy_string}',
                    'https': f'http://{proxy_string}'
                }
                
                response = requests.get(url, proxies=proxies, timeout=3, verify=False)
                if response.status_code == 200:
                    return True
            except:
                continue
        
        # SOCKS5 прокси
        try:
            proxies = {
                'http': f'socks5://{proxy_string}',
                'https': f'socks5://{proxy_string}'
            }
            
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=3, verify=False)
            if response.status_code == 200:
                return True
        except:
            pass
            
        return False
    
    def test_all_proxies(self, proxy_list: List[str], max_test: int = 500):
        """Тестируем прокси"""
        print(f"Тестирую первые {max_test} прокси...")
        
        working = []
        test_list = proxy_list[:max_test]
        
        for i, proxy_string in enumerate(test_list):
            print(f"[{i+1}/{len(test_list)}] {proxy_string}", end=" ")
            
            if self.test_proxy(proxy_string):
                working.append(proxy_string)
                print(f"✅")
                
                # Если нашли 20 рабочих - хватит
                if len(working) >= 20:
                    print(f"\nНашли {len(working)} рабочих прокси - достаточно!")
                    break
            else:
                print(f"❌")
        
        print(f"\n✅ Рабочих прокси: {len(working)}")
        print(f"❌ Нерабочих прокси: {len(test_list) - len(working)}")
        
        return working
    
    def save_to_file(self, proxy_list: List[str], filename: str = 'working_proxies.txt'):
        """Сохраняем рабочие прокси в файл"""
        with open(filename, 'w') as f:
            for proxy in proxy_list:
                f.write(f"{proxy}\n")
        
        print(f"Сохранено {len(proxy_list)} прокси в {filename}")

def main():
    broker = ProxyBroker()
    
    print("=== АВТОМАТИЧЕСКИЙ ПАРСЕР ПРОКСИ ===")
    
    # Парсим прокси со всех источников
    all_proxies = broker.parse_all_sources()
    
    if not all_proxies:
        print("❌ Прокси не найдены!")
        return
    
    # Тестируем прокси (первые 500)
    print("\n=== ТЕСТИРОВАНИЕ ПРОКСИ ===")
    working_proxies = broker.test_all_proxies(all_proxies, max_test=500)
    
    if working_proxies:
        # Сохраняем рабочие прокси
        broker.save_to_file(working_proxies, 'working_proxies.txt')
        print(f"\n🎉 Готово! {len(working_proxies)} рабочих прокси сохранены")
    else:
        print("\n❌ Рабочих прокси не найдено")

if __name__ == '__main__':
    main()
