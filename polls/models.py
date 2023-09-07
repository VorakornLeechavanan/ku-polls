import datetime
from django.db import models
from django.utils import timezone

# Create your models here.


class Question(models.Model):
    """The question as a part of KU Poll"""
    question_text = models.CharField(max_length=250)
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    end_date = models.DateTimeField("date ended", null=True)

    def __str__(self):
        """Set the question name"""
        return self.question_text

    def is_published(self):
        """Check if the question is ready to be published"""
        now = timezone.now()
        return self.pub_date <= now

    def was_published_recently(self):
        """Check whether the publication date is after the previous day or not"""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def can_vote(self):
        """
        Check if the question is between the published date and end date or not.
        If the end date is Null, the function will check only the published date.
        """
        now = timezone.now()
        if self.end_date is None:
            return self.is_published()
        return self.pub_date <= now <= self.end_date


class Choice(models.Model):
    """The choice for each question"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Set the choice name"""
        return self.choice_text

