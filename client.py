import socket
import time
import secrets
from encryption import curve, encrypt_ECC
from user_info import UserInfo
from packets import LoginPacket, SignUpPacket, RequestUsersPacket, MessagePacket, GetKeyPacket
import pickle

SERVER = "192.168.1.8"
PORT = 9797

privKey = None
username = None

def send_message(client):
    global username
    print(username)
    key_req = RequestUsersPacket()
    client.send(key_req.content)
    client.settimeout(1)
    rec_data = client.recv(4000)

    #process packet
    magic_no = rec_data[0]<<8 | rec_data[1]
    r_id = rec_data[2]

    if magic_no != 0xAE73:
        raise ValueError("magic number incorrect")
    if r_id != 13:
        raise ValueError("wrong!")
    
    info = []
    for i in range(3, 3 + len(rec_data[3:])):
        info.append(rec_data[i])
    user_name_database = pickle.loads(bytearray(info))

    #get key database
    #get users
    print("User List: ")
    for item in user_name_database:
        print(item)
    print("User Options:")
    print("1) Refresh User List")
    print("2) Back")
    print("To send a message, first type a username from the list\n then type your message.")
    
    while True:
        val = input(">")
        if val == 1:
            send_message(client)
        if val == 2:
            user_interface(client)
        else:
            if val in user_name_database:
                #request public key 
                pub_key_req = GetKeyPacket(val)
                client.send(pub_key_req.content)
                rec_data = client.recv(1024)

                #process packet
                magic_no = rec_data[0]<<8 | rec_data[1]
                r_id = rec_data[2]

                if magic_no != 0xAE73:
                    raise ValueError("magic number incorrect")
                if r_id != 14:
                    raise ValueError("wrong!")
                
                info = []
                for i in range(3, 3 + len(rec_data[3:])):
                    info.append(rec_data[i])
                pubkey = pickle.loads(bytearray(info))
                msg = input(">")
                if msg != None:
                    #encrypt msg
                    encrypted_msg = encrypt_ECC(msg, pubkey)
                    msg_packet = MessagePacket(username, val, encrypted_msg)
                    client.send(msg_packet)

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
            send_message(client)
        if val == '2':
            read_messages(client)
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
    global username
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


    

