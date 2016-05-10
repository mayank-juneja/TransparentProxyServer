'''
Created on 12/14/2014

@author: mayank juneja, kaushal
'''

'''
Importing required libraries
'''
import os,sys,thread,socket
import time
import datetime
from os import curdir, sep, linesep
import fcntl
import struct
       
maxData = 9999999
cache = {}
timeout = 2
logf = open('proxyLog.txt', 'w+')
m =''
h =''
p =''
'''
Functions to return various Time Stamps
'''
def timestamp():
    return time.strftime("%a, %d %b %Y %X GMT", time.gmtime())


'''
Function to Log to a file stored in home directory
'''
def logIt(ip, port, url, req):
    logf.write(str(ip)+"       "+str(port)+"        "+str(url)+"        "+str(req)+"        "+str(timestamp())+"\n")

'''
Function to write Block or hold operations on console
'''
def printCon(type,request,address):
    print address[0],"\t",type,"\t",request

'''
Function to get Ip address of the host computer where transparentProxy is running
'''
def getIpAddress(ifname):
	s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

'''
Function to start a thread
'''
def start(client, client_addr):
    dataSent=''
    i=0
    # Receive client request
    data = client.recv(maxData)

    if (len(data)>1):
	#get server address						#Checking if request is received
	m = data.split('\n')[1]
        #to get ip    	
	h = m.split(':')[1]
	#to get port
    	p = m.split(':')[2]
    	h = h.strip()
	forURL = data.split('\n')[0]
	URL = forURL.split(' ')[1]
	if (len(URL)> 2):
		req = URL.strip('/')
	else:
		req = 'Default page'
    	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Adding a SNAT table
		os.system("sudo iptables -t nat -A POSTROUTING -o eth1 -j SNAT --to "+client_addr[0])
 		# Saving edited table   		
		os.system("sudo service iptables save")
    		time.sleep(1)
		#connecting to server
		s.connect((str(h.strip()), int(p)))
		logIt(client_addr[0], client_addr[1], h, req)
    		s.send(data)					#Data request to server
		#TIMER set for 15 sec		
		future = time.time() + 15
		while 1:
	        	data = s.recv(maxData)			#Receiving server's response
			# Checking if reply time is less than 15sec(as code proxy will stop listening and delete SNAT entry, if server do not replies)
			if time.time() < future:
				#Checking if data is received
				if (len(data) > 0):
					if '.jpg' in data:					#Block if request is jpg
						printCon("Blocked",m,client_addr)
	    					response='HTTP/1.1 501 Not Implemented:\r\n'
    						response+="Connection: keep-alive\r\n"
    						response+='Content-Type: text/html\r\n\r\n'
    						response+='<HTML><HEAD><TITLE>Server does not support this filetype\r\n'
    						response+='</TITLE></HEAD>\r\n'
            					response+='<BODY><P>BLOCKED BY PROXY:: Server can not open .jpg'
            					response+='\r\n</BODY></HTML>\r\n'
            					client.send(response)				#Send Block instructions
					else:
						client.send(data)				#Send valid response
			    	else:								#When no data is received
					break
			else:
				break
		os.system("sudo iptables -t nat -D POSTROUTING 1")	#Deleting SNAT entry 
		os.system("sudo service iptables save")
		time.sleep(1)
		s.close()
        	client.close()
    	except socket.error, (value, message):
		if s:
			s.close()
        	if client:
            		client.close()
		os.system("sudo iptables -t nat -D POSTROUTING 1")
		os.system("sudo service iptables save")
		time.sleep(1)
		printCon("Peer Reset",forURL,client_addr)

    else:
	    response='HTTP/1.1 500 Internal Server Error:\r\n'
    	    response+="Connection: keep-alive\r\n"
            response+="Date:"+timestamp()+"\r\n"
            response+='Content-Type: text/html\r\n\r\n'
            response+='<HTML><HEAD><TITLE>Server has unexpected error\r\n'
            response+='</TITLE></HEAD>\r\n'
            response+='<BODY><P>Improper Data Request'
            response+='\r\n</BODY></HTML>\r\n'
            client.send(response)
    
'''
Main function
'''
def main():
    if (len(sys.argv)<2):
        print "Please Enter in format [Filename] [Port Number]" 
        sys.exit(1)
    else:
        port = int(sys.argv[1])
    try:
	#socket to listen to client requests
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        s.listen(50)
    except socket.error, (value, message):
        if s:
            s.close()
        print "Unable to create socket: ", message
        sys.exit(1)
    # Get ip address of the eth0
    ip = getIpAddress('eth0')
    # Creating a DNAT table
    os.system("sudo iptables -t nat -p tcp -A PREROUTING -i eth0 -j DNAT --to "+str(ip)+":"+str(port))
    #Save a the tables that has been added so that these are active when next request comes 
    os.system("sudo service iptables save")
    time.sleep(1)
    while 1:
        client, client_addr = s.accept()
	thread.start_new_thread(start, (client, client_addr))        
    s.close()
'''
__main__ function
'''   
if __name__ == '__main__':
	#open a file to log client request
	logf = open('proxyLog.txt', 'w+')
	logf.write("<ClientIPaddress> <ClientPortnumber> <Host IP> <Filerequested> <Timestamp>\n")	
	try:
		main()
	except KeyboardInterrupt:
		#close log file when all requests have been logged
		logf.close()
		#delete DNAT table when proxy terminates
		os.system("sudo iptables -t nat -D PREROUTING 1")
		os.system("sudo service iptables save")
    		time.sleep(1)
    		print "Ctrl C - Stopping server"
		sys.exit(1)
