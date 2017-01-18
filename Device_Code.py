from RGB_LCD import *


STATE_INACTIVE                      = 0
STATE_ACTIVE                        = 1
STATE_DISPENSING                    = 2
STATE_DISPENSED                     = 3
STATE_ALARMING                      = 4
STATE_NOTIFYING                     = 5

INPUT_NONE                          = 0
INPUT_BUTTON_1_PRESS                = 1  # Power button #
INPUT_BUTTON_2_PRESS                = 2  # Function button #

UPDATE_INTERVAL                     = 0.05
INTRO_DURATION                      = 2
COLOR_RED                           = [255, 000, 000]
COLOR_GREEN                         = [000, 255, 000]
COLOR_WHITE                         = [255, 255, 255]
COLOR_DIMMED                        = [128, 128, 128]

DISPENSE_TIMESTAMPS                 = [1484850000, 1484857200, 1484863400]

systemState                         = STATE_INACTIVE
ledColor                            = COLOR_RED
rgbColor                            = COLOR_DIMMED


def Start():
    Actuate()
    Intro()
    Update()


def Update():
    Check_Active()

    if   systemState == STATE_INACTIVE:
        Inactive()
    elif systemState == STATE_ACTIVE:
        Active()
    elif systemState == STATE_DISPENSING:
        Inactive()
    elif systemState == STATE_DISPENSED:
        Dispensed()
    elif systemState == STATE_ALARMING:
        Inactive()
    elif systemState == STATE_NOTIFYING:
        Inactive()

    time.sleep(UPDATE_INTERVAL)
    Display()
    Update()


def Display():
    global systemState
    # Display relevant information to LCD


def Actuate():
    setRGB(rgbColor[0], rgbColor[1], rgbColor[2])
    # set LED color #


def Dispense():
    global systemState
    # Dispense next medicine blister
    systemState = STATE_DISPENSING
    DISPENSE_TIMESTAMPS.pop(0)


def Inactive():
    global systemState


def Active():
    if Get_Input() == INPUT_BUTTON_1_PRESS:
        Dispense()
        # Discard planned dispense moment
        # Plan new dispense moment
    else:
        # Check whether time matches planned dispense moment
        if time.time() > DISPENSE_TIMESTAMPS[0]:
            Dispense()


def Dispensed():
    global systemState


def Intro():
    setText("==-  MEDIDO  -==\n==-   2000   -==")
    time.sleep(INTRO_DURATION)


def Check_Active():
    global systemState
    global ledColor
    global rgbColor
    # Check and process power button input
    if Get_Input() == INPUT_BUTTON_2_PRESS:
        systemState     = STATE_ACTIVE  if systemState == STATE_INACTIVE else STATE_INACTIVE
        ledColor        = COLOR_RED     if systemState == STATE_INACTIVE else COLOR_GREEN
        rgbColor        = COLOR_DIMMED  if systemState == STATE_INACTIVE else COLOR_WHITE
        Actuate()


def Get_Input():
    # Retrieve and return user input
    return INPUT_NONE


Start()
