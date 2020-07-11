from django.contrib import admin

from .models import Deck, Card, Question, Answer, User, LearningMatrix


class CardAdmin(admin.ModelAdmin):
    list_display = ('front', 'back', 'deck')
    list_filter = ['deck']


admin.site.register(Deck)
admin.site.register(Card, CardAdmin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(User)
admin.site.register(LearningMatrix)
