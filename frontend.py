#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import telebot
from telebot import types


#####################################

class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def start_btns(self):
        gift = types.InlineKeyboardButton('Получить подарок🎁', callback_data='take_gift')
        write = types.InlineKeyboardButton('Написать продавцу✍️', callback_data='write_manager')
        self.__markup.add(gift, write)
        return self.__markup

    def write_manager_btns(self):
        qual = types.InlineKeyboardButton('Качество товара', callback_data='quality_product')
        comp = types.InlineKeyboardButton('Комплектация товара', callback_data='complectation_product')
        another = types.InlineKeyboardButton('Другой вопрос', callback_data='another_question')
        self.__markup.add(qual, comp, another)
        return self.__markup

    def share_number_btn(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = types.KeyboardButton(text="Поделиться контактом👤", request_contact=True)

        keyboard.add(button)
        return keyboard

    def review_manager_btns(self):
        all_good = types.InlineKeyboardButton('Выдать бонус✅', callback_data='give_bonus')
        not_good = types.InlineKeyboardButton('Отклонить выдачу бонуса❌', callback_data='not_give_bonus')
        self.__markup.add(all_good, not_good)
        return self.__markup

    def give_review_btns(self):
        problem_sloved = types.InlineKeyboardButton('Проблема решена, запросить отзыв✅', callback_data='problem_sloved')
        self.__markup.add(problem_sloved)
        return self.__markup