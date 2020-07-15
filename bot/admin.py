from django.contrib import admin

from .models import Deck, Card, Question, Answer, User, LearningMatrix, ShownQuestion


class CardAdmin(admin.ModelAdmin):
    list_display = ('front', 'back', 'deck')
    list_filter = ['deck']


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question','correct','text')

admin.site.register(Deck)
admin.site.register(Card, CardAdmin)
admin.site.register(Question)
admin.site.register(Answer,AnswerAdmin)
admin.site.register(User)
admin.site.register(LearningMatrix)
admin.site.register(ShownQuestion)
