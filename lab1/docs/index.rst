Lab 1 — BigInt and Post Machine
===============================

.. toctree::
   :maxdepth: 2

   overview
   architecture
   big_int
   post_machine
   algorithms
   examples
   testing
   changelog

Lab 1 implements two independent domain classes:

- **BigInt** — a signed integer of unbounded length.
- **PostMachine** with a companion **Tape** — a Post machine simulator.

Both are covered by 100 pytest cases, documented with Sphinx, and validated by
a GitHub Actions CI pipeline.
