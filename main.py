#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import telebot
from telebot import types

from frontend import Bot_inline_btns

#####################################
tg_api = '6667593230:AAH2ZgrEVgdE4DEt49ksZ-qD1ThJkEXIPag'
bot = telebot.TeleBot(tg_api)


#####################################

def main():
    @bot.message_handler(commands=['start'])
    def start_msg(message):
        buttons = Bot_inline_btns()
        bot.send_message(message.chat.id, 'Привет!👋\n'
                                          'Благодарим за покупку🖤\n'
                                          'Мы подготовили для вас приятный бонус, '
                                          'чтобы получить его, напишите отзыв😊\n'
                                          'Если у вас возникли какие-то проблемы с заказом '
                                          'свяжитесь с нашим менеджером👨‍💻\n'
                                          'Мы поможем в решении любого вопроса!', reply_markup=buttons.start_btns())

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        buttons = Bot_inline_btns()
        if call.data == 'take_gift':
            bot.send_message(call.message.chat.id, 'Для получения подарка:\n1.Отправьте фото отзыва!\n2.Нажмите кнопку "Поделиться контактом"', reply_markup=buttons.share_number_btn())
             # должен создаваться чат, куда будут передаваться данные (имя, номер, nickname) пользователя и фото отзыва. https://core.telegram.org/bots/api#contact
        elif call.data == 'write_manager':
            bot.send_message(call.message.chat.id, 'Выберите пожалуйста категорию обращения!',
                             reply_markup=buttons.write_manager_btns())

        elif call.data == 'quality_product' or call.data == 'complectation_product' or call.data == 'another_question':
            bot.send_message(call.message.chat.id, 'Пожалуйста, подробно опишите проблему!\n'
                                                   'Так же по возможности приложите фотографии, демонстрирующие проблему.\n'
                                                   'Мы ответим в течении 24 часов!')
            # тут создается чат с менеджера с человеком (общение через бота).

    bot.polling(none_stop=True)


if '__main__' == __name__:
    main()
