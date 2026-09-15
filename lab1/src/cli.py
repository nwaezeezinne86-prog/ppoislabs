"""Console UI for demonstrating BigInt and PostMachine.

The UI is fully separated from the implementation: the BigInt and
PostMachine classes know nothing about this module.
"""
from __future__ import annotations
import sys
from typing import List

from .big_int import BigInt
from .post_machine import PostMachine, PostMachineError


def _read(prompt: str) -> str:
    return input(prompt).strip()


def _print_menu(title: str, items: List[str]) -> None:
    print(f"\n=== {title} ===")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    print("  0. Back")


def big_int_menu() -> None:
    """Menu for the BigInt demo."""
    a = BigInt(0)
    b = BigInt(0)
    while True:
        print(f"\nA = {a}\nB = {b}")
        _print_menu(
            "BigInt",
            [
                "Set A",
                "Set B",
                "A + B",
                "A - B",
                "A * B",
                "A / B",
                "A % B",
                "A += B",
                "A -= B",
                "A *= B",
                "A /= B",
                "A++ (post)",
                "A-- (post)",
                "++A (pre)",
                "--A (pre)",
                "Compare A and B",
                "Convert A to int",
                "Serialize A to string",
                "Read A from string",
            ],
        )
        choice = _read("Choice: ")
        if choice == "0":
            return
        try:
            if choice == "1":
                a = BigInt(_read("A = "))
            elif choice == "2":
                b = BigInt(_read("B = "))
            elif choice == "3":
                print(f"A + B = {a + b}")
            elif choice == "4":
                print(f"A - B = {a - b}")
            elif choice == "5":
                print(f"A * B = {a * b}")
            elif choice == "6":
                print(f"A / B = {a // b}")
            elif choice == "7":
                print(f"A % B = {a % b}")
            elif choice == "8":
                a += b
                print(f"A = {a}")
            elif choice == "9":
                a -= b
                print(f"A = {a}")
            elif choice == "10":
                a *= b
                print(f"A = {a}")
            elif choice == "11":
                a //= b
                print(f"A = {a}")
            elif choice == "12":
                old = a.increment()
                print(f"Post-increment: was {old}, now {a}")
            elif choice == "13":
                old = a.decrement()
                print(f"Post-decrement: was {old}, now {a}")
            elif choice == "14":
                a.pre_increment()
                print(f"Pre-increment: {a}")
            elif choice == "15":
                a.pre_decrement()
                print(f"Pre-decrement: {a}")
            elif choice == "16":
                print(f"A < B: {a < b}, A <= B: {a <= b}")
                print(f"A > B: {a > b}, A >= B: {a >= b}")
                print(f"A == B: {a == b}, A != B: {a != b}")
            elif choice == "17":
                print(f"int(A) = {int(a)}")
            elif choice == "18":
                print(f"to_string: {a.to_string()}")
            elif choice == "19":
                a = BigInt.from_string(_read("String: "))
            else:
                print("Unknown command")
        except (ValueError, ZeroDivisionError, TypeError) as exc:
            print(f"Error: {exc}")


def post_machine_menu() -> None:
    """Menu for the Post machine demo."""
    machine = PostMachine()
    default_program = ["V", "R", "V", "R", "V", "!"]
    machine.load_program(default_program)
    while True:
        print(f"\nState: {machine}")
        _print_menu(
            "Post machine",
            [
                "Load default program (V R V R V !)",
                "Enter program manually",
                "Load tape",
                "Execute one step",
                "Run until halt",
                "Reset state",
                "Show serialized state",
                "Load state from text",
            ],
        )
        choice = _read("Choice: ")
        if choice == "0":
            return
        try:
            if choice == "1":
                machine.load_program(default_program)
                print("Program loaded")
            elif choice == "2":
                raw = _read("Commands separated by spaces (L R V X ? !): ")
                machine.load_program(raw.split())
                print("Program loaded")
            elif choice == "3":
                raw = _read("Marks (0/1 separated by spaces): ")
                values = [int(x) for x in raw.split()]
                machine.set_tape(values)
                print("Tape loaded")
            elif choice == "4":
                machine.step()
                print(f"Step executed: {machine}")
            elif choice == "5":
                steps = machine.run()
                print(f"Halted after {steps} steps: {machine}")
            elif choice == "6":
                machine.reset()
                print("State reset")
            elif choice == "7":
                print(machine.to_string())
            elif choice == "8":
                print("Enter state text (empty line ends input):")
                lines: List[str] = []
                while True:
                    line = input()
                    if not line:
                        break
                    lines.append(line)
                machine = PostMachine.from_string("\n".join(lines))
                print("State loaded")
            else:
                print("Unknown command")
        except (PostMachineError, ValueError) as exc:
            print(f"Error: {exc}")


def main() -> int:
    """CLI entry point."""
    while True:
        _print_menu(
            "Main menu",
            ["BigInt (signed arbitrary-precision)", "Post machine"],
        )
        choice = _read("Choice: ")
        if choice == "0":
            print("Goodbye!")
            return 0
        if choice == "1":
            big_int_menu()
        elif choice == "2":
            post_machine_menu()
        else:
            print("Unknown command")


if __name__ == "__main__":
    sys.exit(main())
