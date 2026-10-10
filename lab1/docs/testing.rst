Testing
=======

- 100 pytest tests.
- Coverage 100 % for ``big_int.py`` and ``post_machine.py``.

Command:

.. code-block:: bash

   PYTHONPATH=. python -m pytest lab1/tests --cov=lab1/src --cov-report=term-missing
