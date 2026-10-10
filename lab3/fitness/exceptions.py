"""Custom exceptions of the fitness tracker domain."""


class FitnessException(Exception):
    """Base class for all domain errors."""


class InvalidUserDataException(FitnessException):
    """User, profile or account data is invalid."""


class AuthenticationException(FitnessException):
    """Login credentials are wrong or the account is inactive."""


class InvalidMeasurementException(FitnessException):
    """A body, health or GPS measurement is out of range."""


class InvalidWorkoutException(FitnessException):
    """Workout, exercise or activity data is invalid."""


class WorkoutNotFoundException(FitnessException):
    """Requested workout does not exist."""


class InvalidNutritionDataException(FitnessException):
    """Food, meal or recipe data is invalid."""


class GoalNotAchievableException(FitnessException):
    """The goal cannot be reached with the given parameters."""


class DeviceNotConnectedException(FitnessException):
    """The wearable device is disconnected."""


class SubscriptionRequiredException(FitnessException):
    """A feature needs an active subscription or a better plan."""


class ChallengeFullException(FitnessException):
    """The challenge has no free places."""


class TrainerNotAvailableException(FitnessException):
    """The trainer cannot accept clients or sessions."""


class DuplicateEntryException(FitnessException):
    """An entity with the same identity already exists."""


class InvalidContentException(FitnessException):
    """A post, comment or notification has invalid text."""
