import time

# Tijden waarop medicatie moet worden ingenomen
# Format is HH:MM (HH 00-23, MM 00-59)
dispenseTimeStamps = [
    "09:00",
    "13:15",
    "17:30",
    "21:45"
]

currentTime = 0
nextDispense = 0
dispensed = False

def timeForTakeOut():
    global currentTime
    global nextDispense
    global dispensed

    currentTime = time.strftime("%H:%M", time.localtime())
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

# Demo
while True:
    timeForTakeOut()
    print(currentTime)
    print(nextDispense)
    time.sleep(5)