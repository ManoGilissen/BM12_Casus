# Snippet voor de detectie van een blister in de dispenser
# Zorg dat grovepi.py in dezelfde map staat als onderstaande snippet
import grovepi
import time

ultrasonicPort = 4      # Poortnummer voor de ultrasonic ranger (standaard D4)
present = False         # Of een blister aanwezig is of niet

def proxDetect():
    global ultrasonicPort
    global present

    limit = 10

    try:
        # Afstand bepalen m.b.v. sensor
        ultrasonicDetected = grovepi.ultrasonicRead(ultrasonicPort)
        print(ultrasonicDetected)
        if ultrasonicDetected > limit:
            print("Afstand is groter dan limit. Geen blister aanwezig.")
            present = False
        elif ultrasonicDetected <= limit:
            print("Afstand is kleiner dan limit. Blister aanwezig.")
            present = True

    except TypeError:
        print("TypeError")
    except IOError:
        print("IOError")

while True:
    proxDetect()
    print(present)
    time.sleep(5)
