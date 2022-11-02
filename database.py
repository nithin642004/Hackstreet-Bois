# from multiprocessing.connection import Connection
import psycopg2

#establishing the connection
conn = psycopg2.connect(
   database="postgres", user='postgres', password='nithin', host='127.0.0.1', port= '5432'
)
# conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Doping database table if already exists.
# cursor.execute("DROP TABLE IF EXISTS mydb4")
# #Creating table as per requirement
# sql ='''CREATE TABLE mydb4(
#    username VARCHAR(255),
#    password VARCHAR(255)
# )'''
#Creating a database
# cursor.execute(sql)
# sql ='''CREATE TABLE mydb5(
#    receiver VARCHAR(255),
#    sender VARCHAR(255),
#    date_time VARCHAR(255),
#    msg VARCHAR(255)
# )'''
# cursor.execute(sql)

def insert(usrname, pswd):
   if(usrname=="" or pswd==""):
      print("Invalid Username and Password")
      return
   if(checkuser(usrname, pswd)):
      print("Username is already in use")
      return
   cursor.execute('''INSERT INTO mydb4(username, password)
               VALUES(%s, %s)
               ''', (usrname, pswd,))
   print("Welcome to Server...!")
   conn.commit()

def checkuser(usrname, pswd):
   cursor.execute("SELECT * FROM mydb4 WHERE username =%s AND password =%s", (usrname,pswd,))
   # cursor.execute("SELECT * FROM mydb4 WHERE username =%s", (usrname,))
   res=cursor.fetchall()
   if(len(res)==0):
      return False
   else:
      return True

def change_pswd(usrname, oldpswd, newpswd):
   if(checkuser(usrname,oldpswd)):
      cursor.execute("UPDATE mydb4 SET password =%s WHERE username =%s AND password =%s" , (newpswd, usrname, oldpswd))
      conn.commit()
   else:
      print("Username and Password are incorrect")

def store_undeliverd_msg(reci,sende, time,msg):
   if(reci==""):
      print("Invalid Username")
      return
   if(not checkuser(reci, "abc")):
      print("Reciver doesnot exist")
      return
   cursor.execute('''INSERT INTO mydb5(receiver, sender, date_time, msg)
               VALUES(%s, %s, %s, %s)
               ''', (reci, sende, time, msg,))
   conn.commit()

# insert("mohit", "5251abcfff")
# insert("harshit", "bjksdbkddj")
# insert("adhitya", "jbdiuwb")
# insert("mohit", "5251abc")
# checkuser("adhitya", "jbdiuwb")
# change_pswd("mohit", "5251abc", "qqqq456")
# cursor.execute("SELECT * FROM mydb4 WHERE username ='mohit'")
# print(cursor.fetchall())
# store_undeliverd_msg("adhitya", "mohit", "Hi")
# store_undeliverd_msg("Rao", "adhitya", "Hi")
def del_delivered_msg(reci, sende, time, mss):
   cursor.execute("DELETE FROM mydb5 WHERE receiver=%s AND sender=%s AND date_time=%s AND msg=%s", (reci, sende, time, mss,))
   conn.commit()
   
# store_undeliverd_msg("adhitya", "harshit","abc", "Hlo")
# store_undeliverd_msg("adhitya", "harshit","abcd", "Hlo")
# del_delivered_msg("adhitya", "mohit","----", "Hi")
# store_undeliverd_msg("adhitya", "Rao", "----","Hi")

print("Login/SignUp")
a=input("Enter 1 to Login and 0 to SignUp: ")
print(type(a))
if(a=="1"):
   name=input("Enter Username: ")
   pas=input("Enter password: ")
   if(checkuser(name, pas)):
      print("Welcome back..!")
   else:
      print("Incorrect Username or Password")
else:
   name=input("Enter Username: ")
   pas=input("Enter password: ")
   insert(name, pas)
conn.commit()
#Closing the connection
conn.close()
