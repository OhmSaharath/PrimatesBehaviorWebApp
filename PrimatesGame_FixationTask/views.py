from django.shortcuts import render
from PrimatesGameAPI.models import RPiBoards, RPiStates, Primates, Games, GameInstances ,GameConfig, FixationGameConfig , Reports , FixationGameReport , FixationGameResult
from django.http import Http404
from django.http import HttpRequest , HttpResponse

# Create your views here
def game_view(request, gameinstance):
    try:
    # Using get() to retrieve a single object
        gameinstance_id = GameInstances.objects.get(id=gameinstance)
        print(gameinstance_id)
    except :
        raise Http404("Gameinstance does not exist")
    
    
    return render(request, "fixation.html")


def fixationtask_signal_response(request, gameinstance):
    
    try:
        # get gameinstance object 
        gameinst =  GameInstances.objects.get(pk=gameinstance)
        
        # Get info
        rpiboard_id = gameinst.rpiboard.pk
        try : 
            # get rpi state
            rpi_state = RPiStates.objects.get(rpiboard=rpiboard_id)
            
        except RPiStates.DoesNotExist:
            raise Http404("No RPiStates matches the given query.")
        
        print('here')
        rpi_state.gp17 = True
        rpi_state.save()
        # For simplicity, let's just print a message
        print("button press")
        
        return HttpResponse("Signal received")
        
        
    except GameInstances.DoesNotExist:
        raise Http404("No GameInstances matches the given query.")