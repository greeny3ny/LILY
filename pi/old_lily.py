from firebase import firebase
import time
import RPi.GPIO as GPIO

"""
TODO:
POSSIBLY REPLACE OLD MOTORS WITH NEW MOTORS
"""
mtrBfor = 5 #19        #orig 7, changing so step_mot works
mtrBbac = 8 #21

mtrAfor = 9 #24
mtrAbac = 10 #26

triggerPin = 17
echoPin = 18

step_mot_pins = [7,11,13,15]

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
GPIO.setwarnings(False)
#GPIO.setup(forwardPin, GPIO.OUT)
#GPIO.setup(backPin, GPIO.OUT)
#GPIO.setup(rightPin, GPIO.OUT)
#GPIO.setup(leftPin, GPIO.OUT)
#GPIO.setup(motorPin, GPIO.OUT)

for pin in step_mot_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

#GPIO.setup(mtrAfor, GPIO.OUT)
#GPIO.setup(mtrAbac, GPIO.OUT)

#GPIO.setup(mtrBfor, GPIO.OUT)
#GPIO.setup(mtrBbac, GPIO.OUT)

#GPIO.setup(triggerPin, GPIO.OUT)
#GPIO.setup(echoPin, GPIO.IN)


#buzzer - disabled currently
#GPIO.setup(40, GPIO.OUT)

#(pin, freq)
#servo = GPIO.PWM(motorPin, 50)
#servo.start(7.5)

firebase = firebase.FirebaseApplication('https://crogobot.firebaseio.com', None)

firebase.put('/', 'online' , 'Yes') #Turn on website

def editLight(r):
    if (r == 'up'):
        print ("MOVING FORWARD")
        #GPIO.output(forwardPin, GPIO.HIGH)
    elif (r == 'down'):
        print ("MOVING BACKWARD")
        #GPIO.output(backPin, GPIO.HIGH)
    elif (r == 'right'):
        print ("TURNING RIGHT")
        #GPIO.output(rightPin, GPIO.HIGH)
    elif (r == 'left'):
        print ("TURNING LEFT")
        #GPIO.output(leftPin, GPIO.HIGH)
    elif (r == 'horn'):
        print ("SERVO TEST")
        servo.ChangeDutyCycle(2.5)
        time.sleep(1)
        servo.ChangeDutyCycle(12.5)
        #GPIO.output(40, GPIO.LOW)
    else:
        print ("FULL STOP")

turnTime = 0.3
moveTime = 0.8
def motorChange(r):
    if (r == "up"):
        print("Forwards!")
        #GPIO.output(mtrAbac, 0) #no movement backwards
        #GPIO.output(mtrAfor, 1) #forward movement!
        
        #GPIO.output(mtrBbac, 0) #no movement backwards
        #GPIO.output(mtrBfor, 1) #forward movement!

        time.sleep(moveTime)
        motorStop()
    elif (r == "down"):
        print("Backwards!")
        #GPIO.output(mtrAbac, 1) #no movement backwards
        #GPIO.output(mtrAfor, 0) #forward movement!
        
        #GPIO.output(mtrBbac, 1) #no movement backwards
        #GPIO.output(mtrBfor, 0) #forward movement!

        time.sleep(moveTime)
        motorStop()
    elif (r == "left"):
        print("Left turn")
       # GPIO.output(mtrAbac, 0) #no movement backwards
        #GPIO.output(mtrAfor, 1) #forward movement!
        
       # GPIO.output(mtrBbac, 1) #no movement backwards
       # GPIO.output(mtrBfor, 0) #forward movement!

        time.sleep(turnTime)
        motorStop()
    elif (r == "right"):
        print("Right turn!")
       # GPIO.output(mtrAbac, 1) #no movement backwards
       # GPIO.output(mtrAfor, 0) #forward movement!
        
       # GPIO.output(mtrBbac, 0) #no movement backwards
      #  GPIO.output(mtrBfor, 1) #forward movement!

        time.sleep(turnTime)
        motorStop()

#Stop all motor movement!
def motorStop():
    print ("allstop")
       # GPIO.output(mtrAbac, 0) 
      #  GPIO.output(mtrAfor, 0) 
      #  GPIO.output(mtrBbac, 0) 
      #  GPIO.output(mtrBfor, 0) 

def movementBuffer():
    
    movementList = firebase.get('/movement', None)
  
    print ("First on list : " + movementList[0])
    if (len(movementList)>1):
        motorChange(movementList[0]) #Move the motor!
        movementList = firebase.get('/movement', None) ##Get new database before updating, due to time.sleep function in motorchange
        restOfList = movementList[1:]
        firebase.put('/', 'movement' , restOfList) 
    else:
        motorChange(movementList[0])
        firebase.put('/', 'movement' , ["empty"])

        
#TO DO:
# Make this more efficient!!!

def step_mot_control():
    
    rotation_deg = int(firebase.get('/rot', None))
    
    print  (rotation_deg)
    
    
    
    if (rotation_deg > 0):
        rotation_ticks = int(rotation_deg*1.6)
        
        print (rotation_ticks)
        
        for i in range (rotation_ticks):
            for halfstep in range(8):
                for pin in range(4):
                    GPIO.output(step_mot_pins[pin], halfstep_seq[halfstep][pin])
                time.sleep(0.001)
        
    firebase.put('/', 'rot' , '0')

try:
    while True:
        result = firebase.get('/cont', None)

        movementBuffer()

        #thread the rest?
        
        #editLight(result)
        #print(result)
        #checkResult(result)
        ##remove first instance of 
        

        #servoRotation = firebase.get('/servo', None)
        #setServo(servoRotation)
        time.sleep(0.5)

        #RESET ALL HERE
        motorStop()
        step_mot_control()

        #GPIO.output(forwardPin, GPIO.LOW)
        #GPIO.output(backPin, GPIO.LOW)
        #GPIO.output(rightPin, GPIO.LOW)
        #GPIO.output(leftPin, GPIO.LOW)

        #need to stop the servo to fix the stuttery servo issue
        #servo.ChangeDutyCycle(7.5)

        # You can play with the values.
        # 7.5 is in most cases the middle position
        # 12.5 is the value for a 180 degree move to the right
        # 2.5 is the value for a -90 degree move to the left

        #Buzzer - disabled
        #GPIO.output(40, GPIO.HIGH)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Shutting down")
    firebase.put('/', 'online' , 'No')
