import sys, os, paramiko

input_address = sys.argv[1]
input_port = sys.argv[2]
input_name = sys.argv[3]
input_path = sys.argv[4]
input_prefix = sys.argv[5]
input_counts = sys.argv[6]
input_mode = sys.argv[7]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(input_address, port=input_port, username=input_name, password=None, key_filename=os.path.join(os.path.expanduser('~'),'.ssh','id_rsa'))

def create_folders(input_path, input_prefix, input_counts, input_mode):
    for i in range(1, int(input_counts) + 1): 
        folder_path = str(input_path) + '/' + str(input_prefix) + str(i)
        try:
            command = 'mkdir -p -m '+ str(input_mode) + ' ' + str(folder_path)
            print(command)
            stdin = ssh.exec_command(command)
        except OSError:
            print("Folder creation failed")
        else:
             print("Created directory " + folder_path)

create_folders(input_path, input_prefix, input_counts, input_mode)

ssh.close()