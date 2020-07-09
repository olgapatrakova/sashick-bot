from django.db import models
from django.db.models import DateTimeField, IntegerField

class Deck(models.Model):
    title = models.CharField()

    def __unicode__(self):
        return self.title

class Card(models.Model):
    deck = models.ForeignKey('Deck', on_delete=models.CASCADE, related_name='deck')
    front = models.CharField()
    back = models.CharField()

    def __unicode__(self):
        return self.front

class Question(models.Model):
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='card')
    text = models.TextField()
    def __unicode__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='question')
    text = models.TextField()
    type = models.CharField()

    def __unicode__(self):
        return self.text

class User(models.Model):
    name = models.CharField()
    last_interaction_time = DateTimeField()

    def __unicode__(self):
        return self.name

class LearningMatrix(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user')
    deck = models.ForeignKey('Deck', on_delete=models.CASCADE, related_name='deck')
    card = models.CharField()
    last_shown = DateTimeField()
    show_after = DateTimeField()
    show_count = IntegerField()
    easy_count = IntegerField()
    hard_count = IntegerField()

    def __unicode__(self):
        return self.card
