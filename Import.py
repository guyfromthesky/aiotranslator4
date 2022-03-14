import subprocess

import time
import win32api
	
from win32gui import GetWindowText, GetForegroundWindow


cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description,Id,Path'
proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
index = -1
for line in proc.stdout:
	if not line.decode()[0].isspace():
		index+=1
		if index <2:
			continue
		process = line.decode().rstrip().rsplit()
		PID = ''
		for i in range(len(process)):
			if process[i].isnumeric():
				sub_string = process[i].rsplit()
				for j in range(len(sub_string)):
					if sub_string[j].isnumeric():
						PID =sub_string[j]
						break
		if not PID.isspace():
			app_name = line.decode().rstrip().split(PID)[0].rstrip()
		else:
			app_name = line	
		print(app_name)

print('Active', GetWindowText(GetForegroundWindow()))

def getIdleTime():
    return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0

time.sleep(10)
print(getIdleTime())