from openpyxl import Workbook



def create_excel(client, data):

	wb = Workbook()
	std = wb.get_sheet_by_name('Sheet')
	wb.remove_sheet(std)

	for server_id in data:
		lst = data[server_id]
		name = client.get_guild(server_id).name

		ws = wb.create_sheet(name)
		ws.append(['Date', 'Value', 'Gm_amount', 'Members'])

		for row in lst:
			ws.append(row)

	wb.save("gm_data.xlsx")