import serial
import time
ser = serial.Serial('COM3', 115200, timeout=5)
time.sleep(5)

#<Timestamp, track number, MIDI channel, type, key, value>
ser.write('<0,0,0,8,0,0>')
ser.write('<0,0,0,7,0,0>')
