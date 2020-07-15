from django.db import models
from django.db.models import DateTimeField, IntegerField


class Deck(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title


class Card(models.Model):
    deck = models.ForeignKey('Deck', on_delete=models.SET_NULL, related_name='cards', blank=True, null=True)
    front = models.TextField()
    back = models.TextField()

    def __str__(self):
        return self.front


class Question(models.Model):
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    BUTTON = 'BTN'
    TEXT = 'TXT'
    TYPE_CHOICES = [
        (BUTTON, 'Button'),
        (TEXT, 'Text'),
    ]
    type = models.CharField(
        max_length=3,
        choices=TYPE_CHOICES,
        default=TEXT,
    )

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')
    correct = models.NullBooleanField(blank=True)
    text = models.TextField()

    def __str__(self):
        return self.text


class User(models.Model):
    user_id = models.CharField(max_length=255, primary_key=True)
    last_interaction_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_id


class LearningMatrix(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user')
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='card')
    deck_title = models.CharField(max_length=255)
    last_shown = DateTimeField()
    show_after = DateTimeField()
    show_count = IntegerField()
    easy_count = IntegerField()
    hard_count = IntegerField()

    class Meta:
        unique_together = [['user', 'card']]

        indexes = [
            models.Index(fields=['user', 'card']),
        ]

    def __str__(self):
        return f"{self.user} {self.card}"


class ShownQuestion(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    card = models.ForeignKey('Card', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='question')

    class Meta:
        unique_together = [['user', 'card']]

        indexes = [
            models.Index(fields=['user', 'card']),
        ]

    def __str__(self):
        return f"{self.user} {self.question}"
