Отчёт по лабораторной работе №2
===============================

**Министерство образования Республики Беларусь**
**Учреждение образования «Белорусский государственный университет информатики и радиоэлектроники»**
Факультет информационных технологий и управления
Кафедра интеллектуальных информационных технологий

**Дисциплина:** ППОИС
**Лабораторная работа №2:** «Крупный ООП-проект»

**Выполнил:** [ФИО], гр. [номер группы]
**Предметная область:** Кулинария
**Проверил:** [ФИО преподавателя]
**Дата:** [YYYY-MM-DD]

1. Цель работы
--------------

Спроектировать и реализовать крупный объектно-ориентированный проект для
индивидуально назначенной предметной области, удовлетворяющий следующим
количественным требованиям:

- не менее 50 классов;
- не менее 150 полей суммарно по всем классам;
- не менее 100 уникальных поведений;
- не менее 30 ассоциаций между классами;
- не менее 12 собственных классов исключений.

Дополнительно: README с описанием всех классов, модульные тесты с
покрытием > 90 %, консольный интерфейс, документация Sphinx и CI/CD.

2. Достигнутые показатели
-------------------------

.. list-table::
   :header-rows: 1

   * - Показатель
     - Требование
     - Достигнуто
   * - Классы
     - ≥ 50
     - 108
   * - Поля
     - ≥ 150
     - ~250
   * - Поведения
     - ≥ 100
     - ~180
   * - Ассоциации
     - ≥ 30
     - ~60
   * - Исключения
     - ≥ 12
     - 18
   * - Покрытие
     - > 90 %
     - 96 %

3. Выбранный язык и инструменты
-------------------------------

.. list-table::
   :header-rows: 1

   * - Назначение
     - Выбор
   * - Язык программирования
     - Python 3.13
   * - Тестирование
     - pytest + pytest-cov
   * - Документация
     - Sphinx (autodoc, napoleon, viewcode)
   * - Статический анализ
     - flake8
   * - CI/CD
     - GitHub Actions

4. Структура проекта
--------------------

.. code-block:: text

   lab2/
   ├── README.md
   ├── src/
   │   ├── exceptions.py
   │   ├── money.py
   │   ├── units.py
   │   ├── allergens.py
   │   ├── ingredients.py
   │   ├── nutrition.py
   │   ├── technique.py
   │   ├── equipment.py
   │   ├── recipes.py
   │   ├── dishes.py
   │   ├── people.py
   │   ├── staff.py
   │   ├── supply.py
   │   ├── storage.py
   │   ├── business.py
   │   ├── education.py
   │   ├── analytics.py
   │   ├── kitchen.py
   │   └── cli.py
   ├── tests/
   └── docs/

Проект разделён на три уровня:

- **Предметный уровень** — все модули ``src``, кроме ``cli.py``.
- **Уровень представления** — ``cli.py``.
- **Уровень тестирования** — ``tests/``.

5. Архитектура предметной области
---------------------------------

5.1. Базовые типы-значения
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Money** — сумма в одной валюте, хранится в минорных единицах.
- **Unit**, **Quantity** — единицы измерения и величина.
- **Allergen**, **AllergenSet** — аллергены и их множества.
- **Nutrition**, **NutritionTracker** — пищевая ценность и трекер.

.. automodule:: lab2.src.money
   :members:
   :undoc-members:

.. automodule:: lab2.src.units
   :members:
   :undoc-members:

.. automodule:: lab2.src.allergens
   :members:
   :undoc-members:

.. automodule:: lab2.src.nutrition
   :members:
   :undoc-members:

5.2. Ингредиенты
~~~~~~~~~~~~~~~~

**Ingredient** — базовый класс ингредиента с названием, единицей измерения,
ценой и аллергенами. Подклассы: **Vegetable** (сезонность, органика),
**Fruit** (спелость, сладость), **Meat** (безопасная температура),
**Fish** (свежесть, кости), **Dairy** (жирность), **Spice** (шкала
Сковилла), **Grain** (глютен, время приготовления). **IngredientLot** —
партия с датой истечения и методом ``consume()``.

.. automodule:: lab2.src.ingredients
   :members:
   :undoc-members:
   :show-inheritance:

5.3. Техники приготовления
~~~~~~~~~~~~~~~~~~~~~~~~~~

Абстрактный класс **Technique** и семь конкретных техник: ``Boil``,
``Fry``, ``Bake``, ``Grill``, ``Steam``, ``SousVide``, ``Mix``. Каждая
реализует ``apply()``; превышение времени вызывает ``OvercookedError``.

.. automodule:: lab2.src.technique
   :members:
   :undoc-members:
   :show-inheritance:

5.4. Оборудование
~~~~~~~~~~~~~~~~~

Абстрактный класс **Equipment** с состоянием «свободно / занято / сломано»
и девять конкретных реализаций: ``Oven``, ``Stove``, ``Blender``,
``Machine``, ``Mixer``, ``Fridge``, ``Freezer``, ``Workstation``.

.. automodule:: lab2.src.equipment
   :members:
   :undoc-members:
   :show-inheritance:

5.5. Рецепты
~~~~~~~~~~~~

- **RecipeStep** — шаг рецепта.
- **RecipeIngredient** — ингредиент с количеством.
- **Recipe** — рецепт: ингредиенты, шаги, порции, пищевая ценность.
- **RecipeBook** — коллекция с поиском по стоимости, времени и аллергенам.
- **RecipeAnalyzer** — аналитика по одному рецепту.

.. automodule:: lab2.src.recipes
   :members:
   :undoc-members:
   :show-inheritance:

5.6. Блюда и меню
~~~~~~~~~~~~~~~~~

- **Portion** — порция рецепта.
- **Dish** — блюдо с гарниром и оформлением.
- **Course** — курс приёма пищи.
- **Menu** — набор курсов.
- **MenuPlanner** — планировщик меню по эвристикам.

.. automodule:: lab2.src.dishes
   :members:
   :undoc-members:
   :show-inheritance:

5.7. Люди
~~~~~~~~~

Иерархия: **Person** → **Employee** → **Cook** → **Chef** → **SousChef**,
плюс **Waiter**, **Bartender**, **Instructor**, **Customer**, **Critic**,
**Student**.

.. automodule:: lab2.src.people
   :members:
   :undoc-members:
   :show-inheritance:

5.8. Персонал
~~~~~~~~~~~~~

- **Shift** — смена с проверкой пересечения.
- **Schedule** — недельное расписание.
- **Salary** — расчёт зарплаты.
- **Staff** — список сотрудников.
- **Team** — команда с лидером.

.. automodule:: lab2.src.staff
   :members:
   :undoc-members:
   :show-inheritance:

5.9. Поставки
~~~~~~~~~~~~~

- **Supplier** — поставщик с каталогом.
- **PurchaseOrder** — заказ на закупку со статусами.
- **Delivery** — доставка.
- **Invoice** — счёт-фактура.
- **Inventory** — склад с уровнями пополнения.

.. automodule:: lab2.src.supply
   :members:
   :undoc-members:
   :show-inheritance:

5.10. Хранение
~~~~~~~~~~~~~~

- **Rack**, **StorageZone**, **StorageUnit**, **Warehouse**.

.. automodule:: lab2.src.storage
   :members:
   :undoc-members:
   :show-inheritance:

5.11. Бизнес
~~~~~~~~~~~~

- **Table**, **Reservation**, **Review**, **Promotion**.
- **Branch** — филиал ресторана.
- **Restaurant** — сеть ресторанов.

.. automodule:: lab2.src.business
   :members:
   :undoc-members:
   :show-inheritance:

5.12. Образование
~~~~~~~~~~~~~~~~~

- **Lesson**, **Course**, **CulinarySchool**, **Enrollment**, **Workshop**,
  **Certificate**.

.. automodule:: lab2.src.education
   :members:
   :undoc-members:
   :show-inheritance:

5.13. Аналитика
~~~~~~~~~~~~~~~

- **CostCalculator**, **ProfitAnalyzer**, **TaxCalculator** — расчёты.
- **Metric**, **MetricsReport**, **PerformanceMetric**,
  **FuelConsumption**, **TrafficInfo**, **ExpenseTracker**,
  **ReportGenerator** — метрики и отчёты.

.. automodule:: lab2.src.analytics
   :members:
   :undoc-members:
   :show-inheritance:

5.14. Кухня
~~~~~~~~~~~

- **KitchenTask** — задача со статусами.
- **Workstation** — рабочее место.
- **Kitchen** — кухня.
- **ShiftHandover** — передача смены.

.. automodule:: lab2.src.kitchen
   :members:
   :undoc-members:
   :show-inheritance:

6. Исключения
-------------

Все 18 собственных исключений наследуются от базового
**CulinaryException**:

1. CulinaryException
2. RecipeNotFoundError
3. IngredientNotFoundError
4. InsufficientIngredientError
5. InvalidQuantityError
6. InvalidUnitError
7. AllergenConflictError
8. OvercookedError
9. EquipmentUnavailableError
10. EquipmentBrokenError
11. ReservationConflictError
12. TableNotFoundError
13. OrderAlreadyClosedError
14. PaymentFailedError
15. InsufficientFundsError
16. InvalidMenuItemError
17. SupplierUnavailableError
18. InvalidScheduleError
19. CertificateExpiredError

.. automodule:: lab2.src.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

7. Консольный интерфейс
-----------------------

``lab2/src/cli.py`` — меню на основе ``while True`` с пятью разделами:

1. **Recipes** — добавление рецепта, ингредиентов и шагов, просмотр,
   удаление, поиск по стоимости.
2. **Menus** — построение меню из рецептов.
3. **People** — наём персонала и регистрация клиентов.
4. **Restaurant** — добавление ресторана, филиала, столика, бронирование,
   отзывы.
5. **Education** — добавление школы, курса, зачисление студента, выдача
   сертификата.

CLI не обращается к приватным полям классов, не дублирует логику
предметной области и корректно ловит исключения.

**Запуск:**

.. code-block:: bash

   PYTHONPATH=. python -m lab2.src.cli

8. Тестирование
---------------

- **450 тестов** pytest в 15 файлах.
- Покрытие предметного слоя — **96 %** (требование > 90 %).
- CLI исключён из измерения через ``.coveragerc``.

Команда:

.. code-block:: bash

   PYTHONPATH=. python -m pytest lab2/tests --cov=lab2/src --cov-report=term-missing

**Основные тестовые сценарии**

- создание всех классов и подклассов;
- проверка инвариантов (занятое оборудование, конфликт бронирования,
  истёкший сертификат);
- граничные случаи (пустые рецепты, нулевые количества, деление на ноль);
- работа с аллергенами и множествами;
- сериализация и обратное восстановление;
- взаимодействие подсистем (заказ → доставка → счёт → оплата).

9. Документация
---------------

Документация сгенерирована Sphinx с расширениями ``autodoc``, ``napoleon``,
``viewcode``. ``conf.py`` добавляет корень репозитория в ``sys.path`` через
``os.path.dirname(__file__)``, чтобы не зависеть от текущей рабочей
директории.

Сборка:

.. code-block:: bash

   cd lab2/docs
   sphinx-build -b html . _build/html

Результат — ``lab2/docs/_build/html/index.html``.

10. Непрерывная интеграция и доставка
-------------------------------------

Файл ``.github/workflows/ci.yml`` запускается при push в ``main``, при push
в ветки ``feature/**``, при Pull Request в ``main`` и при создании тега
``v*``.

**Этапы pipeline**

1. Checkout репозитория.
2. Установка Python 3.12.
3. Установка зависимостей из ``requirements.txt``.
4. Проверка стиля: ``flake8 lab1/src lab2/src``.
5. Тесты Lab 1 с покрытием и порогом 90 %.
6. Тесты Lab 2 с покрытием и порогом 90 %.
7. Сборка документации Sphinx для обоих лаб.
8. Упаковка ``lab1/src`` и ``lab2/src`` в ``lab-src.zip``.
9. Публикация артефакта в GitHub Releases при пуше тега.

11. Рабочий процесс Git
-----------------------

- Основная ветка — ``main``.
- Работа велась в ветке ``feature/lab2``, созданной от ``main``.
- Изменения фиксировались логически раздельными коммитами.
- Изменения влиты в ``main`` через Pull Request №2.
- Создан тег ``v2.0.0``; артефакт ``lab-src.zip`` опубликован на странице
  Releases.

12. Результаты
--------------

Все требования лабораторной работы выполнены и перевыполнены:

- 108 классов (требование ≥ 50);
- ~250 полей (требование ≥ 150);
- ~180 поведений (требование ≥ 100);
- ~60 ассоциаций (требование ≥ 30);
- 18 собственных исключений (требование ≥ 12);
- покрытие тестами — 96 % (требование > 90 %);
- CI/CD настроен и работает;
- артефакт сборки опубликован в GitHub Releases.

13. Воспроизведение проекта
---------------------------

.. code-block:: bash

   git clone https://github.com/nwaezeezinne86-prog/ppoislabs.git
   cd ppoislabs
   python -m venv .venv
   source .venv/Scripts/activate
   pip install -r requirements.txt
   PYTHONPATH=. python -m pytest lab2/tests --cov=lab2/src --cov-report=term-missing
   PYTHONPATH=. python -m lab2.src.cli

14. Заключение
--------------

В ходе работы спроектирован и реализован крупный объектно-ориентированный
проект на тему «Кулинария», полностью удовлетворяющий количественным
требованиям задания. Проект демонстрирует практическое применение
принципов ООП: абстракции, наследования, полиморфизма, инкапсуляции и
композиции.

Отделение предметной логики от CLI, документирование Sphinx и настройка
CI/CD с публикацией артефактов делают проект воспроизводимым, тестируемым
и готовым к сопровождению.
