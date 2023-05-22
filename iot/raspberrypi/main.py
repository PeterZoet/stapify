import json
import time
import network
import urequests
import random
import math
from machine import Pin

SSID = "Mutahar"
PASSWORD = "someGeamers"
wlan = network.WLAN(network.STA_IF)

print("SSID + PASSWORD ingevuld")

wlan.active(True)
wlan.connect(SSID, PASSWORD)
print("WLAN connectie gemaakt")

while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print('Connected to WiFi!')

url = 'https://schoolmoettestdomeinenhebben.nl/graphql'
headers = {'Content-Type': 'application/json'}
query = '''
query{
    login(username: "azertycho", password: "123")
}
'''
variables = {'cookie': 'my-cookie'}
data = {'query': query, 'variables': variables}

print('Sending request...')
response = urequests.post(url, headers=headers, data=json.dumps(data))
login = response.json()['data']['login']

print('Cookie: ' + login)

# Mutation to add step count
voegStapToe = '''
mutation AddStap($aantalStappen: Int!, $cookie: String!) {
    stappen(aantalStappen: $aantalStappen, cookie: $cookie) {
        code
        message
    }
}
'''

# stap varriabelen
variablesStap = {
    'aantalStappen': 1,
    'cookie': login
}

totaalStap = 0
cacheStap = 0

# Mutation to add heart rate
voegHartslagToe = '''
        mutation AddHartslag($hartslag: Int!, $cookie: String!) {
            hartslag(hartslag: $hartslag, cookie: $cookie) {
                code
                message
            }
        }
        '''

# hartslag varriabelen
variablesHartslag = {
    'hartslag': 0,
    'cookie': login
}

# Set up GPIO for PulseSensor
PulseSensorPin = Pin(26, Pin.IN)

Threshold = 0


# Set up GPIO for PulseSensor
PulseSensorPin = machine.ADC(26)

Threshold = 1000


def calculate_average_bpm(beats, duration):
    if duration == 0:
        return 0

    # Calculate average beats per minute
    average_bpm = beats / duration * 60
    return average_bpm


def send_data():
    start_time = time.time()
    beats = 0
    # Read the PulseSensor value
    Signal = PulseSensorPin.read_u16()

    # Print signal
    print("Signal: " + str(Signal))

    # If the signal is above the threshold, increment beat count
    if Signal > Threshold:
        print("Heartbeat detected!")
        beats += 1

        # Calculate duration in seconds
        duration = time.time() - start_time

        while Signal > Threshold:
            # wait for the signal to drop below the threshold
            Signal = PulseSensorPin.read_u16()

        # If the duration exceeds a minute, calculate average beats per minute
        if duration >= 60:
            average_bpm = calculate_average_bpm(beats, duration)
            print("Average Beats Per Minute: ", average_bpm)

            # send heart rate to database
            variablesHartslag['hartslag'] = average_bpm
            dataHartslag = {'query': voegHartslagToe,
                            'variables': variablesHartslag}
            responseHartslag = urequests.post(
                url, headers=headers, data=json.dumps(dataHartslag))
            print(responseHartslag.json())

    # Reset variables
    start_time = time.time()
    beats = 0


while True:
    print('Sending request...')
    try:
        # create a random x, y, z value between 0 and 5
        x = random.randint(0, 5)
        y = random.randint(0, 5)
        z = random.randint(0, 5)
        # print the x, y, z values
        print('x = {0:0.3f}G'.format(x))
        print('y = {0:0.3f}G'.format(y))
        print('z = {0:0.3f}G'.format(z))

        # calculate the length
        length = math.sqrt(x*x + y*y + z*z)
        print('length = {0:0.3f}G'.format(length))

        # if the length is greater than 2 a step has been taken
        if length > 2:
            totaalStap += 1

        send_data()

    except OSError as e:
        print('Error: ' + str(e))

    time.sleep(1)
