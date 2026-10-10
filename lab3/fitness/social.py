"""Friends, challenges, leaderboards and the activity feed."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING

from .constants import DEFAULT_FEED_SIZE, DEFAULT_MAX_PARTICIPANTS, MAX_COMMENT_LENGTH, MAX_POST_LENGTH
from .exceptions import (
    ChallengeFullException, DuplicateEntryException, InvalidContentException, InvalidUserDataException,
)

if TYPE_CHECKING:
    from .users import User

STATUS_PENDING = "pending"
STATUS_ACCEPTED = "accepted"
STATUS_DECLINED = "declined"


@dataclass
class FriendRequest:
    """An invitation to become friends."""

    sender: User
    receiver: User
    sent_on: date
    status: str = STATUS_PENDING

    def is_pending(self) -> bool:
        return self.status == STATUS_PENDING

    def accept(self) -> None:
        if not self.is_pending():
            raise InvalidUserDataException("Request was already answered")
        self.status = STATUS_ACCEPTED

    def decline(self) -> None:
        if not self.is_pending():
            raise InvalidUserDataException("Request was already answered")
        self.status = STATUS_DECLINED


@dataclass
class Challenge:
    """A time-boxed competition with points."""

    name: str
    start_date: date
    end_date: date
    max_participants: int = DEFAULT_MAX_PARTICIPANTS
    participants: list[User] = field(default_factory=list)
    scores: dict[int, float] = field(default_factory=dict)

    def is_full(self) -> bool:
        return len(self.participants) >= self.max_participants

    def is_active(self, today: date) -> bool:
        return self.start_date <= today <= self.end_date

    def has_participant(self, user: User) -> bool:
        return user.user_id in self.scores

    def join(self, user: User) -> None:
        if self.is_full():
            raise ChallengeFullException(f"Challenge {self.name} is full")
        if self.has_participant(user):
            raise DuplicateEntryException(f"{user.name} already joined {self.name}")
        self.participants.append(user)
        self.scores[user.user_id] = 0.0

    def record_score(self, user: User, points: float) -> None:
        if not self.has_participant(user):
            raise InvalidUserDataException(f"{user.name} is not in {self.name}")
        self.scores[user.user_id] += points

    def winner(self) -> User | None:
        if not self.participants:
            return None
        return max(self.participants, key=lambda item: self.scores[item.user_id])


@dataclass
class Leaderboard:
    """Ranks the participants of a challenge."""

    challenge: Challenge

    def ranking(self) -> list[tuple[User, float]]:
        pairs = [(user, self.challenge.scores[user.user_id]) for user in self.challenge.participants]
        return sorted(pairs, key=lambda pair: pair[1], reverse=True)

    def position_of(self, user: User) -> int:
        for position, (member, _) in enumerate(self.ranking(), start=1):
            if member.user_id == user.user_id:
                return position
        raise InvalidUserDataException(f"{user.name} is not on the leaderboard")

    def top(self, count: int) -> list[tuple[User, float]]:
        return self.ranking()[:count]


@dataclass
class Comment:
    """A reply under a post."""

    author: User
    text: str
    created_at: datetime

    def validate(self) -> None:
        if not self.text.strip() or len(self.text) > MAX_COMMENT_LENGTH:
            raise InvalidContentException("Comment is empty or too long")

    def preview(self, length: int) -> str:
        return self.text if len(self.text) <= length else self.text[:length] + "..."


@dataclass
class ActivityPost:
    """A shared update in the feed."""

    author: User
    content: str
    created_at: datetime
    likes: set[int] = field(default_factory=set)
    comments: list[Comment] = field(default_factory=list)

    def validate(self) -> None:
        if not self.content.strip() or len(self.content) > MAX_POST_LENGTH:
            raise InvalidContentException("Post is empty or too long")

    def like(self, user: User) -> None:
        self.likes.add(user.user_id)

    def unlike(self, user: User) -> None:
        self.likes.discard(user.user_id)

    def like_count(self) -> int:
        return len(self.likes)

    def add_comment(self, comment: Comment) -> None:
        comment.validate()
        self.comments.append(comment)


@dataclass
class ActivityFeed:
    """Chronological list of posts."""

    posts: list[ActivityPost] = field(default_factory=list)

    def publish(self, post: ActivityPost) -> None:
        post.validate()
        self.posts.append(post)

    def posts_by(self, user: User) -> list[ActivityPost]:
        return [post for post in self.posts if post.author.user_id == user.user_id]

    def latest(self, count: int = DEFAULT_FEED_SIZE) -> list[ActivityPost]:
        return sorted(self.posts, key=lambda post: post.created_at, reverse=True)[:count]
