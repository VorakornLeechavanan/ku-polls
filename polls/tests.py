import datetime
from .models import Question, Choice, Vote
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
# Create your tests here.


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class IsPublishedTests(TestCase):

    def test_is_published_no_future_question(self):
        """
        No future question will be visible in the index page.
        """
        question1 = create_question(question_text="First Future question.",
                                    days=1)
        question2 = create_question(question_text="Second Future question.",
                                    days=10)
        self.assertFalse(question1.is_published(), question2.is_published())

    def test_is_published_past_questions(self):
        """
        Past question is possible to be visible in the index page.
        """
        question1 = create_question(question_text="First Past question.",
                                    days=-1)
        question2 = create_question(question_text="Second Past question.",
                                    days=-10)
        self.assertTrue(question1.is_published(), question2.is_published())

    def test_is_published_turn_past_into_future_question(self):
        """
        If the question published date has been modified from past to future,
        is_published must return False.
        """
        question = create_question(question_text="Question", days=-1)
        self.assertTrue(question.is_published())
        time = timezone.now() + datetime.timedelta(days=1)
        question.pub_date = time
        question.save()
        self.assertFalse(question.is_published())

    def test_is_published_turn_future_into_past_question(self):
        """
        If the question published date has been modified from future to past,
        is_published must return True.
        """
        question = create_question(question_text="Question", days=1)
        self.assertFalse(question.is_published())
        time = timezone.now() + datetime.timedelta(days=-1)
        question.pub_date = time
        question.save()
        self.assertTrue(question.is_published())

    def test_is_published_default_pub_date_question(self):
        """
        Default published date question must be displayed in the detail page
        """
        question = Question(question_text="Question")
        self.assertTrue(question.is_published())


class CanVoteTests(TestCase):

    def test_can_vote_between_start_and_end_date(self):
        """
        The available questions must be in between
        the range of start date and end date.
        """
        question1 = Question(
            pub_date=timezone.now() - timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=1)
        )
        question2 = Question(
            pub_date=timezone.now() - timezone.timedelta(days=2),
            end_date=timezone.now() - timezone.timedelta(days=1)
        )
        self.assertTrue(question1.can_vote())
        self.assertFalse(question2.can_vote())

    def test_can_vote_without_end_date(self):
        """
        The available questions must be in between
        the range of start date and end date.
        """
        question1 = Question(
            pub_date=timezone.now() - timezone.timedelta(days=1)
        )
        question2 = Question(
            pub_date=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertTrue(question1.can_vote())
        self.assertFalse(question2.can_vote())

    def test_can_vote_in_current_time(self):
        """
        The index page must show the question with current published time.
        """
        question1 = Question(pub_date=timezone.now())
        question2 = Question(
            pub_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertTrue(question1.can_vote(), question2.can_vote())

    def test_can_not_vote_future_question(self):
        """
        No future question will be visible in the index page.
        """
        question = Question(
            pub_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=2)
        )
        self.assertFalse(question.can_vote())


class Authentication(TestCase):

    def test_authentication_logged_in_user_can_vote(self):
        """
        Test that user can submit his/her desired choice in the application
        """
        user = User.objects.create_user(username='mandatory',
                                        password='NotMandatory')
        question = create_question("Question", days=0)
        choice = Choice.objects.create(choice_text="Choice", question=question)
        self.client.login(username='mandatory', password='NotMandatory')
        self.client.post(reverse('polls:vote', args=[question.pk]),
                         {'choice': choice.pk})
        vote = Vote.objects.get(user=user, choice__question=question)
        self.assertEqual(vote.choice, choice)

    def test_authentication_user_redo_the_question(self):
        """
        Test the updating after a user redo the question and
        submit new choice.
        """
        user = User.objects.create_user(username='mandatory2',
                                        password='NotMandatory')
        question = create_question("Question", days=0)
        choice = Choice.objects.create(choice_text="Choice", question=question)
        choice2 = Choice.objects.create(choice_text="Choice 2",
                                        question=question)
        self.client.login(username='mandatory2', password='NotMandatory')
        self.client.post(reverse('polls:vote', args=[question.pk]),
                         {'choice': choice.pk})
        vote = Vote.objects.get(user=user, choice__question=question)
        self.assertEqual(vote.choice, choice)
        self.assertNotEqual(vote.choice, choice2)
        self.assertEqual(choice.votes, 1)
        self.assertEqual(choice2.votes, 0)
        self.client.post(reverse('polls:vote', args=[question.pk]),
                         {'choice': choice2.pk})
        vote2 = Vote.objects.get(user=user, choice__question=question)
        self.assertNotEqual(vote2.choice, choice)
        self.assertEqual(vote2.choice, choice2)
        self.assertEqual(choice.votes, 0)
        self.assertEqual(choice2.votes, 1)
