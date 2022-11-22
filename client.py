import socket
import select
import getpass
import errno
import sys
import pickle
import threading
import time
from termcolor import colored, cprint
from PIL import Image
import io
import datetime

HEADER_LENGTH = 10

IP = socket.gethostbyname(socket.gethostname())
PORT = 7629

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

currvalup = "00"
def auth():
    todo = input("Type LOGIN to login or SIGNUP to register: ")
    if (todo == "LOGIN"):
        my_username = input("Username: ")
        username = my_username.encode('utf-8')
        my_password = getpass.getpass()
        data = ("LOGIN", my_username, my_password)
        data=pickle.dumps(data)
        data_header = bytes(f"{len(data) :<{HEADER_LENGTH}}", 'utf-8')
        client_socket.send(data_header + data)
        tup = (username, True)
        return tup
    elif (todo == "SIGNUP"):
        usrnm = input("Choose Username: ")
        psswd = input("Choose Password (greater than 8 characters): ")
        while (len(psswd)<8):
            psswd = getpass.getpass("Please choose a password with 8 or more characters: ")
        secans = input("Your favorite song(this is a security question): ")
        data = ("SIGNUP", usrnm, psswd, secans)
        data = pickle.dumps(data)
        data_header = bytes(f"{len(data) :<{HEADER_LENGTH}}", 'utf-8')
        client_socket.send(data_header + data)
        tup = (usrnm, True)
        return tup
    else:
        print("Wrong input :(")
        tup = ("", False)
        return tup

a = auth()
username = a[0]
b = a[1]
while not b:
    a = auth()
    username = a[0]
    b = a[1]

def colors_256(stri, id):
    num1 = str(hash(id)%100)
    return(f"\033[38;5;{num1}m{stri}\033[0;0m")

def grp(grp_name, listofpart):
    Name = {}
    Name["GROUP_NAME"] = grp_name
    Name["Admin"] = username.decode('utf-8')
    for i in range(len(listofpart)):
        Name[f"group participant {i+1}"] = listofpart[i]
    return Name

def sending(HEADER_LENGTH):
    global currvalup
    time.sleep(0.1)
    while True:
        print("Choose one of the actions:\n"+"  1-ENTER A PERSONAL CHAT\n"+"  2-CREATE A GROUP\n"+"  3-ENTER A GROUP CHAT\n"+"  4-PRINT LIST OF CHATS\n")
        input_command = input()

        if input_command == "4":
            li = ("list of chats" , "SERVER")
            li = pickle.dumps(li)
            he = bytes(f"{len(li) :<{HEADER_LENGTH}}", 'utf-8')
            client_socket.send(he + li)
            continue
            
        elif input_command == "1":
            f_uname = input("Username you want to send message or @#@EXIT@#@ to exit this:")
            if f_uname == "@#@EXIT@#@":
                continue
            elif f_uname:
                while True:
                    nori = input("Type of message you want to send (text or image or 0(to exit)): ")
                    if(nori == "text"):
                        print("type @#@EXIT@#@ to stop sending text messages")
                        while True:
                            message = input()
                            if message == "@#@EXIT@#@":
                                break
                            elif message:
                                message = (message, "@text@")
                                message = (message, f_uname)
                                message = pickle.dumps(message)
                                message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", 'utf-8')
                                client_socket.send(message_header + message)
                    elif(nori == "image"):
                        message = input("image name or @#@EXIT@#@ to withdraw: ")
                        if message == "@#@EXIT@#@":
                            continue
                        if message:
                            with open(message, "rb") as image:
                                f = image.read()
                            message = (f, "@image@")
                            message = (message, f_uname)
                            message = pickle.dumps(message)
                            message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", 'utf-8')
                            client_socket.send(message_header + message)
                    elif(nori == "0"):
                        break
                    else:
                        print("Wrong input :(")
            
        elif input_command == "2":
            group_name = input("Enter group name: ")
            participants = []
            while True:
                prpnt = input("Enter Participant username: ")
                if prpnt == "-1":
                    break
                else:
                    participants.append(prpnt)      
            group = grp(group_name, participants)
            group = (group, "GROUP")
            group = pickle.dumps(group)
            group_header = bytes(f"{len(group) :<{HEADER_LENGTH}}", 'utf-8')
            client_socket.send(group_header + group)
            continue
        
        elif input_command == "3":
            g_name = input("Group-name you want to enter or @#@EXIT@#@ to exit:")
            if g_name == "@#@EXIT@#@":
                continue
            if g_name:
                while True:
                    print("choose one of the actions:\n" + "1-message\n" +"2-Add a Participant(for admin only)\n" + "3-Remove a Participant(for admin only)\n" + "0-EXIT")
                    wtd = input()
                    if (wtd == "1"):
                        while True:
                            nori = input("text or image or 0(to exit): ")
                            if(nori == "text"):
                                print("type @#@EXIT@#@ to stop sending text messages")
                                while True:
                                    message = input()
                                    if message == "@#@EXIT@#@":
                                        break
                                    elif message:
                                        message = (message, "@text@")
                                        message = (message, g_name)
                                        message = (message, "GROUP_MESSAGE")
                                        message = pickle.dumps(message)
                                        message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", 'utf-8')
                                        client_socket.send(message_header + message)
                            elif(nori == "image"):
                                message = input("image name or @#@EXIT@#@ to withdraw: ")
                                if message == "@#@EXIT@#@":
                                    continue   
                                if message:
                                    with open(message, "rb") as image:
                                        f = image.read()
                                    message = (f, "@image@") 
                                    message = (message, g_name)
                                    message = (message, "GROUP_MESSAGE")
                                    message = pickle.dumps(message)
                                    message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", 'utf-8')
                                    client_socket.send(message_header + message)
                            elif(nori == "0"):
                                break
                            else:
                                print("Wrong input :(")
                
                    elif (wtd == "2"):
                        message = (g_name, "gManipl")
                        message = pickle.dumps(message)
                        message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", 'utf-8')
                        client_socket.send(message_header + message)
                        time.sleep(0.01)
                        if (currvalup != "11"):
                            continue
                        else:
                            message_2 = input("username you want to add: ")
                            message_2 = (message_2, g_name)
                            message_2 = (message_2, "apowadd")
                            message_2 = pickle.dumps(message_2)
                            message2_header = bytes(f"{len(message_2) :<{HEADER_LENGTH}}", 'utf-8')
                            client_socket.send(message2_header + message_2)

                    elif (wtd == "3"):
                        message = (g_name, "gManipl")
                        message = pickle.dumps(message)
                        message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", 'utf-8')
                        client_socket.send(message_header + message)
                        time.sleep(0.01)
                        if (currvalup != "11"):
                            continue
                        else:
                            message_2 = input("username you want to remove: ")
                            message_2 = (message_2, g_name)
                            message_2 = (message_2, "apowrem")
                            message_2 = pickle.dumps(message_2)
                            message2_header = bytes(f"{len(message_2) :<{HEADER_LENGTH}}", 'utf-8')
                            client_socket.send(message2_header + message_2)
                    
                    elif (wtd == "0"):
                        break
                

def receiving(HEADER_LENGTH):
    global currvalup
    while True:
        try:
            while True:
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("connection closed by the server")
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                if(username != "SERVER"):
                    message = pickle.loads(client_socket.recv(message_length))
                    if (message[1] == "@text@"):
                        tbp_u = colors_256(username, username)
                        tbp_m = colors_256(message[0], username)
                        tbp = (f"{tbp_u} > {tbp_m}")
                        print(tbp)
                    elif (message[1] == "@image@"):
                        name = f"{datetime.datetime.now()}"
                        with open(f"{name}.png", "wb") as file:
                            print("image received as " + name)
                            file.write(message[0])
                else:
                    message = client_socket.recv(message_length).decode('utf-8')
                    currvalup = message
                    tbp = colors_256(message, username)
                    print(tbp)

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error', str(e))
                sys.exit()
            continue

        except Exception as e:
            print('General error', str(e))
            sys.exit()

send = threading.Thread(target=sending, args=(HEADER_LENGTH,))
receive = threading.Thread(target=receiving, args=(HEADER_LENGTH,))

send.start()
receive.start()