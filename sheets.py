import gspread
from oauth2client.service_account import ServiceAccountCredentials

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json')

file = gspread.authorize(creds)
workbook = file.open("test")
sheet = workbook.sheet1
for cell in sheet.range('A1:C3'):
    print(cell.value)
    image_id = ""  # put the id
    insert_image = '=IMAGE(f"https://drive.google.com/uc?export=view&id={image_id}")'
    sheet_range = "A6"  # Add where you want to insert the image for example A2:A2 to insert the image into the cell A2
    sheet.update(sheet_range, [[insert_image]], value_input_option="USER_ENTERED")
#sheet.update_acell('A6', 'E:\\Work\\wilberriesbotv2\\photos\\2.png') #крч, в ячейку A4 добавиться текст 123456789

#sheet.update('A6:C6', [['test1', 'test2', 'test3']])

