from ast import While
from http import client
import socket
import select
import pickle
import psycopg2
import datetime
import bcrypt

conn = psycopg2.connect(
   database="postgres", user='postgres', password='nithin', host='127.0.0.1', port= '5432'
)
cursor = conn.cursor()

HEADERLENGTH = 10
IP = socket.gethostbyname(socket.gethostname())
PORT = 7629

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]
group_list = [server_socket]

clients = {}
GROUP = []

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADERLENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    
    except:
        return False

while True:
    read_sockets, not_req, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)

            if user is False:
                continue

            sockets_list.append(client_socket) #DB adding the client data into the list
            doin = pickle.loads(user['data'])[0]
            if (doin == "LOGIN"):
                username = pickle.loads(user['data'])[1]
                password = pickle.loads(user['data'])[2]
                # print(0, username, password)
                cursor.execute("SELECT * FROM user_info WHERE username =%s AND password =%s", (username,bcrypt.hashpw(password.encode('utf-8'), b'$2b$12$hwqJlFqHRP659BwR5VnUz.').decode(),))
                res=cursor.fetchall()
                if(len(res)==0):
                    mms = "Incorrect username or password"
                else:
                    mms = "Welcome back to fastchat...!"
                # print(0, username, password)

            elif (doin == "SIGNUP"):
                username = pickle.loads(user['data'])[1]
                password = pickle.loads(user['data'])[2]
                # secansr = pickle.loads(user['data'])[3]
                # print(1, username, password)
                cursor.execute("SELECT * FROM user_info WHERE username =%s", (username,))
                res=cursor.fetchall()
                if(len(res)==0):
                    bytes2 = password.encode('utf-8')
                    salt = b'$2b$12$hwqJlFqHRP659BwR5VnUz.'
                    hash = bcrypt.hashpw(bytes2, salt)
                    cursor.execute('''INSERT INTO user_info(username, password)
                        VALUES(%s, %s)
                        ''', (username, hash.decode(),))
                    conn.commit()
                    mms = "Welcome to fastchat...!"
                else:
                    mms = "Username is already in use"
       
            clients[client_socket] = user #DB adding current into clients list
            if(mms == "Welcome to fastchat...!" or mms == "Welcome back to fastchat...!"):  
                mms = mms + '\n' + "Here is the list of your chats\n" + "Personal chats:\n"
                i = 0
                for client_socket in clients:
                    if pickle.loads(clients[client_socket]['data'])[1] != pickle.loads(user['data'])[1]:
                        sel = "SERVER"
                        sel_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                        mms = mms + "   " + pickle.loads(clients[client_socket]['data'])[1] + '\n'
                        i+=1
                    
                if (i==0):
                    mms = mms + "   You have no personal chats\n"
                mms = mms + "group chats:\n"
                i=0
                for grp in GROUP:
                    if list(grp.values()).count(pickle.loads(user['data'])[1]):
                        mms = mms + "   " + grp["GROUP_NAME"] + '\n'
                if (i==0):
                    mms = mms + "   You have no group chats\n"

                serv = "SERVER"
                serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                mms_he = bytes(f"{len(mms) :<{HEADERLENGTH}}", 'utf-8')
                client_socket.send(serv_he + serv.encode('utf-8') + mms_he + mms.encode('utf-8'))
                print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{pickle.loads(user['data'])[1]}")
            else:
                serv = "SERVER"
                serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                mms_he = bytes(f"{len(mms) :<{HEADERLENGTH}}", 'utf-8')
                client_socket.send(serv_he + serv.encode('utf-8') + mms_he + mms.encode('utf-8'))
                sockets_list.remove(client_socket)
                del clients[client_socket]
                client_socket.close()
                continue

        else:
            message = receive_message(notified_socket)

            if message is False:
                print(f"Closed connection from {pickle.loads(clients[notified_socket]['data'])[1]}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            message_con = pickle.loads(message['data'])[0] 
            message_to = pickle.loads(message['data'])[1]

            if message_to == "SERVER":
                if message_con == "list of chats":
                    ms = "Here is the list of your chats\n" + "Personal chats:\n"
                    i = 0
                    for client_socket in clients:
                        if pickle.loads(clients[client_socket]['data'])[1] != pickle.loads(user['data'])[1]:
                            sel = "SERVER"
                            sel_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                            ms = ms + "   " + pickle.loads(clients[client_socket]['data'])[1] + '\n'
                            i+=1
                    if (i==0):
                        ms = ms + "    You have no personal chats\n"
                    ms = ms + "group chats:\n"
                    i=0
                    for grp in GROUP:
                        if list(grp.values()).count(pickle.loads(user['data'])[1]):
                            ms = ms + "   " + grp["GROUP_NAME"] + '\n'
                            i+=1
                    if (i==0):
                        ms = ms + "    You have no group chats\n"

                    serv = "SERVER"
                    serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                    ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                    notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))

            elif message_to != "GROUP" and message_to != "GROUP_MESSAGE" and message_to != "gManipl" and message_to != "apowrem" and message_to != "apowadd":
                print(f"Received message from {pickle.loads(user['data'])[1]} to {message_to}: {message_con}")
                for client_socket in clients:
                    if pickle.loads(clients[client_socket]['data'])[1] == message_to:
                        se = bytes(f"{len(pickle.loads(user['data'])[1]) :<{HEADERLENGTH}}", 'utf-8')
                        client_socket.send(se + pickle.loads(user['data'])[1].encode('utf-8') + message['header'] + pickle.dumps(message_con))

            elif message_to == "GROUP":
                print(f"GROUP {message_con['GROUP_NAME']} created by {message_con['Admin']}")
                l=[]
                for part in message_con:
                    if message_con[part] != "GROUP_NAME" or message_con[part] != "Admin":
                        print(f"{part}: {message_con[part]}")
                        l.append(message_con[part])
                        
                cursor.execute("SELECT * FROM groups_info WHERE group_name =%s", (message_con['GROUP_NAME'],))
                res=cursor.fetchall()
                if(len(res)!=0):
                    # print("A group with this name already exists")
                    ms="A group with this name already exists"
                    serv = "SERVER"
                    serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                    ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                    notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                    continue
                cursor.execute('''INSERT INTO groups_info(group_name, admin_name, group_participants)
                            VALUES(%s, %s, ARRAY[%s])
                            ''', (message_con['GROUP_NAME'], message_con['Admin'], message_con['Admin'],))
                conn.commit()
                l=l[2:]
                for par_name in l:
                    cursor.execute("SELECT * FROM user_info WHERE username =%s", (par_name,))
                    res1=cursor.fetchall()
                    if(len(res1)==0):
                        ms=f"Participant with name {par_name} not exists"
                        serv = "SERVER"
                        serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                        ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                        notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                        continue
                    cursor.execute("SELECT * FROM groups_info WHERE group_name =%s", (message_con['GROUP_NAME'],))
                    res=cursor.fetchall()
                    # if(res[0][1]!=message_con['Admin']):
                    #     print("Only admin can add partipants")
                    check=0
                    for i in res[0][2]:
                        if(i==par_name):
                            check=1
                            ms=f"Participant with name {par_name} already exits in group"
                            serv = "SERVER"
                            serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                            ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                            notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                    if(check):
                        continue
                    cursor.execute("UPDATE groups_info SET group_participants = array_append(group_participants, %s) WHERE group_name = %s" , (par_name, message_con['GROUP_NAME'],))
                    conn.commit()
                    
                GROUP.append(message_con)
                for client_socket in clients:
                    if list(message_con.values()).count(pickle.loads(clients[client_socket]['data'])[1]):
                        if pickle.loads(clients[client_socket]['data'])[1] != message_con['Admin']:
                            stri = f"you were added to the group {message_con['GROUP_NAME']} by {message_con['Admin']}"
                            serv = "SERVER"
                            serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                            client_socket.send(serv_he + serv.encode('utf-8') + message['header'] + stri.encode('utf-8'))

            elif message_to == "gManipl":
                a = "00"
                cursor.execute("SELECT * FROM groups_info WHERE group_name =%s", (message_con,))
                res=cursor.fetchall()      
                if(len(res)==0):
                    ms="Group with this name doesnot exists"
                    serv = "SERVER"
                    serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                    ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                    notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                    a="10"
                elif(res[0][1]!=pickle.loads(user['data'])[1]):
                    ms="Only admin can add/remove partipants"
                    serv = "SERVER"
                    serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                    ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                    notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                    a="10"
                else:
                    a="11"
                a_he = bytes(f"{len(a) :<{HEADERLENGTH}}", 'utf-8')
                serv = "SERVER"
                serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                notified_socket.send(serv_he + serv.encode('utf-8') + a_he + a.encode('utf-8'))

            elif message_to == "apowadd":
                # part_nam = message_con[0]
                # gp_nam = message_con[1]
                check1=1
                cursor.execute("SELECT * FROM user_info WHERE username =%s", (message_con[0],))
                res1=cursor.fetchall()
                if(len(res1)==0):
                    print(f"Participant with name {message_con[0]} not exists")
                    ms="Participant with that name not exists"
                    serv = "SERVER"
                    serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                    ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                    notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                    check1=0
                cursor.execute("SELECT * FROM groups_info WHERE group_name =%s", (message_con[1],))
                res=cursor.fetchall()      
                if(len(res)==0):
                    ms=f"Group with name {message_con[1]} doesnot exists"
                    serv = "SERVER"
                    serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                    ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                    notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                    check1=0
                for i in res[0][2]:
                    if(i==message_con[0]):
                        ms=f"Participant with name {message_con[0]} already exits in group"
                        serv = "SERVER"
                        serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                        ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                        notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                        check1=0
                if(check1==1):
                    cursor.execute("UPDATE groups_info SET group_participants = array_append(group_participants, %s) WHERE group_name = %s" , (message_con[0],message_con[1],))
                    conn.commit()

            elif message_to == "apowrem":
                # part_nam = message_con[0]
                # gp_nam = message_con[1]
                cursor.execute("SELECT * FROM user_info WHERE username =%s", (message_con[0],))
                res2=cursor.fetchall()
                if(len(res2)==0):
                    print(f"Participant with name {message_con[0]} not exists")
                    ms="Participant with that name not exists"
                    serv = "SERVER"
                    serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                    ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                    notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                cursor.execute("SELECT * FROM groups_info WHERE group_name =%s", (message_con[1],))
                res=cursor.fetchall()      
                if(len(res)==0):
                    ms=f"Group with name {message_con[1]} doesnot exists"
                    serv = "SERVER"
                    serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                    ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                    notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                for i in res[0][2]:
                    if(i==message_con[0]):
                        cursor.execute("UPDATE groups_info SET group_participants = array_remove(group_participants, %s) WHERE group_name = %s" , (message_con[0],message_con[1],))
                        conn.commit()

            elif message_to == "GROUP_MESSAGE":
                message_is = message_con[0]
                message_gpn = message_con[1]
                # for gr in GROUP:
                #     if gr["GROUP_NAME"] == message_gpn:
                #         group = gr
                # if list(group.values()).count(pickle.loads(user['data'])[1]):
                #     print(f"Received message from {pickle.loads(user['data'])[1]} to group {message_gpn}: {message_is}")
                #     for client_socket in clients:
                #         if list(group.values()).count(pickle.loads(clients[client_socket]['data'])[1]):
                #             if pickle.loads(clients[client_socket]['data'])[1] != pickle.loads(user['data'])[1].encode('utf-8'):
                #                 se = bytes(f"{len(pickle.loads(user['data'])[1]) :<{HEADERLENGTH}}", 'utf-8')
                #                 client_socket.send(se + pickle.loads(user['data'])[1].encode('utf-8') + message['header'] + message_is.encode('utf-8'))                
                # else:
                #     sff = "you are not in this group :)"
                #     se = bytes(f"{len(pickle.loads(user['data'])[1]) :<{HEADERLENGTH}}", 'utf-8')
                #     client_socket.send(se + pickle.loads(user['data'])[1].encode('utf-8') + message['header'] + sff.encode('utf-8'))
                cursor.execute("SELECT * FROM groups_info WHERE group_name =%s", (message_con[1],))
                res=cursor.fetchall()      
                if(len(res)==0):
                    ms=f"Group with name {message_con[1]} doesnot exists"
                    serv = "SERVER"
                    serv_he = bytes(f"{len(serv) :<{HEADERLENGTH}}", 'utf-8')
                    ms_he = bytes(f"{len(ms) :<{HEADERLENGTH}}", 'utf-8')
                    notified_socket.send(serv_he + serv.encode('utf-8') + ms_he + ms.encode('utf-8'))
                group=res[0][2]
                if (pickle.loads(user['data'])[1] in group):
                    print(f"Received message from {pickle.loads(user['data'])[1]} to group {message_gpn}: {message_is}")
                    for client_socket in clients:
                        if (pickle.loads(clients[client_socket]['data'])[1] in group):
                            if pickle.loads(clients[client_socket]['data'])[1] != pickle.loads(user['data'])[1].encode('utf-8'):
                                se = bytes(f"{len(pickle.loads(user['data'])[1]) :<{HEADERLENGTH}}", 'utf-8')
                                client_socket.send(se + pickle.loads(user['data'])[1].encode('utf-8') + message['header'] + pickle.dumps(message_is))                
                else:
                    sff = "you are not in this group :)"
                    se = bytes(f"{len(pickle.loads(user['data'])[1]) :<{HEADERLENGTH}}", 'utf-8')
                    client_socket.send(se + pickle.loads(user['data'])[1].encode('utf-8') + message['header'] + sff.encode('utf-8'))

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]

conn.commit()
conn.close()
