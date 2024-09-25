from django.shortcuts import render
from PrimatesGameAPI.models import RPiBoards, RPiStates, Primates, Games, GameInstances ,GameConfig, FixationGameConfig , Reports , FixationGameReport , FixationGameResult
from django.http import Http404
from django.http import HttpRequest , HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import json
import pytz
from datetime import datetime
from django.utils.timezone import make_aware, get_current_timezone


# Create your views here
def game_view(request, gameinstance):
    try: 
        gameinstance_id = GameInstances.objects.get(id=gameinstance)
    except:
        raise Http404("Gameinstance does not exist")
   
    try: 
        config = FixationGameConfig.objects.get(instance=gameinstance_id)    
    except:
        raise Http404("Configuration has not been setup yet.")
    print(gameinstance_id)
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
        
        #print('here')
        rpi_state.gp17 = True
        rpi_state.save()
        # For simplicity, let's just print a message
        #print("button press")
        
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
    

@csrf_exempt
def update_report(request, gameinstance):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            
            # Retrieve data from JSON
            timestamp_utc_str = data.get('timestamp')
            area = data.get('area') 
            status = data.get('status')
            is_correct = data.get('isCorrect')  # Boolean value
            
            
            # Convert string timestamp to a datetime object in UTC
            timestamp_utc = datetime.strptime(timestamp_utc_str, '%Y-%m-%dT%H:%M:%S.%fZ')

            # Make it timezone-aware in UTC
            timestamp_utc = make_aware(timestamp_utc, pytz.UTC)

            # Convert the timestamp to Bangkok timezone
            bangkok_tz = pytz.timezone('Asia/Bangkok')
            timestamp_bangkok = timestamp_utc.astimezone(bangkok_tz)
            
            

            # Log received data for debugging (optional)
            print(f"Button data recieved - Timestamp: {timestamp_bangkok}, Area: {area}, Status: {status}, IsCorrect: {is_correct}")
            
            
            # Send a JSON response back to the client
            return JsonResponse({'message': 'Data received and saved successfully!'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    # Return method not allowed if not POST
    return JsonResponse({'error': 'POST request required'}, status=405)
    
    