import os
from shutil import copyfile
src = "G:\\database\\fluovisor\\dictionary.xml"
def put_dictionary(dir_name_):
    for f in os.listdir(dir_name_):
        f = os.path.join(dir_name_, f)
        if os.path.isdir(f):
            file_name = os.path.join(f, "dictionary.xml")
            copyfile(src, file_name)

if __name__ == '__main__':
    dir_name = "G:\\database\\fluovisor\\"
    put_dictionary(dir_name)
