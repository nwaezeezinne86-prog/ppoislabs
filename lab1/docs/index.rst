Лабораторная работа №1 — BigInt и машина Поста
=============================================

**Дисциплина:** ППОИС
**Выполнил:** [Нваезе Эзинне Роуз], гр. [521703]
**Проверил:** [Гуменный Н.А.]

1. Цель работы
--------------

Реализовать класс-значение и класс-состояние на ООП-языке. Обеспечить
инкапсуляцию, разделение интерфейса и реализации, модульные тесты,
документацию Sphinx и CI/CD.

Реализованы варианты:

- **1.6.3** — знаковое длинное целое неограниченной длины.
- **1.8.1** — машина Поста.

2. Инструменты
--------------

- Python 3.13
- pytest + pytest-cov
- Sphinx (autodoc, napoleon, viewcode)
- flake8
- GitHub Actions

3. Класс BigInt
---------------

Число хранится как знак (``_sign`` ∈ {-1, 0, 1}) и список десятичных цифр
(``_digits``), младшая цифра первой. Арифметика не использует встроенный
``int``.

Поддерживается:

- ``+ - * / %`` и составные ``+= -= *= /=``;
- ``increment``, ``decrement``, ``pre_increment``, ``pre_decrement``;
- ``== < <= > >=`` и ``__hash__``;
- ``int()``, ``float()``;
- ``from_string``, ``to_string``, ``copy``.

Ошибки: ``TypeError``, ``ValueError``, ``ZeroDivisionError``,
``NotImplemented``.

.. automodule:: lab1.src.big_int
   :members:
   :undoc-members:
   :show-inheritance:

4. Классы PostMachine и Tape
----------------------------

``Tape`` — бесконечная двусторонняя лента (словарь ``позиция → метка``).

``PostMachine`` — программа команд ``L R V X ? !``, методы ``step``,
``run``, ``reset``, ``set_tape``, ``load_program``, ``to_string``,
``from_string``, ``copy``. Собственное исключение ``PostMachineError``.

.. automodule:: lab1.src.post_machine
   :members:
   :undoc-members:
   :show-inheritance:

5. Консольный интерфейс
-----------------------

``lab1/src/cli.py`` — меню, полностью отделённое от классов.

.. code-block:: bash

   PYTHONPATH=. python -m lab1.src.cli

6. Тестирование
---------------

100 pytest-тестов, покрытие ``big_int.py`` и ``post_machine.py`` — 100 %.

.. code-block:: bash

   PYTHONPATH=. python -m pytest lab1/tests --cov=lab1/src --cov-report=term-missing

7. CI/CD
--------

GitHub Actions: flake8, pytest с порогом 90 %, сборка Sphinx, артефакт в
Releases при пуше тега ``v*``.
