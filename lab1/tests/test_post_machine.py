"""Tests for the Post machine."""
import pytest

from lab1.src.post_machine import PostMachine, PostMachineError, Tape


class TestTape:
    def test_read_write(self):
        t = Tape()
        assert t.read() == 0
        t.write(1)
        assert t.read() == 1
        t.write(0)
        assert t.read() == 0

    def test_invalid_write(self):
        with pytest.raises(PostMachineError):
            Tape().write(2)

    def test_moves(self):
        t = Tape()
        t.move_right()
        t.write(1)
        t.move_left()
        assert t.read() == 0
        t.move_left()
        assert t.head == -1

    def test_load_and_snapshot(self):
        t = Tape()
        t.load([1, 0, 1, 1], start=-1)
        assert t.snapshot() == [-1, 1, 2]

    def test_load_invalid(self):
        with pytest.raises(PostMachineError):
            Tape().load([0, 2])

    def test_to_string_empty(self):
        assert Tape().to_string() == "[0]"

    def test_to_string_nonempty(self):
        t = Tape()
        t.load([1, 1])
        t.head = 1
        assert "[" in t.to_string()


class TestProgram:
    def test_load_valid(self):
        m = PostMachine(["V", "R", "!"])
        assert m.program == ["V", "R", "!"]

    def test_load_invalid(self):
        with pytest.raises(PostMachineError):
            PostMachine(["V", "Z"])

    def test_program_copy(self):
        m = PostMachine(["V"])
        p = m.program
        p.append("!")
        assert m.program == ["V"]


class TestExecution:
    def test_step_marks_and_moves(self):
        m = PostMachine(["V", "R", "V", "R", "V", "!"])
        m.run()
        assert m.halted
        assert m.tape.snapshot() == [0, 1, 2]

    def test_conditional_jump_taken(self):
        m = PostMachine(["V", "?", "!", "!"])
        m.run()
        assert m.halted

    def test_conditional_jump_not_taken(self):
        m = PostMachine(["?", "V", "!"])
        m.run()
        assert m.halted
        assert m.tape.snapshot() == []

    def test_reset(self):
        m = PostMachine(["V", "R", "!"])
        m.run()
        m.reset()
        assert m.pc == 0 and not m.halted and m.tape.head == 0

    def test_step_after_halt(self):
        m = PostMachine(["!"])
        m.run()
        pc_before = m.pc
        m.step()
        assert m.pc == pc_before

    def test_pc_out_of_range(self):
        m = PostMachine(["V"])
        m.step()
        with pytest.raises(PostMachineError):
            m.step()

    def test_run_max_steps(self):
        m = PostMachine(["R"])
        with pytest.raises(PostMachineError):
            m.run(max_steps=10)

    def test_set_tape(self):
        m = PostMachine(["!"])
        m.set_tape([1, 1], start=5)
        assert m.tape.snapshot() == [5, 6]


class TestSerialization:
    def test_round_trip(self):
        m = PostMachine(["V", "R", "?"])
        m.tape.load([1, 1], start=0)
        m.step()
        m.step()
        text = m.to_string()
        restored = PostMachine.from_string(text)
        assert restored == m

    def test_eq_non_machine(self):
        assert PostMachine(["!"]).__eq__("x") is NotImplemented

    def test_hash(self):
        m1 = PostMachine(["!"])
        m2 = PostMachine(["!"])
        assert hash(m1) == hash(m2)

    def test_copy_independent(self):
        m = PostMachine(["V", "!"])
        c = m.copy()
        c.step()
        assert m != c

    def test_str_and_repr(self):
        m = PostMachine(["!"])
        assert "PostMachine" in repr(m)
        assert "halted" in str(m)
