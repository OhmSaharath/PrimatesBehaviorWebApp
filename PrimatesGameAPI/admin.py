
from django.contrib import admin
from .models import RPiBoards, RPiStates,Primates, Games, GameInstances

# Register your models here.
admin.site.register(RPiBoards)
admin.site.register(RPiStates)
admin.site.register(Primates)
admin.site.register(Games)
admin.site.register(GameInstances)
