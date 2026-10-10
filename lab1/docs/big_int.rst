BigInt — signed integer of unbounded length
===========================================

Purpose
-------

``BigInt`` stores a signed integer of any magnitude without falling back to the
built-in ``int`` for arithmetic.

Representation
--------------

- ``_sign`` ∈ ``{-1, 0, 1}``.
- ``_digits`` — decimal digits, least significant first.
- Zero: ``sign = 0``, ``digits = [0]``.

Public API
----------

- Constructor, properties, arithmetic ``+ - * / %``, compound forms,
  increment/decrement, comparisons, ``int()``/``float()`` conversions,
  ``from_string``/``to_string``, ``copy``.

Full class documentation
------------------------

.. automodule:: lab1.src.big_int
   :members:
   :undoc-members:
   :show-inheritance:
