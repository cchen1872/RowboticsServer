import data.sensors.TCA9548A as TCA9548A
from data.sse import format_sse

import smbus, time, sys, math
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
 
gpio_pins = [17, 18, 27, 22]
 
# Declare an named instance of class pass a name and type of motor
mymotortest = RpiMotorLib.BYJMotor("MyMotorOne", "Nema")

 
 
AS5600_ADDR = 0x36 # Default AS5600 I2C address

TCA9548A_ADDR = 0x70 # Default Multiplexer I2C address

twist = 0 #channel of twist
flywheel = 1 #channel of flywheel
height = 2 # channel of height angle

bus = smbus.SMBus(1)

I= 0.1001 #kg m^2

LEVEL_TWIST = 240 #Subject to change on calibration

MIN_START_MOVING = 5

IN_WATER_ANGLE = -15

ANGLE_INCREMENTS = 30

CATCH_ANGLE = 170

c = 2.8

def ReadAngle(channel) :# Read angle (0-360 represented as 0-4096)
    TCA9548A.I2C_setup(0x70,channel)
    read_bytes = bus.read_i2c_block_data(AS5600_ADDR, 0x0C, 2)
    raw_angle = (read_bytes[0]<<8) | read_bytes[1]
    return raw_angle*360.0/4096.0



def MoveMotor(direction, angle): #move motor angle degrees. CW = False CCW = True
    
    mymotortest.motor_run(gpio_pins , 0.002, angle*100/360, direction, False, "full", .001)

def ReadSensors(dummy, announcer):
    last_five_angles = [None] * 5
    empty_angle_slots = 5
    curr_angle_slot = 0

    last_five_velocities = [None] * 5
    empty_vel_slots = 5
    curr_vel_slot = 0

    twist_angle = ReadAngle(twist)
    old_twist_angle = twist_angle
    
    above_stroke_bool = True
    total_strokes = 0
    
    flywheel_moving = False
    start_time = None
    
    flywheel_rotations = 0
    last_angle = -1
    while announcer.isOpen():
        P = 0 # initialize power
        k = 0 # initialize drag factor
        
        twist_angle = ReadAngle(twist)
        if abs(twist_angle - old_twist_angle) > 9: # 9 = 90 oar * 18 degrees flywheel/1.8 per step
            if twist_angle > old_twist_angle :
                #increase resistance (prob need to tune the ratio but whatever for now
                MoveMotor(False, (twist_angle - old_twist_angle)/9)
            else:
                #decrease resostamce
                MoveMotor(True, (old_twist_angle - twist_angle)/9)
            old_twist_angle = twist_angle
        
        if above_stroke_bool and twist_angle > LEVEL_TWIST:
            total_strokes += 1
            above_stroke_bool = False
        elif not above_stroke_bool and twist_angle < LEVEL_TWIST:
            above_stroke_bool = True

        if last_angle > twist_angle: #SWAP IF ROTATE TO SMALLER ANGLE
            flywheel_rotations += 1
        last_angle = twist_angle
        
        print("Twist: ","%6.2f deg  "%twist_angle)

        print("#",end="")
        
        
        flywheel_angle = ReadAngle(flywheel)
        print("Flywheel: ","%6.2f deg  "%flywheel_angle)

        height_angle = ReadAngle(height)
        print("Height: ","%6.2f deg  "%height_angle)

        print("#",end="")

        

        curr_time = time.time()
        last_five_angles[curr_angle_slot] = {"angle": flywheel_angle, "time": curr_time}
        curr_angle_slot = (curr_angle_slot + 1) % 5
        omega = 0
        total_time = 0
        if empty_angle_slots == 0:
            for i in range(1, 5):
                time_change = last_five_angles[i]["time"] - last_five_angles[i - 1]["time"]
                angle_change = (last_five_angles[i]["angle"] - last_five_angles[i - 1]["angle"] + 360) % 360
                omega += (angle_change) * time_change
                total_time += time_change
            omega /= total_time
            last_five_velocities[curr_vel_slot] = {"velocity":omega, "time":curr_time}
            curr_vel_slot = (curr_vel_slot + 1) % 5
            total_time = 0
            alpha = 0
            if not flywheel_moving and omega > MIN_START_MOVING:
                flywheel_moving = True
                start_time = time.time()
                
            if empty_vel_slots == 0:
                for i in range(1, 5):
                    time_change = last_five_velocities[i]["time"] - last_five_velocities[i - 1]["time"]
                    vel_change = last_five_velocities[i]["velocity"] - last_five_velocities[i - 1]["velocity"]
                    alpha += (vel_change) * time_change
                    total_time += time_change
                alpha /= total_time
            else:
                empty_vel_slots -= 1
            if omega == 0:
                k = 0
            else:
                k=-I*alpha*1/pow(omega, 2)*180/math.pi
            P = I * alpha * omega * pow(math.pi/180, 3)
        else:
            empty_angle_slots -= 1
        
        if flywheel_moving and start_time != curr_time:
            dictionary = {"twist_angle":(twist_angle - CATCH_ANGLE) % ANGLE_INCREMENTS,
                          "in_water":"IN WATER" if (height_angle > IN_WATER_ANGLE) else "OUT OF WATER",
                          "time_diff_sec":(curr_time - start_time) % 60 // 1,
                          "time_diff_min":(curr_time - start_time) // 60,
                          "pace": 500/60/pow(P/c, 1/3) if pow(P/c, 1/3) else 0,
                          "boat_dist": pow(k/c, 1/3) * flywheel_rotations,
                          "stroke_rate": total_strokes / ((curr_time - start_time)),               
                          }
            msg = format_sse(data=dictionary, event='message')
            announcer.announce(msg)
        
        
        time.sleep(0.10)

