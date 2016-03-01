def run_concatenation(directory=None):
    import re, os
    from xlwings import Workbook, Range, Application
    wb = Workbook(app_visible=False)
    lastRow = 3
    newlastRow = lastRow
    lastColumn = 6
    if directory is None:
        directory = os.getcwd()    
    for file in os.listdir(directory):
        findling = re.search(r'.*Data.*[0-9]{2,3}.*.xls$', file)
        if findling:
            wb2 = Workbook(os.path.abspath(findling.group()), \
                           app_visible=False)
            addedRows = Range((4, 1), wkb = wb2).table.last_cell.row - 3
            newlastRow = lastRow + addedRows
            Range((lastRow+1, lastColumn+1), wkb = wb).value = \
                            findling.group()
            Range((lastRow+1, 1), wkb = wb).table.value = \
                Range((4, 1), (newlastRow, lastColumn), wkb = wb2).value
            lastRow = newlastRow
            wb2.close()
    wb.save(os.path.join(os.getcwd(), 'Output.xlsx'))
    wb.close()

run_concatenation()