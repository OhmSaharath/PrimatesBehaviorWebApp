from django.shortcuts import render
from PrimatesGameAPI.models import RPiBoards, RPiStates, Primates, Games, GameInstances ,GameConfig, FixationGameConfig , Reports , FixationGameReport , FixationGameResult
from django.http import Http404
from django.http import HttpRequest , HttpResponse
from django.http import JsonResponse
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

def get_game_config(request,gameinstance):
    try:
        game_instance = GameInstances.objects.get(id=gameinstance)
        config = FixationGameConfig.objects.get(instance=game_instance)
        if config:
            return JsonResponse({
                'interval_correct': config.interval_correct,
                'interval_incorrect': config.interval_incorrect,
                'interval_absent': config.interval_absent,
            })
        else:
            return JsonResponse({
                'interval_correct': 2,
                'interval_incorrect': 5,
                'interval_absent': 60
            })  # Default values if no config is found
    except GameInstances.DoesNotExist:
        return JsonResponse({'error': 'Game instance not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)