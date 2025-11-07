# نظام الرد التلقائي باستخدام Gemini 2.5 Pro
# Gemini Auto-Reply System

نظام رد تلقائي ذكي باستخدام Google Gemini 2.5 Pro API

## المميزات

- ✨ ردود تلقائية ذكية باستخدام Gemini 2.5 Pro
- 💬 دعم المحادثات مع الاحتفاظ بالسياق
- 📝 حفظ وتحميل سجل المحادثات
- 🔧 قابل للتخصيص بسهولة
- 🌐 دعم اللغة العربية والإنجليزية

## المتطلبات

- Python 3.8 أو أحدث
- مفتاح API من Google AI Studio

## التثبيت

1. استنساخ المشروع:
```bash
git clone <repository-url>
cd index
```

2. تثبيت المكتبات المطلوبة:
```bash
pip install -r requirements.txt
```

3. إعداد مفتاح API:
```bash
# انسخ ملف المثال
cp .env.example .env

# عدل الملف وأضف مفتاحك
# GEMINI_API_KEY=your_api_key_here
```

## الحصول على مفتاح API

1. اذهب إلى [Google AI Studio](https://makersuite.google.com/app/apikey)
2. سجل دخول بحساب Google
3. انقر على "Create API Key"
4. انسخ المفتاح وضعه في ملف `.env`

## الاستخدام

### الاستخدام الأساسي

```python
from gemini_auto_reply import GeminiAutoReplySystem
import os

# إنشاء النظام
api_key = os.getenv("GEMINI_API_KEY")
auto_reply = GeminiAutoReplySystem(api_key)

# توليد رد
message = "مرحباً، كيف يمكنني مساعدتك؟"
reply = auto_reply.generate_reply(message)
print(reply)
```

### محادثة مع سياق

```python
# بدء محادثة
auto_reply.set_system_prompt("أنت مساعد خدمة عملاء محترف")

# إرسال رسائل متتابعة
reply1 = auto_reply.generate_reply_with_chat("ما هي خدماتكم؟")
reply2 = auto_reply.generate_reply_with_chat("كم التكلفة؟")
reply3 = auto_reply.generate_reply_with_chat("شكراً")

# حفظ السجل
auto_reply.save_history("chat_history.json")
```

### معالجة دفعة من الرسائل

```python
messages = [
    "مرحباً",
    "أحتاج مساعدة",
    "شكراً لك"
]

replies = auto_reply.batch_reply(messages)
for msg, reply in zip(messages, replies):
    print(f"الرسالة: {msg}")
    print(f"الرد: {reply}\n")
```

## تشغيل المثال

```bash
export GEMINI_API_KEY='your-api-key-here'
python gemini_auto_reply.py
```

## هيكل المشروع

```
index/
├── gemini_auto_reply.py      # الملف الرئيسي للنظام
├── config.example.json        # مثال على ملف الإعدادات
├── .env.example               # مثال على متغيرات البيئة
├── requirements.txt           # المكتبات المطلوبة
└── README.md                  # هذا الملف
```

## خيارات التخصيص

يمكنك تخصيص النظام من خلال:

1. **System Prompt**: تعيين التعليمات الأساسية للنظام
2. **Model Name**: اختيار نموذج Gemini مختلف
3. **Context**: إضافة سياق إضافي لكل رسالة

## الأمان

⚠️ **تحذير**: لا تشارك مفتاح API الخاص بك أو ترفعه على GitHub

- احتفظ بمفتاح API في ملف `.env`
- أضف `.env` إلى `.gitignore`
- استخدم متغيرات البيئة في الإنتاج

## الترخيص

MIT License

## الدعم

للمساعدة والدعم، يرجى فتح issue في المشروع.
