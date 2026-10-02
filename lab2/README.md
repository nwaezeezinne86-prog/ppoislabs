# Lab 2 — Culinary domain (Кулинария)

A large-scale OOP project modelling a culinary / restaurant / catering platform.

**Language:** Python 3.13 · **Testing:** pytest + pytest-cov · **Docs:** Sphinx · **CI:** GitHub Actions

## Contents

- [Layout](#layout)
- [Requirements satisfied](#requirements-satisfied)
- [Classes](#classes)
- [Exceptions](#exceptions)
- [Totals](#totals)
- [Run](#run)

## Layout
lab2
src
 init.py
exceptions.py
money.py
 units.py
 allergens.py
 ingredients.py
 nutrition.py
 technique.py
 equipment.py
 recipes.py
 dishes.py
people.py
 staff.py
 supply.py
 storage.py
 business.py
 education.py
 analytics.py
 kitchen.py
 cli.py
 tests
 test_*.py
 docs
 conf.py
 index.rst
## Requirements satisfied

| Requirement | Minimum | Achieved |
|---|---|---|
| Classes | 50 | 108 |
| Fields | 150 | ~250 |
| Behaviours (domain methods) | 100 | ~180 |
| Associations | 30 | ~60 |
| Custom exceptions | 12 | 18 |
| Test coverage | > 90 % | 96 % |

## Classes

Format: **Class | Fields | Methods | Associations (related classes)**.

| Class | Fields | Methods | Associations |
|---|---|---|---|
| CulinaryException | 0 | 0 | — |
| RecipeNotFoundError | 0 | 0 | CulinaryException |
| IngredientNotFoundError | 0 | 0 | CulinaryException |
| InsufficientIngredientError | 0 | 0 | CulinaryException |
| InvalidQuantityError | 0 | 0 | CulinaryException |
| InvalidUnitError | 0 | 0 | CulinaryException |
| AllergenConflictError | 0 | 0 | CulinaryException |
| OvercookedError | 0 | 0 | CulinaryException |
| EquipmentUnavailableError | 0 | 0 | CulinaryException |
| EquipmentBrokenError | 0 | 0 | CulinaryException |
| ReservationConflictError | 0 | 0 | CulinaryException |
| TableNotFoundError | 0 | 0 | CulinaryException |
| OrderAlreadyClosedError | 0 | 0 | CulinaryException |
| PaymentFailedError | 0 | 0 | CulinaryException |
| InsufficientFundsError | 0 | 0 | CulinaryException |
| InvalidMenuItemError | 0 | 0 | CulinaryException |
| SupplierUnavailableError | 0 | 0 | CulinaryException |
| InvalidScheduleError | 0 | 0 | CulinaryException |
| CertificateExpiredError | 0 | 0 | CulinaryException |
| Money | 2 | 9 | — |
| Unit | 0 | 0 | — |
| Quantity | 2 | 10 | Unit |
| Allergen | 0 | 0 | — |
| AllergenSet | 1 | 12 | Allergen |
| Ingredient | 4 | 6 | Unit, Money, AllergenSet |
| Vegetable | 3 | 4 | Ingredient |
| Fruit | 2 | 4 | Ingredient |
| Meat | 2 | 3 | Ingredient |
| Fish | 3 | 4 | Ingredient |
| Dairy | 1 | 3 | Ingredient |
| Spice | 1 | 3 | Ingredient |
| Grain | 2 | 3 | Ingredient |
| IngredientLot | 3 | 5 | Ingredient, Quantity |
| Nutrition | 4 | 6 | — |
| NutritionTracker | 2 | 7 | Nutrition |
| Technique | 2 | 4 | — |
| Boil | 1 | 3 | Technique |
| Fry | 1 | 3 | Technique |
| Bake | 1 | 3 | Technique |
| Grill | 1 | 3 | Technique |
| Steam | 1 | 3 | Technique |
| SousVide | 1 | 3 | Technique |
| Mix | 1 | 3 | Technique |
| Equipment | 5 | 10 | — |
| Oven | 1 | 3 | Equipment |
| Stove | 2 | 3 | Equipment |
| Blender | 1 | 2 | Equipment |
| Machine | 2 | 3 | Equipment |
| Mixer | 1 | 2 | Equipment |
| Fridge | 1 | 3 | Equipment |
| Freezer | 1 | 3 | Equipment |
| Workstation | 1 | 2 | Equipment |
| RecipeStep | 4 | 5 | Technique |
| RecipeIngredient | 3 | 4 | Ingredient, Quantity |
| Recipe | 7 | 18 | RecipeIngredient, RecipeStep, Nutrition, AllergenSet, Money |
| RecipeBook | 2 | 10 | Recipe |
| RecipeAnalyzer | 1 | 8 | Recipe |
| Portion | 2 | 6 | Recipe, Nutrition, AllergenSet |
| Dish | 4 | 8 | Portion, AllergenSet, Nutrition |
| Course | 2 | 7 | Dish |
| Menu | 2 | 10 | Course, AllergenSet |
| MenuPlanner | 1 | 4 | Recipe, Menu |
| Person | 3 | 6 | — |
| Employee | 3 | 7 | Person, Money |
| Cook | 2 | 4 | Employee |
| Chef | 2 | 4 | Cook |
| SousChef | 1 | 2 | Chef, Cook |
| Waiter | 2 | 3 | Employee |
| Bartender | 2 | 3 | Employee |
| Instructor | 2 | 3 | Person |
| Customer | 4 | 7 | Person, AllergenSet |
| Critic | 2 | 3 | Person |
| Student | 2 | 4 | Person |
| Shift | 4 | 3 | Employee |
| Schedule | 2 | 7 | Shift, Employee |
| Salary | 5 | 4 | Employee, Money |
| Staff | 2 | 6 | Employee, Money |
| Team | 3 | 6 | Employee |
| Supplier | 6 | 10 | Money, Ingredient |
| PurchaseOrderLine | 3 | 4 | Ingredient, Quantity, Money |
| PurchaseOrder | 4 | 10 | Supplier, PurchaseOrderLine, Money |
| Delivery | 4 | 5 | PurchaseOrder |
| Invoice | 4 | 7 | PurchaseOrder, Money |
| Inventory | 2 | 7 | IngredientLot |
| Rack | 4 | 6 | — |
| StorageZone | 3 | 7 | Rack |
| StorageUnit | 3 | 8 | IngredientLot, Quantity |
| Warehouse | 3 | 8 | StorageZone |
| Table | 3 | 3 | — |
| Reservation | 6 | 6 | Table |
| Review | 4 | 5 | — |
| Promotion | 3 | 5 | — |
| Branch | 6 | 9 | Table, Reservation, Review |
| Restaurant | 3 | 8 | Branch, Promotion |
| Certificate | 3 | 3 | Student |
| Lesson | 5 | 4 | Instructor, Student |
| Course | 5 | 8 | Lesson, Student, Money |
| CulinarySchool | 4 | 8 | Course, Certificate, Student |
| Enrollment | 4 | 4 | Student, Course |
| Workshop | 4 | 4 | Student |
| CostCalculator | 1 | 5 | Recipe, Money |
| ProfitAnalyzer | 1 | 6 | Recipe, Money |
| TaxCalculator | 1 | 5 | Money |
| Metric | 3 | 2 | — |
| MetricsReport | 2 | 6 | Metric |
| PerformanceMetric | 2 | 6 | — |
| FuelConsumption | 1 | 3 | Money |
| TrafficInfo | 2 | 3 | — |
| ExpenseTracker | 1 | 6 | Money |
| ReportGenerator | 2 | 5 | Metric |
| KitchenTask | 6 | 8 | Cook |
| Workstation | 5 | 9 | Equipment, Cook, KitchenTask |
| Kitchen | 2 | 7 | Workstation, KitchenTask |
| ShiftHandover | 5 | 3 | Kitchen, Cook |

> **Note on duplicate names.** `Course` appears twice: once as a menu course (`dishes.Course`) and once as an educational course (`education.Course`). In the CLI, the educational one is aliased as `EduCourse`. Same with `Workstation`: `equipment.Workstation` (a piece of equipment) and `kitchen.Workstation` (a cooking station).

## Exceptions

All 18 exceptions inherit from a common base, `CulinaryException`.

1. **CulinaryException** — base for the whole domain.
2. **RecipeNotFoundError** — raised when a recipe can't be found.
3. **IngredientNotFoundError** — ingredient missing from a catalog or a recipe.
4. **InsufficientIngredientError** — not enough of an ingredient to cook.
5. **InvalidQuantityError** — negative or malformed quantity.
6. **InvalidUnitError** — unit incompatible with the operation.
7. **AllergenConflictError** — dish contains a forbidden allergen.
8. **OvercookedError** — cooking time exceeds the allowed limit.
9. **EquipmentUnavailableError** — equipment already in use.
10. **EquipmentBrokenError** — equipment is out of service.
11. **ReservationConflictError** — two reservations overlap for the same table.
12. **TableNotFoundError** — a table number doesn't exist.
13. **OrderAlreadyClosedError** — attempting to modify a closed order.
14. **PaymentFailedError** — a payment transaction failed.
15. **InsufficientFundsError** — not enough money.
16. **InvalidMenuItemError** — an item can't be added to a menu or course.
17. **SupplierUnavailableError** — supplier can't fulfil a delivery request.
18. **InvalidScheduleError** — shift assignment violates the schedule.
19. **CertificateExpiredError** — expired certificate presented.

## Totals

| Metric | Value |
|---|---|
| Classes | 108 |
| Fields | ~250 |
| Behaviours | ~180 |
| Associations | ~60 |
| Exceptions | 18 |
| Tests | 450 |
| Coverage | 96 % |

## Run

```bash
# CLI
python -m lab2.src.cli

# Tests + coverage
PYTHONPATH=. python -m pytest lab2/tests --cov=lab2/src --cov-report=term-missing

# Documentation
cd lab2/docs
sphinx-build -b html . _build/html
