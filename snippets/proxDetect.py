# Snippet voor de detectie van een blister in de dispenser
# Zorg dat grovepi.py in dezelfde map staat als onderstaande snippet
import grovepi
import time             # Alleen nodig voor de while loop als bewijs dat het werkt

ultrasonicPort = 2      # Poortnummer voor de ultrasonic ranger (standaard D4)
present = False         # Of een blister aanwezig is of niet

def proxDetect():
    global ultrasonicPort
    global present

    limit = 10          # Eventueel andere range: Is de grenswaarde tussen wel/niet aanwezig zijn van een blister

    try:
        # Afstand bepalen m.b.v. sensor
        ultrasonicDetect = grovepi.ultrasonicRead(ultrasonicPort)
        print(ultrasonicDetect)
        if ultrasonicDetect > limit:
            print("Afstand is groter dan limit. Geen blister aanwezig.")
            present = False
        elif ultrasonicDetect <= limit:
            print("Afstand is kleiner dan limit. Blister aanwezig.")
            present = True

    except TypeError:
        print("TypeError")
    except IOError:
        print("IOError")

# Bewijs dat het werkt
while True:
    proxDetect()
    print(present)
    time.sleep(5)
