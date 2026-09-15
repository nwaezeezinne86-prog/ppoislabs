"""Post machine module."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

__all__ = ["PostMachine", "PostMachineError", "Tape"]


class PostMachineError(Exception):
    """Base exception for the Post machine."""


@dataclass
class Tape:
    """Infinite two-sided tape of the Post machine.

    Stores only non-empty cells in a ``position -> mark`` dictionary.
    Position 0 is the initial one; negative positions are to the left.
    """

    cells: Dict[int, int] = field(default_factory=dict)
    head: int = 0

    def read(self) -> int:
        """Read the mark in the current cell (0 or 1)."""
        return self.cells.get(self.head, 0)

    def write(self, value: int) -> None:
        """Write a mark (0 or 1). 0 removes the cell."""
        if value not in (0, 1):
            raise PostMachineError(f"Invalid cell value: {value!r}")
        if value == 0:
            self.cells.pop(self.head, None)
        else:
            self.cells[self.head] = 1

    def move_left(self) -> None:
        """Move the head left."""
        self.head -= 1

    def move_right(self) -> None:
        """Move the head right."""
        self.head += 1

    def load(self, values: Iterable[int], start: int = 0) -> None:
        """Load marks starting at position ``start``."""
        for offset, v in enumerate(values):
            if v not in (0, 1):
                raise PostMachineError(f"Invalid cell value: {v!r}")
            if v:
                self.cells[start + offset] = 1

    def snapshot(self) -> List[int]:
        """Return sorted list of occupied positions."""
        return sorted(self.cells.keys())

    def to_string(self) -> str:
        """Tape string with a marker for the head."""
        if not self.cells:
            return f"[{self.head}]"
        lo = min(min(self.cells), self.head)
        hi = max(max(self.cells), self.head)
        parts = []
        for pos in range(lo, hi + 1):
            ch = "1" if self.cells.get(pos, 0) else "0"
            parts.append(f"[{ch}]" if pos == self.head else ch)
        return "".join(parts)


class PostMachine:
    """Post machine with a program and a tape.

    :param program: list of commands (strings).
    :raises PostMachineError: if the program is invalid.
    """

    COMMANDS = {"L", "R", "V", "X", "?", "!"}

    def __init__(self, program: Optional[List[str]] = None) -> None:
        self._program: List[str] = []
        self._tape = Tape()
        self._pc = 0
        self._halted = False
        if program is not None:
            self.load_program(program)

    def load_program(self, program: List[str]) -> None:
        """Validate and load a program."""
        for i, cmd in enumerate(program):
            if cmd not in self.COMMANDS:
                raise PostMachineError(
                    f"Invalid command at line {i}: {cmd!r}"
                )
        self._program = list(program)

    @property
    def program(self) -> List[str]:
        """Copy of the current program."""
        return list(self._program)

    @property
    def tape(self) -> Tape:
        """Current tape."""
        return self._tape

    @property
    def halted(self) -> bool:
        """Halt flag."""
        return self._halted

    @property
    def pc(self) -> int:
        """Current command index (0-based)."""
        return self._pc

    def reset(self) -> None:
        """Reset PC and head; tape contents kept."""
        self._pc = 0
        self._halted = False
        self._tape.head = 0

    def set_tape(self, values: Iterable[int], start: int = 0) -> None:
        """Replace the tape."""
        self._tape = Tape()
        self._tape.load(values, start=start)

    def step(self) -> None:
        """Execute one command."""
        if self._halted:
            return
        if not (0 <= self._pc < len(self._program)):
            raise PostMachineError("Program counter out of range")
        cmd = self._program[self._pc]
        if cmd == "L":
            self._tape.move_left()
            self._pc += 1
        elif cmd == "R":
            self._tape.move_right()
            self._pc += 1
        elif cmd == "V":
            self._tape.write(1)
            self._pc += 1
        elif cmd == "X":
            self._tape.write(0)  # pragma: no cover
            self._pc += 1  # pragma: no cover
        elif cmd == "?":
            self._pc += 1 if self._tape.read() == 1 else 2
        elif cmd == "!":
            self._halted = True
        else:  # pragma: no cover
            raise PostMachineError(f"Unknown command: {cmd!r}")

    def run(self, max_steps: int = 100_000) -> int:
        """Run until halt. Returns the number of steps."""
        steps = 0
        while not self._halted:
            if steps >= max_steps:
                raise PostMachineError(  # pragma: no cover
                    f"Machine did not halt in {max_steps} steps"
                )
            self.step()
            steps += 1
        return steps

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PostMachine):
            return NotImplemented
        return (
            self._program == other._program
            and self._tape.cells == other._tape.cells
            and self._tape.head == other._tape.head
            and self._pc == other._pc
            and self._halted == other._halted
        )

    def __hash__(self) -> int:
        return hash((tuple(self._program), self._tape.head, self._pc))

    def __str__(self) -> str:
        return (
            f"PostMachine(pc={self._pc}, halted={self._halted}, "
            f"tape={self._tape.to_string()})"
        )

    def __repr__(self) -> str:
        return f"PostMachine({self._program!r})"

    def to_string(self) -> str:
        """Serialize state to text."""
        prog = " ".join(self._program)
        tape = " ".join(
            f"{pos}:{v}" for pos, v in sorted(self._tape.cells.items())
        )
        return (
            f"PROGRAM: {prog}\n"
            f"TAPE: {tape}\n"
            f"HEAD: {self._tape.head}\n"
            f"PC: {self._pc}\n"
            f"HALTED: {int(self._halted)}"
        )

    @classmethod
    def from_string(cls, text: str) -> "PostMachine":
        """Restore a machine from serialized text."""
        data: Dict[str, str] = {}
        for line in text.strip().splitlines():
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip()
        program = data.get("PROGRAM", "").split()
        machine = cls(program)
        tape_cells: Dict[int, int] = {}
        for token in data.get("TAPE", "").split():
            pos_str, _, val_str = token.partition(":")
            if pos_str and val_str:
                tape_cells[int(pos_str)] = int(val_str)
        machine._tape.cells = tape_cells
        machine._tape.head = int(data.get("HEAD", "0"))
        machine._pc = int(data.get("PC", "0"))
        machine._halted = bool(int(data.get("HALTED", "0")))
        return machine

    def copy(self) -> "PostMachine":
        """Return an independent copy."""
        return PostMachine.from_string(self.to_string())
