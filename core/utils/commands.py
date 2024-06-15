from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Launch the bot'
        ),
        BotCommand(
            command='restart',
            description='Restart the bot'
        ),
        BotCommand(
            command='info',
            description='Info about the bot'
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
