
from django.contrib import admin
from .models import RPiBoards, RPiStates,Primates, Games, GameInstances, GameConfig, FixationGameConfig ,Reports , FixationGameReport , FixationGameResult

# Register your models here.
admin.site.register(RPiBoards)
admin.site.register(RPiStates)
admin.site.register(Primates)
admin.site.register(Games)
admin.site.register(GameInstances)
admin.site.register(GameConfig)
admin.site.register(FixationGameConfig)
admin.site.register(Reports)
admin.site.register(FixationGameReport)
admin.site.register(FixationGameResult)

