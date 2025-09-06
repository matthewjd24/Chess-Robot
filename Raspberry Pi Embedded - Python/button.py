from gpiozero import Button
import time

# Configure button with pull-down resistor
button = Button(26, pull_up=True)

def is_pressed():
	return button.is_pressed

def WaitForPress():
	print(f"Waiting for button press")

	while True:
		if button.is_pressed:
			print(f"Button pressed!")
			return
		time.sleep(0.01)

# is_pressed = False
# while True:
# 	if button.is_pressed == True and is_pressed == False:
# 		print("Press!")
# 		is_pressed = True
# 	elif button.is_pressed == False and is_pressed == True:
# 		print("Release!")
# 		is_pressed = False