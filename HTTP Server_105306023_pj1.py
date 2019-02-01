
# coding: utf-8

# In[1]:


import socket
import threading
import struct


# In[2]:


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pars = ('127.0.0.1', 80) 
s.bind(pars)
s.listen(5)


# In[3]:


def serveClient(clientsocket, address):

    while True:
        data = clientsocket.recv(1024)
        
        # if the received data is not empty, then we send something back by using send() function
        if data:
            try:
                print(data.decode('ASCII'))
                lines = data.decode('ASCII').split("\r\n")  # 根據換行符號切割
                first_line = lines[0].split(" ")            # 根據空白鍵切割
                request_url = first_line[1]
                request_version = first_line[2]
                print("request URL: ", request_url)
                
                response_version = 'HTTP/1.1'.encode('ASCII')
                space = ' '.encode('ASCII')
                end_of_line = '\r\n'.encode('ASCII')
                content_length = 'Content-Length:'.encode('ASCII')
                connection = 'Connection:'.encode('ASCII')
                
                if(request_url == '/good.html'):
                    status_code = '200'.encode('ASCII')
                    response_phrase = 'OK'.encode('ASCII')
                    body = '<html><body>good.html</body></html>'.encode('ASCII')
                    send_back_pkt = struct.pack('!8ss3ss2s2s15ss2s2s11ss5s2s2s35s',response_version,space,status_code,space,response_phrase,end_of_line,content_length,space,str(len(body)).encode('ASCII'),end_of_line,connection,space,'close'.encode('ASCII'),end_of_line,end_of_line,body)
                    clientsocket.send(send_back_pkt)
                    print(send_back_pkt)
                    print('')
                    print('')
                    
                elif(request_url == '/redirect.html'):
                    status_code = '301'.encode('ASCII')
                    response_phrase = 'Moved Permanently'.encode('ASCII')
                    location = 'good.html'.encode('ASCII')
                    send_back_pkt = struct.pack('!8ss3ss17s2s11ss5s2s9ss9s2s2s',response_version,space,status_code,space,response_phrase,end_of_line,connection,space,'close'.encode('ASCII'),end_of_line,'Location:'.encode('ASCII'),space,location,end_of_line,end_of_line)
                    clientsocket.send(send_back_pkt)
                    print(send_back_pkt)
                    print('')
                    print('')
                
                else:
                    status_code = '404'.encode('ASCII')
                    response_phrase = 'Not Found'.encode('ASCII')
                    body = '<html><body>404 Not Found</body></html>'.encode('ASCII')
                    send_back_pkt = struct.pack('!8ss3ss9s2s15ss2s2s11ss5s2s2s39s',response_version,space,status_code,space,response_phrase,end_of_line,content_length,space,str(len(body)).encode('ASCII'),end_of_line,connection,space,'close'.encode('ASCII'),end_of_line,end_of_line,body)
                    clientsocket.send(send_back_pkt)
                    print(send_back_pkt)
                    print('')
                    print('')   
    
            except (struct.error):
                pass
        


# In[ ]:


# since at most we can serve many clients (5 in this example), we need a way to distinguish them 
# as mentioned in the class, TCP use 4-tuple (src IP, dst IP, src port, dst port) to distinguish a socket
# we use accept() function to confirm that we connect to the client socket
# and accept() function will return the client's socket instance and IP
# we need a loop to keep accepting new clients (until 5 clients are accepted)

while True:
    # accept a new client and get it's information
    (clientsocket, address) = s.accept()
    
    # create a new thread to serve this new client
    # after the thread is created, it will start to execute 'target' function with arguments 'args' 
    threading.Thread(target = serveClient, args = (clientsocket, address)).start()

