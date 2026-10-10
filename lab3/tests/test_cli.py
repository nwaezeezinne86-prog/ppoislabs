import unittest

from cli import FitnessCli
from fitness.app import FitnessApp

REGISTER = ["1", "180", "80", "male", "Alex", "alex@mail.com", "1995-05-20", "secret123"]
WORKOUT = ["3", "Bench", "chest", "6", "3", "10", "50", "60", "45"]
RUN = ["4", "30", "5"]
MEAL = ["5", "lunch", "Egg", "80", "6", "1", "5"]
GOAL = ["6", "75", "30"]
REPORT = ["7"]
CHALLENGE = ["8", "Steps"]
BOARD = ["9", "Steps"]


def run_cli(answers: list[str]) -> list[str]:
    queue = iter(answers + ["0"])
    output: list[str] = []
    FitnessCli(FitnessApp(), lambda prompt: next(queue), output.append).run()
    return output


class CliTest(unittest.TestCase):
    def test_full_scenario(self):
        output = run_cli(REGISTER + WORKOUT + RUN + MEAL + GOAL + REPORT + CHALLENGE + BOARD)
        text = "\n".join(output)
        self.assertIn("Registered Alex", text)
        self.assertIn("Workout saved", text)
        self.assertIn("Run saved", text)
        self.assertIn("Meal saved", text)
        self.assertIn("Goal set", text)
        self.assertIn("Workouts: 2", text)
        self.assertIn("1. Alex: 0", text)
        self.assertEqual(output[-1], "Goodbye!")

    def test_login_flow(self):
        app = FitnessApp()
        queue = iter(REGISTER + ["2", "alex@mail.com", "secret123", "0"])
        output: list[str] = []
        FitnessCli(app, lambda prompt: next(queue), output.append).run()
        self.assertIn("Welcome back, Alex!", output)

    def test_requires_login(self):
        output = run_cli(["3"])
        self.assertIn("Error: Please register or log in first.", output)

    def test_unknown_choice(self):
        self.assertIn("Unknown menu item.", run_cli(["42"]))

    def test_bad_number_is_reported(self):
        output = run_cli(["1", "tall"])
        self.assertTrue(any(line.startswith("Error:") for line in output))

    def test_domain_error_is_reported(self):
        output = run_cli(["2", "ghost@mail.com", "whatever1"])
        self.assertIn("Error: Invalid login or password", output)

    def test_main_runs_until_exit(self):
        import contextlib
        import io
        import sys
        from unittest import mock
        import cli
        with mock.patch.object(sys, "stdin", io.StringIO("0\n")), contextlib.redirect_stdout(io.StringIO()) as out:
            cli.main()
        self.assertIn("Goodbye!", out.getvalue())
