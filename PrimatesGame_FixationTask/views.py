from django.shortcuts import render
from PrimatesGameAPI.models import RPiBoards, RPiStates, Primates, Games, GameInstances ,GameConfig, FixationGameConfig , Reports , FixationGameReport , FixationGameResult
from django.http import Http404

# Create your views here
def game_view(request, gameinstance):
    try:
    # Using get() to retrieve a single object
        gameinstance_id = GameInstances.objects.get(id=gameinstance)
        print(gameinstance_id)
    except :
        raise Http404("Gameinstance does not exist")
    
    
    return render(request, "fixation.html")
