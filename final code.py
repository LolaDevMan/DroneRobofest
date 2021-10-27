from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time
import argparse
import sys
import cv2

parser = argparse.ArgumentParser()
parser.add_argument("--connect", default="/dev/ttyACM0")
args = parser.parse_args()

cap = cv2.VideoCapture(0)
clip=cv2.VideoWriter('clip.avi')

# Connect to the Vehicle
print("Connecting to vehicle on: %s" % args.connect)
vehicle = connect(args.connect, baud=921600, wait_ready=True)

# Function to arm and then takeoff to a user specified altitude
def arm_and_takeoff(aTargetAltitude):
    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Check that vehicle has reached takeoff altitude
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


arm_and_takeoff(3)
print("Take off complete\n")

while True:
    _, frame = cap.read()
    
    res=cv2.QRCodeDetector().detectAndDecode(frame)

    if  res=='b':
        print("Break\n")
        break

    elif res=='a':
        print("Circle\n")
        vehicle.parameters["CIRCLE_RADIUS"] = 10
        vehicle.mode = VehicleMode("CIRCLE")

    if cv2.waitKey(5) & 0xFF == ord("q"):
        break

print("Return to launch")
vehicle.parameters["RTL_ALT"] = 0
vehicle.mode = VehicleMode("RTL")

cap.release()
vehicle.close()