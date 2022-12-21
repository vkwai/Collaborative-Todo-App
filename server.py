import socket
import json
import re
import threading
from pymongo_get_database import get_database

db = get_database()

user_collection = db["users"]
todo_collection = db["todos"]


hostname=socket.gethostname()   
bind_ip=socket.gethostbyname(hostname)   
bind_port =1117 # need to open this port if using Linux
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip,bind_port))
server.listen(5)

def server_program(conn, address):
    
    """
    #boilerplate codes
    host = socket.gethostname()
    port = 8109  
    server_socket = socket.socket()  
    server_socket.bind((host, port))  
    server_socket.listen(2) #num of clients
    """
    
    
    #client connection with initial request
    # conn, address = server_socket.accept()  
    request = {"request": ""}
    response = {"response": ""}
    buff = {"buff": ""}
    # conn.send(json.dumps(request).encode())
    
    def prompt(message):
        buff["buff"] += message + "\n"
        # request["request"] = message
        # conn.send(json.dumps(request).encode())  
        # return
        
    def get(message):
        request["request"] = buff["buff"] +  message
        conn.send(json.dumps(request).encode())  
        response = json.loads(conn.recv(2048).decode())
        buff["buff"] = ""
        
        return response["response"]
    state = {
        "menuLayer": 1,
        "user": {},
        "todo": {}
    }
    def prepMenu(title):
        s = ""
        if (len(state["user"]) > 0):
            s += state["user"]["name"]
            
        if (len(state["todo"]) > 0):
            s += "/" + state["todo"]["name"]
        prompt("\n")
        prompt(title+ " (" + s + ")")
        prompt("*Press 0 for any prompts cancel")
        prompt("-----------------")
    def selectMenu(choices, again=False):
        if (again):
            inp = get("0 to return. Or anything else to try again ->")
            if (inp == "0"):
                return 0
        # valid return ranges [1 - #ofchoices], #ofchoices+1 for exit
        prepMenu("Select")
        prompt(str(0) + ". "+ " Back")
        index = 1
        for option in choices:
            prompt(str(index) + ". "+ option)
            index += 1
        prompt(str(index) + ". "+ " Exit")
        inp = get("-> ")
        if (not inp.isdigit() ):
            prompt("Invalid Choice")
            return selectMenu(choices, True)
        if (inp == "0"): #back option
            return 0
        elif (int(inp) == len(choices)+1): #exit option
            return -1 
        elif (int(inp) < 0 or (int(inp) > (len(choices)+1))):
            prompt("Invalid Choice. Try again")
            return selectMenu(choices, True)
        return int(inp)
    def registerMenu(again=False): #validate or add to db_users
        if (again):
            inp = get("0 to return. Or anything else to try again ->")
            if (inp == "0"):
                return 0
        prepMenu("Register")
        prompt("1. Usernames should have atleast 3 of any characters")
        prompt("2. Passwords should have atleast 5 characters. atleast 1 number")
        name = get("Username: ")
        if (name=="0"):
            return 0
        password = get("Password: ")
        if (password=="0"):
            return 0
            
        #guard clauses here
        find = {"name": name}
        if (user_collection.find_one(find) != None):
            prompt("A user has already chosen that username.")
            return registerMenu(True)
        
        if ((len(name) < 3) or (len(password) < 5)):
            prompt("A field entered is not long enough")
            return registerMenu(True)
        #elif regex check
        if (re.search("[a-z]{3,}", password) and re.search("[0-9]", password)):
            prompt("")
        else:
            prompt("Password is missing restrictions. Try again")
            return registerMenu(True)
        
        #success
        newUser = {"name": name, "password": password}
        user_collection.insert_one(newUser)
        return 0
    def loginMenu(again=False): #take get. find get inside db. exit or repeat. if found. update state
        if (again):
            inp = get("0 to return. Or anything else to try again ->")
            if (inp == "0"):
                return 0
        prepMenu("Login")
        name = get("Username: ")
        if (name=="0"):
            return 0
        password = get("Password: ")
        if (password=="0"):
            return 0
        #guard clause here
        find = {"name": name}
        result = user_collection.find_one(find)
        if (result == None):
            prompt("That username is not recognized. Try again or register")
            return loginMenu(True)
        if (result["password"] != password):
            prompt("Wrong password")
            return loginMenu(True)
            
        state["user"] = result
        state["menuLayer"] += 1 
        return 0
    def createtodoMenu(): #take get. add to db_todos
        prepMenu("Create todo")
        name = get("todo name: ")
        if (name=="0"):
            return 0
        newtodo = {"name": name, "users": [state["user"]["name"]], "tasks": []}
        todo_collection.insert_one(newtodo)
        return 0
    def selecttodoMenu(again=False): #get all db_todos 
        if (again):
            inp = get("0 to return. Or anything else to try again ->")
            if (inp == "0"):
                return 0
        prepMenu("Select todo")
        
        found = []
        for p in todo_collection.find():
          for u in p["users"]:
              if (u == state["user"]["name"]):
                  found.append(p)
        index = 1
        for i in found:
            prompt(str(index) + ": " + i["name"])
            index += 1
        index -=1
        inp = get("Choice ->")
        if (inp == "0"):
            return 0
        if (not inp.isdigit() ):
            prompt("Invalid Choice")
            return selecttodoMenu(True)
        elif (int(inp) <0 or int(inp) > index):
            prompt("Invalid Choice")
            return selecttodoMenu(True)
        
        
        state["todo"] = found[index-1]
        state["menuLayer"] += 1 
        
        # if (name=="0"):
        #     return 0
        return 0
    def filterSortMenu():
        inp = get("Enter a keyword to match (sort keyword can used to sort alphabetically (case sensitive)): ")
        if (inp == "sort"):
            state["todo"]["tasks"].sort()
            for i in state["todo"]["tasks"]:
                prompt("- "+ i)
            return 0
            
        valid = []
        for i in state["todo"]["tasks"]:
            if (re.search(inp, i)):
                valid.append(i)
            
        if (len(valid) < 1):
            prompt("No results found")
        else: 
            prompt("Showing results for the match: "+ inp)
            for i in valid:
                prompt("- "+ i)
        inp = get("Press 1 to request another filter or any other key to return -> ")
        if (inp == "1"):
            return filterSortMenu()
        return 0
    def showtodo():
        prepMenu("todo")
        s = ""
        for i in state["todo"]["users"]:
            s += i + ", "
        prompt("Users that can access this todo: (" + s + ")")
        for i in state["todo"]["tasks"]:
            prompt("- "+i)
        inp = get("Press 0 to filter or any other key to go back to menu ->")
        if (inp == "0"):
            return filterSortMenu()
        return 0
    def createTaskMenu(): #take get. find/store col with state data. append/delete task to taskList.  
        prepMenu("Add Task")
        name = get("Task name: ")
        if (name=="0"):
            return 0
        state["todo"]["tasks"].append(name)
        find = {"_id": state["todo"]["_id"]}
        update = {"$set": {"tasks": state["todo"]["tasks"]}}
        todo_collection.update_one(find, update)
        return 0
        # return {"taskName": name}
    def deleteTaskMenu(again=False): #display all tasks using todo state. map choice with todo. delete choice if exists
        if (again):
            inp = get("0 to return. Or anything else to try again ->")
            if (inp == "0"):
                return 0
        prepMenu("Delete Task")
        index = 1
        for i in state["todo"]["tasks"]:
            prompt(str(index) + ":"+ i)
            index += 1
        inp = get("Choice ->")
        if (inp == "0"):
            return 0
        if (not inp.isdigit() ):
            prompt("Invalid Choice")
            return deleteTaskMenu(True)
        elif (int(inp) <0 or int(inp) > index-1):
            prompt("Invalid Choice")
            return deleteTaskMenu(True)
        state["todo"]["tasks"].pop(int(inp)-1)
        find = {"_id": state["todo"]["_id"]}
        update = {"$set": {"tasks": state["todo"]["tasks"]}}
        todo_collection.update_one(find, update)
        
        return 0
    def inviteUserMenu(again=False): #display all users. map choice with todo. grab current todo with todo state
        if (again):
            inp = get("0 to return. Or anything else to try again ->")
            if (inp == "0"):
                return 0
        prepMenu("Invite Users")
        found = []
        for u in user_collection.find():
            if (u["name"] == state["user"]["name"]):
                continue
            found.append(u)
        index = 1
        for i in found:
            prompt(str(index) + ": " + i["name"])
            index += 1
        index -=1
        inp = get("Choice ->")
        if (inp == "0"):
            return 0
        if (not inp.isdigit() ):
            prompt("Invalid Choice")
            return inviteUserMenu(True)
        elif (len(u) == 0):
            prompt("No Users Found")
            return 0
        elif (int(inp) <0 or int(inp) > index):
            prompt("Invalid Choice")
            return inviteUserMenu(True)
        
        chosen = found[int(inp)-1]["name"]
        # prompt(chosen)
        state["todo"]["users"].append(chosen)
        find = {"_id": state["todo"]["_id"]}
        update = {"$set": {"users": state["todo"]["users"]}}
        todo_collection.update_one(find, update)
        
        return 0
    
        
    #for reference,
    #state = {
    #     "menuLayer": 1,
    #     "user": {},
    #     "todo": ""
    # }
    
    menus = {
        1: { 
            "start" : ["Register","Login"],
            1: registerMenu,
            2: loginMenu #->
            },
        2: {
            "start" : ["Create Todo List","Select Todo List"],  
            1: createtodoMenu,
            2: selecttodoMenu #->
        },
        3: {
            "start" : ["Show Todos", "Create Task", "Delete Task", "Invite Users"],
            1: showtodo,
            2: createTaskMenu,
            3: deleteTaskMenu,
            4: inviteUserMenu
        }
    }
    while (state["menuLayer"] != -1):
        c = selectMenu(menus[state["menuLayer"]]["start"])
        if (c == 0):
            if (state["menuLayer"] == 3):
                state["todo"].clear()
            elif (state["menuLayer"] == 2):
                state["user"].clear()
            else:
                prompt("Exiting")
                break
            state["menuLayer"] -= 1
        elif (c == -1):
            prompt("Exiting")
            break
        else: 
            menus[state["menuLayer"]][c]()
            # menus[state["menuLayer"]][c]()
            # prompt(state["menuLayer"])
    

    request["request"] = "bye"
    conn.send(json.dumps(request).encode())  
    conn.close()  


# if __name__ == '__main__':
#     server_program()
while True:
    client,addr = server.accept()
    print ("[*] Accepted connection from: {:16s}:{:d}".format(addr[0],addr[1]))
    # spin up our client thread to handle incoming data
    client_handler = threading.Thread(target=server_program,args=(client,addr,))
    client_handler.start()