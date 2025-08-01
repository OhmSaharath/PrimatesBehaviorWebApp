import json
import threading
import requests
import time
import logging
import sys
import yaml
import RPi.GPIO as GPIO
from websocket import WebSocketApp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.PETRFIDReader import PETRFIDReader

# --- Config & Logging ---
with open('loginDetails.yaml', 'r') as file:
    conf = yaml.safe_load(file)

USERNAME = conf['account']['username']
PASSWORD = conf['account']['password']
ROOT_URI = 'http://192.168.0.100:8000'
STANDBY_URI = ROOT_URI + "/standby/"
WS_URL = f"ws://192.168.0.100:8000/ws/rpi-states/1/"
TOKEN = '0828684a73506b61ae2dfa8f0ba0c0f7e02b4208'
HEADERS = { 'Authorization': f"Token {TOKEN}" }
RPI_NUM = "1" # Number of device (Hard Code)
DEVICE_NAME = "Device1"
API_ENDPOINT_STATE = ROOT_URI + "/api/rpi-states/" + RPI_NUM
API_ENDPOINT_GAMEINSTANCE = ROOT_URI + '/api/games-instances/'
API_ENDPOINT_GAME = ROOT_URI + '/api/games/'
LOGIN_URL = ROOT_URI +  '/accounts/login/'
API_ENDPOINT_RFID_RESPONSE = ROOT_URI + "/backend/rfid_response/"
RFID1 = '/dev/ttyACM0'

logging.basicConfig(
    filename='error_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_exc(t, v, tb):
    if issubclass(t, KeyboardInterrupt):
        sys.__excepthook__(t, v, tb)
        return
    logging.error('Uncaught exception', exc_info=(t,v,tb))
sys.excepthook = log_exc


# --- GPIO Setup ---
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
    
# --- Selenium Setup ---
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
s = Service('/usr/bin/chromedriver')
browser = webdriver.Chrome(service=s, options=options)

def selenium_login(url, usernameId, username, passwordId, password, submit_buttonId):
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


# --- API function ---
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


# --- WebSocket Handlers ---

def on_open(ws):
    logging.info('WS opened')
    ws.send(json.dumps({'type':'identify','rpi_num':RPI_NUM}))

def on_message(ws, msg):
    try:
        state = json.loads(msg)
        logging.debug(state)
    except:
        logging.error('Invalid JSON')
        return

    if (state['is_occupied'] == False) and state['start_game']:
        logging.info('start game')
        # Find out which game it is : check from gameinstance API
        gameinstance_data = get_arbitary_info(API_ENDPOINT_GAMEINSTANCE,HEADERS,int_key = state['game_instance_running'])
        game_id = gameinstance_data["game"]
        # 1) Navigate to the game
        if game_id == 1: # Fixation_Task
            GAME_URI = f"{ROOT_URI}/game/fixation/{state['game_instance_running']}"
            browser.get(GAME_URI)
            
            # 2) Update the model via HTTP PUT
            state['start_game'] = False
            state['is_occupied'] = True
            state['motor'] = False
            try:
                resp = requests.put(API_ENDPOINT_STATE, json=state, headers=HEADERS, timeout=5)
                resp.raise_for_status()
                logging.info("Updated state after start_game")
            except Exception as e:
                logging.error("Failed to update state in CASE 2: %s", e)
    elif state['is_occupied'] and (state['motor']== False):
        disable_motor()
    elif state['is_occupied'] and state['stop_game']: # stop the game
        browser.get(ROOT_URI + '/standby/')
        # Update the model via HTTP PUT
        state['start_game'] = False
        state['is_occupied'] = False
        state['motor'] = False
        state['stop_game'] = False
        try:
                resp = requests.put(API_ENDPOINT_STATE, json=state, headers=HEADERS, timeout=5)
                resp.raise_for_status()
                logging.info("Updated state after stop_game")
        except Exception as e:
                logging.error("Failed to update state in CASE 2: %s", e)
        disable_motor()
    elif state['motor']:
        turn_motor_CCW(steps,speed)
        ws.send(json.dumps({'type':'ack_motor','rpi_num':RPI_NUM}))

def on_error(ws, err): 
    logging.error(f"WS error: {err}")

def on_close(ws, code, msg):
    logging.info(f"WS closed: {code} {msg}")
    time.sleep(5)
    start_ws()

        
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

        
def RFID_reader():
    try:
        print("RFID start")
        def tag_callback(reader, tag):
            print(f"[{reader.port}] Tag: {tag}")
            if reader == reader1:
                print("reader1")
            #if reader == reader2:
            #    print("reader2")
        reader1 = PETRFIDReader(RFID1, callback=tag_callback)
        #reader2 = PETRFIDReader(RFID2, callback=tag_callback)

        
        while True:
            tag1 = reader1.get_last_tag()
            #tag2 = reader2.get_last_tag()
            if tag1:
                
                data1 = {
                    "tag": tag1,
                    "device_name": DEVICE_NAME
                }
                
                
                post_request(data1, API_ENDPOINT_RFID_RESPONSE, HEADERS)
            #elif tag2:
            #    data2 = {
            #        "tag": tag2,
            #        "device_name": DEVICE_NAME
            #    }
                
                
            #    post_request(data2, API_ENDPOINT_RFID_RESPONSE, HEADERS)
            else:
                pass
                
            time.sleep(0.5)  # Small delay to avoid excessive CPU usage
    except Exception as e:
        print(f"RFID Reader Error: {e}")


# --- Runner ---

def start_ws():
    global ws
    ws = WebSocketApp(WS_URL, header=HEADERS,
                      on_open=on_open,
                      on_message=on_message,
                      on_error=on_error,
                      on_close=on_close)
    ws.run_forever()

if __name__ == '__main__':
    selenium_login(LOGIN_URL, "username", USERNAME, "password", PASSWORD, "submit")
    browser.get(STANDBY_URI)
    threading.Thread(target=RFID_reader, daemon=True).start()
    try:
        start_ws()
    except KeyboardInterrupt:
        pass
    finally:
        disable_motor(); GPIO.cleanup(); browser.quit()