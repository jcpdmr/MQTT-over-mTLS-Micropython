import os

def rm(d):  # Remove file or tree
    try:
        if os.stat(d)[0] & 0x4000:  # Dir
            for f in os.ilistdir(d):
                if f[0] not in ('.', '..'):
                    rm("/".join((d, f[0])))  # File or Dir
            os.rmdir(d)
        else:  # File
            os.remove(d)
    except Exception as e:
        print(e)
        print("rm of '%s' failed" % d)

if __name__ == "__main__":
    for dir in os.listdir("./"):
        rm(dir)