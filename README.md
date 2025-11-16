# Руководство по запуску тестов для микросервиса Авито

## Предварительные требования:

- **Python 3.8+** 
- **Git**
- **Терминал**

**Проверка установки:**
```bash
python3 --version
git --version
```
---

## Клонирование репозитория

### 1. Клонирование репозитория
```bash
git clone <URL-репозитория>

cd Avito-internship
```

### 2. Навигация в нужную директорию
```bash
cd task2
```
---

## Установка зависимостей

### 3. Создание виртуального окружения
```bash
# Создайте виртуальное окружение
python3 -m venv venv
```

### 4. Активация виртуального окружения
```bash
# Для macOS/Linux:
source venv/bin/activate

# Для Windows:
venv\Scripts\activate
```

**Индикатор правильности:** В командной строке появится префикс `(venv)`

### 5. Обновление pip
```bash
python3 -m ensurepip --upgrade
```

### 6. Установка зависимостей
```bash
pip3 install -r requirements.txt
```

**Проверка установки:**
```bash
pip3 list
```
**Ожидаемые пакеты:** `pytest`, `requests`, `pytest-html`, `pytest-metadata`

---

## Запуск тестов

### 7. Базовый запуск тестов
```bash
# Запустите все тесты с подробным выводом
python3 -m pytest test_avito_api.py -v
```

### 8. Проверка результатов
После выполнения команды вы увидите детальный вывод:

```
test_avito_api.py::TestAvitoAPI::test_tc001_create_item_success FAILED
test_avito_api.py::TestAvitoAPI::test_tc002_create_item_minimal_data PASSED
...
```

**Ключ `-v` (verbose)** обеспечивает подробный вывод о ходе выполнения тестов.

---

## Генерация отчетов

### 9. Создание HTML отчета
```bash
python3 -m pytest test_avito_api.py --html=report.html --self-contained-html -v
```
---

## Просмотр результатов

### 10. Просмотр HTML отчета
```bash
# Откройте HTML отчет в браузере
open report.html
```
