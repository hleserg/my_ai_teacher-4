#!/usr/bin/env python3
"""Простой тест функции разбивки сообщений"""

def split_long_message(text: str, max_length: int = 4096):
    """Копия функции разбивки из bot.py для тестирования"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    # Разбиваем по абзацам (двойной перенос строки)
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        # Если добавление абзаца превысит лимит
        if len(current_part) + len(paragraph) + 2 > max_length:
            if current_part:  # Если есть накопленный текст
                parts.append(current_part.strip())
                current_part = paragraph + '\n\n'
            else:  # Если абзац слишком длинный, разбиваем по предложениям
                sentences = paragraph.split('. ')
                for sentence in sentences:
                    if len(current_part) + len(sentence) + 2 > max_length:
                        if current_part:
                            parts.append(current_part.strip())
                            current_part = sentence + '. '
                        else:  # Если предложение слишком длинное, принудительно разбиваем
                            while len(sentence) > max_length:
                                parts.append(sentence[:max_length])
                                sentence = sentence[max_length:]
                            current_part = sentence + '. '
                    else:
                        current_part += sentence + '. '
                current_part += '\n\n'
        else:
            current_part += paragraph + '\n\n'
    
    # Добавляем последнюю часть
    if current_part.strip():
        parts.append(current_part.strip())
    
    return parts

def test_splitting():
    # Создаем длинное сообщение
    long_text = """
**📖 Детекция аномалий в данных 1C с ИИ**

_Интегрируйте алгоритмы для выявления необычных транзакций в бухгалтерии 1C._

⏱️ **Время изучения:** 1-2 дня
📊 **Сложность:** Средний

**📚 Материалы для изучения:**

**Краткое введение в тему**
Детекция аномалий в данных 1C с использованием ИИ — это метод выявления необычных паттернов в бухгалтерских транзакциях. """ + "А" * 1500 + """

**Основные концепции включают:**
- **Точечные аномалии** - одиночные выбросы
- **Контекстные аномалии** - аномалии в зависимости от условий
- **Коллективные аномалии** - групповые отклонения

**Пошаговый план изучения (1-3 дня):**
1. **День 1: Основы** - изучение теории детекции аномалий
2. **День 2: Практика** - работа с данными из 1C
3. **День 3: Интеграция** - создание собственного решения

**🔗 Полезные ссылки:**
• **Официальная документация:** [scikit-learn: IsolationForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
• **GitHub репозитории:** [Anomaly Detection Resources](https://github.com/yzhao062/anomaly-detection-resources)
• **Статьи:** [Детекция аномалий с Python](https://habr.com/ru/articles/338306/)

**🎥 Видео и курсы:**
• **YouTube видео:** [Data Science - Isolation Forest](https://www.youtube.com/watch?v=O9WLaT3rWEw)
• **Онлайн курсы:** [Coursera - Machine Learning](https://www.coursera.org/learn/machine-learning)

**💡 Практические примеры:**

**Пример 1: Базовая детекция с Isolation Forest**

```python
import pandas as pd
from sklearn.ensemble import IsolationForest

# Загрузка данных из CSV (экспортированных из 1C)
data = pd.read_csv('transactions.csv')
features = data[['amount']]

# Создание модели
model = IsolationForest(contamination=0.01, random_state=42)
model.fit(features)

# Предсказание аномалий
data['anomaly'] = model.predict(features)
anomalies = data[data['anomaly'] == -1]
print("Аномалии:", anomalies)
```

Этот код загружает данные транзакций и использует алгоритм Isolation Forest для выявления аномалий. """ + "Б" * 2000 + """

**Пример 2: Интеграция с 1C через ODBC**

Для подключения к базе 1C используйте ODBC драйвер и библиотеку pyodbc для прямого чтения данных.
    """
    
    print(f"📏 Длина исходного текста: {len(long_text)} символов")
    print("📏 Лимит Telegram: 4096 символов")
    print("=" * 50)
    
    parts = split_long_message(long_text)
    
    print(f"🔢 Разбито на {len(parts)} частей:")
    total_length = 0
    for i, part in enumerate(parts, 1):
        total_length += len(part)
        status = "✅ В пределах лимита" if len(part) <= 4096 else "❌ ПРЕВЫШЕН ЛИМИТ!"
        print(f"  Часть {i}: {len(part)} символов - {status}")
    
    print(f"\n📊 Проверка: исходная длина {len(long_text)} = сумма частей {total_length}")
    
    # Показываем начало каждой части
    print("\n📝 Начало каждой части:")
    for i, part in enumerate(parts, 1):
        lines = part.strip().split('\n')[:3]  # Первые 3 строки
        preview = ' | '.join(line.strip() for line in lines if line.strip())
        print(f"  Часть {i}: {preview[:100]}...")

if __name__ == '__main__':
    test_splitting()
