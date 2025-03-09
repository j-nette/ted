# This is a testing script to communicate with the board
import serial
import serial.tools.list_ports
import time

try:
    board_ports = [p.device
      for p in serial.tools.list_ports.comports()
      if 'CH340' in p.description 
    ]
    
    if not board_ports:
        raise IOError("No board found.")

    ser = board_ports[0] # take first board if multiple?

    serialData = serial.Serial(port=ser, baudrate=9600, timeout=2)
    
except(serial.SerialException):
  print(serial.SerialException)
  print("Port in use - close other serial monitors.")

def write_read(x: str): 
  serialData.write(bytes(x, 'utf-8')) 
  time.sleep(0.05) 
     
while(True):
  text = input("Enter action: ") # L - left, R - right, U - Both Up, D - Both Down
  write_read(text)