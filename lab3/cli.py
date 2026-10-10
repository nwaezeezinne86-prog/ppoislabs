"""Console interface for the fitness tracker. Contains no domain logic."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Callable

from fitness.activities import Running
from fitness.app import FitnessApp
from fitness.constants import DAYS_PER_WEEK
from fitness.exceptions import FitnessException
from fitness.exercises import Exercise, Workout, WorkoutSet
from fitness.goals import WeightGoal
from fitness.nutrition import Food, Meal
from fitness.social import Challenge
from fitness.users import User, UserProfile

MENU = """
=== Fitness Tracker ===
1. Register user
2. Log in
3. Log strength workout
4. Log run
5. Log meal
6. Set weight goal
7. Weekly report
8. Create and join challenge
9. Show leaderboard
0. Exit
> """
EXIT_CHOICE = "0"
DEFAULT_CHALLENGE_DAYS = 30
NOT_LOGGED_IN = "Please register or log in first."


class FitnessCli:
    """Menu loop that talks to FitnessApp through injected input and output."""

    def __init__(self, app: FitnessApp, read: Callable[[str], str] = input,
                 write: Callable[[str], None] = print) -> None:
        self.app = app
        self.read = read
        self.write = write
        self.current_user: User | None = None
        self.handlers = {
            "1": self.register, "2": self.login, "3": self.log_workout, "4": self.log_run,
            "5": self.log_meal, "6": self.set_goal, "7": self.weekly_report,
            "8": self.create_challenge, "9": self.show_leaderboard,
        }

    def run(self) -> None:
        choice = self.read(MENU).strip()
        while choice != EXIT_CHOICE:
            self.dispatch(choice)
            choice = self.read(MENU).strip()
        self.write("Goodbye!")

    def dispatch(self, choice: str) -> None:
        handler = self.handlers.get(choice)
        if handler is None:
            self.write("Unknown menu item.")
            return
        try:
            handler()
        except (FitnessException, ValueError) as error:
            self.write(f"Error: {error}")

    def ask(self, prompt: str) -> str:
        return self.read(prompt + ": ").strip()

    def require_user(self) -> User:
        if self.current_user is None:
            raise FitnessException(NOT_LOGGED_IN)
        return self.current_user

    def register(self) -> None:
        profile = UserProfile(float(self.ask("Height, cm")), float(self.ask("Weight, kg")),
                              self.ask("Gender (male/female)"))
        user = self.app.register_user(self.ask("Name"), self.ask("Email"),
                                      date.fromisoformat(self.ask("Birth date YYYY-MM-DD")),
                                      self.ask("Password"), profile, datetime.now())
        self.current_user = user
        self.write(f"Registered {user.name} with id {user.user_id}.")

    def login(self) -> None:
        self.current_user = self.app.login(self.ask("Email"), self.ask("Password"))
        self.write(f"Welcome back, {self.current_user.name}!")

    def log_workout(self) -> None:
        user = self.require_user()
        exercise = Exercise(self.ask("Exercise name"), self.ask("Muscle group"),
                            float(self.ask("Calories per minute")), int(self.ask("Difficulty 1-5")))
        exercise.validate()
        workout_set = WorkoutSet(exercise, int(self.ask("Reps")), float(self.ask("Weight, kg")),
                                 int(self.ask("Rest, seconds")))
        workout = Workout(len(self.app.workouts[user.user_id]) + 1, exercise.name, date.today(),
                          int(self.ask("Duration, minutes")))
        workout.add_set(workout_set)
        self.app.log_workout(user, workout, datetime.now())
        self.write(f"Workout saved. Calories: {workout.calories_burned():.0f}")

    def log_run(self) -> None:
        user = self.require_user()
        run = Running(len(self.app.activities[user.user_id]) + 1, user, datetime.now(),
                      float(self.ask("Duration, minutes")), float(self.ask("Distance, km")))
        self.app.log_activity(user, run, datetime.now())
        self.write(f"Run saved. Pace: {run.pace_min_per_km():.2f} min/km")

    def log_meal(self) -> None:
        user = self.require_user()
        meal = Meal(self.ask("Meal type (breakfast/lunch/dinner/snack)"), datetime.now())
        meal.add_food(Food(self.ask("Food name"), float(self.ask("Calories")), float(self.ask("Protein, g")),
                           float(self.ask("Carbs, g")), float(self.ask("Fat, g"))))
        self.app.log_meal(user, meal)
        self.write(f"Meal saved: {meal.total_calories():.0f} kcal")

    def set_goal(self) -> None:
        user = self.require_user()
        today = date.today()
        goal = WeightGoal(len(self.app.achievements[user.user_id].goals) + 1, "Target weight",
                          float(self.ask("Target weight, kg")), today + timedelta(days=int(self.ask("Days to reach"))),
                          user, user.profile.weight_kg, user.profile.weight_kg)
        self.app.add_goal(user, goal, today)
        self.write(f"Goal set. Required change per week: {goal.required_weekly_change(today):+.2f} kg")

    def weekly_report(self) -> None:
        user = self.require_user()
        today = date.today()
        report = self.app.weekly_report(user, today - timedelta(days=DAYS_PER_WEEK), today)
        self.write(f"Workouts: {report.total_workouts()}, calories: {report.total_calories():.0f}, "
                   f"distance: {report.total_distance_km():.1f} km")

    def create_challenge(self) -> None:
        user = self.require_user()
        today = date.today()
        name = self.ask("Challenge name")
        self.app.create_challenge(Challenge(name, today, today + timedelta(days=DEFAULT_CHALLENGE_DAYS)))
        self.app.join_challenge(name, user)
        self.write(f"Challenge {name} created and joined.")

    def show_leaderboard(self) -> None:
        board = self.app.leaderboard(self.ask("Challenge name"))
        for place, (member, score) in enumerate(board.ranking(), start=1):
            self.write(f"{place}. {member.name}: {score:.0f}")


def main() -> None:
    FitnessCli(FitnessApp()).run()


if __name__ == "__main__":
    main()
