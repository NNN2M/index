"""
Telegram Bot with Gemini 2.5 Flash Integration
Professional bot built with aiogram 3.x
"""

import asyncio
import logging
import os
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Validate environment variables
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Create Gemini model instance
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Store chat sessions per user
chat_sessions = {}

# Initialize bot and dispatcher
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()


def get_chat_session(user_id: int):
    """Get or create a chat session for a user"""
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])
    return chat_sessions[user_id]


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    """Handle /start command"""
    user_name = message.from_user.first_name
    welcome_text = f"""
مرحباً *{user_name}*! 👋

أنا بوت ذكاء اصطناعي مدعوم بـ Gemini 2.5 Flash ⚡

*الميزات:*
• محادثة طبيعية وذكية
• ذاكرة المحادثة محفوظة
• إجابات سريعة ودقيقة
• دعم اللغة العربية والإنجليزية

*الأوامر المتاحة:*
/start - بدء المحادثة
/new - بدء محادثة جديدة
/help - المساعدة

أرسل لي أي سؤال أو رسالة وسأساعدك! 💬
"""
    await message.answer(welcome_text)


@dp.message(Command("new"))
async def command_new_handler(message: Message):
    """Handle /new command - start a new conversation"""
    user_id = message.from_user.id
    if user_id in chat_sessions:
        del chat_sessions[user_id]

    await message.answer(
        "✅ تم بدء محادثة جديدة!\n"
        "تم مسح سجل المحادثة السابق."
    )


@dp.message(Command("help"))
async def command_help_handler(message: Message):
    """Handle /help command"""
    help_text = """
*كيفية استخدام البوت:* 📖

1️⃣ أرسل أي سؤال أو رسالة نصية
2️⃣ انتظر الرد من الذكاء الاصطناعي
3️⃣ استمر في المحادثة - البوت يتذكر السياق

*أمثلة على الأسئلة:*
• اشرح لي مفهوم البرمجة الكائنية
• ما هي عاصمة فرنسا؟
• اكتب لي قصيدة عن البحر
• ساعدني في حل مسألة رياضية

*الأوامر:*
/start - بدء البوت
/new - محادثة جديدة
/help - هذه الرسالة

💡 *ملاحظة:* البوت يحتفظ بسياق المحادثة حتى تستخدم /new
"""
    await message.answer(help_text)


@dp.message(F.text)
async def handle_message(message: Message):
    """Handle text messages"""
    user_id = message.from_user.id
    user_text = message.text

    # Show typing action
    await bot.send_chat_action(message.chat.id, "typing")

    try:
        # Get user's chat session
        chat = get_chat_session(user_id)

        # Send message to Gemini
        response = chat.send_message(user_text)

        # Get response text
        response_text = response.text

        # Split long messages (Telegram has 4096 char limit)
        if len(response_text) > 4000:
            # Split into chunks
            chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for chunk in chunks:
                await message.answer(chunk)
        else:
            await message.answer(response_text)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await message.answer(
            "❌ عذراً، حدث خطأ أثناء معالجة رسالتك.\n"
            "يرجى المحاولة مرة أخرى."
        )


@dp.message()
async def handle_other_types(message: Message):
    """Handle non-text messages"""
    await message.answer(
        "⚠️ عذراً، حالياً أدعم الرسائل النصية فقط.\n"
        "يرجى إرسال رسالة نصية."
    )


async def main():
    """Start the bot"""
    logger.info("Starting bot...")

    # Delete webhook if exists
    await bot.delete_webhook(drop_pending_updates=True)

    # Start polling
    logger.info("Bot is running!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
