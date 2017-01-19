from grove_rgb_lcd import *
from time import *
import grovepi
import random

# Verschillende staten van het programma
STATE_INACTIVE = 0
STATE_ACTIVE = 1
STATE_DISPENSING = 2
STATE_DISPENSED = 3
STATE_ALARMING = 4
STATE_NOTIFYING = 5

#INPUT_NONE                          = 0
#INPUT_BUTTON_1_PRESS                = 1         # Power button
#INPUT_BUTTON_2_PRESS                = 2         # Function button

UPDATE_INTERVAL                     = 0.05
INTRO_DURATION                      = 2
DISPENSE_DURATION                   = 4

# Geluiden voor het alarm
TONE_DISPENSING                     = 440       # Note A4
TONE_ALARMING                       = 2093      # Note C6
TONE_SILENCE                        = -1

# Aantal characters dat getoond kan worden op lcd scherm
MAX_DISPLAY_CHARS                   = 32
MAX_LINE_CHARS                      = 16

COLOR_RED                           = [255, 100, 100]
COLOR_GREEN                         = [100, 255, 100]
COLOR_BLUE                          = [100, 100, 255]
COLOR_WHITE                         = [255, 255, 255]
COLOR_ORANGE                        = [255, 165, 000]
COLOR_DIMMED                        = [100, 100, 100]

# Aantal variablen voor het indrukken van de knop
button = 3  #Knop is aangesloten op D3
grovepi.pinMode(button, "INPUT")
buttonState = 0     # Current state of the button
lastDebounceTime = 0    # the last time the output pin was toggled
druk = False    #boolean om aan te geven of er gedrukt is
tijdseenheid = 500  #how long the button was held (ms) & tijd tussen het drukken
begindruk = 0   #tijd zodra de knop ingedrukt wordt
einddruk = 0    # tijd zodra de knop losgelaten wordt

DISPENSE_TIMESTAMPS                 = [
    1484846000,
    1484850000,
    1484854000,
    1484858000
]

systemState                         = STATE_ACTIVE
ledColor                            = COLOR_RED
rgbColor                            = COLOR_DIMMED
buzzerTone                          = TONE_SILENCE


def Start():
    #Set_Actuators()
    #Check_Timestamps()
    Play_Intro()
    # Update()
    #Alarming()
    checkButton()


def Update():
    Check_Active()

    if systemState == STATE_INACTIVE:
        Inactive()
    elif systemState == STATE_ACTIVE:
        Active()
    elif systemState == STATE_DISPENSED:
        Dispensed()
    elif systemState == STATE_ALARMING:
        Alarming()
    elif systemState == STATE_NOTIFYING:
        Notifying()

    sleep(UPDATE_INTERVAL)
    Update()


def Dispense():
    global systemState
    global rgbColor
    global ledColor
    global buzzerTone

    DISPENSE_TIMESTAMPS.pop(0)

    systemState                     = STATE_DISPENSING
    rgbColor                        = COLOR_BLUE
    ledColor                        = COLOR_BLUE
    buzzerTone                      = TONE_DISPENSING

    Set_Actuators()
    Set_Display("  Uw medicatie  ", "wordt uitgegeven")

    sleep(DISPENSE_DURATION)

    systemState                     = STATE_DISPENSED
    rgbColor                        = COLOR_WHITE
    ledColor                        = COLOR_ORANGE
    buzzerTone                      = TONE_ALARMING

    Set_Actuators()
    Set_Display(" Uw medicatie ", "  ligt gereed   ")


def Inactive():
    global systemState


def Active():
    if Get_Input() == INPUT_BUTTON_1_PRESS or DISPENSE_TIMESTAMPS[0] < int(time()):
        Dispense()
    else:
        Set_Display("Volgende inname:", Get_Remaining())


def Dispensed():
    global systemState
    # Read ultra sonic sensor value

    # if EMPTY_HOLDER_VALUE + ERROR_MARGIN > readValue > EMPTY_HOLDER_VALUE - ERROR_MARGIN:
        # Conclude blister taken by user
        # systemState = STATE_ACTIVE

    # if time() > TIME_ALARM_USER:
        # New alarm to alert user to take blister

    # if time() > TIME_ALERT_RESPONDERS:
        # Alert connected responders about user not taking blister
        # systemState = STATE_NOTIFYING


def Alarming():
    global systemState
    Set_Display("     ALARM      ", " ")
    for i in range(0, 255):
        setRGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        sleep(.1)

def Notifying():
    global systemState


def Get_Input():
    # Retrieve and return user button input
    # Check for button release to avoid double input due to short update interval
    return INPUT_NONE


def Get_Remaining():
    # Return readable time to next dispense
    minutes, seconds = divmod(DISPENSE_TIMESTAMPS[0] - int(time()), 60)
    hours,   minutes = divmod(minutes, 60)
    return("    " + "%02d:%02d:%02d" % (hours, minutes, seconds) + "    ")


def Set_Display(displayText):
    if len(displayText) <= MAX_DISPLAY_CHARS:
        Set_Display(displayText[:MAX_LINE_CHARS], displayText[MAX_LINE_CHARS:])


def Set_Display(textTop, textBottom):
    # Printing instead of setText for debugging
    setText(textTop[:MAX_LINE_CHARS] + "\n" + textBottom[:MAX_LINE_CHARS])
    #print(textTop[:MAX_LINE_CHARS] + "\n" + textBottom[:MAX_LINE_CHARS])


def Set_Actuators():
    global systemState

    # setRGB(rgbColor[0], rgbColor[1], rgbColor[2])
    # setLED(ledColor[0], ledColor[0], ledColor[0])
    # setBuzzer(buzzerTone)

def checkButton():
    global druk
    global begindruk
    global einddruk
    global tijdseenheid

    buttonState = grovepi.digitalRead(button)
    if buttonState == 1:  # knop is ingedrukt
        #lastDebounceTime = int(round(time.time() * 1000))
        if druk == False:
            druk = True
            begindruk = int(time() * 1000)

    elif buttonState == 0:  # knop is niet ingedrukt
        if druk == True:  # er wordt losgelaten nadat er gedrukt is
            druk = False
            einddruk = int(time() * 1000)

            if (einddruk - begindruk) <= tijdseenheid:  # berekening van de lengte van de druk
                print("Short press")
                Set_Display("Short press", " ")
                # Shortpress
                #  Alarm moet worden uitgezet
            else:
                print("Long press")
                Set_Display("Long press", " ")
                # Longpress
                # Medicatie moet voortijdig gepakt worden


def Check_Active():
    global systemState
    global ledColor
    global rgbColor

    # Check and process power button input
    if Get_Input() == INPUT_BUTTON_2_PRESS:
        systemState     = STATE_ACTIVE  if systemState == STATE_INACTIVE else STATE_INACTIVE
        ledColor        = COLOR_RED     if systemState == STATE_INACTIVE else COLOR_GREEN
        rgbColor        = COLOR_DIMMED  if systemState == STATE_INACTIVE else COLOR_WHITE
        Set_Actuators()


def Check_Timestamps():
    global DISPENSE_TIMESTAMPS

    # Remove expired timestamps
    for timestamp in DISPENSE_TIMESTAMPS:
        if timestamp < int(time()):
            DISPENSE_TIMESTAMPS.remove(timestamp)


def Play_Intro():
    Set_Display("     DSPNZR     ", "      2000      ")
    sleep(INTRO_DURATION)


Start()

while True:
    checkButton()

