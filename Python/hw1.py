import os, sys

def create_folders(path, prefix, counts, mode):
    for i in range(1, int(counts) + 1): 
        folder_path = os.path.join(path, prefix + str(i))
        try:
            os.mkdir(folder_path, int('0o' + mode, 8))
        except OSError:
            print("Folder creation failed")
        else:
             print("Created directory " + folder_path)

if __name__ == '__main__':             
    create_folders(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
