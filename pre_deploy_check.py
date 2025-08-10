#!/usr/bin/env python3
"""
Полная проверка проекта перед развертыванием в продакшен
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

def check_file_exists(filepath: str) -> bool:
    """Проверить существование файла"""
    return os.path.exists(filepath)

def check_docker_files() -> List[Tuple[str, bool, str]]:
    """Проверка Docker файлов"""
    results = []
    
    # Проверка основных Docker файлов
    docker_files = [
        'docker-compose.prod.yml',
        'Dockerfile.prod',
        '.env.prod.example',
        'requirements.txt',
        'postgresql.conf'
    ]
    
    for file in docker_files:
        exists = check_file_exists(file)
        results.append((f"Docker file: {file}", exists, "" if exists else "Файл отсутствует"))
    
    # Проверка валидности docker-compose
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.prod.yml', 'config', '--quiet'],
            capture_output=True, text=True, check=True
        )
        results.append(("Docker Compose валидность", True, "Файл валиден"))
    except subprocess.CalledProcessError as e:
        results.append(("Docker Compose валидность", False, f"Ошибка валидации: {e.stderr}"))
    except FileNotFoundError:
        results.append(("Docker Compose валидность", False, "docker-compose не установлен"))
    
    return results

def check_python_files() -> List[Tuple[str, bool, str]]:
    """Проверка Python файлов"""
    results = []
    
    # Основные Python файлы
    python_files = [
        'main.py',
        'bot.py', 
        'database.py',
        'grok_service.py',
        'topic_service.py',
        'scheduler.py',
        'health_check.py'
    ]
    
    for file in python_files:
        exists = check_file_exists(file)
        if exists:
            # Проверка синтаксиса Python
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    compile(f.read(), file, 'exec')
                results.append((f"Python syntax: {file}", True, "Синтаксис корректен"))
            except SyntaxError as e:
                results.append((f"Python syntax: {file}", False, f"Синтаксическая ошибка: {e}"))
        else:
            results.append((f"Python file: {file}", False, "Файл отсутствует"))
    
    return results

def check_requirements() -> List[Tuple[str, bool, str]]:
    """Проверка requirements файлов"""
    results = []
    
    req_files = ['requirements.txt', 'requirements-dev.txt']
    
    for req_file in req_files:
        if check_file_exists(req_file):
            try:
                with open(req_file, 'r') as f:
                    lines = f.readlines()
                    valid_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
                    results.append((f"Requirements: {req_file}", True, f"Содержит {len(valid_lines)} пакетов"))
            except Exception as e:
                results.append((f"Requirements: {req_file}", False, f"Ошибка чтения: {e}"))
        else:
            results.append((f"Requirements: {req_file}", False, "Файл отсутствует"))
    
    return results

def check_deployment_scripts() -> List[Tuple[str, bool, str]]:
    """Проверка скриптов развертывания"""
    results = []
    
    scripts = [
        'deploy.sh',
        'deploy.ps1'
    ]
    
    for script in scripts:
        exists = check_file_exists(script)
        results.append((f"Deploy script: {script}", exists, "Готов к использованию" if exists else "Файл отсутствует"))
    
    return results

def check_documentation() -> List[Tuple[str, bool, str]]:
    """Проверка документации"""
    results = []
    
    docs = [
        'README.md',
        'PRODUCTION.md',
        'DEPLOYMENT.md'
    ]
    
    for doc in docs:
        exists = check_file_exists(doc)
        if exists:
            try:
                with open(doc, 'r', encoding='utf-8') as f:
                    content = f.read()
                    word_count = len(content.split())
                    results.append((f"Documentation: {doc}", True, f"Содержит ~{word_count} слов"))
            except Exception as e:
                results.append((f"Documentation: {doc}", False, f"Ошибка чтения: {e}"))
        else:
            results.append((f"Documentation: {doc}", False, "Файл отсутствует"))
    
    return results

def check_configuration() -> List[Tuple[str, bool, str]]:
    """Проверка конфигурационных файлов"""
    results = []
    
    # Проверка примера конфигурации
    if check_file_exists('.env.prod.example'):
        try:
            with open('.env.prod.example', 'r') as f:
                content = f.read()
                required_vars = [
                    'TELEGRAM_BOT_TOKEN',
                    'GROK_API_KEY', 
                    'POSTGRES_PASSWORD',
                    'REDIS_PASSWORD'
                ]
                
                missing_vars = []
                for var in required_vars:
                    if var not in content:
                        missing_vars.append(var)
                
                if missing_vars:
                    results.append((
                        "Configuration template", 
                        False, 
                        f"Отсутствуют переменные: {', '.join(missing_vars)}"
                    ))
                else:
                    results.append((
                        "Configuration template", 
                        True, 
                        "Все обязательные переменные присутствуют"
                    ))
        except Exception as e:
            results.append(("Configuration template", False, f"Ошибка чтения: {e}"))
    else:
        results.append(("Configuration template", False, ".env.prod.example отсутствует"))
    
    return results

def main():
    """Главная функция проверки"""
    print("🔍 Полная проверка проекта AI Learning Bot перед продакшен развертыванием")
    print("=" * 80)
    print()
    
    all_results = []
    
    # Выполняем все проверки
    checks = [
        ("🐳 Docker файлы", check_docker_files),
        ("🐍 Python файлы", check_python_files),
        ("📦 Requirements", check_requirements),
        ("🚀 Скрипты развертывания", check_deployment_scripts),
        ("📚 Документация", check_documentation),
        ("⚙️ Конфигурация", check_configuration),
    ]
    
    for section_name, check_func in checks:
        print(f"\n{section_name}")
        print("-" * 40)
        
        results = check_func()
        all_results.extend(results)
        
        for test_name, success, message in results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")
            if message:
                print(f"     {message}")
    
    # Подсчет результатов
    total_checks = len(all_results)
    passed_checks = sum(1 for _, success, _ in all_results if success)
    failed_checks = total_checks - passed_checks
    
    print()
    print("=" * 80)
    print(f"📊 ИТОГО: {passed_checks}/{total_checks} проверок пройдено")
    
    if failed_checks == 0:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Проект готов к развертыванию в продакшен.")
        return 0
    else:
        print(f"⚠️  {failed_checks} проверок не прошли. Исправьте ошибки перед развертыванием.")
        print()
        print("❌ Не прошедшие проверки:")
        for test_name, success, message in all_results:
            if not success:
                print(f"  • {test_name}: {message}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
