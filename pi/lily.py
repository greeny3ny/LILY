from firebase import firebase
import time
import RPi.GPIO as GPIO

wheel_pins = [7,11,13,15]

halfstep_seq = [
        [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [1,0,0,1]
    ]


#setup GPIO
GPIO.setmode(GPIO.BOARD)
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

for pin in wheel_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

servoPin = 40
GPIO.setup(servoPin, GPIO.OUT)
servo = GPIO.PWM(servoPin, 50)  #(pin, freq)
servo.start(7.5)                #12.5 right, 2.5left

firebase = firebase.FirebaseApplication('https://crogobot.firebaseio.com', None)

firebase.put('/', 'online' , 'Yes') #Turn on website

wheelTickLength = 288
turnTickLength = 144
def motorChange(r):
        
        if (r == "up"):
                print("Forwards!")
                motor_forward(wheelTickLength)
                
        elif (r == "down"):
                print("Backwards!")
                motor_backward(wheelTickLength)
                
        elif (r == "left"):
                print("Left turn")
                servo.ChangeDutyCycle(12.5)
                motor_forward(turnTickLength)
                
        elif (r == "right"):
                print("Right turn!")
                servo.ChangeDutyCycle(2.5)
                motor_forward(turnTickLength)

def movementBuffer():
    
    movementList = firebase.get('/movement', None)
  
    print ("First on list : " + movementList[0])
    if (len(movementList)>1):
        #switch it so it isnt reading "empty"
        if (movementList[0] == "empty"):
                print(movementList[0])
        motorChange(movementList[0]) #Move the motor!
        print ("this should appear after motor moves")
        #movementList = firebase.get('/movement', None) ##Get new database before updating, due to time.sleep function in motorchange
        restOfList = movementList[1:]
        firebase.put('/', 'movement' , restOfList) 
    else:
        motorChange(movementList[0])
        firebase.put('/', 'movement' , ["empty"])

        
def step_mot_control():
    rotation_deg = int(firebase.get('/rot', None))
    if (rotation_deg > 0):
        rotation_ticks = int(rotation_deg*1.6)
        print ("Rotating for : " + str(rotation_ticks))
        for i in range (rotation_ticks):
            for halfstep in range(8):
                for pin in range(4):
                    GPIO.output(wheel_pins[pin], halfstep_seq[halfstep][pin])
                time.sleep(0.001)
    firebase.put('/', 'rot' , '0')

def motor_forward(w):
        for i in range(w):
                for halfstep in range(8):
                        for pin in range(4):
                            GPIO.output(wheel_pins[pin], halfstep_seq[halfstep][pin])
                        time.sleep(0.001)

def motor_backward(w):
        for i in range(w):
                for halfstep in reversed(range(8)):
                        for pin in range(4):
                            GPIO.output(wheel_pins[pin], halfstep_seq[halfstep][pin])
                        time.sleep(0.001)


try:
    while True:
        movementBuffer()
        step_mot_control()
       
        #need to stop the servo to fix the stuttery servo issue
        #servo.ChangeDutyCycle(7.5)

        # approx SERVO VALUES : 
        # 7.5 is in most cases the middle position
        # 12.5 is the value for a 180 degree move to the right
        # 2.5 is the value for a -90 degree move to the left

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Shutting down")
    firebase.put('/', 'online' , 'No')
