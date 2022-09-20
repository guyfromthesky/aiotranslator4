from pathlib import Path
import glob, os

while True:
    print('Enter the file path:')
    x = input()
    path = x + '\**'
    print("intput path", path)
    _total = 0
    _counter = 0
    for filename in glob.iglob(path, recursive=True):
        _total+=1
        try:
            new_name = filename.encode('cp437').decode('euc_kr')   
        except Exception as e:
            print("Error while decode file: ", filename)
            print("Error:",e)
            continue
        if filename != new_name:
            
            try:
                print("Error while rename file: ", filename, 'to,', new_name)
                os.rename(filename, new_name)
                _counter+=1
            except Exception as e:
                print("Error:",e)

    print("Total files: ", _total)       
    print("Total malformed file name:", _counter)    