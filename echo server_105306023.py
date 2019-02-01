
# coding: utf-8

# In[1]:


import socket
import threading
import struct
import binascii


# In[2]:


# 開一個socket，並使用TCP port 8899
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pars = ('127.0.0.1', 8899) 
s.bind(pars)
s.listen(5)


# In[3]:


def print_result(pkt_type,unused,pkt_id,seq_num,msg):

    print('           1         2         3 ')
    print(' 01234567890123456789012345678901')
    print('+--------------------------------+')
    print('|'+('{:0>8}'.format(format(pkt_type,'b')))+'00000000'+ format(unused,'b')                     +'|')
    print('|'+('{:0>16}'.format(format(pkt_id,'b')))            + ('{:0>16}'.format(format(seq_num,'b')))+'|')
    print('|'+('{:0>24}'.format(format((int(binascii.hexlify(msg), 16)),'b'))+'00000000'                 +'|'))
    
    print('Type = '+ str(pkt_type))
    print('Code = 00000000')
    print('Unused = ' +str(format(unused,'b')))
    print('Identifier = '+str(format(pkt_id,'b')))
    print('Sequence Number = '+str(seq_num))
    print('Message = '+str(msg)+' = '+str(binascii.hexlify(msg))+' = '+ format((int(binascii.hexlify(msg), 16)),'b'))
    print(' ')


# In[4]:


# server接受client的連線後，新起的thread會執行的function
def serveClient(clientsocket, address):
    
    while True:
        #開一個暫存區存放client傳過來的東西(參數為data)
        data = clientsocket.recv(12)

        #對送過來的東西做處理
        if(len(data)==struct.calcsize('!BxHHH3sx')):
            ans = struct.unpack('!BxHHH3sx', data)
            pkt_type = ans[0]
            unused = ans[1]
            pkt_id = ans[2]
            seq_num = ans[3]
            msg = ans[4]
            
            print("packet from client", ans)
            print(' ')
            print('packet(from client) info.')
            print(binascii.hexlify(data))
            print(' ')

            print_result(pkt_type,unused,pkt_id,seq_num,msg)
            
            pkt_type = 0
                
            send_back_pkt = struct.pack('!BxHHH3sx',pkt_type,unused,pkt_id,seq_num,msg)
            clientsocket.send(send_back_pkt)
            
            print('send packet back to client!')
            print(' ')
            print('packet(send to client) info.')
            print(binascii.hexlify(send_back_pkt))
            print(' ')

            print_result(pkt_type,unused,pkt_id,seq_num,msg)
        
        #關閉socket 
        if data == b'close':
            clientsocket.close()
            break


# In[ ]:


# 讓server不斷處於listen狀態
while True:
    # 接受新的client和傳過來的資訊
    (clientsocket, address) = s.accept()
    
    # 每個被接受的client socket擁有一個新的thread去處理後續的通訊
    threading.Thread(target = serveClient, args = (clientsocket, address)).start()

