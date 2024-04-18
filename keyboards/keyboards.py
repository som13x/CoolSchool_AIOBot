from lexicon.lexicon import LEXICON_RU
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

apply_button = InlineKeyboardButton(
    text=LEXICON_RU['apply_button'],
    callback_data='apply_button_pressed'
)

faq_button = InlineKeyboardButton(
    text=LEXICON_RU['faq_button'],
    callback_data='faq_button_pressed'
)

cancel_button = InlineKeyboardButton(
    text=LEXICON_RU['cancel_button'],
    callback_data= 'cancel_pressed'
)

level_button1 = InlineKeyboardButton(
    text=LEXICON_RU['level_button1'],
    callback_data='beginner'
)

level_button2 = InlineKeyboardButton(
    text=LEXICON_RU['level_button2'],
    callback_data='intermediate'
)

level_button3 = InlineKeyboardButton(
    text=LEXICON_RU['level_button3'],
    callback_data='advanced'
)

level_button4 = InlineKeyboardButton(
    text=LEXICON_RU['level_button4'],
    callback_data='dont know'
)

level_button5 = InlineKeyboardButton(
    text=LEXICON_RU['level_button5'],
    callback_data='own answer'
)

target_button1 = InlineKeyboardButton(
    text=LEXICON_RU['target_button1'],
    callback_data='for work'
)

target_button2 = InlineKeyboardButton(
    text=LEXICON_RU['target_button2'],
    callback_data='for exam prep'
)

target_button3 = InlineKeyboardButton(
    text=LEXICON_RU['target_button3'],
    callback_data='for school'
)

target_button4 = InlineKeyboardButton(
    text=LEXICON_RU['target_button4'],
    callback_data='for self development'
)

time_button1 = InlineKeyboardButton(
    text=LEXICON_RU['time_button1'],
    callback_data='in the morning'
)

time_button2 = InlineKeyboardButton(
    text=LEXICON_RU['time_button2'],
    callback_data='in the afternoon'
)

time_button3 = InlineKeyboardButton(
    text=LEXICON_RU['time_button3'],
    callback_data='in the evening'
)

check_my_request = InlineKeyboardButton(
    text=LEXICON_RU['check_button'],
    callback_data='check request'
)

main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[apply_button],
                     [check_my_request],
                     [faq_button]])

cancel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[cancel_button]]
)

level_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[level_button1],
                     [level_button2],
                     [level_button3],
                     [level_button4],
                     [level_button5],
                     [cancel_button]])

target_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[target_button1],
                     [target_button2],
                     [target_button3],
                     [target_button4],
                     [cancel_button]])

time_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[time_button1],
                     [time_button2],
                     [time_button3],
                     [cancel_button]])