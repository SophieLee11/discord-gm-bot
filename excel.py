from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.utils import get_column_letter



def create_excel(headers, data):

	wb = Workbook()
	ws = wb.active

	ws.append(headers)

	for row in data:
		ws.append(row)

	width = len(data[0])
	height = len(data) + 1

	values = Reference(ws, min_col = 2, min_row = 1, max_col = width, max_row = height)
	chart = LineChart()

	for idx, col in enumerate(ws.columns, 1):
		ws.column_dimensions[get_column_letter(idx)].auto_size = True

	for col in ws.columns:
		for cell in [col[0]]:
			alignment_obj = cell.alignment.copy(horizontal='center', vertical='center')
			cell.alignment = alignment_obj

	ws.column_dimensions["A"].width = 28

	wb.save("gm_data.xlsx")