#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import os
import telebot
from threading import Lock
from db import DB
from frontend import Bot_inline_btns
from backend import TempUserData, DbAct

####################################################################
tg_api = '6667593230:AAH2ZgrEVgdE4DEt49ksZ-qD1ThJkEXIPag'
db_name = 'db.sqlite3'
xlsx_path = 'dump.xlsx'
image_folder = 'photos'
bot = telebot.TeleBot(tg_api)


####################################################################


def main():
    @bot.message_handler(commands=['start'])
    def start_msg(message):
        #print(f'{message.from_user.first_name}, {message.from_user.last_name}')  # имя фамилия пользователя
        buttons = Bot_inline_btns()
        bot.send_message(message.chat.id, 'Привет!👋\n'
                                          'Благодарим за покупку🖤\n'
                                          'Мы подготовили для вас приятный бонус, '
                                          'чтобы получить его, напишите отзыв😊\n'
                                          'Если у вас возникли какие-то проблемы с заказом '
                                          'свяжитесь с нашим менеджером👨‍💻\n'
                                          'Мы поможем в решении любого вопроса!', reply_markup=buttons.start_btns())

    @bot.message_handler(content_types=['text', 'photo', 'contact'])
    def text(message):
        user_input = message.text
        user_id = message.chat.id
        user_current_action = temp_user_data.temp_data(user_id)[user_id][0]
        if user_current_action == 0:
            bot.send_message(message.chat.id, 'Отправьте фото отзыва')
            contact = message.chat.id
            temp_user_data.temp_data(message.chat.id)[message.chat.id][0] = 1
        elif user_current_action == 1:
            temp_user_data.temp_data(user_id)[user_id][2] = user_input
            photo_id = message.photo[-1].file_id
            photo_file = bot.get_file(photo_id)
            photo_bytes = bot.download_file(photo_file.file_path)
            temp_user_data.temp_data(user_id)[user_id][2] = photo_bytes
            bot.send_message(message.chat.id, 'Проверка информации...')
            db_actions.add_review(temp_user_data.temp_data(message.chat.id)[message.chat.id][1:])
            topic_id = telebot.TeleBot.create_forum_topic(bot, chat_id=-1002003996301,
                                                          name=f'{message.from_user.first_name} {message.from_user.last_name} ОТЗЫВ',
                                                          icon_color=0x6FB9F0).message_thread_id
            bot.forward_message(chat_id=-1002003996301, from_chat_id=message.chat.id, message_id=message.id, message_thread_id=topic_id)
        elif user_current_action == 2:
            bot.send_message(message.chat.id, 'Заявка принята! Ожидайте...')
            topic_id = telebot.TeleBot.create_forum_topic(bot, chat_id=-1002003996301,
                                               name=f'{message.from_user.first_name} {message.from_user.last_name} ПРОБЛЕМА С ТОВАРОМ',
                                               icon_color=0x6FB9F0,
                                               icon_custom_emoji_id='T').message_thread_id
            bot.forward_message(chat_id=-1002003996301, from_chat_id=message.chat.id, message_id=message.id, message_thread_id=topic_id)

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        buttons = Bot_inline_btns()
        if call.data == 'take_gift':
            bot.send_message(call.message.chat.id,
                             'Для получения подарка:\n1.Нажмите кнопку: "Поделиться контактом"',
                             reply_markup=buttons.share_number_btn())

            temp_user_data.temp_data(call.message.chat.id)[call.message.chat.id][0] = 0

        elif call.data == 'write_manager':
            bot.send_message(call.message.chat.id, 'Выберите пожалуйста категорию обращения!',
                             reply_markup=buttons.write_manager_btns())
        elif call.data in ['another_question', 'complectation_product', 'quality_product']:
            if call.message and call.message.chat:
                bot.send_message(call.message.chat.id, 'Пожалуйста, подробно опишите проблему!\n'
                                                       'Так же по возможности приложите фотографии, демонстрирующие '
                                                       'проблему.\n'
                                                       'Мы ответим в течении 24 часов!')
                temp_user_data.temp_data(call.message.chat.id)[call.message.chat.id][0] = 2

    # контакт пользователя
    @bot.message_handler(content_types=['contact'])
    def text(message):
        if message.contact is not None:
            print(message.contact)

    bot.polling(none_stop=True)


if '__main__' == __name__:
    if not os.path.exists(image_folder):
        os.mkdir(image_folder)
    temp_user_data = TempUserData()
    db = DB('db.sqlite3', Lock())
    db_actions = DbAct(db, xlsx_path, image_folder)
    main()
