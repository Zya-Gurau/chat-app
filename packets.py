import pickle

class PacketHeader:
    def __init__(self, id):
        self.content = bytearray(3)
        self.content[0] = 0xAE
        self.content[1] = 0x73
        self.content[2] = id

class LoginPacket(PacketHeader):
    def __init__(self, user_info):
        super().__init__(1)
        serialised_info = bytearray(pickle.dumps(user_info))
        for byte in serialised_info:
            self.content.append(byte)

class SignUpPacket(PacketHeader):
    def __init__(self, user_info):
        super().__init__(2)
        serialised_info = bytearray(pickle.dumps(user_info))
        for byte in serialised_info:
            self.content.append(byte)

class MessagePacket(PacketHeader):
    def __init__(self, name, rec_name, message):
        super().__init__(5)
        self.content.append(len(name))
        for byte in name:
            self.content.append(byte)

        self.content.append(len(rec_name))
        for byte in rec_name:
            self.content.append(byte)
            
        serialised_info = bytearray(pickle.dumps(message))
        self.content.append(len(serialised_info))
        for byte in serialised_info:
            self.content.append(byte)

class MessagesForUserPacket(PacketHeader):
    def __init__(self, messages):
        super().__init__(8)
        self.content.append(len(messages))

        for item in messages:
            self.content.append()
        
            self.content.append(len(item[0]))
            self.content.append(len(item[1])>>8)
            self.content.append(0xff & len(item[1])) 

            for byte in item[0]:
                self.content.append(byte)
            for byte in item[1]:
                self.content.append(byte)


class GetMessagePacket(PacketHeader):
    def __init__(self):
        super().__init__id(6)

class GetKeysPacket(PacketHeader):
    def __init__(self):
        super().__init__id(7)

class LoginStaus(PacketHeader):
    def __init__(self, id):
        super().__init__(id)


