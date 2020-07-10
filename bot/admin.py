from django.contrib import admin

from .models import Deck, Card, Question, Answer, User, LearningMatrix

admin.site.register(Deck)
admin.site.register(Card)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(User)
admin.site.register(LearningMatrix)