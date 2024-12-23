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
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.urls import reverse
import requests

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
        rpi_state.motor = True
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
                'botton_holdDuration': config.botton_holdDuration,
            })
        else:
            return JsonResponse({
                'interval_correct': 2,
                'interval_incorrect': 5,
                'interval_absent': 60,
                'botton_holdDuration': 2000 # ms
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

            timestamp_utc = pytz.utc.localize(timestamp_utc)  # Make it timezone-aware in UTC

            # Convert the timestamp to Bangkok timezone
            bangkok_tz = pytz.timezone('Asia/Bangkok')
            timestamp_bangkok = timestamp_utc.astimezone(bangkok_tz)
            
            

            # Log received data for debugging (optional)
            print(f"Button data recieved - Timestamp: {timestamp_bangkok}, Area: {area}, Status: {status}, IsCorrect: {is_correct}")
            
            ##### Populate Report #########
            
            # Get current user in session
            user = User.objects.get(username=request.user)
            
            # Assuming you have already generated a token for the user
            token = Token.objects.get(user=user)
            
            # get correct report Id
            fixation_report = FixationGameReport.objects.get(instance=gameinstance)
            fixation_report_id = fixation_report.id
            
            data = {
               'fixationreport': fixation_report_id,
                'timestamp': timestamp_bangkok.isoformat(),
                'feedback': is_correct,
                'feedbacktype' : status,
                'buttonsize' : area
            }
            
            print(data)
            #print(data)
            # Set up the request headers with the token
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json'  # Adjust content type if necessary
            }
            
            # POST to /api/fixationgameresult
            url = request.build_absolute_uri(reverse('api:fixationgameresult'))
            
            # Send the POST request with the data and headers
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 201:
                # Return True to indicate javascript to process futher
                return JsonResponse({'message': 'Data received and POST successfully!'}, status=201)
            # authenthication failed
            elif response.status_code == 401:
                return JsonResponse({'errors': 'Unauthorized'})
            
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
    # Return method not allowed if not POST
    return JsonResponse({'error': 'POST request required'}, status=405)
    
    