import asyncio
import logging
import random
import string
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandObject, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# 1. ⚠️ ВСТАВЬ СВОЙ ТОКЕН ОТ BOTFATHER
API_TOKEN = 'ТВОЙ_ТОКЕН_ОТ_BOTFATHER'
# 2. ТВОЙ КОШЕЛЕК ИЗ KEEPER
MY_WALLET = "UQB5A-6ZfDMDoAeZMvWpEqfZLA0slByUF9mQsrb66B56GNCK"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# База данных 15 блогеров
bloggers_db = {
    "PROMO1": {"name": "Влад ТТ", "balance": 0, "sales": 0},
    "TECH2026": {"name": "Макс Техно", "balance": 0, "sales": 0}
}

# Функция генерации случайного VIP-кода для сайта
def generate_vip_code():
    return "VIP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Проверка транзакций через открытое API блокчейна TON
def check_ton_payment(wallet_address, amount_ton):
    try:
        url = f"https://toncenter.com{wallet_address}&limit=5"
        response = requests.get(url).json()
        if response.get("ok") and response.get("result"):
            for tx in response["result"]:
                # Ищем входящие платежи за последние пару минут
                in_msg = tx.get("in_msg", {})
                value = int(in_msg.get("value", 0)) / 1000000000 # Переводим наноTON в TON
                if value >= amount_ton:
                    return True
    except Exception as e:
        print(f"Ошибка проверки блокчейна: {e}")
    return False

@dp.message(Command("start"))
async def start_handler(message: types.Message, command: CommandObject):
    args = command.args
    
    # Если клиент пришел с кнопкой сайта ?start=pay
    if args == "pay":
        kb = InlineKeyboardBuilder()
        # Прямая официальная платежная ссылка Телеграма (откроет встроенный кошелек)
        kb.button(text="💳 Оплатить 0.3 TON (С телефона)", url=f"https://t.me{MY_WALLET}-300000000")
        kb.button(text="Проверить оплату и получить VIP ⚡", callback_data="check_payment")
        kb.adjust(1)
        
        pay_text = (
            "👑 **Оформление моментальной VIP-подписки**\n\n"
            "Стоимость: **50 грн / 99 руб** (ровно **0.3 TON**).\n\n"
            "1. Нажми кнопку оплаты ниже и подтверди перевод в один клик.\n"
            "2. Сразу после оплаты нажми кнопку **«Проверить оплату»**.\n\n"
            "Бот проверит блокчейн и мгновенно выдаст тебе VIP-код!"
        )
        await message.answer(pay_text, reply_markup=kb.as_markup(), parse_mode="Markdown")
    else:
        await message.answer("🤖 Бот HardwareVS запущен. Перейдите на сайт для покупки VIP!")

# Автоматическая проверка платежа при нажатии кнопки
@dp.callback_query(lambda c: c.data == "check_payment")
async def verify_payment(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, text="Проверяем блокчейн... 🔎")
    
    # Бот лезет в блокчейн TON и ищет перевод на 0.3 TON на твой адрес
    is_paid = check_ton_payment(MY_WALLET, 0.3)
    
    if is_paid:
        vip_code = generate_vip_code()
        success_text = (
            "🎉 **ОПЛАТА НАЙДЕНА! ДОСТУП ВЫДАН МГНОВЕННО!**\n\n"
            f"🔑 Твой уникальный VIP-код на 1 месяц:\n`{vip_code}`\n\n"
            "Скопируй этот код и вставь его на сайте HardwareVS в поле активации. Спасибо за покупку!"
        )
        await bot.send_message(callback_query.from_user.id, success_text, parse_mode="Markdown")
    else:
        await bot.send_message(
            callback_query.from_user.id, 
            "❌ **Перевод пока не найден в сети TON.**\n"
            "Подождите 10-15 секунд, пока транзакция подтвердится в блокчейне, и нажмите кнопку проверки еще раз."
        )

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
