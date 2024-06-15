from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

select_language = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Ukrainian',
            callback_data='ukrainian_language'
        )
    ],
    [
        InlineKeyboardButton(
            text='English',
            callback_data='english_language'
        )
    ],
    [
        InlineKeyboardButton(
            text='Our site',
            url='https://optimahotels.com.ua/uk/hotels/gallery-poltava/'
        )
    ]
])

ukrainian_select_message_type = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Скарга',
            callback_data='скарга',
        )
    ],
    [
        InlineKeyboardButton(
            text='Пропозиція для покращення комплексу',
            callback_data='пропозиція'
        )
    ],
    [
        InlineKeyboardButton(
            text='Подяка та оцінка',
            callback_data='подяка'
        )
    ],
    [
        InlineKeyboardButton(
            text="Змінити ім'я або мову",
            callback_data='cancel'
        )
    ]
])

english_select_message_type = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Complaint',
            callback_data='complaint'
        )
    ],
    [
        InlineKeyboardButton(
            text='Proposal for improving complex',
            callback_data='proposal'
        )
    ],
    [
        InlineKeyboardButton(
            text='Gratitude',
            callback_data='gratitude'
        )
    ],
    [
        InlineKeyboardButton(
            text='Change name or language',
            callback_data='cancel'
        )
    ]
])

first_row_rate_buttons = [
    InlineKeyboardButton(text='1', callback_data='one_star'),
    InlineKeyboardButton(text='2', callback_data='two_stars'),
    InlineKeyboardButton(text='3', callback_data='three_stars'),
    InlineKeyboardButton(text='4', callback_data='four_stars'),
    InlineKeyboardButton(text='5', callback_data='five_stars'),
]

second_row_rate_buttons = [
    InlineKeyboardButton(text='6', callback_data='six_stars'),
    InlineKeyboardButton(text='7', callback_data='seven_stars'),
    InlineKeyboardButton(text='8', callback_data='eight_stars'),
    InlineKeyboardButton(text='9', callback_data='nine_stars'),
    InlineKeyboardButton(text='10', callback_data='ten_stars'),
]

rating_buttons = InlineKeyboardMarkup(inline_keyboard=[first_row_rate_buttons, second_row_rate_buttons])
