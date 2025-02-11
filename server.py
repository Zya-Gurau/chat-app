import socket
import threading
import pickle
from user_info import UserInfo
from packets import LoginStaus

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 9797

#key:username value:password
user_info_database = dict()
key_data_base = dict()

def client_thread(conn, addr):
    with conn:
        print(f"[CONNECTION] Connected to {addr}")
        while True:
            rec_data = conn.recv(1024)
            if not rec_data:
                break
            
            #read header
            magic_no = rec_data[0]<<8 | rec_data[1]
            r_id = rec_data[2]
            if magic_no != 0xAE73:
                raise ValueError("magic number incorrect")
            
            #login attempt
            if r_id == 1:
                info = []
                for i in range(3, 3 + len(rec_data[3:])):
                    info.append(rec_data[i])
                user_data = pickle.loads(bytearray(info))
                if user_data.username in user_info_database.keys() and user_data.password == user_info_database[user_data.username]:
                    response_packet = LoginStaus(3)
                else:
                    response_packet = LoginStaus(4)
                conn.send(response_packet.content)

            #signup attempt
            if r_id == 2:
                info = []
                #info_len = rec_data[3]
                for i in range(3, 3+ len(rec_data[3:])):
                    info.append(rec_data[i])
    
                user_data = pickle.loads(bytes(info))
                if user_data.username not in user_info_database.keys():
                    user_info_database[user_data.username] = user_data.password
                    response_packet = LoginStaus(3)
                    key_data_base[user_data.username] = user_data.public_key
                else:
                    response_packet = LoginStaus(4)
                print(key_data_base)
                conn.send(response_packet.content)

    print(f"[CONNECTION] Disconnected from {addr}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((SERVER, PORT))
    s.listen(5)
    print(f"[INFO] Listening on {SERVER}:{PORT}")

    while True:
        conn, addr = s.accept()
        print(f"[INFO] Starting thread for connection {addr}")
        thread = threading.Thread(target=client_thread, args=(conn, addr))
        thread.start()