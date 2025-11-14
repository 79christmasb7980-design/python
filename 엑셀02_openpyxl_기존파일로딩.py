import openpyxl as op 

wb = op.load_workbook("infrom_note.xlsx")

#새로운 시트 추가 
ws = wb.create_sheet("sheet1")

wb.save("infrom_note.xlsx")

