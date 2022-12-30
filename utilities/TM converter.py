
import pickle

print('Please input the TM path:')
tm_path = input()

with open(tm_path, 'rb') as pickle_load:
    all_tm = pickle.load(pickle_load)
print('All tm available in the TM file: ', all_tm.keys())

print('Please input the Project you want to move:')
_to_move_key = input()

temp_tm = all_tm[_to_move_key]

print('Please input the Project you want to move to:')
_to_move_to_key = input()

all_tm[_to_move_to_key] = temp_tm
del all_tm[_to_move_key]

print('Current project in the TM:')
print(all_tm.keys())

with open(tm_path, 'wb') as pickle_file:
    print("Updating pickle file....", tm_path)
    pickle.dump(all_tm, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)    
    print('Done!')

