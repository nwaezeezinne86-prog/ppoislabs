# Лабораторная работа №3 — Приложение для отслеживания фитнеса

Предметная область: **приложение для отслеживания фитнеса** (тренировки, кардио с GPS, пульс и сон,
питание, цели и достижения, соревнования, персональные тренеры, носимые устройства).
Реализация на Python 3.10+, без внешних зависимостей.

## Структура

- `fitness/` — объектная модель предметной области (без ввода-вывода);
- `cli.py` — консольное меню, отделённое от модели (работает через фасад `FitnessApp`);
- `tests/` — unit-тесты (`unittest`);
- `docs/` — документация Sphinx (autodoc);
- `tools/gen_readme_stats.py` — генератор этого файла.

## Запуск

```bash
python cli.py                                   # консольное меню
python -m unittest discover -s tests -t .       # тесты
coverage run -m unittest discover -s tests -t . # покрытие
coverage report --fail-under=90
python tools/gen_readme_stats.py                # перегенерировать README
pip install sphinx && python -m sphinx -b html docs docs/_build/html  # документация
```

Формат строки таблицы: Класс | число полей | число методов | связанные классы.

| Класс | Поля | Методы | Ассоциации (связанные классы) |
|---|---|---|---|
| Account | 4 | 7 | — |
| AchievementManager | 4 | 5 | Badge, Goal, Streak, User |
| ActivityFeed | 1 | 3 | ActivityPost, User |
| ActivityPost | 5 | 5 | Comment, User |
| BMICalculator | 1 | 3 | UserProfile |
| Badge | 4 | 2 | — |
| BodyMeasurement | 4 | 3 | — |
| CalorieCalculator | 1 | 4 | UserProfile, WeightGoal |
| CardioActivity | 6 | 5 | Route, User |
| Challenge | 6 | 6 | User |
| Comment | 3 | 2 | User |
| Cycling | 1 | 2 | CardioActivity |
| Device | 5 | 6 | User |
| DeviceSyncService | 2 | 4 | Device |
| DistanceGoal | 0 | 2 | Goal |
| Exercise | 4 | 3 | — |
| FitnessApp | 9 | 14 | AchievementManager, ActivityFeed, CardioActivity, Challenge, Goal, Meal, NotificationService, NutritionLog, User, UserProfile, Workout |
| Food | 5 | 3 | — |
| FriendRequest | 4 | 3 | User |
| GPSPoint | 4 | 3 | — |
| Goal | 6 | 6 | User |
| HeartRateMonitor | 3 | 7 | Device, HeartRateReading, HeartRateZone |
| HeartRateReading | 2 | 1 | — |
| HeartRateZone | 3 | 1 | — |
| HydrationEntry | 2 | 0 | — |
| HydrationLog | 2 | 4 | HydrationEntry |
| Leaderboard | 1 | 3 | Challenge, User |
| Meal | 3 | 5 | Food |
| MealPlan | 3 | 4 | Meal, User |
| Notification | 4 | 2 | User |
| NotificationService | 1 | 3 | Notification, User |
| NutritionLog | 2 | 4 | Meal, User |
| ProgressAnalyzer | 1 | 4 | Exercise, ProgressReport, Workout |
| ProgressReport | 5 | 5 | CardioActivity, User, Workout |
| Recipe | 4 | 4 | Food, User |
| Reminder | 4 | 4 | User |
| Route | 2 | 4 | GPSPoint |
| Running | 1 | 2 | CardioActivity |
| SleepRecord | 4 | 4 | User |
| StepCounter | 3 | 5 | — |
| Streak | 3 | 3 | — |
| Subscription | 4 | 5 | SubscriptionPlan |
| SubscriptionPlan | 4 | 3 | — |
| Swimming | 2 | 3 | CardioActivity |
| Trainer | 6 | 6 | User |
| TrainingSession | 5 | 5 | Trainer, User |
| User | 8 | 8 | Account, BodyMeasurement, Subscription, UserProfile |
| UserProfile | 4 | 4 | — |
| WeightGoal | 1 | 4 | Goal |
| Workout | 5 | 6 | WorkoutSet |
| WorkoutFrequencyGoal | 1 | 2 | Goal |
| WorkoutPlan | 4 | 4 | Trainer, Workout |
| WorkoutSession | 5 | 5 | HeartRateMonitor, User, Workout |
| WorkoutSet | 4 | 4 | Exercise |

## Подробное описание классов

### Account
Login credentials of a user.
- **Поля:** login, password_hash, created_at, is_active
- **Методы:** hash_password, is_strong_password, create, check_password, authenticate, change_password, deactivate

### AchievementManager
Keeps goals, badges and the streak of one user.
- **Поля:** user, goals, badges, streak
- **Методы:** add_goal, award_badge, total_points, achieved_goals, overdue_goals

### ActivityFeed
Chronological list of posts.
- **Поля:** posts
- **Методы:** publish, posts_by, latest

### ActivityPost
A shared update in the feed.
- **Поля:** author, content, created_at, likes, comments
- **Методы:** validate, like, unlike, like_count, add_comment

### BMICalculator
Body mass index calculations.
- **Поля:** precision
- **Методы:** calculate, category, classify

### Badge
A reward for an achievement.
- **Поля:** name, description, points, earned_on
- **Методы:** award, is_earned

### BodyMeasurement
A dated record of body composition.
- **Поля:** measured_on, weight_kg, body_fat_percent, waist_cm
- **Методы:** validate, fat_mass_kg, lean_mass_kg

### CalorieCalculator
Energy expenditure calculations.
- **Поля:** rounding_digits
- **Методы:** basal_rate, daily_needs, calories_for_weight_change, daily_adjustment

### CardioActivity
A generic cardio session.
- **Поля:** activity_id, user, started_at, duration_minutes, distance_km, route
- **Методы:** intensity_met, validate, average_speed_kmh, pace_min_per_km, calories_burned

### Challenge
A time-boxed competition with points.
- **Поля:** name, start_date, end_date, max_participants, participants, scores
- **Методы:** is_full, is_active, has_participant, join, record_score, winner

### Comment
A reply under a post.
- **Поля:** author, text, created_at
- **Методы:** validate, preview

### Cycling
A bike ride with elevation data.
- **Поля:** elevation_gain_m
- **Методы:** intensity_met, climbing_ratio

### Device
A wearable tracker owned by a user.
- **Поля:** device_id, model, owner, battery_percent, connected
- **Методы:** connect, disconnect, require_connected, drain, charge, needs_charging

### DeviceSyncService
Synchronises all registered devices.
- **Поля:** devices, last_sync
- **Методы:** register, connected_devices, low_battery_devices, sync_all

### DistanceGoal
Cover a total distance in kilometres.
- **Поля:** —
- **Методы:** add_distance, remaining_km

### Exercise
A named movement that trains a muscle group.
- **Поля:** name, muscle_group, calories_per_minute, difficulty
- **Методы:** validate, calories_burned, targets

### FitnessApp
Entry point used by the console interface.
- **Поля:** users, workouts, activities, nutrition_logs, achievements, challenges, notifications, feed, next_user_id
- **Методы:** register_user, find_by_email, find_user, login, log_workout, log_activity, log_meal, add_goal, weekly_report, create_challenge, get_challenge, join_challenge, leaderboard, share_post

### Food
A food item with macronutrients.
- **Поля:** name, calories, protein_g, carbs_g, fat_g
- **Методы:** validate, macro_calories, scaled

### FriendRequest
An invitation to become friends.
- **Поля:** sender, receiver, sent_on, status
- **Методы:** is_pending, accept, decline

### GPSPoint
A geographic position.
- **Поля:** latitude, longitude, altitude_m, timestamp
- **Методы:** validate, distance_to, elevation_change

### Goal
A measurable target with a deadline.
- **Поля:** goal_id, title, target_value, deadline, owner, current_value
- **Методы:** validate, progress_percent, is_achieved, update_progress, days_remaining, is_overdue

### HeartRateMonitor
Collects heart rate readings from a device.
- **Поля:** device, readings, zones
- **Методы:** zones_for_age, record, average_bpm, peak_bpm, resting_bpm, zone_for, readings_in_zone

### HeartRateReading
A single pulse measurement.
- **Поля:** bpm, timestamp
- **Методы:** validate

### HeartRateZone
A named pulse range.
- **Поля:** name, min_bpm, max_bpm
- **Методы:** contains

### HydrationEntry
A glass of water or other drink.
- **Поля:** volume_ml, timestamp
- **Методы:** —

### HydrationLog
Tracks water intake against a daily goal.
- **Поля:** entries, daily_goal_ml
- **Методы:** add_entry, total_on, remaining_on, goal_reached

### Leaderboard
Ranks the participants of a challenge.
- **Поля:** challenge
- **Методы:** ranking, position_of, top

### Meal
Foods eaten together.
- **Поля:** meal_type, eaten_at, foods
- **Методы:** validate, add_food, total_calories, total_protein, macro_split

### MealPlan
Planned meals for a day against a calorie target.
- **Поля:** owner, daily_calorie_target, meals
- **Методы:** add_meal, planned_calories, remaining_calories, is_within_target

### Notification
A message addressed to a user.
- **Поля:** user, message, created_at, read
- **Методы:** mark_read, is_unread

### NotificationService
Stores and delivers notifications.
- **Поля:** queue
- **Методы:** send, unread_for, mark_all_read

### NutritionLog
History of eaten meals for one user.
- **Поля:** user, meals
- **Методы:** log_meal, calories_on, protein_on, average_daily_calories

### ProgressAnalyzer
Compares reports and detects trends.
- **Поля:** trend_threshold
- **Методы:** compare_volume, trend, best_workout, personal_record

### ProgressReport
Summary of a user's activity over a period.
- **Поля:** user, period_start, period_end, workouts, activities
- **Методы:** total_workouts, total_calories, total_volume, total_distance_km, average_workout_minutes

### Recipe
A dish assembled from ingredients.
- **Поля:** title, servings, ingredients, author
- **Методы:** add_ingredient, total_calories, calories_per_serving, to_meal

### Reminder
A scheduled reminder for a workout or meal.
- **Поля:** user, message, remind_at, repeat_daily
- **Методы:** is_due, next_occurrence, snooze, advance

### Route
An ordered track of GPS points.
- **Поля:** name, points
- **Методы:** add_point, point_count, total_distance_km, elevation_gain_m

### Running
A run with cadence data.
- **Поля:** cadence_spm
- **Методы:** intensity_met, estimated_steps

### SleepRecord
One night of sleep.
- **Поля:** user, sleep_start, sleep_end, quality_score
- **Методы:** validate, duration_hours, is_sufficient, quality_label

### StepCounter
Daily step totals.
- **Поля:** steps_by_day, daily_goal, stride_m
- **Методы:** add_steps, steps_on, goal_reached, weekly_total, distance_km

### Streak
Consecutive days with activity.
- **Поля:** current_days, longest_days, last_active
- **Методы:** record_activity, is_active, reset

### Subscription
A plan bought by a user for a period.
- **Поля:** plan, start_date, end_date, auto_renew
- **Методы:** is_active, days_left, ensure_active, renew, cancel_auto_renew

### SubscriptionPlan
A purchasable plan with its feature set.
- **Поля:** name, monthly_price, includes_coaching, max_challenges
- **Методы:** total_price, allows_coaching, allows_challenges

### Swimming
A pool swim counted in laps.
- **Поля:** laps, pool_length_m
- **Методы:** intensity_met, pool_distance_km, laps_per_minute

### Trainer
A personal trainer with a list of clients.
- **Поля:** trainer_id, name, specialization, hourly_rate, is_available, clients
- **Методы:** accept_client, has_client, release_client, session_cost, pause, resume

### TrainingSession
A booked meeting between a trainer and a client.
- **Поля:** trainer, client, scheduled_at, duration_minutes, status
- **Методы:** confirm, cancel, complete, cost, is_upcoming

### User
A registered person who tracks fitness data.
- **Поля:** user_id, name, email, birth_date, account, profile, measurements, subscription
- **Методы:** validate, has_valid_email, age, record_measurement, latest_measurement, weight_change, subscribe, has_active_subscription

### UserProfile
Physical parameters of a user.
- **Поля:** height_cm, weight_kg, gender, activity_level
- **Методы:** validate, height_m, activity_multiplier, update_weight

### WeightGoal
Reach a target body weight.
- **Поля:** start_weight_kg
- **Методы:** validate, progress_percent, is_achieved, required_weekly_change

### Workout
A strength workout made of sets.
- **Поля:** workout_id, name, performed_on, duration_minutes, sets
- **Методы:** validate, add_set, total_volume, calories_burned, muscle_groups, exercise_count

### WorkoutFrequencyGoal
Train a number of times per week.
- **Поля:** sessions_per_week
- **Методы:** register_workout, is_on_track

### WorkoutPlan
A multi-week programme of workouts.
- **Поля:** name, weeks, workouts, author
- **Методы:** add_workout, find_workout, total_sessions, average_duration

### WorkoutSession
A live execution of a workout by a user.
- **Поля:** workout, user, started_at, finished_at, monitor
- **Методы:** begin, finish, is_finished, elapsed_minutes, average_heart_rate

### WorkoutSet
Repetitions of one exercise with a load.
- **Поля:** exercise, reps, weight_kg, rest_seconds
- **Методы:** validate, volume, estimated_one_rep_max, duration_seconds


## Исключения (14)

- `FitnessException` — Base class for all domain errors.
- `InvalidUserDataException` — User, profile or account data is invalid.
- `AuthenticationException` — Login credentials are wrong or the account is inactive.
- `InvalidMeasurementException` — A body, health or GPS measurement is out of range.
- `InvalidWorkoutException` — Workout, exercise or activity data is invalid.
- `WorkoutNotFoundException` — Requested workout does not exist.
- `InvalidNutritionDataException` — Food, meal or recipe data is invalid.
- `GoalNotAchievableException` — The goal cannot be reached with the given parameters.
- `DeviceNotConnectedException` — The wearable device is disconnected.
- `SubscriptionRequiredException` — A feature needs an active subscription or a better plan.
- `ChallengeFullException` — The challenge has no free places.
- `TrainerNotAvailableException` — The trainer cannot accept clients or sessions.
- `DuplicateEntryException` — An entity with the same identity already exists.
- `InvalidContentException` — A post, comment or notification has invalid text.

## Итоговая статистика

| Показатель | Значение | Требование |
|---|---|---|
| Классы | 54 | ≥ 50 |
| Поля | 185 | ≥ 150 |
| Поведения | 219 | ≥ 100 |
| Ассоциации | 76 | ≥ 30 |
| Исключения | 14 | ≥ 12 |
