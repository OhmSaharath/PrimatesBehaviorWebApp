
from django.contrib import admin
from .models import RPiBoards, RPiStates,Primates, Games, GameInstances, GameConfig, FixationGameConfig

# Register your models here.
admin.site.register(RPiBoards)
admin.site.register(RPiStates)
admin.site.register(Primates)
admin.site.register(Games)
admin.site.register(GameInstances)
admin.site.register(GameConfig)
admin.site.register(FixationGameConfig)
