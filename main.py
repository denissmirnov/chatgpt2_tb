import logging
import os

from aiogram.types import ParseMode
from loguru import logger as LOGGER

from aiogram import Bot, Dispatcher, executor, types

from clients.gpt_node import GptApiClient

API_TOKEN = '5920129044:AAH_6OB6VAFtZqNI6JJR99PttKkO0MMg8ZY'

gpt_node_url = os.environ.get('CHATGPT_TB_GPT_NODE_URL', 'http://127.0.0.1:8000')
gpt = GptApiClient(gpt_node_url)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def setup_logging():
    logging.basicConfig(level=logging.INFO)

setup_logging()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Hi!\nI'm ChatGPT bot!\nAsk me something through /ask")

@dp.message_handler(commands=['ask'])
async def ask_gpt(message: types.Message):
    chats = {
        f"{message.chat.id}": {}
    }

    conversations = chats[f"{message.chat.id}"]
    conversation_id, parent_id, account_id = None, None, None

    if conversations:
        for conversation in conversations:
            conversation_id = conversation
            msgs = conversations[conversation]
            if msgs:
                msg = msgs[-1]
                parent_id = f"{msg['parent_id']}"
                account_id = msg['account_id']

    try:
        response = await gpt.ask(message.text, conversation_id, parent_id, account_id)
    except Exception as e:
        LOGGER.error(f"Exception during request to gpt: {e}")
        await message.reply("Some exception happened during making request to GPT. Please re-ask your question.")
    else:
        if response and response.message:
            msg = {
                'query': message.text,
                'answer': response.message,
                'parent_id': f"{response.parent_id}",
                'account_id': response.account_id
            }

            if f"{response.conversation_id}" in conversations:
                conversations[f"{response.conversation_id}"].append(msg)
            else:
                conversations[f"{response.conversation_id}"] = [msg]
            LOGGER.info("Response was received")
            await message.reply(response.message, parse_mode=ParseMode.MARKDOWN)
        else:
            LOGGER.error(f"Exception during parsing response. res: {response}")
            await message.reply("Some exception happened during parsing response. Please re-ask your question.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
