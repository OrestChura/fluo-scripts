import os
from shutil import copyfile
src = "G:\\database\\fluovisor\\dictionary.xml"
def put_dictionary(dir_name):
    for f in os.listdir(dir_name):
        f = os.path.join(dir_name, f)
        baseName, ext = os.path.splitext(f)
        if os.path.isdir(f):
            file_name = os.path.join(f,"dictionary.xml")
            copyfile(src, file_name)

if __name__ == '__main__':
    dir_name = "G:\\database\\fluovisor\\"
    put_dictionary(dir_name)