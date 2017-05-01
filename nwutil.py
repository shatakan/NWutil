#!/usr/bin/python

# Module imports and global vars

import threading
import sys
import socket
import getopt
import subprocess

listen = False
command = False
upload_file = False
execute = ""
target = ""
upload_destination = ""
port = 0

# Command/usage help text
def help():
    print "Generic client/server network utility"
    print "------------"
    print "Use: nwutil.py -t target_host -p port"
    print "-l --listen              - listen on [host]:[port] for incoming connections"
    print "-e --excute=file_to_run  - execute the given file upon recieving a connection"
    print "-c --command             - initialise a command shell"
    print "-u --upload-destination  - upon receiving connection upload a file and write to [destination]"
    print ""
    print ""
    print "Examples: "
    print "nwutil.py -t 192.168.0.1 -p 5555 -l -c"
    print "nwutil.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "nwutil.py -t 192.168.0.1 -p 5555 -l -e=\ 'cat etc/passwd\'"
    print "echo 'ABCDEFGHI' | ./nwutil.py -t 192.168.11.12 -p 135"
    sys.exit(0)

def client_sender(buffer):
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((target, port))
        
        if len(buffer):
            client.send(buffer)
        while True:
            recv_len = 1
            response = ""
        while recv_len:
            data = client.recv(4096)
            recv_len = len(data)
            response += data
            if recv_len < 4096:
                break
            
            print response,
            
            # Wait for more input from client 
            buffer = raw_input("")
            buffer += "\n"
            
            client.send(buffer)
    
    except:
        print "[*] Exception! Exiting now..."
        # Terminate connection
        client.close()        
            

def server_loop():
    global target
    
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        
        # Create a new thread
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()
        
    # Remove all whitespace chars from command
    
def run_command(command):
    command = command.rstrip()
    
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command. \r\n"
    return output

def client_handler(client_socket):
    global upload_file
    global execute
    global command
    
    #Check if upload exists
    if len(upload_destination):
        
        #Store output as a buffer
        file_buffer = ""
        
        while True:
            data = client_socket.recv(1024)
            if not data:
                break            
            file_buffer += data
        
        #Write our file to destination specified 
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            
        #If successful:
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        #If unsuccessful:
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
            
    #If command to execute exists:        
    if len(execute):
        output = run_command(execute)
        client_socket.send(output) 
        
    if command:
        while True:
            #Send a command prompt
            client_socket.send("NW_UTIL:#> ")
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            
            response = run_command(cmd_buffer)
            client_socket.send(response)
    
# Main function 
def main():
    global listen
    global command
    global execute
    global target
    global port
    global upload_destination
    
    if not len(sys.argv[1:]):
        help()
        
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", ["help","listen","execute","target","port","command","upload_file"])
    except getopt.GetoptError as err:
        print str(err)
        help()
        
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
    # "Client" mode
    if not listen and len(target) and port > 0:
        # Save keyboard input into a buffer
        buffer = sys.stdin.read()
        
        client_sender(buffer)
    #"Server" mode    
    if listen:
        server_loop()
 
main()