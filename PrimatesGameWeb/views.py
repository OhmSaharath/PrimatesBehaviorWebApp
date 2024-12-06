from django.shortcuts import render , redirect
from .forms import PrimatesForm , UserUpdateForm , StartGameForm
from django.urls import reverse
from django.http import JsonResponse
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
        "experiments": [{"id":i, "name": rpi_state.rpiboard ,"status": "Running" if rpi_state.is_occupied else "Standby"} for i,rpi_state in enumerate(rpi_states)],
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
        if form.is_valid():

            
            ##### Create new gameinstance #########
            
            # Get current user in session
            user = User.objects.get(username=request.user)
            
            # Assuming you have already generated a token for the user
            token = Token.objects.get(user=user)

            #Serialize the form data
            
            rpiboard = form.cleaned_data['rpi_name']
            primate = form.cleaned_data['primate_name']
            game = form.cleaned_data['game_name']
            report_id = form.cleaned_data['report_name']
            config = get_config_id(game)

            if config == None:
                raise Http404("Configuration does not exist")
            else:
                pass #### WHAT IS IT -> TO BE CHECkED

            
            data = {
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
            url = request.build_absolute_uri(reverse('api:game-instance'))
            
            # Make a POST request to your API endpoint
            # Send the POST request with the data and headers
            response = requests.post(url, json=data, headers=headers)
            print(primate)
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
                
                data = {
               'configtype': game_configtype_id,
                'instance': game_instance_id,
                'interval_correct': 2,
                'interval_incorrect' : 5,
                'interval_absent' : 60
                }
                
                # POST to /api/games-instances
                url = request.build_absolute_uri(reverse('api:fixationconfigs'))
                print(url)
                
                response = requests.post(url, json=data, headers=headers)
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
                    
                    # POST to /api/games-instances
                    url = request.build_absolute_uri(reverse('api:fixationgamreport'))
                    print(url)
                    
                    response = requests.post(url, json=report_instance_data, headers=headers)
                    
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
                        print(response)
                        return JsonResponse({'errors': 'something wrong'})
                elif response.status_code == 401:
                    return JsonResponse({'errors': 'Unauthorized'})
                else:
                    print(response)
                    return JsonResponse({'errors': 'something wrong'})
                # User is alreay authenthecated, we can now edit the model directly
                
                # Gameinstance created successful
                # GameConFiguration for that instance created successful

                
            # authenthication failed
            elif response.status_code == 401:
                return JsonResponse({'errors': 'Unauthorized'})
            else:
                print(response)
                return JsonResponse({'errors': 'something wrong'})
        else:
            return JsonResponse({'errors': 'something wrong'})
            
    
    
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