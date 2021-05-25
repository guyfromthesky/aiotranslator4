from multiprocessing import Process, freeze_support
import sys
def greet_me(**kwargs):
	for key, value in kwargs.items():
		print("{0} = {1}".format(key, value))

	if 'name' in kwargs:
		print("{0} = {1}".format('name', value))

def test(value = 1, value_2 = 2, **kwargs):
	print(value)
	print(value_2)

def Execuser():
	UpdateProcess = Process(target=test, kwargs= {'value_2': 3})
	UpdateProcess.start()

if __name__ == '__main__':
	if sys.platform.startswith('win'):
		freeze_support()
	Execuser()
