# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@ Server.py by Syed Afraz & Muhammad Abdullah @@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

from socket import *
import sys
import time
import multiprocessing
import subprocess
import math
import os
from os import path
from stat import *  # ST_SIZE etc
import threading

"""IMPORTANT README"""
# Run script using the following command in linux terminal.
# python3 server.py -i 2 -n 4 -f <fileName.mp4> -a <Your IP Address> -p 21018 27215 35416 19222 39223


class Server:
    'Common base class for all servers.'

# --------- Global Variables ---------
    serverIpAddr = ""  # Constructor updates this.
    splitSize = 12  # Divide a file into these many parts(User can provide)
    serverNumber = 1  # Will be re-assigned by constructor.
    liveStatus = "Alive"  # Status toggled on/off
    shutdown = [False, False, False, False]
    # shutdown list is shared between instances, i.e. if one object changes it, the change is reflected to all objects. It starts with all False because all servers are up initially.


# --------- Constructor ---------


    def __init__(self, splitSize, serverNumber, serverIpAddr):
        self.splitSize = splitSize
        self.serverNumber = serverNumber
        self.serverIpAddr = serverIpAddr
        # print("Constructing server...")


# ----------------------------------------
# --------- Segmenting video file --------
# ----------------------------------------

# This function is used to divide the length(in bytes) of a mp4 file by a constant to create a variable called splitCount. Next, a for loop is used that runs from 0 to total length. Each iteration is splitCount apart. Inside the loop we use a conditional that identifies if we're on the last segment because the size of the last segment differs from all other segments. Lastly, we create and save each file with its respective size.


    def ceilDiv(self, a, b):
        return int(math.ceil(a / float(b)))

    def segmentation(self, fileName):
        try:
            file = open(fileName, "rb")
            data = file.read()
            splitCount = self.ceilDiv(len(data), self.splitSize)
            # print("file size:", st[ST_SIZE])
            # print(ceilDiv(st[ST_SIZE], 12))
            j = 1
            for i in range(0, len(data), splitCount):
                chunk = data[i:i + splitCount]
                f = open("segment" + str(j) + ".mp4", "wb")
                if i == (self.splitSize - 1) * splitCount:
                    lastSplit = len(data) - ((self.splitSize - 1) * splitCount)
                    chunk = data[i:i + lastSplit]
                    f.write(chunk)
                else:
                    f.write(chunk)
                j += 1
                f.close()
            file.close()
        except IOError:
            print("failed to get information about", fileName)

# ----------------------------------------
# - Socket Programming for Server 1 to 4 -
# ----------------------------------------

    def serverProgram(self, chosenPort):
        serverPort = chosenPort
        serverIP = self.serverIpAddr
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serverSocket.bind((serverIP, serverPort))
        serverSocket.listen(5)
        liveStatus = "Alive"
        conn, address = serverSocket.accept()
        while True:
            try:
                # print("Connection from: " + str(address))
                data = conn.recv(4096)
                # Decode received data into UTF-8
                data = data.decode('utf-8')
                # Convert decoded data into list
                data = eval(data)
                if (self.liveStatus == "Dead"):
                    # print("Im here")
                    continue
                # print(data)
                file1 = open("segment"+str(data[0])+".mp4", "rb")
                fileData = file1.read(100000000)
                conn.send(fileData)
                # print("Segment "+str(data[0]) +
                #       " sent by " + str(self.serverNumber))
                continue
            except Exception as e:
                # Block runs when all segments asked by client have been sent.
                # Do last minute programming here
                # print("Server "+str(self.serverNumber)+" list over")
                continue
        # print("Server not listening")
        # serverSocket.close()

# ---------------------------------------
# --- Socket Programming for Server 5 ---
# ---------------------------------------

    def closingServer(self, chosenPort):
        serverPort = chosenPort
        serverIP = self.serverIpAddr
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serverSocket.bind((serverIP, serverPort))
        serverSocket.listen(5)
        conn, address = serverSocket.accept()
        tempArray = []
        while True:
            try:
                # print("Connection from: " + str(address))
                # x1 is a boolean list that tells which servers are down.
                x1 = []
                for x in range(len(self.shutdown)):  # Loop to populate x1
                    if (self.shutdown[x] == True):
                        x1.append(0)
                        # self.shutdown[x] = False
                    else:
                        x1.append(1)
                if(tempArray == x1):  # If list is same as before, continue
                    continue
                else:  # If list different, send its contents.
                    x1 = str(x1)
                    x1 = x1.encode()
                    conn.send(x1)
            except Exception as e:
                # print("Server 5 connection over.")
                raise e  # Throws exception to try/except in runServer5 block
                break

# Function to carry out the finsihing tasks(updating shutdown array etc..) before a server is forecfully shutdown.

    def kill(self):
        self.liveStatus = "Dead"
        self.shutdown[self.serverNumber-1] = True

# Function to carry out the starting tasks(updating shutdown array etc..) before a server is forecfully woken up.
    def alive(self):
        self.liveStatus = "Alive"
        self.shutdown[self.serverNumber-1] = False


# ----------------------------------------
# ------------- Main function ------------
# ----------------------------------------

def main():
    # --------- Retrieve info from the terminal command ---------
    argSize = len(sys.argv)
    argList = sys.argv
    # print(argSize, argList)

    # --------- Constants ---------
    STATUS_INTERVAL = int(argList[2])
    NUM_OF_SERVERS = int(argList[4])
    PORT_NUMBERS = []
    FILE_NAME = argList[6]
    SERVER_IP = argList[8]
    # PORT_NUMBERS = [21018, 27215, 35416, 19222, 39223]

    # --------- Populating PORT_NUMBERS with 'n' number of ports ---------
    for n in range(10, argSize):
        port = int(argList[n])
        PORT_NUMBERS.append(port)

    # Creating 5 instances of Servers with args as splitSize and serverNumber and common IP Address
    Server1 = Server(12, 1, SERVER_IP)
    Server2 = Server(12, 2, SERVER_IP)
    Server3 = Server(12, 3, SERVER_IP)
    Server4 = Server(12, 4, SERVER_IP)
    Server5 = Server(12, 5, SERVER_IP)

    # Server 1 is responsible of segmentation.
    Server1.segmentation(FILE_NAME)

    # Function to safely exit program.
    def exitProgram():
        p1.terminate()
        p2.terminate()
        p3.terminate()
        p4.terminate()
        os._exit(os.EX_OK)

    # Function to create Server 1, also responsible of file SEGMENTATION
    def runServer1():
        Server1.serverProgram(PORT_NUMBERS[0])

    # Function to create Server 2 only.
    def runServer2():
        Server2.serverProgram(PORT_NUMBERS[1])

    # Function to create Server 3 only.
    def runServer3():
        Server3.serverProgram(PORT_NUMBERS[2])

    # Function to create Server 4 only.
    def runServer4():
        Server4.serverProgram(PORT_NUMBERS[3])

    def runServer5():
        try:
            Server5.closingServer(PORT_NUMBERS[4])
        except Exception as e:
            exitProgram()

    # ------------- Output function ------------

    def output():
        while True:
            print("\n ---------------------")
            print("MultiServer Downloader")
            print(" ---------------------")
            print("Server 1 at Port: " +
                  str(PORT_NUMBERS[0]) + " Status: " + Server1.liveStatus + " To shutdown/wakeup enter 1")
            print("Server 2 at Port: " +
                  str(PORT_NUMBERS[1]) + " Status: " + Server2.liveStatus + " To shutdown/wakeup enter 2")
            print("Server 3 at Port: " +
                  str(PORT_NUMBERS[2]) + " Status: " + Server3.liveStatus + " To shutdown/wakeup enter 3")
            print("Server 4 at Port: " +
                  str(PORT_NUMBERS[3]) + " Status: " + Server4.liveStatus + " To shutdown/wakeup enter 4")
            print("To quit, enter -1: ")
            val = int(input("\nEnter your Choice: "))
            if val == 1:
                if (Server1.liveStatus == "Alive"):
                    Server1.kill()
                else:
                    Server1.alive()
            elif val == 2:
                if (Server2.liveStatus == "Alive"):
                    Server2.kill()
                else:
                    Server2.alive()
            elif val == 3:
                if (Server3.liveStatus == "Alive"):
                    Server3.kill()
                else:
                    Server3.alive()
            elif val == 4:
                if (Server4.liveStatus == "Alive"):
                    Server4.kill()
                else:
                    Server4.alive()
            elif val == -1:
                exitProgram()
            else:
                print("Wrong input, try again..")
            os.system("clear")

    # 4 processes and 2 thread created.
    p1 = multiprocessing.Process(target=runServer1)
    p2 = multiprocessing.Process(target=runServer2)
    p3 = multiprocessing.Process(target=runServer3)
    p4 = multiprocessing.Process(target=runServer4)
    t1 = threading.Thread(target=runServer5)
    t2 = threading.Thread(target=output)

    p1.start()
    time.sleep(0.04)
    p2.start()
    time.sleep(0.04)
    p3.start()
    time.sleep(0.04)
    p4.start()
    time.sleep(0.04)
    t1.start()
    time.sleep(0.04)
    t2.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    t1.join()
    t2.join()


# Driver code
if __name__ == "__main__":
    main()
