# Snippet voor de detectie van een blister in de dispenser
# Zorg dat grovepi.py in dezelfde map staat als onderstaande snippet
import grovepi

# Poortnummer voor de ultrasonic ranger (standaard D4)
ultrasonicPort = 4

# Grens tussen wel/niet aanwezig
limit = 10

while True:
    try:
        # Afstand bepalen m.b.v. sensor
        ultrasonicDetected = grovepi.ultrasonicRead(ultrasonicPort)
        print(ultrasonicDetected)
        if ultrasonicDetected > limit:
            print("Afstand is groter dan limit. Geen blister aanwezig.")
        elif ultrasonicDetected <= limit:
            print("Afstand is kleiner dan limit. Blister aanwezig.")
        else:
            print("Er is iets mis gegaan.")

    except TypeError:
        print ("TypeError")
    except IOError:
        print ("IOError")

print("Exit")