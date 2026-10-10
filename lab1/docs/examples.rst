Examples
========

.. code-block:: python

   from lab1.src.big_int import BigInt
   a = BigInt("99999999999999999999")
   print(a + BigInt(1))          # 100000000000000000000

.. code-block:: python

   from lab1.src.post_machine import PostMachine
   m = PostMachine(["V", "R", "V", "R", "V", "!"])
   m.run()
   print(m.tape.to_string())     # 111

.. code-block:: bash

   PYTHONPATH=. python -m lab1.src.cli
