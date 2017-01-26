#from grove_rgb_lcd import *
from time import time, strftime, localtime, sleep
from datetime import datetime
tempTimes = []
dispenseTimeStamps = []
currentTime = 0
nextDispense = 0
dispensed = False
importedTimes = ['Should', 'be', 'empty']


def timeForTakeOut():
    global currentTime
    global nextDispense
    global dispensed
    global dispenseTimeStamps
    tempTimeStamps = []

    currentTime = strftime("%H:%M", localtime())
    nextDispense = dispenseTimeStamps[0]

    if currentTime == nextDispense and not dispensed:
        print("Je pillen liggen klaar!")
        # dispense de blisters
        dispensed = True

    elif currentTime != nextDispense and not dispensed:
        print("Blijf van die pillen af")
        # niks doen verder

    elif dispensed:
        print('Je pillen liggen er nog!')
        # alarm, notificaties enz.
        # niet vergeten dispensed naar False te zetten als weggepakt/opgelost
        # Daarna dispenseTimeStamps.append(dispenseTimeStamps[0], [0] verwijderen

def Get_Dispense_Times():
    global importedTimes
    global dispenseTimeStamps

    # Empty list
    importedTimes = []

    # Open the text file
    importFile = open("time.txt", "r")
    # Remove linebreaks ('\n')
    importFile = importFile.read().splitlines()
    # Check if times are in a valid format, add to importTimes
    for time in importFile:
        HH = time[0] + time[1]
        MM = time[3] + time[4]
        if 00 <= int(HH) < 24 and 00 <= int(MM) < 60 and time[2] == ":" and len(time) == 5:
            importedTimes.append(time)
        else:
            print("Error: Tijd", time, "voldoet niet aan eisen (HH:MM)")
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


Get_Dispense_Times()
while True:
    timeForTakeOut()
    print(currentTime)
    print(nextDispense)
    sleep(5)