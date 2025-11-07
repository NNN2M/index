"""
نظام رد تلقائي باستخدام Gemini 2.5 Pro
Automatic Reply System using Gemini 2.5 Pro
"""

import os
import json
import time
from typing import List, Dict, Optional
import google.generativeai as genai


class GeminiAutoReplySystem:
    """نظام رد تلقائي ذكي باستخدام Gemini 2.5 Pro"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        تهيئة النظام

        Args:
            api_key: مفتاح API من Google AI Studio
            model_name: اسم النموذج (افتراضي: gemini-2.0-flash-exp)
        """
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        self.conversation_history: List[Dict] = []

    def set_system_prompt(self, system_prompt: str):
        """
        تعيين التعليمات الأساسية للنظام

        Args:
            system_prompt: التعليمات التي تحدد سلوك النظام
        """
        self.system_prompt = system_prompt

    def generate_reply(self, message: str, context: Optional[str] = None) -> str:
        """
        توليد رد تلقائي على الرسالة

        Args:
            message: الرسالة المستلمة
            context: سياق إضافي (اختياري)

        Returns:
            الرد المولد من Gemini
        """
        try:
            # بناء الرسالة مع السياق
            full_prompt = ""

            if hasattr(self, 'system_prompt'):
                full_prompt += f"تعليمات النظام: {self.system_prompt}\n\n"

            if context:
                full_prompt += f"السياق: {context}\n\n"

            full_prompt += f"الرسالة: {message}\n\nالرد:"

            # إرسال الطلب إلى Gemini
            response = self.model.generate_content(full_prompt)

            # حفظ في السجل
            self.conversation_history.append({
                "timestamp": time.time(),
                "message": message,
                "reply": response.text,
                "context": context
            })

            return response.text

        except Exception as e:
            error_msg = f"خطأ في توليد الرد: {str(e)}"
            print(error_msg)
            return error_msg

    def generate_reply_with_chat(self, message: str) -> str:
        """
        توليد رد مع الاحتفاظ بسياق المحادثة

        Args:
            message: الرسالة المستلمة

        Returns:
            الرد المولد
        """
        try:
            if not hasattr(self, 'chat'):
                self.chat = self.model.start_chat(history=[])

            response = self.chat.send_message(message)

            # حفظ في السجل
            self.conversation_history.append({
                "timestamp": time.time(),
                "message": message,
                "reply": response.text
            })

            return response.text

        except Exception as e:
            error_msg = f"خطأ في توليد الرد: {str(e)}"
            print(error_msg)
            return error_msg

    def batch_reply(self, messages: List[str]) -> List[str]:
        """
        معالجة دفعة من الرسائل

        Args:
            messages: قائمة الرسائل

        Returns:
            قائمة الردود
        """
        replies = []
        for msg in messages:
            reply = self.generate_reply(msg)
            replies.append(reply)
            time.sleep(0.5)  # تأخير بسيط لتجنب تجاوز الحدود

        return replies

    def save_history(self, filename: str = "conversation_history.json"):
        """
        حفظ سجل المحادثات

        Args:
            filename: اسم الملف
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        print(f"تم حفظ السجل في: {filename}")

    def load_history(self, filename: str = "conversation_history.json"):
        """
        تحميل سجل المحادثات

        Args:
            filename: اسم الملف
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            print(f"تم تحميل السجل من: {filename}")
        except FileNotFoundError:
            print(f"الملف غير موجود: {filename}")

    def clear_history(self):
        """مسح سجل المحادثات"""
        self.conversation_history = []
        if hasattr(self, 'chat'):
            self.chat = self.model.start_chat(history=[])
        print("تم مسح سجل المحادثات")


def main():
    """مثال على استخدام النظام"""

    # قراءة مفتاح API من المتغيرات البيئية
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("تحذير: لم يتم العثور على GEMINI_API_KEY")
        print("يرجى تعيين مفتاح API:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        return

    # إنشاء النظام
    auto_reply = GeminiAutoReplySystem(api_key)

    # تعيين التعليمات الأساسية
    auto_reply.set_system_prompt(
        "أنت مساعد ذكي ومهذب. ترد على الرسائل بشكل احترافي وودود. "
        "تجيب بالعربية بشكل واضح ومختصر."
    )

    print("=" * 50)
    print("نظام الرد التلقائي باستخدام Gemini 2.5 Pro")
    print("=" * 50)
    print()

    # أمثلة على الاستخدام
    messages = [
        "مرحباً، كيف حالك؟",
        "ما هي خدماتكم؟",
        "شكراً لك"
    ]

    print("مثال 1: ردود بسيطة")
    print("-" * 50)
    for msg in messages:
        reply = auto_reply.generate_reply(msg)
        print(f"الرسالة: {msg}")
        print(f"الرد: {reply}")
        print()

    print("\nمثال 2: محادثة مع سياق")
    print("-" * 50)
    auto_reply.clear_history()

    conversation = [
        "ما هو اسمك؟",
        "ما هي اهتماماتك؟",
        "شكراً على المعلومات"
    ]

    for msg in conversation:
        reply = auto_reply.generate_reply_with_chat(msg)
        print(f"أنت: {msg}")
        print(f"النظام: {reply}")
        print()

    # حفظ السجل
    auto_reply.save_history()

    print("\nتم الانتهاء! تم حفظ سجل المحادثات.")


if __name__ == "__main__":
    main()
