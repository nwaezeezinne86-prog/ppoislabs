Architecture
============

Three layers
------------

.. code-block:: text

   lab1/
   ├── src/
   │   ├── big_int.py         # domain
   │   ├── post_machine.py    # domain
   │   └── cli.py             # presentation
   ├── tests/
   └── docs/

Class diagram
-------------

.. code-block:: text

   BigInt                PostMachine
     │                     │
     │ uses                │ owns
     ▼                     ▼
   (none)                Tape
