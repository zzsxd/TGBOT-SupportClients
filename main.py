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
work_dir = '/root/wilberriesbotv2/'
tg_api = '6667593230:AAH2ZgrEVgdE4DEt49ksZ-qD1ThJkEXIPag'
group_id = -1002003996301
db_name = work_dir + 'db.sqlite3'
#xlsx_path = work_dir + 'dump.xlsx'
#image_folder = work_dir + 'photos'
bot = telebot.TeleBot(tg_api)
####################################################################


def main():
    @bot.message_handler(commands=['start'])
    def start_msg(message):
        # print(f'{message.from_user.first_name}, {message.from_user.last_name}')  # имя фамилия пользователя
        user_id = message.chat.id
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name, f'@{message.from_user.username}')
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
        buttons = Bot_inline_btns()
        user_input = message.text
        user_id = message.chat.id
        contact = message.contact
        photo = message.photo
        if db_actions.user_is_existed(user_id):
            user_current_action = temp_user_data.temp_data(user_id)[user_id][0]
            if user_current_action == 0:
                if contact is not None:
                    contact_forward_id = message.id
                    temp_user_data.temp_data(user_id)[user_id][1] = contact.phone_number
                    bot.send_message(message.chat.id, '2. Отправьте фото отзыва📷',
                                     reply_markup=telebot.types.ReplyKeyboardRemove())
                    temp_user_data.temp_data(message.chat.id)[message.chat.id][3][0] = contact_forward_id
                    temp_user_data.temp_data(message.chat.id)[message.chat.id][0] = 1
                else:
                    bot.send_message(message.chat.id, '❌Это не контакт❌')
            elif user_current_action == 1:
                if photo is not None:
                    buttons = Bot_inline_btns()
                    photo_forward_id = message.id
                    temp_user_data.temp_data(message.chat.id)[message.chat.id][3][1] = photo_forward_id
                    photo_id = photo[-1].file_id
                    photo_file = bot.get_file(photo_id)
                    photo_bytes = bot.download_file(photo_file.file_path)
                    temp_user_data.temp_data(user_id)[user_id][2] = photo_bytes
                    db_actions.add_review(user_id, temp_user_data.temp_data(user_id)[user_id][1:3])
                    temp_user_data.temp_data(message.chat.id)[message.chat.id][0] = None
                    topic_id = telebot.TeleBot.create_forum_topic(bot, chat_id=group_id,
                                                                  name=f'{message.from_user.first_name} '
                                                                       f'{message.from_user.last_name} ОТЗЫВ',
                                                                  icon_color=0x6FB9F0).message_thread_id
                    bot.forward_messages(chat_id=group_id, from_chat_id=user_id,
                                         message_ids=temp_user_data.temp_data(message.chat.id)[message.chat.id][3],
                                         message_thread_id=topic_id)
                    db_actions.update_review_id(user_id, topic_id)
                    bot.send_message(chat_id=group_id, message_thread_id=topic_id, text='Получен отзыв!✅\n'
                                                                                        'Проверьте информацию и '
                                                                                        'отправьте вознаграждение на '
                                                                                        f'номер телефона: '
                                                                                        f'{temp_user_data.temp_data(message.chat.id)[message.chat.id][1]}',
                                     reply_markup=buttons.review_manager_btns())
                    db_actions.add_action(user_id, 1)
                    bot.send_message(message.chat.id, 'Проверка информации...')
                else:
                    bot.send_message(message.chat.id, '❌Это не фото❌')
            elif user_current_action == 2:
                topic_id = db_actions.get_quest_id(user_id)
                if topic_id is None:
                    topic_id = telebot.TeleBot.create_forum_topic(bot, chat_id=group_id,
                                                                  name=f'{message.from_user.first_name} '
                                                                       f'{message.from_user.last_name} ПРОБЛЕМА С '
                                                                       f'ТОВАРОМ',
                                                                  icon_color=0x6FB9F0,
                                                                  icon_custom_emoji_id='T').message_thread_id
                    db_actions.update_quest_id(user_id, topic_id)
                    bot.send_message(chat_id=group_id, message_thread_id=topic_id, text='Проблема с товаром!\n'
                                                                                        'Проверьте информацию и '
                                                                                        'ответьте на проблему пользователя',
                                     reply_markup=buttons.give_review_btns())
                bot.forward_message(chat_id=group_id, from_chat_id=message.chat.id, message_id=message.id,
                                    message_thread_id=topic_id)
                db_actions.update_question_status(user_id, True)
                temp_user_data.temp_data(message.chat.id)[message.chat.id][0] = None
                db_actions.add_action(user_id, 0)
                bot.send_message(message.chat.id, 'Заявка принята! Ожидайте...')
            elif db_actions.get_question_status_user_id(user_id):
                client_id = db_actions.user_id_from_question_id(user_id)
                bot.forward_message(chat_id=group_id, from_chat_id=message.chat.id, message_id=message.id,
                                    message_thread_id=client_id)
                db_actions.add_action(user_id, 2)
        elif user_id == group_id:
            topic_id = message.reply_to_message.id
            client_id = db_actions.get_question_id(topic_id)
            question_status = db_actions.get_question_status(topic_id)
            if client_id is not None and question_status:
                if user_input is not None:
                    bot.send_message(chat_id=client_id,
                                     text=user_input)
                elif photo is not None:
                    pass  # здесь можно добавить отправку фото от модера к клиенту
                db_actions.add_action(client_id, 3)
        else:
            bot.send_message(user_id, 'Введите /start для запуска бота')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        user_id = call.message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):
            if call.data == 'take_gift':
                if not db_actions.bonus_already_get(user_id):
                    db_actions.update_question_status(user_id, False)
                    bot.send_message(call.message.chat.id,
                                     'Для получения подарка:🎁\n1.Нажмите кнопку: "Поделиться контактом👤"',
                                     reply_markup=buttons.share_number_btn())

                    temp_user_data.temp_data(call.message.chat.id)[call.message.chat.id][0] = 0
                else:
                    bot.send_message(user_id, 'Вы уже получали бонус✅')
            elif call.data == 'write_manager':
                bot.send_message(call.message.chat.id, 'Выберите пожалуйста категорию обращения!',
                                 reply_markup=buttons.write_manager_btns())
            elif call.data in ['another_question', 'complectation_product', 'quality_product']:
                if call.message and call.message.chat:
                    bot.send_message(call.message.chat.id, 'Пожалуйста, подробно опишите проблему!\n'
                                                           'Так же по возможности приложите фотографии, демонстрирующие'
                                                           ' проблему.\n'
                                                           'Мы ответим в течении 24 часов!')
                    temp_user_data.temp_data(call.message.chat.id)[call.message.chat.id][0] = 2
        elif call.message.chat.id == group_id:
            if call.data == 'give_bonus':
                bot.send_message(chat_id=db_actions.get_user_id_from_topic(call.message.reply_to_message.id),
                                 text='Вы успешно получили бонус✅\n'
                                      f'Бонус отправлен вам на данный номер телефона: {db_actions.get_phone_numer_from_topic(call.message.reply_to_message.id)}')
            elif call.data == 'not_give_bonus':
                bot.send_message(chat_id=db_actions.get_user_id_from_topic(call.message.reply_to_message.id),
                                 text='К сожалению, мы не можем выдать вам бонус❌')
            elif call.data == 'problem_sloved':
                topic_id = call.message.reply_to_message.id
                client_id = db_actions.get_question_id(topic_id)
                if not db_actions.bonus_already_get(client_id):
                    db_actions.update_question_status(client_id, False)
                    bot.send_message(chat_id=client_id,
                                     text='Ваша проблема была решена!\n'
                                          'Можете отправить ваш отзыв нам✅', reply_markup=buttons.share_number_btn())
                    temp_user_data.temp_data(client_id)[client_id][0] = 0
                else:
                    bot.send_message(chat_id=group_id, message_thread_id=topic_id, text='Вы уже запрашивали бонус✅')
        else:
            bot.send_message(user_id, 'Введите /start для запуска бота')

    # контакт пользователя
    @bot.message_handler(content_types=['contact'])
    def text(message):
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            if message.contact is not None:
                print(message.contact)
        else:
            bot.send_message(user_id, 'Введите /start для запуска бота')

    bot.polling(none_stop=True)


if '__main__' == __name__:
    #if not os.path.exists(image_folder):
        #os.mkdir(image_folder)
    temp_user_data = TempUserData()
    db = DB(db_name, Lock())
    db_actions = DbAct(db)
    main()

# получить id топика с ВОПРОСОМ для конкретного пользователя db_actions.get_quest_id(user_id)
# получить id топика с ПОДАРКОМ для конкретного пользователя db_actions.get_review_id(user_id)
