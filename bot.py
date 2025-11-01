"""
Telegram Bot with Gemini 2.5 Flash Integration
Professional bot built with aiogram 3.x and official google-genai SDK
"""

import asyncio
import logging
import os
from typing import Dict, List

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from google import genai
from google.genai import types

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

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash"

# Store chat history per user
chat_histories: Dict[int, List[types.Content]] = {}

# Initialize bot and dispatcher
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()


def get_chat_history(user_id: int) -> List[types.Content]:
    """Get or create chat history for a user"""
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    return chat_histories[user_id]


async def generate_gemini_response(user_id: int, user_message: str) -> str:
    """Generate response from Gemini API with conversation history"""
    history = get_chat_history(user_id)

    # Add user message to history
    history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)]
        )
    )

    # Generate response
    response_text = ""
    try:
        generate_config = types.GenerateContentConfig(
            temperature=1.0,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=history,
            config=generate_config,
        )

        response_text = response.text

        # Add assistant response to history
        history.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=response_text)]
            )
        )

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise

    return response_text


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
    if user_id in chat_histories:
        chat_histories[user_id] = []

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
        # Generate response from Gemini
        response_text = await generate_gemini_response(user_id, user_text)

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
