# FASTCHAT

### ✨HackStreet Boys✨

Our FastChat project is currently under progress. We have done the chatting part and the database part. Now we are working on the encryption and load balancing.

## Working Features

- Creates an account for a client and allows him to login at any time.
- Personal chat between two persons.
- Group creation, Group chat and Admin Powers.

## To Be Done

- End to End Encryption of chat between Clients
- Load Balancing of servers

## Tech

- Python
- Postgres
- Socket Library 
- Threading
- Bcrypt Library

## Working

- server:
```sh
python3 server.py
```

For Login/Signup..

- client:
```sh
python3 client.py
# Enter the username and password
```

<img src="login.png" width=70%>

For Personal Chat between two persons...

```sh
Python3 client.py
# Login/Signup
# Input: 1
# Input: Person name
# Input: text/image
# For leaving
#   Input: @#@EXIT@#@
```

<img src="person.png" width=90%>


For Group Creation...

```sh
Python3 client.py
# Login/Signup
# Input: 2
# Input: Group name
# Input: Participant names
# Input: -1 to stop
```

<img src="grpcreate.png" width=40%>


For Group Chat...

```sh
Python3 client.py
# Login/Signup
# Input: 3
# Input: Group name
# For Chatting
#   Input: 1
#   Input: text/image
#   Input: Messages
#   Input: @#@EXIT@#@ to stop
# For Adding a participant
#   Input: 2
#   Output(if not an admin): Only admin can add/remove partipants
#   Input: Participant name
# For Removing a participant
#   Input: 3
#   Output(if not an admin): Only admin can add/remove partipants
#   Input: Participant name
# For leaving
#   Input: 0
```

<img src="grpchat.png" width=50%>

## Team Members Contribution

Members: Mohith, Nithin and Adhitya

Most of the work we have done in team and helped each other

Major contributions:
- Adithya: Personal Chat
- Mohith: Group Chat
- Nithin: DataBase
