from grove_rgb_lcd import *
import time
import datetime

import grovepi
import random

# System states
STATE_INACTIVE                      = "State inactive"
STATE_ACTIVE                        = "State active"
STATE_DISPENSING                    = "State dispensing"
STATE_DISPENSED                     = "State dispensed"
STATE_ALARMING                      = "State alarming"
STATE_NOTIFYING                     = "State notifying"

# Input identifiers
INPUT_NONE                          = 0
INPUT_TYPE_SHORT                    = 1     # Short press
INPUT_TYPE_LONG                     = 2     # Long press
INPUT_TYPE_POWER                    = 3     # Power button press

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
BUTTON_PIN                          = 3

# Color constants
COLOR_RED                           = [255, 100, 100]
COLOR_GREEN                         = [100, 255, 100]
COLOR_BLUE                          = [100, 100, 255]
COLOR_WHITE                         = [255, 255, 255]
COLOR_ORANGE                        = [255, 165, 000]
COLOR_DIMMED                        = [100, 100, 100]

# Input and time variables
buttonDown                          = False
inputStart                          = 0         # Timestamp start button press
inputRelease                        = 0         # Timestamp end button press
inputInterval                       = 500       # Long press threshold
powerInterval                       = 10000     # Shut down press threshold
dispenseTime                        = 0
nextDispense                        = -1
remainingTime                       = ""
importedTimes                       = []

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
    Get_Timestamps()
    Play_Intro()


def Update():
    Check_Input()
    Check_Active()

    if systemState == STATE_INACTIVE:
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
    global rgbColor
    global ledColor
    global buzzerTone
    global dispenseTime
    global nextDispense

    Set_State(STATE_DISPENSING)

    nextDispense                    = -1
    rgbColor                        = COLOR_BLUE
    ledColor                        = COLOR_BLUE
    buzzerTone                      = TONE_DISPENSING

    Set_Actuators()
    Set_Display("  Uw medicatie  ", "wordt uitgegeven")

    sleep(DISPENSE_DURATION)

    Set_State(STATE_ALARMING)

    dispenseTime                    = int(time())
    rgbColor                        = COLOR_WHITE
    ledColor                        = COLOR_ORANGE
    buzzerTone                      = TONE_ALARMING

    Set_Actuators()
    Set_Display("  Uw medicatie  ", "  ligt gereed   ")


def Inactive():
    if userInput == INPUT_TYPE_SHORT:
        Set_State(STATE_ACTIVE)


def Active():
    global remainingTime

    if nextDispense == -1:
        Set_Next_Dispense()

    print("NextDispense: ", nextDispense)
    print("Time Now: ", (datetime.now().second + datetime.now().minute * 60 + datetime.now().hour * 60))
    if userInput == INPUT_TYPE_LONG or nextDispense <= (datetime.now().second + datetime.now().minute * 60 + datetime.now().hour * 60):
        Dispense()
    elif (remainingTime != Get_Remaining()):
            remainingTime = Get_Remaining()
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
    logWrite(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " | Alarming")
    if userInput == INPUT_TYPE_SHORT or dispenseTime < int(time()) - ALARM_DURATION:
        Set_State(STATE_DISPENSED)
    else:
        setRGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def Notifying():
    global systemState


# Geeft de tijd aan waarop de volgende inname plaatsvindt.
def Get_Remaining():
    minutes, seconds = divmod(nextDispense - 120, 60) #Waarom -2 minuten???
    hours,   minutes = divmod(minutes, 60)
    return("    " + "%02d:%02d" % (hours, minutes) + "    ")


# Verandert de state en schrijft dit in het logfile
def Set_State(newState):
    global systemState

    systemState = newState
    logWrite(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " | " + newState)


# Zet de doorgegeven tekst op het LCD-display
def Set_Display(textTop, textBottom):
    setText(textTop[:MAX_LINE_CHARS] + "\n" + textBottom[:MAX_LINE_CHARS])
    print(textTop[:MAX_LINE_CHARS] + "\n" + textBottom[:MAX_LINE_CHARS])

# ?
def Set_Actuators():
    setRGB(rgbColor[0], rgbColor[1], rgbColor[2])
    # setLED(ledColor[0], ledColor[0], ledColor[0])
    # setBuzzer(buzzerTone)


# H
def Set_Hardware():
    grovepi.pinMode(BUTTON_PIN, "INPUT")

#
def Set_Next_Dispense():
    global nextDispense

    currentDayTime = datetime.now().second + datetime.now().minute * 60 + datetime.now().hour * 60

    for time in importedTimes:
        if time > currentDayTime:
            nextDispense = time

    if nextDispense == -1:
        nextDispense = min(importedTimes)

    print("Next dispense time (seconds in day): " + str(nextDispense))
    print(currentDayTime, nextDispense, time, importedTimes)


def Get_Timestamps():
    global importedTimes

    importedTimes = []

    # Open and read data file
    importFile = open("time.txt", "r")
    importFile = importFile.read().splitlines()

    # Check if times are in a valid format, add to importTimes
    for time in importFile:
        HH = time[0] + time[1]
        MM = time[3] + time[4]
        if 00 <= int(HH) < 24 and 00 <= int(MM) < 60 and time[2] == ":" and len(time) == 5:
            try:
                importedTimes.append(int(HH) * 3600 + int(MM) * 60)
            except ValueError:
                print("Error: Tijd conversie naar unix timestamp")
        else:
            print("Error: Tijd", time, "voldoet niet aan eisen (HH:MM)")

def Check_Active():
    global systemState
    global ledColor
    global rgbColor

    # Check and process power button input
    if userInput == INPUT_TYPE_POWER:
        systemState     = STATE_ACTIVE  if systemState == STATE_INACTIVE else STATE_INACTIVE
        ledColor        = COLOR_RED     if systemState == STATE_INACTIVE else COLOR_GREEN
        rgbColor        = COLOR_DIMMED  if systemState == STATE_INACTIVE else COLOR_WHITE


def Check_Input():
    global buttonDown
    global inputStart
    global inputRelease
    global inputInterval
    global userInput

    # Check and set current button input

    userInput = INPUT_NONE

    print(time.time())

    if grovepi.digitalRead(BUTTON_PIN) == 1:                    # Button 1 wordt ingedrukt
        if not buttonDown:
            buttonDown = True
            inputStart = int(time.time() * 1000)
    else:
        if buttonDown:                                        # Button 1 wordt losgelaten
            buttonDown = False
            inputRelease = int(time.time() * 1000)
            inputDuration = (inputRelease - inputStart)
            if inputDuration <= inputInterval:
                userInput = INPUT_TYPE_SHORT          # Short press
            elif inputDuration < powerInterval:
                userInput = INPUT_TYPE_LONG           # Long press
            elif inputDuration >= powerInterval:
                Set_Display("  Shutting down ", "    Goodbye     ")
                userInput = INPUT_TYPE_POWER          # Shutdown press


def Play_Intro():
    logWrite(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " | Starting")
    setRGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    Set_Display("     DSPNZR     ", "      2000      ")
    sleep(INTRO_DURATION)


# Append a line to action.log
def logWrite(logLine):
    logFile = open("action.log", "a")
    logFile.write(logLine + "\n")
    logFile.close()

Start()

while True:
    Update()
