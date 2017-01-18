import time

STATE_INACTIVE			= 0
STATE_ACTIVE 			= 1
STATE_DISPENSING		= 2
STATE_DISPENSED			= 3
STATE_ALARMING			= 4
STATE_NOTIFYING			= 5

INPUT_NONE				= 0
INPUT_BUTTON_1_PRESS	= 1		# Power button #
INPUT_BUTTON_2_PRESS	= 2		# Function button #

UPDATE_SPEED			= 0.01
COLOR_RED				= [1, 0, 0]
COLOR_GREEN				= [0, 1, 0]

systemState
ledColor

def Start():
	systemState = STATE_INACTIVE
	Update()

def Update():
	Check_Active()

	if 	 systemState == STATE_INACTIVE:
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
	
	time.sleep(UPDATE_SPEED)
	Display()
	Update()

def Display():
	# Display relevant information to LCD #
	# Update LED color if changed #

def Dispense():
	# Dispense next medicine blister #

def Inactive():
	#  #

def Active():
	if Get_Input() == INPUT_BUTTON_1_PRESS:
		Dispense()
		# Discard planned dispense moment #
		# Plan new dispense moment #
	else:
		# Check whether time matches planned dispense moment #:
			Dispense()

def Check_Active():
	if Get_Input() == INPUT_BUTTON_2_PRESS:
		systemState 	= STATE_ACTIVE if systemState == STATE_INACTIVE else STATE_INACTIVE
		ledColor 		= COLOR_RED if systemState == STATE_INACTIVE else COLOR_GREEN

def Get_Input():
	# Retrieve and return user input #
	return INPUT_NONE

Start()
