import xlwings as xw


wb = xw.Book()  # this will open a new workbook
wb = xw.Book(r'C:\Users\evan\Documents\GitHub\aiotranslator4\test script\Test file for shape and rich text.xlsx')  # connect to a file that is open or in the current working directory

wb.save(r'C:\Users\evan\Documents\GitHub\aiotranslator4\test script\Test file for shape and rich text 2.xlsx')