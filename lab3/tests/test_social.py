import unittest
from datetime import timedelta

from fitness.exceptions import (
    ChallengeFullException, DuplicateEntryException, InvalidContentException, InvalidUserDataException,
)
from fitness.social import ActivityFeed, ActivityPost, Challenge, Comment, FriendRequest, Leaderboard
from tests.factories import NOW, TODAY, make_user

ALEX, BOB, CARA = make_user(1, "Alex"), make_user(2, "Bob"), make_user(3, "Cara")


def make_challenge(max_participants: int = 3) -> Challenge:
    return Challenge("Steps", TODAY, TODAY + timedelta(days=7), max_participants)


class FriendRequestTest(unittest.TestCase):
    def test_accept_and_decline(self):
        request = FriendRequest(ALEX, BOB, TODAY)
        self.assertTrue(request.is_pending())
        request.accept()
        self.assertEqual(request.status, "accepted")
        with self.assertRaises(InvalidUserDataException):
            request.accept()
        other = FriendRequest(ALEX, CARA, TODAY)
        other.decline()
        self.assertEqual(other.status, "declined")
        with self.assertRaises(InvalidUserDataException):
            other.decline()


class ChallengeTest(unittest.TestCase):
    def test_join_and_score(self):
        challenge = make_challenge()
        self.assertIsNone(challenge.winner())
        challenge.join(ALEX)
        challenge.join(BOB)
        challenge.record_score(BOB, 50.0)
        challenge.record_score(ALEX, 20.0)
        self.assertTrue(challenge.has_participant(ALEX))
        self.assertEqual(challenge.winner(), BOB)
        self.assertTrue(challenge.is_active(TODAY))
        self.assertFalse(challenge.is_active(TODAY + timedelta(days=8)))

    def test_errors(self):
        challenge = make_challenge(1)
        challenge.join(ALEX)
        self.assertTrue(challenge.is_full())
        with self.assertRaises(ChallengeFullException):
            challenge.join(BOB)
        roomy = make_challenge()
        roomy.join(ALEX)
        with self.assertRaises(DuplicateEntryException):
            roomy.join(ALEX)
        with self.assertRaises(InvalidUserDataException):
            roomy.record_score(CARA, 1.0)


class LeaderboardTest(unittest.TestCase):
    def test_ranking(self):
        challenge = make_challenge()
        for user, points in ((ALEX, 10.0), (BOB, 30.0), (CARA, 20.0)):
            challenge.join(user)
            challenge.record_score(user, points)
        board = Leaderboard(challenge)
        self.assertEqual([user.name for user, _ in board.ranking()], ["Bob", "Cara", "Alex"])
        self.assertEqual(board.position_of(CARA), 2)
        self.assertEqual(len(board.top(2)), 2)

    def test_unknown_member(self):
        with self.assertRaises(InvalidUserDataException):
            Leaderboard(make_challenge()).position_of(ALEX)


class FeedTest(unittest.TestCase):
    def test_comment(self):
        comment = Comment(BOB, "Great job!", NOW)
        comment.validate()
        self.assertEqual(comment.preview(5), "Great...")
        self.assertEqual(comment.preview(50), "Great job!")
        for text in ("   ", "x" * 300):
            with self.assertRaises(InvalidContentException):
                Comment(BOB, text, NOW).validate()

    def test_post(self):
        post = ActivityPost(ALEX, "Ran 5k today", NOW)
        post.validate()
        post.like(BOB)
        post.like(BOB)
        post.like(CARA)
        post.unlike(CARA)
        self.assertEqual(post.like_count(), 1)
        post.add_comment(Comment(BOB, "Nice", NOW))
        self.assertEqual(len(post.comments), 1)
        with self.assertRaises(InvalidContentException):
            post.add_comment(Comment(BOB, "", NOW))
        with self.assertRaises(InvalidContentException):
            ActivityPost(ALEX, "", NOW).validate()

    def test_feed(self):
        feed = ActivityFeed()
        old = ActivityPost(ALEX, "old", NOW - timedelta(days=1))
        new = ActivityPost(BOB, "new", NOW)
        feed.publish(old)
        feed.publish(new)
        self.assertEqual(feed.latest(1), [new])
        self.assertEqual(feed.posts_by(ALEX), [old])
        with self.assertRaises(InvalidContentException):
            feed.publish(ActivityPost(ALEX, " ", NOW))
