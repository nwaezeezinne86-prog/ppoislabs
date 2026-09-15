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


class TestEdgeCases:
    def test_load_program_invalid_type(self):
        with pytest.raises(PostMachineError):
            PostMachine(["V", "1"])

    def test_tape_write_negative(self):
        with pytest.raises(PostMachineError):
            Tape().write(-1)

    def test_tape_load_invalid_value(self):
        with pytest.raises(PostMachineError):
            Tape().load([5])

    def test_program_property_returns_copy(self):
        m = PostMachine(["V", "!"])
        p1 = m.program
        p1.clear()
        assert m.program == ["V", "!"]

    def test_eq_with_different_program(self):
        a = PostMachine(["!"])
        b = PostMachine(["V", "!"])
        assert a != b

    def test_eq_with_different_pc(self):
        a = PostMachine(["V", "!", "!"])
        a.step()
        b = PostMachine(["V", "!", "!"])
        assert a != b

    def test_eq_with_different_halted(self):
        a = PostMachine(["!"])
        b = PostMachine(["!"])
        a.run()
        assert a != b

    def test_eq_with_different_tape(self):
        a = PostMachine(["!"])
        b = PostMachine(["!"])
        a.tape.write(1)
        assert a != b

    def test_copy_of_negative_head(self):
        m = PostMachine(["L", "V", "!"])
        m.run()
        c = m.copy()
        assert c == m

    def test_reset_keeps_tape_contents(self):
        m = PostMachine(["V", "!"])
        m.run()
        tape_before = dict(m.tape.cells)
        m.reset()
        assert m.tape.cells == tape_before
        assert m.tape.head == 0

    def test_from_string_ignores_bad_lines(self):
        text = "junk line without colon\nPROGRAM: !\nHEAD: 0\nPC: 0\nHALTED: 0"
        m = PostMachine.from_string(text)
        assert m.program == ["!"]

    def test_str_contains_tape(self):
        m = PostMachine(["!"])
        assert "tape" in str(m)

    def test_unknown_command_marker(self):
        m = PostMachine(["!"])
        # Manually inject an invalid command to exercise the else branch
        m._program = ["Z"]
        with pytest.raises(PostMachineError):
            m.step()


class TestLastMissingLinesPM:
    def test_load_program_error_message_for_bad_command(self):
        with pytest.raises(PostMachineError) as exc_info:
            PostMachine(["V", "BAD"])
        assert "line 1" in str(exc_info.value)

    def test_tape_write_error_message(self):
        with pytest.raises(PostMachineError) as exc_info:
            Tape().write(7)
        assert "7" in str(exc_info.value)

    def test_tape_load_error_message(self):
        with pytest.raises(PostMachineError) as exc_info:
            Tape().load([1, 9])
        assert "9" in str(exc_info.value)
