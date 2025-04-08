
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

from utils.PETRFIDReader import *

import logging
import sys


# Configure logging
logging.basicConfig(filename="error_log.txt", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to log uncaught exceptions
def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)  # Allow Ctrl+C exit without logging
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Set global exception handler
sys.excepthook = log_exception


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
    
def turn_motor_CCW(steps,speed):
    enable_motor()

    #### Motor control logic
    
    # Set the direction to ccounter-lockwise and run for 200 steps
    GPIO.output(DIR, CCW)
    for x in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(speed)
    
    disable_motor()
    
def turn_motor_CW(steps,speed):
    enable_motor()

    #### Motor control logic
    
    # Set the direction to clockwise and run for 200 steps
    GPIO.output(DIR, CW)
    for x in range(steps):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(speed)
    
    disable_motor()


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

####3 Device Information
RPI_NUM = "1" # Number of device (Hard Code)
DEVICE_NAME = "Device1"

##### API information
API_ENDPOINT_STATE = ROOT_URI + "/api/rpi-states/" + RPI_NUM
API_ENDPOINT_GAMEINSTANCE = ROOT_URI + '/api/games-instances/'
API_ENDPOINT_GAME = ROOT_URI + '/api/games/'
LOGIN_URL = ROOT_URI +  '/accounts/login/'
API_ENDPOINT_RFID_RESPONSE = ROOT_URI + "/backend/rfid_response/"

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

def post_request(data, endpoint, headers):
    '''
    POST request to endpoint 
    return True if update is successful , False otherwise

    '''
    try:
        # Send the POST request
        response = requests.post(endpoint, data=data, headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print("Error:", e)


gpio_lock = multiprocessing.Lock()

        
def RFID_reader():
    try:
        print("RFID start")
        def tag_callback(reader, tag):
            print(f"[{reader.port}] Tag: {tag}")
            if reader == reader1:
                print("reader1")
            #if reader == reader2:
                #print("reader2")
        reader1 = PETRFIDReader('/dev/ttyACM0', callback=tag_callback)
        #reader2 = PETRFIDReader('COM8', callback=tag_callback)

        
        while True:
            tag = reader1.get_last_tag()
            if tag:
                #print(f"Detected Tag: {tag}")  # Print every time a tag is read
                # You can use the `tag` variable in other parts of your code
                #print("Call API")
                
                data = {
                    "tag": tag,
                    "device_name": DEVICE_NAME
                }
                
                #print(data)
                
                post_request(data, API_ENDPOINT_RFID_RESPONSE, HEADERS)
                
            time.sleep(0.1)  # Small delay to avoid excessive CPU usage
    except Exception as e:
        print(f"RFID Reader Error: {e}")


        

def main_algorithm():
    
    # Web application Response base on RPI state status
    
    #Start by standby page
    browser.get(STANDBY_URI)
    
    while True:
        
        # Receive Raspberrypi state stattus
        pi_status = get_pi_status(API_ENDPOINT_STATE,HEADERS)
        
        #print(pi_status)
        if pi_status:
            
            # CASE0 : Game Running, no motot signal
            if (pi_status['is_occupied'] == True) and (pi_status['stop_game'] == False) and (pi_status['motor'] == False):
                print('Game is running')
                print('Motor off')
                disable_motor()  # Ensure motor is disabled
                time.sleep(0.5)
                continue
            
            # CASE1 : Game Running, receive command to turn motor on
            elif (pi_status['is_occupied'] == True) and (pi_status['stop_game'] == False) and (pi_status['motor'] == True):
                print('Game is running')
                print('Motor on')
                
                # Turn motor once
                turn_motor_CCW(steps,speed)
                
                # stop motor
                pi_status['motor'] = False
                update_pi_status(pi_status, API_ENDPOINT_STATE,HEADERS)
                
                time.sleep(0.5)
                continue
            
            
            # CASE2 : Start game signal (Board is available and recive start game flag == True)
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
                pi_status['motor'] = False
                update_pi_status(pi_status, API_ENDPOINT_STATE,HEADERS)
            
            # CASE3 : Close game signal
            elif (pi_status['is_occupied'] == True) and (pi_status['stop_game'] == True):
                
                STANDBY_PAGE = STANDBY_URI
                browser.get(STANDBY_PAGE)
                
                pi_status['stop_game'] = False
                pi_status['start_game'] = False
                pi_status['is_occupied'] = False
                pi_status['motor'] = False
                pi_status['game_instance_running'] = None
                
                update_pi_status(pi_status, API_ENDPOINT_STATE, HEADERS)

            
            else: # Standby Phase, Make sure motor is disable to conserve energy
                print('Standby....')
                disable_motor()
                time.sleep(0.5)
                continue
        else :
            # Further work: False to request from API 
            print('Something wrong with the server, or authentecation failed')

def main():
    try:
        ctx = multiprocessing.get_context("fork") 
        main_logic = ctx.Process(target=main_algorithm)
        RFID_read = ctx.Process(target=RFID_reader)
        
        main_logic.start()
        RFID_read.start()
        
        main_logic.join()
        RFID_read.join()
        

    except KeyboardInterrupt:
        print('Stopping motor...')
    finally:
        disable_motor()  # Ensure motor is disabled
        GPIO.cleanup()



if __name__ == "__main__":
    login(LOGIN_URL, "username", username, "password", password, "submit")
    main()
