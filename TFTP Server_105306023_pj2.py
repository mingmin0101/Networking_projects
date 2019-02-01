
# coding: utf-8

# In[ ]:


import struct
import socket
from threading import Thread
import os


# In[ ]:


# Client download thread
def download_thread(fileName, clientInfo):
    print("Responsible for processing client download files")
    print(fileName)
    print(clientInfo)

    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    fileNum = 0 #Indicates the serial number of the received file
    
    #如果 TFTP server 上有這個檔案，就開始傳輸給 client，若沒有，則傳遞 error 封包
    if(os.path.isfile(fileName)):
        f = open(fileName,'rb')
        st = os.stat(fileName)
        fileSize = st.st_size
        
        print("has file and file size is : ")
        print(fileSize)
        
        while(True):
            if(f.closed==True):
                pass
            else:
                readFileData = f.read(512)
                
            # 檔案大小超過512byte
            if(f.closed==False and fileSize>512 and f.tell()==512):
                fileNum += 1
                sendData = struct.pack('!HH', 3, fileNum) + readFileData 
                # Send file data to the client
                s.sendto(sendData, clientInfo)  #Data sent for the first time

            
            # 檔案大小只有512byte
            elif(f.closed==False and fileSize <=512 and f.tell()==fileSize):
                fileNum += 1
                sendData = struct.pack('!HH', 3, fileNum) + readFileData 
                # Send file data to the client
                s.sendto(sendData, clientInfo)  #Data sent for the first time
                
                # Receiving data for the second time   ACK
                recvData, clientInfo = s.recvfrom(1024)
                #print(recvData, clientInfo)

                # Unpacking
                packetOpt = struct.unpack("!H", recvData[:2])  #Opcode
                packetNum = struct.unpack("!H", recvData[2:4]) #Block number

                if(packetOpt[0] != 4 or packetNum[0] != fileNum):
                    print("File transfer error！")
                    break
                    
                print("User"+str(clientInfo), end='')
                print('：Download '+fileName+' completed！')
                # Close file
                f.close()
                break
                   
            else:
                # Receiving data for the second time   ACK
                recvData, clientInfo = s.recvfrom(1024)
                #print(recvData, clientInfo)

                # Unpacking
                packetOpt = struct.unpack("!H", recvData[:2])  #Opcode
                packetNum = struct.unpack("!H", recvData[2:4]) #Block number
                #print(packetOpt, packetNum)


                if(packetOpt[0] != 4 or packetNum[0] != fileNum):
                    print("File transfer error！")
                    break
                else:
                    if(f.closed==True):
                        break
                    else:
                        # The block number starts at 0 and increments by one each time. Its range is [0, 65535]
                        fileNum += 1

                        # roll-over
                        # block number 1~65535 如果不夠用要用第二輪，會從0開始 roll-over block id.
                        if(fileNum > 65535):
                            fileNum = 0

                        sendData = struct.pack('!HH', 3, fileNum) + readFileData    
                        # Send file data to the client
                        s.sendto(sendData, clientInfo)  #Data sent for the first time

                        if len(sendData) < 516:
                            print("User"+str(clientInfo), end='')
                            print('：Download '+fileName+' completed！')
                            # Close file
                            f.close()

    else:
        print('error!')
        
        errorData = struct.pack('!HHHb', 5, 5, 5, fileNum)
        
        s.sendto(errorData, clientInfo)  #Sent the message when the file does not exist
        
        exit()  #Exit the download thread     
        
    
    # Close UDP port
    s.close()

    # Exit the download thread
    exit()


# In[ ]:


# Client uploading thread
def upload_thread(fileName, clientInfo):
    print("Responsible for processing client upload files")
    
    fileNum = 0 #Indicates the serial number of the received file
    
    # Open the file in binary mode
    f = open(fileName, 'wb')
    
    # Create a UDP port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sendDataFirst = struct.pack("!HH", 4, fileNum) 

    # Reply to the client upload request
    s.sendto(sendDataFirst, clientInfo)  #Sent with a random port at first time

    while True:
        # Receive data sent by the client
        recvData, clientInfo = s.recvfrom(1024) #Client connects to my random port at second time
        
        print(recvData, clientInfo)
        
        # Unpacking
        packetOpt = struct.unpack("!H", recvData[:2])  #Identify opcode
        packetNum = struct.unpack("!H", recvData[2:4]) #Block number
        
        #print(packetOpt, packetNum)
        
        # Client upload data
        # opcode == 3 means Data
        if packetOpt[0] == 3 and packetNum[0] == fileNum:
            #　Save data to file
            f.write(recvData[4:])
            
            # Packing
            sendData = struct.pack("!HH", 4, fileNum)
            
            # Reply client's ACK signal
            s.sendto(sendData, clientInfo) #The second time using a random port to sent
            
            fileNum += 1
            
            #If len(recvData) < 516 means the file goes to the end
            if len(recvData) < 516:
                print("User"+str(clientInfo), end='')
                print('：Upload '+fileName+' complete!')
                break
                
    # Close the file
    f.close()
    
    # Close UDP Port
    s.close()
    
    # Exit upload thread
    exit()


# In[ ]:


# Main function
def main():
    # Create a UDP port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Resolve duplicate binding ports
    # setsockopt(level,optname,value)
    # Level: defines which option will be used. Usually use "SOL_SOCKET", it means the socket option being used.
    # optname: Provide special options for use. Ex: SO_BINDTODEVICE, SO_BROADCAST, SO_DONTROUTE, SO_REUSEADDR, etc.
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind local host and port number 69
    s.bind(('127.0.0.1', 69))
    
    print("TFTP Server start successfully!")
    print("Server is running...")
    
    while True:
        
        # Receive messages sent by the client
        recvData, clientInfo = s.recvfrom(1024)  #　Client connects to port 69 at the first time
        print(clientInfo) 
        
        # Unpacking
        # !: Indicates that we want to use network character order parsing because our data is received from the network. 
        #    When transmitting on the network, it is the network character order. 
        # b: signed char
        # There can be one number before each format, indicating the number
        # s: char[]
        if struct.unpack('!b5sb', recvData[-7:]) == (0, b'octet', 0):
            opcode = struct.unpack('!H',recvData[:2])  #　Opcode
            fileName = recvData[2:-7].decode('ascii') #　Filename
            
            # Request download
            # opcode == 1 means download
            if opcode[0] == 1:
                t = Thread(target=download_thread, args=(fileName, clientInfo))
                t.start() # Start the download thread
                
            # Request uploading
            # opcode == 2 means uploading
            elif opcode[0] == 2:
                t = Thread(target=upload_thread, args=(fileName, clientInfo))
                t.start() # Start uploading thread
                
    # Close UDP port
    s.close()


# In[ ]:


# Call the main function
if __name__ == '__main__':
    main()

