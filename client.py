import socket
import time
import secrets
from encryption import curve
from user_info import UserInfo
from packets import LoginPacket, SignUpPacket
import pickle

SERVER = "192.168.1.21"
PORT = 9797

privKey = None

def send_message(client):
    #get key database
    #get users
    pass

def read_messages(client):
    #get key database
    pass

def user_interface(client):
    global privKey
    print("User Options: ")
    print("1) Send Message")
    print("2) Read Messages")

    while True:
        val = input(">")
        if val == '1':
            login(client)
        if val == '2':
            signup(client)
        else:
            print("Invalid input - try again")

def login(client):
    global privKey
    username = input("enter user name: ")
    password = input("enter password: ")

    info = UserInfo(username, password)
    login_packet = LoginPacket(info)
    client.send(login_packet.content)
    client.settimeout(1)

    rec_data = client.recv(3)
    magic_no = rec_data[0]<<8 | rec_data[1]
    r_id = rec_data[2]

    if magic_no != 0xAE73:
        raise ValueError("magic number incorrect")
    
    if r_id == 3:
        dbfile = open(username+'priv_pem', 'rb')
        privKey = pickle.load(dbfile)  
        dbfile.close()
        user_interface(client)
    if r_id != 3:
        print("invalid credentials! - try again")
        login(client)

def signup(client):
    global privKey
    username = input("enter user name: ")
    password = input("enter password: ")
    
    # create key
    privKey = secrets.randbelow(curve.field.n)

    dbfile = open(username+'priv_pem', 'ab')
    pickle.dump(privKey, dbfile)                    
    dbfile.close()

    pubKey = privKey * curve.g

    info = UserInfo(username, password, pubKey)
    signup_packet = SignUpPacket(info)
    client.send(signup_packet.content)
    client.settimeout(1)

    rec_data = client.recv(3)
    magic_no = rec_data[0]<<8 | rec_data[1]
    r_id = rec_data[2]

    if magic_no != 0xAE73:
        raise ValueError("magic number incorrect")
    
    if r_id == 3:
        user_interface(client)
    if r_id != 3:
        print("invalid credentials! - try again")
        signup(client)

def login_signup(client):
    print("1) login")
    print("2) Sign up")

    while True:
        val = input(">")
        if val == '1':
            login(client)
        if val == '2':
            signup(client)
        else:
            print("Invalid input - try again")

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    login_signup(client)

main()


    

