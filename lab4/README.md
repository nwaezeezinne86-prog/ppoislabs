# Lab 4 — Generic programming: sorting and containers (C++17)

Variant: **Task 1** — Bubble sort and Patience sorting; **Task 2** — 2.1.1 undirected graph on an adjacency matrix.

## Layout
| Path | Content |
|---|---|
| `include/lab4/sorting.hpp` | `bubble_sort`, `patience_sort` (iterator-range and container forms) |
| `include/lab4/student.hpp` | demo user-defined class `Student` |
| `include/lab4/graph.hpp` | `UndirectedGraph<T>` with bidirectional, reverse and const iterators |
| `include/lab4/menu.hpp`, `src/menu.cpp` | console menu (streams are injected, so it is testable) |
| `src/main.cpp` | entry point |
| `tests/` | unit tests (small built-in framework, no external dependencies) |
| `Doxyfile` | Doxygen configuration |

## Commands
```
make                 # build build/lab4
make run             # build and start the menu
make test            # build and run unit tests
make coverage        # tests + gcov, fails if line coverage < 90 %
make lint            # cppcheck
make docs            # Doxygen HTML in docs/html/index.html
```
Requires `g++` (C++17), `make`, `python3` (coverage script); `doxygen` and `cppcheck` for `docs` / `lint`.

## Sorting
Both algorithms accept an iterator range or a whole container (C array, `std::vector`, `std::list`, ...) and an
optional comparator (functor or lambda); the default is `std::less<>`.

```cpp
std::vector<lab4::Student> students = ...;
lab4::patience_sort(students);                          // natural order (operator<)
lab4::bubble_sort(students, lab4::ByGradeDescending()); // functor
int numbers[] = {5, 3, 1};
lab4::bubble_sort(numbers);                             // C array
```

## Graph
`UndirectedGraph<T>` stores values of type `T` in vertices; vertices are addressed by stable `vertex_id`s.
Four iterator families (vertices, edges, edges incident to a vertex, vertices adjacent to a vertex) each exist as
mutable, const, reverse and const-reverse versions (`*_begin/_end`, `*_cbegin/_cend`, `*_rbegin/_rend`,
`*_crbegin/_crend`). Vertex iterators dereference to `{id, value&}`, edge iterators to `std::pair<id, id>`.
`erase_vertex` / `erase_edge` remove by iterator and return an iterator to the following element; any other
modification invalidates all iterators.
