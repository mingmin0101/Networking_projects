
# coding: utf-8

# In[1]:


import socket
import threading
import struct
import random
import binascii


# In[2]:


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pars = ('127.0.0.1', 8899) # server IP and server port
s.connect(pars)


# In[3]:


pkt_type = 8 # clinet request
unused = 65535
pkt_id = random.randint(0,65536)
seq_num = 1 
msg = 'Amy'.encode('ASCII')

data = struct.pack('!BxHHH3sx',pkt_type,unused,pkt_id,seq_num,msg)

print(binascii.hexlify(data))


# In[4]:


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


# In[5]:


# client有無數次的send和receive要執行
while True:
    # 送東西給server
    s.send(data)
    print('send packet to server!')
    print(' ')
    print('packet(send to server) info.')
    print(binascii.hexlify(data))
    print(' ')
    
    print_result(pkt_type,unused,pkt_id,seq_num,msg)

    # then wait for server response
    rcv_data = s.recv(12)
    if rcv_data:
        ans = struct.unpack('!BxHHH3sx',rcv_data)
        pkt_type = ans[0]
        unused = ans[1]
        pkt_id = ans[2]
        seq_num = ans[3]
        msg = ans[4]
        
        print("pkt from server:", ans)
        print(' ')
        print('packet(from server) info.')
        print(binascii.hexlify(rcv_data))
        print(' ')

        print_result(pkt_type,unused,pkt_id,seq_num,msg)

    # terminate
    s.send(b'close')
    break
    
# close directly
s.close()

