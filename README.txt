Transparent Proxy Server Program Version 1.0 12/14/2014
author: Mayank Juneja, Kaushal Deodhar

OBJECTIVE
------------------
- To build a transparent proxy capable of accepting requests, making requests from remote servers, and returning data to a client. As before, you should be able to accept multiple client requests concurrently. 
- Proxy should be able to selectively block requests for certain file types, in this case, for .jpg files.
- Proxy should maintain a log of all the clients that connect to it, and the files each client requests.

THINGS TO CHANGE BEFORE STARTING PROXY SERVER
--------------------------------------------------------------------------------------
- Set up network configuration:
	- Set a static IP to client VM, proxy VM and server VM.
	- Set proxy VM's IP as default gateway of client VM.
	- Set server VM's IP as default gateway of proxy VM.
- Set IP_forwarding off as proxy server will be handling all requests and forwarding to the server. 
- Add user of proxy VM in the sudoers list (using visudo) so that it can act as a root.
- Disable user password, so that we can directly fire sudo commands in command prompt.
- Check that there is no static route in iptables.

GENERAL USAGE NOTES
--------------------------------------
- Navigate to file location in command prompt in proxy VM.
- Run the python file. To run enter "python proxy.py 9090"
- Navigate to file location in command prompt in server VM.
- Run any HTTP server in server VM
- Open a web browser in client VM and enter server address.
- Use KeyboardInterrupt (ctrl+c) to exit from the proxy server in proxy VM.

FRAMEWORK DESIGN
----------------------------------
- After proxy is initiated, it creates a log file named 'proxyLog.txt'
- Design creates a new parallel thread everytime when ever client connects to proxy.
- Every request originated from the client reaches the proxy VM where it is DNATed to proxy server's listening port.
- The proxy manipulates the source address and sends the request to the server.
- After the request is created, it is SNATed to change the source address from proxy to client.
- The server reads the request and sends a reply.
- The reply reaches the proxy server. 
- The proxy server checks for .jpg in the reply and blocks such replies.
- After the reply is checked, it is sent to the client.
- The proxy has a timeout of 15 seconds for server to reply.
- The SNAT table is cleared when the reply is sent or if the timeout occurs. 


VERSION INFORMATION
-------------------------------------
- This Version of Transparent Proxy Server is developed using Python 2.7 on Linux VM.
- A Log file is generated named 'proxyLog.txt' at the Home location, which contains the history of requests received by the proxy. 
- Version has been tested on lightweigt servers and webpages.

References
-----------------
- http://www.w3.org/Protocols/rfc1945/rfc1945
- http://www.pythonforbeginners.com/
- https://wiki.python.org/
- http://stackoverflow.com/questions/20242434/how-to-run-python-scripts-on-a-web-servere-g-localhost
- http://ilab.cs.byu.edu/python/socket/echoserver.html

----------------------------------------------------------------------------------------------------------------------------
Mayank Juneja can be reached at:

Voice:	530-820-2311
E-mail:	mayank.juneja@colorado.edu
