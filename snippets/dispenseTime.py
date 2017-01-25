importedTimes = ['Should', 'be', 'empty']

def Get_Dispense_Times():
    global importedTimes

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

Get_Dispense_Times()

print(importedTimes)