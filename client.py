import socket
import select
import getpass
import errno
import sys
import pickle
import threading
import time
import tkinter as tk
from termcolor import colored, cprint
import cv2
import rsa
import datetime
from simplecrypt import encrypt, decrypt

root = tk.Tk()
root.withdraw()

HEADER_LENGTH = 10

IP = socket.gethostbyname(socket.gethostname())
PORT = 5555

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

currvalup = "00"

def colors_256(stri, id, dat):
    if not dat:
        num1 = str(hash(id) % 100)
    else:
        num1 = 82
    return f"\033[38;5;{num1}m{stri}\033[0;0m"

def grp(grp_name, listofpart):
    global username
    Name = {}
    Name["GROUP_NAME"] = grp_name
    Name["Admin"] = username.decode("utf-8")
    for i in range(len(listofpart)):
        Name[f"group participant {i+1}"] = listofpart[i]
    return Name

def auth():
    global username
    global m_key
    todo = input("Type LOGIN to login or SIGNUP to register: ")
    if todo == "LOGIN":
        print(colors_256("#################### USER-LOGIN ####################", "", True))
        my_username = input("Username: ")
        username = my_username
        my_password = getpass.getpass()
        data = ("LOGIN", my_username, my_password)
        data = pickle.dumps(data)
        data_header = bytes(f"{len(data) :<{HEADER_LENGTH}}", "utf-8")
        client_socket.send(data_header + data)
    elif todo == "SIGNUP":
        print(colors_256("#################### USER-REGISTRATION ####################", "", True))
        my_username = input("Choose username: ")
        username = my_username
        my_password = getpass.getpass("choose password: ")
        while (len(my_password)<8):
            my_password = getpass.getpass("Please choose a password with 8 or more characters: ")
        confrm = getpass.getpass("Confirm password: ")
        while(confrm != my_password):
            confrm = getpass.getpass("Confirm password: ")
        (u_pub, u_pri) = rsa.newkeys(512)
        m_key = u_pri
        u_pri = pickle.dumps(u_pri)
        u_pri = encrypt(my_password,u_pri)
        data = ("SIGNUP", my_username, my_password, u_pub, u_pri)
        data=pickle.dumps(data)
        data_header = bytes(f"{len(data) :<{HEADER_LENGTH}}", "utf-8")
        client_socket.send(data_header + data)
    else:
        print("Wrong input :(")
        auth()

auth()
time.sleep(0.01)

def sending(HEADER_LENGTH):
    global currvalup
    global f_key
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
            f_uname = input("Username you want to send message or @#@EXIT@#@ to exit:")
            if ( f_uname == "@#@EXIT@#@"):
                continue
            elif f_uname:
                pp = (f_uname, "PUBLIC-KEY")
                pp = pickle.dumps(pp)
                pp_header = bytes(f"{len(pp) :<{HEADER_LENGTH}}", 'utf-8')
                client_socket.send(pp_header + pp)
                time.sleep(0.01)
                while True:
                    nori = input("Type of message you want to send (text or image or 0(to exit)): ")
                    if(nori == "text"):
                        print("type @#@EXIT@#@ to stop sending text messages")
                        while True:
                            message = input()
                            if message == "@#@EXIT@#@":
                                break
                            elif message:
                                message = message.encode('utf-8')
                                message = rsa.encrypt(message, f_key)
                                message = ("text", message)
                                message = (message, f_uname)
                                message = pickle.dumps(message)
                                message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", 'utf-8')
                                client_socket.send(message_header + message)
                    elif(nori == "image"):
                        message = input("image name or @#@EXIT@#@ to withdraw: ")
                        if message == "@#@EXIT@#@":
                            continue
                        if message:
                            f = open(message, "rb").read()
                            message = ("image",f)
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
            group_header = bytes(f"{len(group) :<{HEADER_LENGTH}}", "utf-8")
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
                    if wtd == "1":
                        while True:
                            nori = input("text or image or 0(to exit): ")
                            if(nori == "text"):
                                print("type @#@EXIT@#@ to stop sending text messages")
                                while True:
                                    message = input()
                                    if message == "@#@EXIT@#@":
                                        break
                                    elif message:
                                        message = ("text",message)
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
                                    message = ("image",f) 
                                    message = (message, g_name)
                                    message = (message, "GROUP_MESSAGE")
                                    message = pickle.dumps(message)
                                    message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", 'utf-8')
                                    client_socket.send(message_header + message)
                            elif(nori == "0"):
                                break
                            else:
                                print("Wrong input :(")


                    elif wtd == "2":
                        message = (g_name, "gManipl")
                        message = pickle.dumps(message)
                        message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", "utf-8")
                        client_socket.send(message_header + message)
                        time.sleep(0.01)
                        if currvalup != "11":
                            continue
                        else:
                            message_2 = input("username you want to add: ")
                            message_2 = (message_2, g_name)
                            message_2 = (message_2, "apowadd")
                            message_2 = pickle.dumps(message_2)
                            message2_header = bytes(
                                f"{len(message_2) :<{HEADER_LENGTH}}", "utf-8"
                            )
                            client_socket.send(message2_header + message_2)

                    elif wtd == "3":
                        message = (g_name, "gManipl")
                        message = pickle.dumps(message)
                        message_header = bytes(f"{len(message) :<{HEADER_LENGTH}}", "utf-8")
                        client_socket.send(message_header + message)
                        time.sleep(0.01)
                        if currvalup != "11":
                            continue
                        else:
                            message_2 = input("username you want to remove: ")
                            message_2 = (message_2, g_name)
                            message_2 = (message_2, "apowrem")
                            message_2 = pickle.dumps(message_2)
                            message2_header = bytes(
                                f"{len(message_2) :<{HEADER_LENGTH}}", "utf-8"
                            )
                            client_socket.send(message2_header + message_2)

                    elif (wtd == "0"):
                        break


def receiving(HEADER_LENGTH):
    global currvalup
    global username
    global f_key
    global m_key
    while True:
        try:
            while True:
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("Connection closed by the server")
                    sys.exit(1)

                username_length = int(username_header.decode("utf-8").strip())
                username_2 = client_socket.recv(username_length).decode("utf-8")
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode("utf-8").strip())
                if username_2 != "SERVER":
                    message = pickle.loads(client_socket.recv(message_length))
                    if (message[0] == "text"):
                        text = rsa.decrypt(message[1], m_key)
                        text = text.decode('utf-8')
                        if (username_2 == username):
                            username_2 = "You"
                        tbp_u = colors_256(username_2, username_2, False)
                        tbp_m = colors_256(text, username_2, False)
                        tbp = (f"{tbp_u} > {tbp_m}")
                        print(tbp)
                    elif (message[0] == "image"):
                        print("image received as from " + username_2)
                        print("    0-TO SAVE")
                        print("    1-TO VIEW AND SAVE")
                        inp = input()
                        if(inp == "0"):
                            pass
                        elif(inp == "1"):
                            name = f"{datetime.datetime.now()}"
                            file = open(f"{name}.png", "wb")
                            file.write(message[1])
                            img = cv2.imread(f"{name}.png", cv2.IMREAD_ANYCOLOR)
                            cv2.imshow(f"Image from {username_2}", img)
                            cv2.waitKey(0)
                            
                else:
                    message = pickle.loads(client_socket.recv(message_length))
                    if (message[1] == "auth-data"):
                        tbp = colors_256(message[0], username_2, True)
                        print(tbp)
                    elif (message[1] == "key-data"):
                        f_key = message[0]
                    elif (message[1] == "adm-data"):
                        currvalup = message[0]
                    
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("Reading error", str(e))
                sys.exit()
            continue

        except Exception as e:
            print("General error", str(e))
            sys.exit()


send = threading.Thread(target=sending, args=(HEADER_LENGTH,))
receive = threading.Thread(target=receiving, args=(HEADER_LENGTH,))

try:
    send.start()
    receive.start()
except KeyboardInterrupt:
    sys.exit(1)
