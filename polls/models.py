import datetime
from django.db import models
from django.utils import timezone

# Create your models here.


class Question(models.Model):
    """The question as a part of KU Poll"""
    question_text = models.CharField(max_length=250)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        """Set the question name"""
        return self.question_text

    def was_published_recently(self):
        """Check whether the publication date is after the previous day or not"""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    """The choice for each question"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Set the choice name"""
        return self.choice_text
