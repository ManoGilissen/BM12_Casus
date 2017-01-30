from grove_rgb_lcd import *
from time import time, strftime, localtime, sleep
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from datetime import datetime

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
ALARM_DURATION                      = 15

# Buzzer tone constants
TONE_DISPENSING                     = 440       # Note A4
TONE_ALARMING                       = 2093      # Note C6
TONE_SILENCE                        = -1

# Hardware constants
MAX_DISPLAY_CHARS                   = 32
MAX_LINE_CHARS                      = 16
BUTTON_PIN                          = 3
PROXIMITY_PIN = 2

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

# Alarm & Proxomity variabelen
present = False
herhaalalarm = 1
MAX_ALARM = 3
dispenseCheckTime = 0
timeBetweenAlarm = 60

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
mailTime                            = 0
mailSent                            = False

dispenseTimeStamps                  = []

def Start():
    Set_Hardware()
    Set_Actuators()
    Get_Dispense_Times()
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
    global mailTime
    global mailSent

    Set_State(STATE_DISPENSING)
    mailSent = False

    nextDispense = -1
    rgbColor = COLOR_BLUE
    ledColor = COLOR_BLUE
    buzzerTone = TONE_DISPENSING

    Set_Actuators()
    Set_Display("  Uw medicatie  ", "wordt uitgegeven")

    sleep(DISPENSE_DURATION)

    Set_State(STATE_ALARMING)

    dispenseTime = int(time())
    mailTime = localtime()
    rgbColor = COLOR_WHITE
    ledColor = COLOR_ORANGE
    buzzerTone = TONE_ALARMING

    Set_Actuators()
    Set_Display("  Uw medicatie  ", "  ligt gereed   ")


def Inactive():
    if userInput == INPUT_TYPE_SHORT:
        Set_State(STATE_ACTIVE)


def Active():
    global remainingTime
    global dispenseTimeStamps

    if userInput == INPUT_TYPE_LONG or strftime("%H:%M", localtime()) == dispenseTimeStamps[0]:
        Dispense()
        dispenseTimeStamps.append(dispenseTimeStamps[0])
        del dispenseTimeStamps[0]


    '''
    elif (remainingTime != Get_Remaining()):
            remainingTime = Get_Remaining()
            Set_Display("Volgende inname:", Get_Remaining())
    '''


def Dispensed():
    global systemState
    global present
    global dispenseCheckTime
    global timeBetweenAlarm
    global herhaalalarm
    global MAX_ALARM

    # Read ultra sonic sensor value
    dispenseCheckTime = int(time())
    proxDetect()

    if present == 1:
        # Medicatie is aanwezig
        if dispenseTime + 60 * herhaalalarm < int(time()) - timeBetweenAlarm and herhaalalarm < MAX_ALARM:
            systemState = STATE_ALARMING
            herhaalalarm += 1
        elif herhaalalarm >= MAX_ALARM:
            systemState = STATE_NOTIFYING
    elif present == 0:
        systemState = STATE_ACTIVE

    # if EMPTY_HOLDER_VALUE + ERROR_MARGIN > readValue > EMPTY_HOLDER_VALUE - ERROR_MARGIN:
    # Conclude blister taken by user
    # systemState = STATE_ACTIVE

    # if time() > TIME_ALARM_USER:
    # New alarm to alert user to take blister

    # if time() > TIME_ALERT_RESPONDERS:
    # Alert connected responders about user not taking blister
    # systemState = STATE_NOTIFYING


def Alarm():
    if userInput == INPUT_TYPE_SHORT or dispenseTime < int(time()) - ALARM_DURATION:
        Set_State(STATE_DISPENSED)
    else:
        setRGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def proxDetect():
    global PROXIMITY_PIN
    global present
    global dispenseCheckTime

    limit = 10          # Eventueel andere range: Is de grenswaarde tussen wel/niet aanwezig zijn van een blister

    try:
        # Afstand bepalen m.b.v. sensor
        ultrasonicDetect = grovepi.ultrasonicRead(PROXIMITY_PIN)
        print(ultrasonicDetect)
        if ultrasonicDetect > 50:       # Onnauwkeurigheid sensor
            print('Gooi weg.')
            present = 2
        elif ultrasonicDetect > limit:
            print("Afstand is groter dan limit. Geen blister aanwezig.")
            present = 0
        elif ultrasonicDetect <= limit:
            print("Afstand is kleiner dan limit. Blister aanwezig.")
            present = 1

    except TypeError:
        print("TypeError")
        Log_Write(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " | Exeption")
    except IOError:
        print("IOError")
        Log_Write(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " | Exeption")

def Notifying():
    global systemState
    global mailTime
    global mailSent

    print("Notify")

    if not mailSent:
        mailTime = strftime("%A, %d %b %Y om %H:%M:%S", mailTime)

        mailPlaintext = patientName + " heeft niet op het medicatie alarm van " + mailTime + " gereageerd."
        # Mail wordt omgezet naar MIMEtype text voor compabiliteit
        mailMsg = MIMEText(mailPlaintext)
        mailMsg['From'] = senderMail
        mailMsg['To'] = recipientMail
        mailMsg['Subject'] = patientName + " reageert niet op medicatie alarm"

        # Inhoud van variabele mailMsg wordt gepiped naar sendmail process
        #mailProcess = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        #mailProcess.communicate(mailMsg.as_string())
        print(mailPlaintext)
        mailSent = True

    elif mailSent:
        print('Mail reeds verzonden.')


# Geeft de tijd aan waarop de volgende inname plaatsvindt.
def Get_Remaining():
    minutes, seconds = divmod(nextDispense - 120, 60)
    hours, minutes = divmod(minutes, 60)
    return ("    " + "%02d:%02d" % (hours, minutes) + "    ")


# Verandert de state en schrijft dit in het logfile
def Set_State(newState):
    global systemState

    systemState = newState
    Log_Write(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " | " + newState)


# Zet de doorgegeven tekst op het LCD-display
def Set_Display(textTop, textBottom):
    setText(textTop[:MAX_LINE_CHARS] + "\n" + textBottom[:MAX_LINE_CHARS])
    print(textTop[:MAX_LINE_CHARS] + "\n" + textBottom[:MAX_LINE_CHARS])


# Set all hardware actuators to current state
def Set_Actuators():
    setRGB(rgbColor[0], rgbColor[1], rgbColor[2])
    # setLED(ledColor[0], ledColor[0], ledColor[0])
    # setBuzzer(buzzerTone)


# Set hardware input and output pin modes
def Set_Hardware():
    grovepi.pinMode(BUTTON_PIN, "INPUT")
    grovepi.pinMode(PROXIMITY_PIN, "INPUT")


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
        systemState = STATE_ACTIVE if systemState == STATE_INACTIVE else STATE_INACTIVE
        ledColor = COLOR_RED if systemState == STATE_INACTIVE else COLOR_GREEN
        rgbColor = COLOR_DIMMED if systemState == STATE_INACTIVE else COLOR_WHITE


def Check_Input():
    global buttonDown
    global inputStart
    global inputRelease
    global inputInterval
    global userInput

    # Check and set current button input

    userInput = INPUT_NONE

    if grovepi.digitalRead(BUTTON_PIN) == 1:  # Button 1 wordt ingedrukt
        if not buttonDown:
            buttonDown = True
            inputStart = int(time() * 1000)
    else:
        if buttonDown:  # Button 1 wordt losgelaten
            buttonDown = False
            inputRelease = int(time() * 1000)
            inputDuration = (inputRelease - inputStart)
            if inputDuration <= inputInterval:
                userInput = INPUT_TYPE_SHORT  # Short press
            elif inputDuration < powerInterval:
                userInput = INPUT_TYPE_LONG  # Long press
            elif inputDuration >= powerInterval:
                Set_Display("  Shutting down ", "    Goodbye     ")
                userInput = INPUT_TYPE_POWER  # Shutdown press


def Play_Intro():
    Log_Write(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " | Starting")
    setRGB(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    Set_Display("     DSPNZR     ", "      2000      ")
    sleep(INTRO_DURATION)


# Append a line to action.log
def Log_Write(logLine):
    logFile = open("action.log", "a")
    logFile.write(logLine + "\n")
    logFile.close()


def Get_Dispense_Times():
    global dispenseTimeStamps
    importedTimes = []
    tempTimes = []

    # Open the text file
    importFile = open("time.txt", "r")
    # Remove linebreaks ('\n')
    importFile = importFile.read().splitlines()
    # Check if times are in a valid format, add to importTimes
    for time in importFile:
        if len(time) == 5:
            HH = time[0] + time[1]
            MM = time[3] + time[4]
            if 00 <= int(HH) < 24 and 00 <= int(MM) < 60 and time[2] == ":" and len(time) == 5:
                importedTimes.append(time)
            else:
                Log_Write(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " | Error: A scheduled timestamp has not been imported (invalid format)")
                print("Error: Tijd", time, "voldoet niet aan eisen (HH:MM)")
        else:
            Log_Write(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " | Error: A scheduled timestamp has not been imported (invalid format)")
            print("Error: Tijd voldoet niet aan eisen (HH:MM)")


# Sort list
    importedTimes.sort()

    # Check if time < now
    now = strftime('%H:%M', localtime())
    print('Het is nu: ', now)
    for sortedTime in importedTimes:
        if sortedTime <= now:
            tempTimes.append(sortedTime)
        else:
            dispenseTimeStamps.append(sortedTime)

    # Append earlier times to the final list
    for earlyTime in tempTimes:
        dispenseTimeStamps.append(earlyTime)


Start()

while True:
    Update()
