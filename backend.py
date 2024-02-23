#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None, None, [None, None], None]})
        return self.__user_data


class ExcellUpdate:
    def __init__(self, db):
        super(ExcellUpdate, self).__init__()
        self.__codes = {0: 'обращение в поддержку', 1: 'запрос на отзыв', 2: 'сообщение от пользователя', 3: 'сообщение от модератора'}
        self.__column_names_db = [['Дата время (UTC)', 'Пользователь (TG)', 'Тип запроса']]
        self.__column_names_quanity = [['Поддержка', 'Отзыв', 'Всего обращений', 'Ответ менеджера']]
        self.__db = db
        self.__sheet = None
        self.init()

    def init(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json')
        file = gspread.authorize(creds)
        workbook = file.open("события бота")
        self.__sheet = workbook.sheet1

    def update_excell(self):
        data = self.__column_names_db + self.get_db_data()
        self.__sheet.update(f'A1:C{len(data)}', data)
        data1 = self.__column_names_quanity + [[self.get_quanity(0), self.get_quanity(1), self.get_quanity(2), self.get_quanity(3)]]
        self.__sheet.update(f'F1:I{len(data1)}', data1)

    def get_db_data(self):
        formated = []
        data = self.__db.db_read("SELECT time, nick_tg, request_type FROM actions", ())
        if len(data) > 0:
            for row in data:
                formated.append([datetime.utcfromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S'), row[1], self.__codes[row[2]]])
        return formated

    def get_quanity(self, req_type):
        data = self.__db.db_read('SELECT count(*) FROM actions WHERE request_type = ?', (req_type, ))
        if len(data) > 0:
            return data[0][0]


class DbAct:
    def __init__(self, db):
        super(DbAct, self).__init__()
        self.__db = db
        self.__fields = ['Номер телефона', 'Артикул', 'Имя', 'Фото']
        #self.__dump_path_xlsx = path_xlsx
        #self.__img_folder_path = image_folder
        self.__excell_update = ExcellUpdate(db)

    def save_photo(self, byte_row, name):
        with open(name, 'wb') as photo:
            photo.write(byte_row)

    def get_user_id_from_topic(self, topic_id):
        data = self.__db.db_read("SELECT user_id FROM users WHERE topic_review_id = ?", (topic_id, ))
        if len(data) > 0:
            return data[0][0]

    def add_action(self, user_id, req_type):
        data = self.__db.db_read("SELECT nick_name FROM users WHERE user_id = ?", (user_id,))
        if len(data) > 0:
            self.__db.db_write('INSERT INTO actions (time, nick_tg, request_type) VALUES (?, ?, ?)', (int(time.time()), data[0][0], req_type)) # 0 - создана проблема, 1 - создан отзыв, 2 - пользователь отправил сообщение, 3 - модератор отправил сообщение
        self.__excell_update.update_excell()

    def add_user(self, user_id, first_name, last_name, nick_name):
        if not self.user_is_existed(user_id):
            self.__db.db_write('INSERT INTO users (user_id, first_name, last_name, nick_name, question_open, have_bonus) VALUES (?, ?, ?, ?, ?, ?)', (user_id, first_name, last_name, nick_name, False, False))

    def update_question_status(self, user_id, status):
        self.__db.db_write('UPDATE users SET question_open = ? WHERE user_id = ?', (status, user_id))

    def get_question_status(self, topic_id):
        data = self.__db.db_read('SELECT question_open FROM users WHERE topic_question_id = ?', (topic_id,))
        if len(data) > 0:
            if data[0][0] == 1:
                ans = True
            else:
                ans = False
            return ans

    def get_question_status_user_id(self, user_id):
        data = self.__db.db_read('SELECT question_open FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] == 1:
                ans = True
            else:
                ans = False
            return ans

    def user_is_existed(self, user_id):
        data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status

    def bonus_already_get(self, user_id):
        data = self.__db.db_read('SELECT have_bonus FROM users WHERE user_id = ?', (user_id, ))
        print(data)
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status

    def update_quest_id(self, user_id, topic_question_id):
        self.__db.db_write('UPDATE users SET topic_question_id = ? WHERE user_id = ?', (topic_question_id, user_id))

    def update_review_id(self, user_id, topic_review_id):
        self.__db.db_write('UPDATE users SET topic_review_id = ? WHERE user_id = ?', (topic_review_id, user_id))

    def get_quest_id(self, user_id):
        data = self.__db.db_read('SELECT topic_question_id FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            return data[0][0]

    def get_review_id(self, user_id):
        data = self.__db.db_read('SELECT topic_review_id FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            return data[0][0]

    def get_phone_numer_from_topic(self, topic_id):
        data = self.__db.db_read('SELECT phone_number FROM users WHERE topic_review_id = ?', (topic_id, ))
        if len(data) > 0:
            return data[0][0]

    def get_question_id(self, topic_id):
        data = self.__db.db_read('SELECT user_id FROM users WHERE topic_question_id = ?', (topic_id, ))
        if len(data) > 0:
            return data[0][0]

    def user_id_from_question_id(self, user_id):
        data = self.__db.db_read('SELECT topic_question_id FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            return data[0][0]

    def add_review(self, user_id, data):
        row_id = int(self.__db.db_read('SELECT row_id FROM users WHERE user_id = ?', (user_id, ))[0][0])
        self.__db.db_write('UPDATE users SET photo_review = ?, phone_number = ?, have_bonus = ? WHERE user_id = ?', (row_id, data[0], True, user_id))
        #self.save_photo(data[1], f'{self.__img_folder_path}/{row_id}.png')
