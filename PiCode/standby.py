
import requests
import time
import subprocess
import multiprocessing

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import yaml

import RPi.GPIO as GPIO 

###### Motor Control #####
# Define GPIO pins
DIR = 18      # Direction pin
STEP = 16      # Step pin
ENABLE = 12   # Enable pin

# Define directions
CW = 1        # Clockwise
CCW = 0       # Counterclockwise

# Step and speed settings
steps = 200   # 200 steps for 360 degrees
speed = 0.0005 # Speed

# Setup GPIO mode
GPIO.setmode(GPIO.BOARD)

# Setup GPIO pins
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(ENABLE, GPIO.OUT)

# Function to disable motor power
def disable_motor():
    GPIO.output(ENABLE, GPIO.HIGH)  # Disable (or LOW, depending on driver)

# Function to enable motor power
def enable_motor():
    GPIO.output(ENABLE, GPIO.LOW)   # Enable (or HIGH, depending on driver)

def motor_test():
    enable_motor()

    #### Motor control logic
    
    # Set the direction to clockwise and run for 200 steps
    GPIO.output(DIR, CW)
    for x in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(speed)

    # Brief pause and switch direction
    time.sleep(1.0)
    GPIO.output(DIR, CCW)
    for x in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(speed)

    time.sleep(1.0)  # Adjust idle time as needed
    
    disable_motor()
    
    
    #GPIO.cleanup()


# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-web-security")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--guest")
options.add_argument("--kiosk")
options.add_argument("--disable-password-manager-reauthentication")
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches",["enable-automation"])



# Selenium Setup
s = Service('/usr/bin/chromedriver')
browser = webdriver.Chrome(service=s, options=options)


with open('loginDetails.yaml', 'r') as file:
    conf = yaml.safe_load(file)

username = conf['account']['username']
password = conf['account']['password']


#### Credential Setup ####
ROOT_URI = "http://192.168.0.100:8000"
STANDBY_URI = ROOT_URI + "/standby/"

API_ENDPOINT_STATE = ROOT_URI + "/api/rpi-states/1"
API_ENDPOINT_GAMEINSTANCE = ROOT_URI + '/api/games-instances/'
API_ENDPOINT_GAME = ROOT_URI + '/api/games/'
LOGIN_URL = ROOT_URI +  '/accounts/login/'

# Token value (RPiClient User token)
TOKEN = "0828684a73506b61ae2dfa8f0ba0c0f7e02b4208"

# Headers containing the token
HEADERS = {
    "Authorization": f"Token {TOKEN}"
}



'''
def login(url,usernameId, username, passwordId, password, submit_buttonId):
   browser.get(url)
   browser.find_element(By.NAME, usernameId).send_keys(username)
   browser.find_element(By.NAME, passwordId).send_keys(password)
   browser.find_element(By.NAME, submit_buttonId).click()
'''

def login(url, usernameId, username, passwordId, password, submit_buttonId):
    # Open the specified URL
    browser.get(url)
    
    try:
        # Wait for the username field to be visible and enter the username
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.NAME, usernameId))
        ).send_keys(username)
        
        # Wait for the password field to be visible and enter the password
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.NAME, passwordId))
        ).send_keys(password)
        
        # Wait until the submit button is clickable, then click it
        submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.NAME, submit_buttonId))
        )
        
        # Optionally, use JavaScript to click if the element is still not clickable
        browser.execute_script("arguments[0].click();", submit_button)
        
    except Exception as e:
        print(f"An error occurred: {e}")
   
   

def get_pi_status(endpoint,headers):
    '''
    GET request from endpoint and return PI status
    #Return JSON payload data or False if some problem occur
    '''
    try:
        response = requests.get(endpoint , headers=headers)
        if response.status_code == 200:
            # Process the signal received from the API
            pi_status = response.json()
            return pi_status 
        else :
            return False
    except Exception as e:
        print("Error:", e)

def update_pi_status(pi_status, endpoint, headers):
    '''
    PUT request to endpoint 
    return True if update is successful , False otherwise

    '''
    try:
        # Send the PUT request
        response = requests.put(endpoint, json=pi_status, headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print("Error:", e)
        
def get_arbitary_info(endpoint,headers,**kwargs):
    '''
    GET request from endpoint and return information
    # Return JSON payload data or False if some problem occur
    '''
    
    # Use int_key = <integer> as keyword argument to add extra query infomation 
    
    # No specific integer query
    if not kwargs:
        fullendpoint = endpoint
    else:
        fullendpoint = endpoint + str(kwargs["int_key"])
    try:
        response = requests.get(fullendpoint , headers=headers)
        if response.status_code == 200:
            # Process the signal received from the API
            data = response.json()

            return data 
        else :
            return False
    except Exception as e:
        print("Error:", e)

 

gpio_lock = multiprocessing.Lock()

def motor_control():
    
    print('Testing')
    motor_test()
    
    while True:
        #print('Test Motor')
        pi_status = get_pi_status(API_ENDPOINT_STATE,HEADERS)
        if pi_status['motor'] == True:
            enable_motor()
            #### Motor control logic
            
            # Set the direction to clockwise and run for 200 steps
            GPIO.output(DIR, CW)
            for x in range(steps):
                GPIO.output(STEP, GPIO.HIGH)
                time.sleep(speed)
                GPIO.output(STEP, GPIO.LOW)
                time.sleep(speed)

            # Brief pause and switch direction
            time.sleep(1.0)
            GPIO.output(DIR, CCW)
            for x in range(steps):
                GPIO.output(STEP, GPIO.HIGH)
                time.sleep(speed)
                GPIO.output(STEP, GPIO.LOW)
                time.sleep(speed)

            time.sleep(1.0)  # Adjust idle time as needed
            
            disable_motor()
            
        elif pi_status['motor'] == False:
            disable_motor()  # Ensure motor is disabled
        time.sleep(0.250) # Wait 0.25 second

def monitor_close_game():
    while True:
        pi_status = get_pi_status(API_ENDPOINT_STATE,HEADERS)
        if pi_status['stop_game'] == True:
            HOME_PAGE = STANDBY_URI
            browser.get(HOME_PAGE)
            
            pi_status['stop_game'] = False
            pi_status['start_game'] = False
            pi_status['is_occupied'] = False
            pi_status['game_instance_running'] = None
            
            update_pi_status(pi_status, API_ENDPOINT_STATE, HEADERS)
        time.sleep(3)
        

def main_standby():
    
    #Start by standby page
    browser.get(STANDBY_URI)
    
    while True:
        pi_status = get_pi_status(API_ENDPOINT_STATE,HEADERS)
        #print(pi_status)
        if pi_status:
            if pi_status['is_occupied'] == True:
                print('Game is running')
                time.sleep(30)
                continue
            # STATE : Start game signal : from user
            elif(pi_status['is_occupied'] == False) and(pi_status['start_game'] == True):
                
                # Find out which game it is : check from gameinstance API
        
                gameinstance_data = get_arbitary_info(API_ENDPOINT_GAMEINSTANCE,HEADERS,int_key = pi_status['game_instance_running'])
                game_id = gameinstance_data["game"]
                
                if game_id == 1: # Fixation_Task
                    GAME_URI = ROOT_URI + f"/game/fixation/{str(pi_status['game_instance_running'])}"
                
                #open_chromium_kiosk(GAME_URL)
                browser.get(GAME_URI)
                # update status and switch to game running mode
                pi_status['start_game'] = False
                pi_status['is_occupied'] = True
                update_pi_status(pi_status, API_ENDPOINT_STATE,HEADERS)
            else:
                print('Standby....')
                time.sleep(5)
        else :
            # Further work: False to request from API 
            print('Something wrong with the server, or authentecation failed')

def main():
    try:
        main_start = multiprocessing.Process(name="main_standby", target = main_standby, args = ())
        ctx = multiprocessing.get_context("fork")  # Use "fork" for compatibility
        pump_motor = multiprocessing.Process(target=motor_control, args=())
        pump_motor = ctx.Process(target=motor_control)
        close_game = multiprocessing.Process(name="monitor_close_game", target = monitor_close_game, args = ())
        main_start.start()
        pump_motor.start()
        pump_motor.join()
        close_game.start()
    except KeyboardInterrupt:
        print('Stopping motor...')
    finally:
        disable_motor()  # Ensure motor is disabled
        GPIO.cleanup()



if __name__ == "__main__":
    login(LOGIN_URL, "username", username, "password", password, "submit")
    main()
