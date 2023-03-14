import logging
import os
import uuid

from dotenv import load_dotenv
from pydantic import BaseModel

from aiogram.types import ParseMode
from loguru import logger as LOGGER

from aiogram import Bot, Dispatcher, executor, types

from clients.gpt_node import GptApiClient

load_dotenv()
gpt_node_url = os.environ.get('CHATGPT_TB_GPT_NODE_URL', 'http://127.0.0.1:8000')
gpt = GptApiClient(gpt_node_url)
bot = Bot(token=os.environ.get('API_TOKEN'))
dp = Dispatcher(bot)

class Chat(BaseModel):
    chat_id: int
    conversation_id: uuid.UUID

class Conversation(BaseModel):
    query: str
    answer: str
    parent_id: uuid.UUID
    account_id: uuid.UUID

chats: list[Chat] = []
conversations: dict[uuid.UUID, list[Conversation]] = {}

def setup_logging():
    logging.basicConfig(level=logging.INFO)

setup_logging()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    conversation_id = uuid.uuid4()
    chat = Chat(chat_id=message.chat.id, conversation_id=conversation_id)
    chats.append(chat)
    conversations[conversation_id] = []
    await message.reply("Hi!\nI'm ChatGPT bot!\nAsk me something through /ask")

@dp.message_handler(commands=['ask'])
async def ask_gpt(message: types.Message):
    conversation_id, account_id = None, None
    for chat in chats:
        if chat.chat_id == message.chat.id:
            conversation_id = chat.conversation_id

    conversation: list[Conversation] = conversations.get(conversation_id, [])
    if len(conversation) > 0:
        msg = conversation[-1]
        parent_id = msg.parent_id
        account_id = msg.account_id
    else:
        parent_id = uuid.uuid4()
        account_id = None

    query = message.text.replace('/ask ', '')
    response = await gpt.ask(query, conversation_id, parent_id, account_id)

    if response and response.message:
        msg = Conversation(
            query=query,
            answer=response.message,
            parent_id=response.parent_id,
            account_id=response.account_id
        )

        conversations[conversation_id].append(msg)

        LOGGER.info("Response was received")
        await message.reply(response.message, parse_mode=ParseMode.MARKDOWN)
    else:
        LOGGER.error(f"Exception during parsing response. res: {response}")
        await message.reply("Some exception happened during parsing response. Please re-ask your question.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
