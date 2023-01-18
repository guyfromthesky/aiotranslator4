import xlwings as xw

wb = xw.Book(r'C:\Users\evan\Downloads\New.xlsx')  # connect to a file that is open or in the current working directory

for sheet_name in wb.sheets:
    sheet = wb.sheets[sheet_name]


wb.save(r'C:\Users\evan\Downloads\New 2.xlsx')