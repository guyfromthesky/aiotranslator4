
def get_version(version_number=1000):
    a,b,c,d = list(str(version_number))
    return a + '.' + b + '.' + c + chr(int(d)+97)