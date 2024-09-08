import pyttsx3

# Initialize the converter
engine = pyttsx3.init()

# Set properties (optional)
engine.setProperty('rate', 160)    # Speed percent (can go over 100)
engine.setProperty('volume', 1)  # Volume 0-1

# Convert text to speech
#engine.say("Ha, you think moving your pawn will save you.")
#engine.say("I'm surprised you've lasted this long.")
#engine.say("My computational power cannot be beaten.")
engine.say("I'm closing in on you now my friend.")


# Wait and let the speech finish
engine.runAndWait()
