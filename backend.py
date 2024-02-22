#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import base64
from openpyxl import load_workbook
from openpyxl.drawing.image import Image
import pandas as pd
import csv
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None, None, None, None]})
        return self.__user_data


class DbAct:
    def __init__(self, db, path_xlsx, image_folder):
        super(DbAct, self).__init__()
        self.__db = db
        self.__fields = ['Номер телефона', 'Артикул', 'Имя', 'Фото']
        self.__dump_path_xlsx = path_xlsx
        self.__img_folder_path = image_folder

    def save_photo(self, byte_row, name):
        with open(name, 'wb') as photo:
            photo.write(byte_row)

    def insert_images_to_excel(self, image_paths, excel_filename):
        counter = -3
        wb = load_workbook(excel_filename)
        ws = wb.active
        for img_path in range(len(image_paths)):
            counter += 5
            img = Image(image_paths[img_path])
            img.height = 100
            img.width = 100
            # Define the cell where you want to insert the image (A1, B2, etc.)
            cell = f"D{counter}"
            ws.add_image(img, cell)
        wb.save(excel_filename)

    def db_export_xlsx(self):
        photos = list()
        d = {'Номер телефона': [], 'Артикул': [], 'Имя': [], 'Фото': []}
        users = self.__db.db_read('SELECT phonenumber, articul, name, photo FROM users', ())
        if len(users) > 0:
            for user in users:
                for info in range(len(list(user))):
                    if info == 3:
                        photos.append(f'{self.__img_folder_path}/{user[info]}.png')
                    d[self.__fields[info]].append(user[info])
                for i in range(4):
                    for j in range(4):
                        d[self.__fields[j]].append(None)
            print(d)
            df = pd.DataFrame(d)
            df.to_excel(self.__dump_path_xlsx, sheet_name='пользователи', index=False)
            self.insert_images_to_excel(photos, self.__dump_path_xlsx)

    def add_review(self, data):
        max_id = self.__db.db_read('SELECT MAX(row_id) FROM users', ())
        print(max_id)
        if max_id[0][0] != None:
            new_entry = int(max_id[0][0]) + 1
        else:
            new_entry = 1
        self.__db.db_write(f'INSERT INTO users (phonenumber, articul, name, photo) VALUES (?, ?, ?, ?)',
                                         (data[0], data[1], data[2], new_entry))
        self.save_photo(data[3], f'{self.__img_folder_path}/{new_entry}.png')
