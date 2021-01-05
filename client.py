# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@ Client.py by Syed Afraz & Muhammad Abdullah @@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

from socket import *
import select
import time
import os
import sys
from os import path
import threading

""" IMPORTANT README """
# Run script using the following command in linux terminal.
# python3 client.py -i 3 -o <Output file name> -a <Server IP> -p 21018 27215 35416 19222 39223


# --------- Retrieve info from the terminal command ---------
argSize = len(sys.argv)
argList = sys.argv
# print(argSize, argList)

# --------- Constants ---------
METRIC_INTERVAL = int(argList[2])
OUTPUT_LOCATION = (argList[4])
PORT_NUMBERS = [21018, 27215, 35416, 19222, 39223]
SERVER_IP = argList[6]

# --------- Populating PORT_NUMBERS with 'n' number of ports ---------
for n in range(8, argSize):
    port = int(argList[n])
    PORT_NUMBERS.append(port)

# Write your IP here
serverIP = SERVER_IP

# Each Segment Size
fileSize = 0  # Will be re assigned later.

# Timer for the functions
startServer1 = 0.00
startServer2 = 0.00
startServer3 = 0.00
startServer4 = 0.00
finishServer1 = 0.00
finishServer2 = 0.00
finishServer3 = 0.00
finishServer4 = 0.00
totalServer1 = 0.00
totalServer2 = 0.00
totalServer3 = 0.00
totalServer4 = 0.00

# Download Speed
speedServer1 = 0
speedServer2 = 0
speedServer3 = 0
speedServer4 = 0

# Average Speed Variable
speed = 0

# Variable to divide average speed with
divideBy = 1

# When download is complete from a server and the correct average spped is required.
multiplyBy = 1.00

# A counter to check how many servers have finished sending all of the data
count = 0

# Checking if all servers are running
server1Active = True  # Will be toggled off whenever Server 5 notifies.
server2Active = True  # Will be toggled off whenever Server 5 notifies.
server3Active = True  # Will be toggled off whenever Server 5 notifies.
server4Active = True  # Will be toggled off whenever Server 5 notifies.
server5Active = True  # Will always stay active

# 4 client sockets to deal with wach server.
clientSocket1 = socket(AF_INET, SOCK_STREAM)
clientSocket2 = socket(AF_INET, SOCK_STREAM)
clientSocket3 = socket(AF_INET, SOCK_STREAM)
clientSocket4 = socket(AF_INET, SOCK_STREAM)
clientSocket5 = socket(AF_INET, SOCK_STREAM)  # To check server status

# Pre-determined Server ports
serverPort1 = PORT_NUMBERS[0]
serverPort2 = PORT_NUMBERS[1]
serverPort3 = PORT_NUMBERS[2]
serverPort4 = PORT_NUMBERS[3]
serverPort5 = PORT_NUMBERS[4]

# x arrays hold data about received segments, will be used in load balancing.
x1 = []
x2 = []
x3 = []
x4 = []

# Connection establishment, try/except blocks to check if any server is down right from the start.
try:
    clientSocket1.connect((serverIP, serverPort1))
except Exception as e:
    server1Active = False
try:
    clientSocket2.connect((serverIP, serverPort2))
except Exception as e:
    server2Active = False
try:
    clientSocket3.connect((serverIP, serverPort3))
except Exception as e:
    server3Active = False
try:
    clientSocket4.connect((serverIP, serverPort4))
except Exception as e:
    server4Active = False
try:
    clientSocket5.connect((serverIP, serverPort5))
except Exception as e:
    server5Active = False  # Unlikely scenario, Server 5 should always be up.


def Server1():
    global server1Active
    # Initial load balancing.
    y1, y2, y3, y4 = loadBalancing()
    while True:  # Run till Server active
        # IMPORTANT, delay process so Server 5 can notify if any servers have gone down on the other side(gives time to load balance efficiently).
        # Delay is machine dependent. 3 seconds seemed safe.
        time.sleep(3)
        # Break out of loop if server is down
        if (server1Active == False) or (server2Active == False) or (server3Active == False) or (server4Active == False):
            if(server1Active == False):
                continue
            else:  # If some other server is down, redo load balancing.
                y1, y2, y3, y4 = loadBalancing()
        try:
            # Midway server status check.
            if(server1Active == False):
                continue
            # Redo load balancing to ensure data integrity in transfers
            y1, y2, y3, y4 = loadBalancing()
            # print("Server 1:", y1) # Debugging code, prints load balanced list.
            # Create/open file to write onto.
            file = open("SegFrom"+str(y1[0])+".mp4", "wb+")
            # Convert To String
            y1 = str(y1)
            # Encode String
            y1 = y1.encode()
            # Send Encoded String version of the List
            # Sends list containing IDs of required segments.
            clientSocket1.send(y1)
            # Rechecking server status before file writing begins.
            if(server1Active == False):
                continue
            else:  # If server is Up, do the following
                global startServer1
                startServer1 = time.perf_counter()
                fileData = clientSocket1.recv(100000000)
                file.write(fileData)
                # Calculate segment size
                sizeFile = os.stat(file.name).st_size
                if (sizeFile == 0):
                    continue
                else:
                    global fileSize
                    fileSize = (sizeFile/1000)
                # Forcefully transfer data to be written to disk from runtime buffer to system buffer using flush.
                file.flush()
                y1 = eval(y1.decode())
                # Print to confirm when file is received.
                # print("File "+str(y1[0])+" received by Server 1.")
                file.close()  # Close to save/confirm changes.
                global finishServer1
                finishServer1 = time.perf_counter()
                global totalServer1
                totalServer1 = round(finishServer1 - startServer1, 2)
                global speedServer1
                speedServer1 = round((fileSize)/totalServer1, 2)
                # Append x1 with first element of y1. x1 acts like proof of segments received.
                x1.append(y1.pop(0))
                continue
        except Exception as e:
            # This block executes when all segments have been received, last minute prgramming before quitting to be done here.
            # print("Server 1 connection over")
            server1Active = False
            speedServer1 = 0
            global multiplyBy
            global count
            count += 1
            break
    clientSocket1.close()


def Server2():
    global server2Active
    # Initial load balancing.
    y1, y2, y3, y4 = loadBalancing()
    while True:  # Run till Server active
        # IMPORTANT, delay process so Server 5 can notify if any servers have gone down on the other side(gives time to load balance efficiently).
        # Delay is machine dependent. 3 seconds seemed safe.
        time.sleep(3)
        # Break out of loop if server is down
        if (server1Active == False) or (server2Active == False) or (server3Active == False) or (server4Active == False):  # Exit loop if server is down
            if(server2Active == False):
                continue
            else:  # If some other server is down, redo load balancing.
                y1, y2, y3, y4 = loadBalancing()
        try:
            # Midway server status check.
            if(server2Active == False):
                continue
            # Redo load balancing to ensure data integrity in transfers
            y1, y2, y3, y4 = loadBalancing()
            # print("Server 2:", y2) # Debugging code, prints load balanced list.
            # Create/open file to write onto.
            file = open("SegFrom"+str(y2[0])+".mp4", "wb+")
            # Convert To String
            y2 = str(y2)
            # Encode String
            y2 = y2.encode()
            # Send Encoded String version of the List.
            # Sends list containing IDs of required segments.
            clientSocket2.send(y2)
            # Rechecking server status before file writing begins.
            if(server2Active == False):
                continue
            else:  # If server is up do the following
                global startServer2
                startServer2 = time.perf_counter()
                fileData = clientSocket2.recv(100000000)
                file.write(fileData)
                sizeFile = os.stat(file.name).st_size
                if (sizeFile == 0):
                    continue
                else:
                    global fileSize
                    fileSize = (sizeFile/1000)
                # Forcefully transfer data to be written to disk from runtime buffer to system buffer using flush.
                file.flush()
                y2 = eval(y2.decode())
                # Print to confirm when file is received.
                # print("File "+str(y2[0])+" received by Server 2.")
                file.close()
                global finishServer2
                finishServer2 = time.perf_counter()
                global totalServer2
                totalServer2 = round(finishServer2 - startServer2, 2)
                global speedServer2
                speedServer2 = round((fileSize)/totalServer2, 2)
                # Append x2 with first element of y2. x2 acts like proof of segments received.
                x2.append(y2.pop(0))
                continue
        except Exception as e:
            # This block executes when all segments have been received, last minute prgramming before quitting to be done here.
            # print("Server 2 connection over")
            server2Active = False
            speedServer2 = 0
            global count
            count += 1
            break
    clientSocket2.close()


def Server3():
    global server3Active
    # Initial load balancing.
    y1, y2, y3, y4 = loadBalancing()
    while True:  # Run till Server active
        # IMPORTANT, delay process so Server 5 can notify if any servers have gone down on the other side(gives time to load balance efficiently).
        # Delay is machine dependent. 3 seconds seemed safe.
        time.sleep(3)
        # Break out of loop if server is down
        if (server1Active == False) or (server2Active == False) or (server3Active == False) or (server4Active == False):  # Exit loop if server is down
            if(server3Active == False):
                continue
            else:  # If some other server is down, redo load balancing.
                y1, y2, y3, y4 = loadBalancing()
        try:
            # Midway server status check.
            if(server3Active == False):
                continue
            # Redo load balancing to ensure data integrity in transfers
            y1, y2, y3, y4 = loadBalancing()
            # print("Server 3:", y3) # Debugging code, prints load balanced list.
            # Create/open file to write onto.
            file = open("SegFrom"+str(y3[0])+".mp4", "wb+")
            # Convert To String
            y3 = str(y3)
            # Encode String
            y3 = y3.encode()
            # Send Encoded String version of the List
            # Sends list containing IDs of required segments.
            clientSocket3.send(y3)
            # Rechecking server status before file writing begins.
            if(server3Active == False):
                continue
            else:  # If server is up, do the following
                global startServer3
                startServer3 = time.perf_counter()
                fileData = clientSocket3.recv(100000000)
                file.write(fileData)
                sizeFile = os.stat(file.name).st_size
                if (sizeFile == 0):
                    continue
                else:
                    global fileSize
                    fileSize = (sizeFile/1000)
                # Forcefully transfer data to be written to disk from runtime buffer to system buffer using flush.
                file.flush()
                y3 = eval(y3.decode())
                # print("File "+str(y3[0])+" received by Server 3.")
                file.close()
                # Append x3 with first element of y3. x3 acts like proof of segments received.
                global finishServer3
                finishServer3 = time.perf_counter()
                global totalServer3
                totalServer3 = round(finishServer3 - startServer3, 2)
                global speedServer3
                speedServer3 = round((fileSize)/totalServer3, 2)
                x3.append(y3.pop(0))
                continue
        except Exception as e:
            # This block executes when all segments have been received, last minute prgramming before quitting to be done here.
            # print("Server 3 connection over")
            server3Active = False
            speedServer3 = 0
            global count
            count += 1
            break
    clientSocket3.close()


def Server4():
    global server4Active
    # Initial load balancing.
    y1, y2, y3, y4 = loadBalancing()
    while True:  # Run till Server active
        # IMPORTANT, delay process so Server 5 can notify if any servers have gone down on the other side(gives time to load balance efficiently).
        # Delay is machine dependent. 3 seconds seemed safe.
        time.sleep(3)
        # Break out of loop if server is down
        if (server1Active == False) or (server2Active == False) or (server3Active == False) or (server4Active == False):  # Exit loop if server is down
            if(server4Active == False):
                continue
            else:  # If some other server is down, redo load balancing.
                y1, y2, y3, y4 = loadBalancing()
        try:
            # Midway server status check
            if(server4Active == False):
                continue
            # Redo load balancing to ensure data integrity in transfers
            y1, y2, y3, y4 = loadBalancing()
            # print("Server 4:", y4) # Debugging code, prints load balanced list.
            # Create/open file to write onto.
            file = open("SegFrom"+str(y4[0])+".mp4", "wb+")
            # Convert To String
            y4 = str(y4)
            # Encode String
            y4 = y4.encode()
            # Send Encoded String version of the List
            # Sends list containing IDs of required segments.
            clientSocket4.send(y4)
            # Rechecking server status before file writing begins.
            if(server4Active == False):
                continue
            else:  # If server up, do the following
                global startServer4
                startServer4 = time.perf_counter()
                fileData = clientSocket4.recv(100000000)
                file.write(fileData)
                sizeFile = os.stat(file.name).st_size
                if (sizeFile == 0):
                    continue
                else:
                    global fileSize
                    fileSize = (sizeFile/1000)
                # Forcefully transfer data to be written to disk from runtime buffer to system buffer using flush.
                file.flush()
                y4 = eval(y4.decode())
                # print("File "+str(y4[0])+" received by Server 4.")
                file.close()
                global finishServer4
                finishServer4 = time.perf_counter()
                global totalServer4
                totalServer4 = round(finishServer4 - startServer4, 2)
                global speedServer4
                speedServer4 = round((fileSize)/totalServer4, 2)
                # Append x4 with first element of y4. x4 acts like proof of segments received.
                x4.append(y4.pop(0))
                continue
        except Exception as e:
            # This block executes when all segments have been received, last minute prgramming before quitting to be done here.
            # print("Server 4 connection over")
            server4Active = False
            speedServer4 = 0
            global count
            count += 1
            break
    clientSocket4.close()

# Server 5 sends "live status" of all other servers to this function of client, this function is responsible of toggling serverActive(s) to true/false in real time.


def Server5():
    while True:
        try:
            status = clientSocket5.recv(100000000)
            status = status.decode('utf-8')
            status = status[:12]
            status = eval(status)
            for each in range(len(status)):
                if(each == 0):
                    global server1Active
                    if status[0] == 0:
                        server1Active = False
                    else:
                        server1Active = True
                elif(each == 1):
                    global server2Active
                    if status[1] == 0:
                        server2Active = False
                    else:
                        server2Active = True
                elif(each == 2):
                    global server3Active
                    if status[2] == 0:
                        server3Active = False
                    else:
                        server3Active = True
                elif(each == 3):
                    global server4Active
                    if status[3] == 0:
                        server4Active = False
                    else:
                        server4Active = True
        except Exception as e:
            continue  # Should run regardless of receiving updates or not.
    clientSocket5.close()

# Function used in metric reporting to tell count of servers down.


def counter():
    global count
    global multiplyBy
    while True:
        if(count == 0):
            break
        elif(count == 1):
            multiplyBy = 4/3
            break
        elif(count == 2):
            multiplyBy = 2
            break
        elif(count == 3):
            multiplyBy = 4
            break
        elif(count == 4):
            multiplyBy = 0
            break
    return multiplyBy


# ----------------------------------------
# -------- Recombining video file --------
# ----------------------------------------

# This function first creates an empty .mp4 file, then, using a loop, each segmented file is visited(read) and concatenated to the new mp4 file.

def recombination(fileName):
    splitSize = 12  # Recombines 12 segments into 1
    try:
        file = open(fileName, "ab")
        for i in range(1, (splitSize + 1)):
            if path.exists("SegFrom" + str(i) + ".mp4"):
                f = open("SegFrom" + str(i) + ".mp4", "rb")
                file.write(f.read())
                f.close()
            else:
                raise IOError
        file.close()
    except IOError:
        print("Failed to recombine")

# Function used to balance load among servers in realtime. Works on reading x and y arrays.
# x is a list of received segments.
# y is a list of required segments.


def loadBalancing():
    # [item for item in [1, 2, 3] if item not in set(x1)]
    # This basically is A - B in Set theory where A is [1,2,3] and B is x1(set of already received segments).
    # Finally yn is a Set of segments we want server to send us.
    global speedServer1
    global speedServer2
    global speedServer3
    global speedServer4

    global divideBy

    if(server1Active == True and server2Active == True and server3Active == True and server4Active == True):
        divideBy = 4
        y1 = [item for item in [1, 2, 3]
              if item not in set([*x1, *x2, *x3, *x4])]
        y2 = [item for item in [4, 5, 6]
              if item not in set([*x1, *x2, *x3, *x4])]
        y3 = [item for item in [7, 8, 9]
              if item not in set([*x1, *x2, *x3, *x4])]
        y4 = [item for item in [10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
    elif(server1Active == False and server2Active == True and server3Active == True and server4Active == True):
        speedServer1 = 0
        divideBy = 3
        y1 = []
        y2 = [item for item in [1, 2, 3, 4]
              if item not in set([*x1, *x2, *x3, *x4])]
        y3 = [item for item in [5, 6, 7, 8]
              if item not in set([*x1, *x2, *x3, *x4])]
        y4 = [item for item in [9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
    elif(server1Active == True and server2Active == False and server3Active == True and server4Active == True):
        speedServer2 = 0
        divideBy = 3
        y1 = [item for item in [1, 2, 3, 4]
              if item not in set([*x1, *x2, *x3, *x4])]
        y2 = []
        y3 = [item for item in [5, 6, 7, 8]
              if item not in set([*x1, *x2, *x3, *x4])]
        y4 = [item for item in [9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
    elif(server1Active == True and server2Active == True and server3Active == False and server4Active == True):
        speedServer3 = 0
        divideBy = 3
        y1 = [item for item in [1, 2, 3, 4]
              if item not in set([*x1, *x2, *x3, *x4])]
        y2 = [item for item in [5, 6, 7, 8]
              if item not in set([*x1, *x2, *x3, *x4])]
        y3 = []
        y4 = [item for item in [9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
    elif(server1Active == True and server2Active == True and server3Active == True and server4Active == False):
        speedServer4 = 0
        divideBy = 3
        y1 = [item for item in [1, 2, 3, 4]
              if item not in set([*x1, *x2, *x3, *x4])]
        y2 = [item for item in [5, 6, 7, 8]
              if item not in set([*x1, *x2, *x3, *x4])]
        y3 = [item for item in [9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
        y4 = []
    elif(server1Active == False and server2Active == False and server3Active == True and server4Active == True):
        speedServer1 = 0
        speedServer2 = 0
        divideBy = 2
        y1 = []
        y2 = []
        y3 = [item for item in [1, 2, 3, 4, 5, 6]
              if item not in set([*x1, *x2, *x3, *x4])]
        y4 = [item for item in [7, 8, 9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
    elif(server1Active == False and server2Active == True and server3Active == False and server4Active == True):
        speedServer1 = 0
        speedServer3 = 0
        divideBy = 2
        y1 = []
        y2 = [item for item in [1, 2, 3, 4, 5, 6]
              if item not in set([*x1, *x2, *x3, *x4])]
        y3 = []
        y4 = [item for item in [7, 8, 9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
    elif(server1Active == False and server2Active == True and server3Active == True and server4Active == False):
        speedServer1 = 0
        speedServer4 = 0
        divideBy = 2
        y1 = []
        y2 = [item for item in [1, 2, 3, 4, 5, 6]
              if item not in set([*x1, *x2, *x3, *x4])]
        y3 = [item for item in [7, 8, 9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
        y4 = []
    elif(server1Active == True and server2Active == False and server3Active == False and server4Active == True):
        speedServer2 = 0
        speedServer3 = 0
        divideBy = 2
        y1 = [item for item in [1, 2, 3, 4, 5, 6]
              if item not in set([*x1, *x2, *x3, *x4])]
        y2 = []
        y3 = []
        y4 = [item for item in [7, 8, 9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
    elif (server1Active == True and server2Active == False and server3Active == True and server4Active == False):
        speedServer2 = 0
        speedServer4 = 0
        divideBy = 2
        y1 = [item for item in [1, 2, 3, 4, 5, 6]
              if item not in set([*x1, *x2, *x3, *x4])]
        y2 = []
        y3 = [item for item in [7, 8, 9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
        y4 = []
    elif (server1Active == True and server2Active == True and server3Active == False and server4Active == False):
        speedServer3 = 0
        speedServer4 = 0
        divideBy = 2
        y1 = [item for item in [1, 2, 3, 4, 5, 6]
              if item not in set([*x1, *x2, *x3, *x4])]
        y2 = [item for item in [7, 8, 9, 10, 11, 12]
              if item not in set([*x1, *x2, *x3, *x4])]
        y3 = []
        y4 = []
    elif(server1Active == False and server2Active == False and server3Active == False and server4Active == True):
        speedServer1 = 0
        speedServer2 = 0
        speedServer3 = 0
        divideBy = 1
        y1 = []
        y2 = []
        y3 = []
        y4 = [item for item in [1, 2, 3, 4, 5, 6, 7, 8, 9,
                                10, 11, 12] if item not in set([*x1, *x2, *x3, *x4])]
    elif (server1Active == False and server2Active == False and server3Active == True and server4Active == False):
        speedServer1 = 0
        speedServer2 = 0
        speedServer4 = 0
        divideBy = 1
        y1 = []
        y2 = []
        y3 = [item for item in [1, 2, 3, 4, 5, 6, 7, 8, 9,
                                10, 11, 12] if item not in set([*x1, *x2, *x3, *x4])]
        y4 = []
    elif (server1Active == False and server2Active == True and server3Active == False and server4Active == False):
        speedServer1 = 0
        speedServer3 = 0
        speedServer4 = 0
        divideBy = 1
        y1 = []
        y2 = [item for item in [1, 2, 3, 4, 5, 6, 7, 8, 9,
                                10, 11, 12] if item not in set([*x1, *x2, *x3, *x4])]
        y3 = []
        y4 = []
    elif (server1Active == True and server2Active == False and server3Active == False and server4Active == False):
        speedServer2 = 0
        speedServer3 = 0
        speedServer4 = 0
        divideBy = 1
        y1 = [item for item in [1, 2, 3, 4, 5, 6, 7, 8, 9,
                                10, 11, 12] if item not in set([*x1, *x2, *x3, *x4])]
        y2 = []
        y3 = []
        y4 = []
    elif (server1Active == False and server2Active == False and server3Active == False and server4Active == False):
        speedServer1 = 0
        speedServer2 = 0
        speedServer3 = 0
        speedServer4 = 0
        divideBy = 1
        y1 = []
        y2 = []
        y3 = []
        y4 = []
    return y1, y2, y3, y4

# Function to calculate total average speed catering all individual speeds of servers.


def avgSpeed():
    global speed
    speed = round(((speedServer1 + speedServer2 + speedServer3
                    + speedServer4)/divideBy)*multiplyBy, 2)
    return speed


def metricReporting():
    # arbitaryCounter needed to go in loop one extra time at the end as it will buy time for all speedServer to become 0, so total speed can be 0 too.
    arbitaryCounter = 0
    while True:
        y1, y2, y3, y4 = loadBalancing()

        global multiplyBy
        multiplyBy = counter()

        print("Server1: " + str(round(len(x1) * fileSize, 2)) + "/" + str(round((len(x1) + len(y1)) * fileSize, 2)) +
              ", download speed: " + str(speedServer1) + "kb/s")
        print("Server2: " + str(round(len(x2) * fileSize, 2)) + "/" + str(round((len(x2) + len(y2)) * fileSize, 2)) +
              ", download speed: " + str(speedServer2) + "kb/s")
        print("Server3: " + str(round(len(x3) * fileSize, 2)) + "/" + str(round((len(x3) + len(y3)) * fileSize, 2)) +
              ", download speed: " + str(speedServer3) + "kb/s")
        print("Server4: " + str(round(len(x4) * fileSize, 2)) + "/" + str(round((len(x4) + len(y4)) * fileSize, 2)) +
              ", download speed: " + str(speedServer4) + "kb/s")
        print("Total: " + str(round(((len(x1) + len(x2) + len(x3) + len(x4)) * fileSize), 2)) +
              ", download speed: " + str(avgSpeed()) + "kb/s")

        if ((len(x1) + len(x2) + len(x3) + len(x4)) == 12):
            if arbitaryCounter != 1:  # Going in loop one extra time here.
                arbitaryCounter = arbitaryCounter + 1
                # Intentional delay for individual speeds to be 0.
                time.sleep(3)
                continue
            else:
                break
        else:
            time.sleep(METRIC_INTERVAL)
            os.system("clear")
            continue

    while True:
        # Check if all segments have been received.
        if (os.path.isfile('./SegFrom1.mp4') and os.stat("SegFrom1.mp4").st_size != 0) and (os.path.isfile('./SegFrom2.mp4') and os.stat("SegFrom2.mp4").st_size != 0) and (os.path.isfile('./SegFrom3.mp4') and os.stat("SegFrom3.mp4").st_size != 0) and (os.path.isfile('./SegFrom4.mp4') and os.stat("SegFrom4.mp4").st_size != 0) and (os.path.isfile('./SegFrom5.mp4') and os.stat("SegFrom5.mp4").st_size != 0) and (os.path.isfile('./SegFrom6.mp4') and os.stat("SegFrom6.mp4").st_size != 0) and (os.path.isfile('./SegFrom7.mp4') and os.stat("SegFrom7.mp4").st_size != 0) and (os.path.isfile('./SegFrom8.mp4') and os.stat("SegFrom8.mp4").st_size != 0) and (os.path.isfile('./SegFrom9.mp4') and os.stat("SegFrom9.mp4").st_size != 0) and (os.path.isfile('./SegFrom10.mp4') and os.stat("SegFrom10.mp4").st_size != 0) and (os.path.isfile('./SegFrom11.mp4') and os.stat("SegFrom11.mp4").st_size != 0) and (os.path.isfile('./SegFrom12.mp4') and os.stat("SegFrom12.mp4").st_size != 0):
            recombination(OUTPUT_LOCATION)
            print("Final file has been received and saved")
            os._exit(os.EX_OK)
            break
        else:
            continue


tforServer1 = threading.Thread(target=Server1)
tforServer2 = threading.Thread(target=Server2)
tforServer3 = threading.Thread(target=Server3)
tforServer4 = threading.Thread(target=Server4)
tforServer5 = threading.Thread(target=Server5)
tforMetricReporting = threading.Thread(target=metricReporting)


tforServer1.start()
time.sleep(0.04)
tforServer2.start()
time.sleep(0.04)
tforServer3.start()
time.sleep(0.04)
tforServer4.start()
time.sleep(0.04)
tforMetricReporting.start()
time.sleep(0.04)
tforServer5.start()
time.sleep(0.04)

tforServer1.join()
tforServer2.join()
tforServer3.join()
tforServer4.join()
tforMetricReporting.join()

tforServer5.join()
