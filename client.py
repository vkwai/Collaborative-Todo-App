import socket
import json

def client_program():
    #boilerplate
    host = socket.gethostname()  
    port = 1117  
    client_socket = socket.socket()  
    client_socket.connect((host, port))  
    
    response = {"response": ""}
    request = {"request": ""}
    # while response["response"].lower().strip() != 'bye':
    while request["request"].lower().strip() != 'bye':

        request = json.loads(client_socket.recv(2048).decode())
        print('Server:', request["request"], end="")  

        if (request["request"] != "bye"):
            inp = input("")  
            response["response"] = inp
            client_socket.send(json.dumps(response).encode())  
    print()
    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()