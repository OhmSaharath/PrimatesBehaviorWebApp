from django.shortcuts import render
from datetime import datetime
from PrimatesGameAPI.models import RPiBoards , Primates , Games , RPiStates , GameInstances , GameConfig, FixationGameConfig, Reports, FixationGameReport, FixationGameResult
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from PrimatesGameAPI.permissions import IsResearcher , IsRPiClient , IsAdmin ,  IsResearcherOrAdmin 
from django.http import JsonResponse
from django.utils import timezone, dateformat
import requests
from django.urls import reverse
from django.http import HttpResponse


# Create your views here.
@api_view(['POST'])
@permission_classes([IsRPiClient])
def response_game_RFID(request):
    '''
    Start by RFID tag
    Step of this view
    1. Recieve RFID tag from RPI via API.
    2. Extract RFID tag
    3. Get a primate information from database
    4. Get default parameters from Fixation tasks (The taks will run in fix order, current task information will be stored in Primates model (TODO))'
    '''
    if request.method == "POST":
        # Extract tag
        RFID_tag = request.POST.get('tag')
        # Get device name
        device_name = request.POST.get('device_name')
        print(RFID_tag)
        # Get primate information form model
        primate = Primates.objects.get(rfid_tag=RFID_tag)
        
        primate_isAvailable = primate.is_occupied
        primate_gameinstance = primate.game_instance
        
        # Get Board Info
        rpiboard = RPiBoards.objects.get(board_name=device_name)

        
        # Get RPI State status
        rpi_state = RPiStates.objects.get(rpiboard=rpiboard)
        
        # if primate has not been registered
        #### Call view to show that primate is not registered -> show HTML page (TODO)
        
        #print(primate.name)
        
        # if primate is not occupied and board is available mean that it signal to start the game-> Check game instance 
        if (primate_isAvailable == False) and rpi_state.is_occupied == False:
            # CASE 1 : Check if gameinstance is exits -> if None -> start from Fixation task
            if primate_gameinstance == None:
                # Create new gameinstance
                game = Games.objects.get(name="Fixation_Task")
                report = Reports.objects.get(game=game)
                config = GameConfig.objects.get(gameid=game)
                
                # Create gameinstancename
                date_time = timezone.now()
                str_timezone = timezone.localtime(date_time).strftime("%Y-%m-%d_%H-%M")
                primate_name = primate.name
                game_name = game.name
                # Create Gamereportname
                gameinstance_name = game_name + '_' +  primate_name + '_' + str_timezone
                
                gameinstance_data = {
                'name' : gameinstance_name,
                'rpiboard': rpiboard.id,
                'primate': primate.id,
                'game': game.id,
                'config' : config.id,
                'login_hist' : str(datetime.now())
                }
                
                print(gameinstance_data)
                print(rpiboard.token)
                
                # Set up the request headers with the token
                headers = {
                    'Authorization': f'Token {rpiboard.token}',
                    'Content-Type': 'application/json'  # Adjust content type if necessary
                }
                # POST to /api/games-instances
                instance_url = request.build_absolute_uri(reverse('api:game-instance'))
                print(gameinstance_data)
                # Make a POST request to your API endpoint
                # Send the POST request with the data and headers
                response_gameinstance = requests.post(instance_url, json=gameinstance_data, headers=headers)
                
                ###### game instance created successfully #######
                if response_gameinstance.status_code == 201:
                    
                    ####### Initialize game configuration  ########
                    #print(response.json())
                    # Access the ID of the newly created instance from the response
                    game_instance_id = response_gameinstance.json().get('id')
                    game_configtype_id = response_gameinstance.json().get('config')
                    
                    ### This section depends on configuration type ###
                    
                    if game_configtype_id == 1: ## FixationGameConfig
                        # Default parameters are stored in model.
                        
                        # Create gameconfig data
                        gameconfig_data = {
                        'configtype': game_configtype_id,
                        'instance': game_instance_id,
                        }
                        
                        # POST to /api/fixationconfigs
                        config_url = request.build_absolute_uri(reverse('api:fixationconfigs'))
                        
                    # POST new gameconfig
                    response_gameconfig = requests.post(config_url, json=gameconfig_data, headers=headers)
                        
                    if response_gameconfig.status_code == 201:
                        ######### Initilize Report instance #########
                        date_time = timezone.now()
                        str_timezone = timezone.localtime(date_time).strftime("%Y-%m-%d_%H-%M")
                        #formatted_date = dateformat.format(
                        #                timezone.localtime(timezone.now()),
                        #               'Y-m-d H:i:s',
                        #                )
                        
                        primate_name = primate.name
                        report_name = report.reportname
                        
                        # Create Gamereportname
                        gamereportname = report_name + '_' +  primate_name + '_' + str_timezone
                        
                        report_instance_data  = {
                            'report': report.id,
                            'instance': game_instance_id,
                            'gamereportname': gamereportname
                            }
                        
                        ### Report instance also depends on record type
                        if report.id == 1: # FixationGameRecord
                            # POST to /api/fixationgamreport
                            report_url = request.build_absolute_uri(reverse('api:fixationgamreport'))
                            #print(url)
                        
                        response_report = requests.post(report_url, json=report_instance_data, headers=headers)
                        
                        if response_report.status_code == 201:
                            # GameReport Created succesfully
                            ################## Invoking the RPI board by updating model ###############
                            # send a signal to start a game on target RPI board
                            
                            # get the state of the target RPI board
                            # Replace `pk_value` with the actual primary key value you want to retrieve
                            
                            # If all process completed -> update status
                            
                            # Flag signal to start the game
                            rpi_state.is_occupied = False
                            rpi_state.start_game = True  
                            rpi_state.game_instance_running = game_instance_id  
                            rpi_state.save()
                            
                            #Update Primate Status -> Use Django
                            primate.is_occupied = True
                            primate.save()
                            
                            # Response Message
                            return JsonResponse({'message': 'Created Fixation Task for' + RFID_tag}) # placeholder
                        elif response_report.status_code == 401:
                            return JsonResponse({'errors': 'Unauthorized'})
                        else:
                            print("Something wrong when creating gamerecord")
                            return JsonResponse({'errors': "Something wrong when creating gamerecord"})
                    # GameConfig Created Failed
                    elif response_gameconfig.status_code == 401:
                        return JsonResponse({'errors': 'Unauthorized'})
                    else:
                        print("Something wrong when creating gameconfiguration")
                        return JsonResponse({'errors': 'Something wrong when creating gameconfiguration'})
                # Gameinstance Created Failed
                elif response_gameinstance.status_code == 401:
                    return JsonResponse({'errors': 'Unauthorized'})
                else:
                    print("Something wrong when creating gameinstance")
                    return JsonResponse({'errors': 'Something wrong when creating gameinstance'})           
        # Tag coming the game is running mean that it signal to stop the game
        elif (primate_isAvailable == True) and (rpi_state.is_occupied == True):
            # Get gameinstance info
            game_instance_id = rpi_state.game_instance_running
            
            # GameInstance -> Update logout record
            game_instance = GameInstances.objects.get(id=game_instance_id)
            game_instance.logout_hist = datetime.now()
            game_instance.save()
            
            # Primate -> is_occupied = False
            primate.is_occupied = False
            primate.save()
            
            # Send signal to stop game at client RPI
            rpi_state.stop_game = True
            rpi_state.save()
            return JsonResponse({'message': 'Close experiment for' + RFID_tag}) # placeholder
            

    return HttpResponse("This is not a POST request") # Placeholder

    
    