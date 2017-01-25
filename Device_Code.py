from grove_rgb_lcd import *
from time import *

import grovepi
import random

# System states
STATE_INACTIVE                      = 0
STATE_ACTIVE                        = 1
STATE_DISPENSING                    = 2
STATE_DISPENSED                     = 3
STATE_ALARMING                      = 4
STATE_NOTIFYING                     = 5

# Input identifiers
INPUT_NONE                          = 0
INPUT_TYPE_SHORT                    = 1     # Button 1 short press
INPUT_TYPE_LONG                     = 2     # Button 1 long press
INPUT_TYPE_POWER                    = 3

# Event durations
UPDATE_INTERVAL                     = 0.05
INTRO_DURATION                      = 2
DISPENSE_DURATION                   = 4
ALARM_DURATION                      = 60

# Buzzer tone constants
TONE_DISPENSING                     = 440       # Note A4
TONE_ALARMING                       = 2093      # Note C6
TONE_SILENCE                        = -1

# Hardware constants
MAX_DISPLAY_CHARS                   = 32
MAX_LINE_CHARS                      = 16
BUTTON_1_PIN                        = 3
#BUTTON_2_PIN                        = 5

# Color constants
COLOR_RED                           = [255, 100, 100]
COLOR_GREEN                         = [100, 255, 100]
COLOR_BLUE                          = [100, 100, 255]
COLOR_WHITE                         = [255, 255, 255]
COLOR_ORANGE                        = [255, 165, 000]
COLOR_DIMMED                        = [100, 100, 100]

DISPENSE_TIMESTAMPS                 = [
    1485337560,
    1484850000,
    1484854000,
    1484858000
]

# Button input variables
buttonDown                          = False
dispenseTime                        = 0
inputStart                          = 0         # Timestamp start button press
inputRelease                        = 0         # Timestamp end button press
inputInterval                       = 500       # Long press threshold
powerInterval                       = 10000     # Shut down press threshold

# System and hardware state variables
systemState                         = STATE_ACTIVE
userInput                           = INPUT_NONE
ledColor                            = COLOR_RED
rgbColor                            = COLOR_DIMMED
buzzerTone                          = TONE_SILENCE

# Mail variables
senderMail	                        = "dspnzr2000@gmail.com"
recipientMail	                    = "svenheinen93@gmail.com"	    # Constant for testing
patientName 	                    = "Anne Beertens"

def Start():
    Set_Hardware()
    Set_Actuators()
    Check_Timestamps()
    Play_Intro()


def Update():
    Check_Input()
    Check_Active()

    if   systemState == STATE_INACTIVE:
        Inactive()
    elif systemState == STATE_ACTIVE:
        Active()
    elif systemState == STATE_DISPENSED:
        Dispensed()
    elif systemState == STATE_ALARMING:
        Alarm()
        Dispensed()
    elif systemState == STATE_NOTIFYING:
        Notifying()

    sleep(UPDATE_INTERVAL)


def Dispense():
    global systemState
    global rgbColor
    global ledColor
    global buzzerTone
    global dispenseTime

    DISPENSE_TIMESTAMPS.pop(0)

    systemState                     = STATE_DISPENSING
    rgbColor                        = COLOR_BLUE
    ledColor                        = COLOR_BLUE
    buzzerTone                      = TONE_DISPENSING

    Set_Actuators()
    Set_Display("  Uw medicatie  ", "wordt uitgegeven")

    sleep(DISPENSE_DURATION)

    dispenseTime                    = int(time())
    systemState                     = STATE_ALARMING
    rgbColor                        = COLOR_WHITE
    ledColor                        = COLOR_ORANGE
    buzzerTone                      = TONE_ALARMING

    Set_Actuators()
    Set_Display("  Uw medicatie  ", "  ligt gereed   ")


def Inactive():
    global systemState

    if userInput == INPUT_TYPE_SHORT:
        systemState = STATE_ACTIVE


def Active():
    if userInput == INPUT_TYPE_SHORT or DISPENSE_TIMESTAMPS[0] < int(time()):
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


def Alarm():
    global systemState

    if userInput == INPUT_TYPE_SHORT or dispenseTime < int(time()) - ALARM_DURATION:
        systemState = STATE_DISPENSED
    else:
        setRGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def Notifying():
    global systemState


# Returns readable time until next dispense
def Get_Remaining():
    minutes, seconds = divmod(DISPENSE_TIMESTAMPS[0] - int(time()), 60)
    hours,   minutes = divmod(minutes, 60)
    return("    " + "%02d:%02d" % (hours, minutes) + "    ")


def Set_Display(textTop, textBottom):
    setText(textTop[:MAX_LINE_CHARS] + "\n" + textBottom[:MAX_LINE_CHARS])
    print(textTop[:MAX_LINE_CHARS] + "\n" + textBottom[:MAX_LINE_CHARS])


def Set_Actuators():
    global systemState

    setRGB(rgbColor[0], rgbColor[1], rgbColor[2])
    # setLED(ledColor[0], ledColor[0], ledColor[0])
    # setBuzzer(buzzerTone)


def Set_Hardware():
    grovepi.pinMode(BUTTON_1_PIN, "INPUT")


def Check_Active():
    global systemState
    global ledColor
    global rgbColor

    # Check and process power button input
    if userInput == INPUT_TYPE_POWER:
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


def Check_Input():
    global button1Pressed
    global inputStart
    global inputRelease
    global inputInterval
    global userInput

    # Check and set current button input

    userInput = INPUT_NONE

    if grovepi.digitalRead(BUTTON_1_PIN) == 1:      # Button 1 is being pressed
        if not button1Pressed:
            button1Pressed          = True
            inputStart              = int(time() * 1000)
    else:                                           # Button 1 is not being pressed
        if button1Pressed:                          # Button 1 is released
            button1Pressed          = False
            inputRelease            = int(time() * 1000)
            inputDuration           = (inputRelease - inputStart)
            if inputDuration <= inputInterval:
                userInput = INPUT_TYPE_SHORT        # Short press
            elif inputDuration <= powerInterval:
                userInput = INPUT_TYPE_LONG         # Long press
            else:
                Set_Display("  Shutting down ", "    Goodbye     ")
                userInput = INPUT_TYPE_POWER        # Shutdown press


def Play_Intro():
    setRGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    Set_Display("   Dispenser    ", "      2000      ")
    sleep(INTRO_DURATION)


Start()

while True:
    Update()

