from django.shortcuts import render , redirect
from .forms import PrimatesForm , UserUpdateForm , StartGameForm, FixationGameConfigForm
from django.urls import reverse
from django.http import JsonResponse
import json
from django.contrib.auth import get_user_model
import requests
from PrimatesGameAPI.models import RPiBoards , Primates , Games , RPiStates , GameInstances , GameConfig, Reports
from django.contrib import messages
from datetime import datetime
from PrimatesGameAPI import views as APIviews
from django.http import HttpRequest , HttpResponse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.http import Http404
from django.utils import timezone, dateformat
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from PrimatesGameAPI.permissions import IsResearcher , IsRPiClient , IsAdmin ,  IsResearcherOrAdmin 
from django.template.loader import render_to_string

# Create your views here.
def home(request):
    rpi_states = RPiStates.objects.all()  # Retrieve all instances of YourModel
    
    # Get all experiments with status 'Running'
    running_experiments = RPiStates.objects.filter(is_occupied=True)
    
    # Check if all statuses are 'Running' (compare count with total experiments)
    all_running = running_experiments.count() == RPiStates.objects.count()
    
    # Get all primates with status 'occupied'
    unavailable_primates = Primates.objects.filter(is_occupied=True)
    
    # Check if all statuses are 'occupied' (compare count with total experiments)
    all_primates_unavailable = unavailable_primates.count() == Primates.objects.count()
    
    data = {
        "cards": [
            {"title": "Card 1", "text": "Content 1", "color": "primary"},
            {"title": "Card 2", "text": "Content 2", "color": "success"},
            {"title": "Card 3", "text": "Content 3", "color": "danger"},
        ],
        "experiments": [{"id":i, "name": rpi_state.rpiboard ,"status": "Running" if rpi_state.is_occupied else "Standby", "instance_name": GameInstances.objects.filter(id=rpi_state.game_instance_running).first(), "instance":rpi_state.game_instance_running} for i,rpi_state in enumerate(rpi_states)],
        "all_running": all_running,
        "all_primates_unavailable" : all_primates_unavailable,
    }
    
    
    #return render(request, "index.html",  {'rpi_states': rpi_states , 'user': request.user})
    return render(request, "index.html",  data)


def primates(request):
    if request.method == 'POST':
        form = PrimatesForm(request.POST)
        if form.is_valid():
            # Serialize the form data
            data = {
                'name': form.cleaned_data['name'],
            }
            
             # URL of the API endpoint
            url = request.build_absolute_uri(reverse('api:primates'))
            
            # Make a POST request to your API endpoint
            response = requests.post(url, data=data)
            if response.status_code == 201:
                # Return True to indicate javascript to process futher
                return JsonResponse({'success': True})
            # authenthication failed
            elif response.status_code == 401:
                return JsonResponse({'errors': 'Unauthorized'})
    else:
        form = PrimatesForm()
    return render(request, 'register-primates.html', {'form': form , 'user': request.user})


def start_game(request):
    '''
    Start the game manually
    Step of this view
    1. Start at start-game.html page, researchers initilizae the game by selecting
        - Raspberry Pi board that's available at the moment
        - Primate 
        - Game Type
        - Config of the game (config will be relative after selecting game, show only config for that game)
    
    
    '''

    def get_config_id(game_id):
        try:
            # Using get() to retrieve a single object
            config = GameConfig.objects.get(gameid=game_id)
            config_id = config.id
        except GameConfig.DoesNotExist:
            config_id = None
        
        return config_id
    
    if request.method == 'POST':
        form = StartGameForm(request.POST)
        config_form = FixationGameConfigForm(request.POST)
        

        if form.is_valid():

            
            ##### Create new gameinstance #########
            
            # Get current user in session
            user = User.objects.get(username=request.user)
            
            # Assuming you have already generated a token for the user
            token = Token.objects.get(user=user)

            #Serialize the form data
            
            print(form)
            
            rpiboard = form.cleaned_data['rpi_name']
            primate = form.cleaned_data['primate_name']
            game = form.cleaned_data['game_name']
            report_id = int(form.cleaned_data['report_name'])
            config = get_config_id(game)

            if config == None:
                raise Http404("Configuration does not exist")
            else:
                pass #### WHAT IS IT -> TO BE CHECkED

            # Create gameinstancename
            date_time = timezone.now()
            str_timezone = timezone.localtime(date_time).strftime("%Y-%m-%d_%H-%M")
            primate_name = Primates.objects.get(id=primate).name
            game_name = Games.objects.get(id=game).name
            # Create Gamereportname
            gameinstance_name = game_name + '_' +  primate_name + '_' + str_timezone
            
            data = {
                'name' : gameinstance_name,
               'rpiboard': rpiboard,
                'primate': primate,
                'game': game,
                'config' : config,
                'login_hist' : str(datetime.now())
            }
            #print(data)
            # Set up the request headers with the token
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json'  # Adjust content type if necessary
            }
            # POST to /api/games-instances
            instance_url = request.build_absolute_uri(reverse('api:game-instance'))
            
            # Make a POST request to your API endpoint
            # Send the POST request with the data and headers
            response = requests.post(instance_url, json=data, headers=headers)
            #print(primate)
            #Update Primate Status -> Use Django
            primate_obj = Primates.objects.get(id=primate)
            primate_obj.is_occupied = True
            primate_obj.save()
            
            ###### game instance created successfully #######
            if response.status_code == 201:
                
                ####### Initialize game configuration  ########
                #print(response.json())
                # Access the ID of the newly created instance from the response
                game_instance_id = response.json().get('id')
                game_configtype_id = response.json().get('config')
                
                ### This section depends on configuration type ###
                
                if game_configtype_id == 1 and config_form.is_valid(): ## FixationGameConfig
                    
                    # Extract Fixation gameconfig
                    
                    interval_correct = config_form.cleaned_data['interval_correct']
                    interval_incorrect = config_form.cleaned_data['interval_incorrect']
                    interval_absent = config_form.cleaned_data['interval_absent']
                    button_holdDuration = config_form.cleaned_data['button_holdDuration']

                
                    #### Hard Code default  FixationGameConfig
                    data = {
                    'configtype': game_configtype_id,
                    'instance': game_instance_id,
                    'interval_correct': interval_correct,
                    'interval_incorrect' : interval_incorrect,
                    'interval_absent' : interval_absent,
                    'button_holdDuration':button_holdDuration # ms
                    }
                    
                    # POST to /api/fixationconfigs
                    config_url = request.build_absolute_uri(reverse('api:fixationconfigs'))
                    #print(url)
                
                
                response = requests.post(config_url, json=data, headers=headers)
                if response.status_code == 201:
                    ######### Initilize Report instance #########
                    date_time = timezone.now()
                    str_timezone = timezone.localtime(date_time).strftime("%Y-%m-%d_%H-%M")
                    #formatted_date = dateformat.format(
                    #                timezone.localtime(timezone.now()),
                     #               'Y-m-d H:i:s',
                    #                )
                    primate =  GameInstances.objects.get(id=game_instance_id).primate
                    
                    primate_name = Primates.objects.get(id=primate.id).name
                    report_name = Reports.objects.get(id=report_id).reportname
                    
                    # Create Gamereportname
                    gamereportname = report_name + '_' +  primate_name + '_' + str_timezone
                    
                    report_instance_data  ={
                        'report': report_id,
                        'instance': game_instance_id,
                        'gamereportname': gamereportname
                        }
                    
                    ### Report instance also depends on record type
                    print(type(report_id))
                    if report_id == 1: # FixationGameRecord
                        # POST to /api/fixationgamreport
                        report_url = request.build_absolute_uri(reverse('api:fixationgamreport'))
                        #print(url)
                    
                    response = requests.post(report_url, json=report_instance_data, headers=headers)
                    
                    if response.status_code == 201:
                        ################## Invoking the RPI board by updating model ###############
                        # send a signal to start a game on target RPI board
                        
                        # get the state of the target RPI board
                        # Replace `pk_value` with the actual primary key value you want to retrieve
                        rpi_state = RPiStates.objects.get(rpiboard=rpiboard)
                        # Flag signal to start the game
                        rpi_state.is_occupied = False
                        rpi_state.start_game = True  
                        rpi_state.game_instance_running = game_instance_id  
                        rpi_state.save()
                        # Redict to dashboard page
                        return redirect('/') # placeholder
                    elif response.status_code == 401:
                        return JsonResponse({'errors': 'Unauthorized'})
                    else:
                        print("Something wrong when creating gamerecord")
                        return JsonResponse({'errors': "Something wrong when creating gamerecord"})
                elif response.status_code == 401:
                    return JsonResponse({'errors': 'Unauthorized'})
                else:
                    print("Something wrong when creating gameconfiguration")
                    return JsonResponse({'errors': 'Something wrong when creating gameconfiguration'})
                # User is alreay authenthecated, we can now edit the model directly
                
                # Gameinstance created successful
                # GameConFiguration for that instance created successful

                
            # authenthication failed
            elif response.status_code == 401:
                return JsonResponse({'errors': 'Unauthorized'})
            else:
                print("Something wrong when creating gameinstance")
                return JsonResponse({'errors': 'Something wrong when creating gameinstance'})
        else:
            print("Something wrong retriveing Form data")
            return JsonResponse({'errors': 'Something wrong retriveing Form data'})
            
    
    
    else:
        form = StartGameForm()
        return render(request, 'start-game.html', {'form': form ,'user': request.user})




def profile(request, username):
    if request.method == 'POST':
        user = request.user
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            user_form = form.save()
            print('test')
            messages.success(request, f'{user_form}, Your profile has been updated!')
            return redirect('webapp:profile', user_form.username)

        for error in list(form.errors.values()):
            print(error)
            messages.error(request, error)

    user = get_user_model().objects.filter(username=username).first()
    if user:
        form = UserUpdateForm(instance=user)
        return render(request, 'profile.html', context={'form': form , 'user': request.user})

    return redirect("")


def standby(request):
    return render(request, "standby.html")

#@csrf_exempt
@csrf_protect
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_games(request):
    if request.method == "POST":
        #data = json.loads(request.body)
        #gameinstance_id = data.get("game_instance")
        game_instance_id = request.data.get("game_instance")
        
        if game_instance_id == None:
            return JsonResponse({"message": "No experiment running!"})
        else: 
        
            # GameInstance -> Update logout record
            game_instance = GameInstances.objects.get(id=game_instance_id)
            game_instance.logout_hist = datetime.now()
            game_instance.save()
            
            
            # Primate -> is_occupied = False
            primate = game_instance.primate
            primate.is_occupied = False
            primate.save()
            
            # RPi State
            rpi_state = RPiStates.objects.get(game_instance_running=game_instance_id)
            rpi_state.stop_game = True
            rpi_state.save()
                # stop_game = True
            
            print(f"Logout {game_instance_id} has been clicked")
            
            # Return success response
            return JsonResponse({"message": "Data received successfully."})
    return JsonResponse({"error": "Invalid request."}, status=400)



def get_game_config_form(request):
    game_type = request.GET.get("game_type")
    # Based on `game_type`, decide which form to return (if different forms are required).
    # id -> string
    # id = 1 : "Fixation_Task"
    if game_type == str(1):  # Adjust condition based on your game types
        form = FixationGameConfigForm()
        form_html = render_to_string("partials/game_config_form.html", {"form": form})
        return JsonResponse({"form_html": form_html})
    else:
        
        return JsonResponse({"form_html": ""})