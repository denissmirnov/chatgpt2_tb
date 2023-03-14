import logging
import os
import uuid

from dotenv import load_dotenv

from aiogram.types import ParseMode
from loguru import logger as LOGGER

from aiogram import Bot, Dispatcher, executor, types

from clients.gpt_node import GptApiClient

load_dotenv()
gpt_node_url = os.environ.get('CHATGPT_TB_GPT_NODE_URL', 'http://127.0.0.1:8000')
gpt = GptApiClient(gpt_node_url)
bot = Bot(token=os.environ.get('API_TOKEN'))
dp = Dispatcher(bot)
chats: list = []
conversations: dict = {}

def setup_logging():
    logging.basicConfig(level=logging.INFO)


setup_logging()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    conversation_id = uuid.uuid4()
    chats.append({f"{message.chat.id}": str(conversation_id)})
    conversations[str(conversation_id)] = []
    await message.reply("Hi!\nI'm ChatGPT bot!\nAsk me something through /ask")


@dp.message_handler(commands=['ask'])
async def ask_gpt(message: types.Message):
    conversation_id, account_id = None, None
    for chat in chats:
        if str(message.chat.id) in chat:
            conversation_id = str(chat[str(message.chat.id)])

    conversation: list = conversations[str(conversation_id)]
    if len(conversation) > 0:
        msg = conversation[-1]
        parent_id = msg.get('parent_id', uuid.uuid4())
        account_id = msg.get('account_id')
    else:
        parent_id = uuid.uuid4()
        account_id = None

    query = message.text.replace('/ask ', '')
    response = await gpt.ask(query, conversation_id, parent_id, account_id)
    print(response)

    if response and response.message:
        msg = {
            'query': query,
            'answer': response.message,
            'parent_id': f"{response.parent_id}",
            'account_id': response.account_id,
        }

        conversations[str(conversation_id)].append(msg)

        LOGGER.info("Response was received")
        print(conversations)
        await message.reply(response.message, parse_mode=ParseMode.MARKDOWN)
    else:
        LOGGER.error(f"Exception during parsing response. res: {response}")
        await message.reply("Some exception happened during parsing response. Please re-ask your question.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
