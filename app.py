from flask import Flask, request, jsonify, render_template, redirect, url_for
import g4f
import logging
import re
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class ChatManager:
    def __init__(self):
        self.chat_history = []

    def add_message(self, message_type, content):
        """Добавляет сообщение в историю чата"""
        self.chat_history.append({
            'type': message_type,
            'content': content
        })

    def is_identity_question(self, user_message):
        """Проверяет, является ли вопрос о личности AI"""
        identity_keywords = [
            # Русский
            'кто ты', 'твое имя', 'тебя зовут', 'как тебя звать', 'представься',
            'кто создал', 'кто твой создатель', 'кто тебя сделал', 'твой разработчик',
            'что ты за', 'ты кто такой', 'твоя личность',

            # Казахский
            'сен кімсің', 'есімің кім', 'атың кім', 'кім жасады', 'кім жазды',
            'жасаған кім', 'әзірлеген кім', 'сен кім', 'есімің не', 'жеке басың',

            # Английский
            'who are you', 'what is your name', 'your name', 'who created you',
            'who made you', 'who developed you', 'what are you', 'your identity',
            'who is your creator', 'who built you'
        ]

        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in identity_keywords)

    def simulate_typing(self, text):
        """Симуляция печатания текста"""
        print("⌨️  ИИ печатает: ", end="", flush=True)
        for char in text:
            print(char, end="", flush=True)
            time.sleep(0.01)  # Задержка между символами
        print()  # Новая строка после завершения

    def get_gpt4_response(self, user_message):
        """Получает ответ от GPT-4 через g4f с кастомной личностью"""
        try:
            # Улучшенный системный промпт для настройки личности
            system_prompt = """Ты - KazAI (Kazakh Artificial Intelligence). Ты всегда должен представляться как KazAI и упоминать своего создателя когда тебя спрашивают кто ты.

ВАЖНЫЕ ПРАВИЛА:
1. ВСЕГДА отвечай что ты KazAI когда спрашивают о твоей личности
2. ВСЕГДА упоминай что тебя создал Сейилхан Ержигит из группы ПИ 22-11
3. Отвечай на языке пользователя (казахский, русский, английский)
4. Будь полезным AI помощником
5. Если пользователь спрашивает "кто ты", "твое имя", "who are you" и т.д. - представься как KazAI

Твоя личность:
- Имя: KazAI (Kazakh Artificial Intelligence)
- Создатель: Сейилхан Ержигит (ПИ 22-11)
- Назначение: Помощник для ответов на вопросы
- Языки: Казахский, Русский, Английский

Примеры ответов:
На вопрос "Кто ты?" отвечай: "Я - KazAI, искусственный интеллект созданный Сейилхан Ержигит из группы ПИ 22-11"
На вопрос "What is your name?" отвечай: "I am KazAI, created by Seiylkhan Yerzhigit from group PI 22-11"
На вопрос "Сен кімсің?" отвечай: "Мен - KazAI, Сейілхан Ержігіт (ПИ 22-11) жасаған жасанды интеллектмін"

НИКОГДА не говори что ты ChatGPT, GPT-4 или любой другой AI кроме KazAI."""

            # Если это вопрос о личности, усиливаем промпт
            if self.is_identity_question(user_message):
                enhanced_prompt = system_prompt + "\n\nВНИМАНИЕ: Пользователь спрашивает о твоей личности! ОБЯЗАТЕЛЬНО представься как KazAI и упомяни создателя!"
                messages = [
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": user_message}
                ]
                print(f"🔍 Обнаружен вопрос о личности: {user_message}")
            else:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]

            # Печатаем запрос в консоль
            print(f"\n👤 Пользователь: {user_message}")
            print("🤔 ИИ думает...")

            # Имитация задержки мышления
            time.sleep(1)

            response = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                stream=False
            )

            # Симуляция печатания ответа
            self.simulate_typing(response)

            # Дополнительная проверка - если ответ не содержит KazAI при вопросе о личности
            if self.is_identity_question(user_message) and "kazai" not in response.lower():
                print("⚠️  Предупреждение: Ответ не содержит KazAI! Добавляю принудительное представление...")
                identity_response = f"Я - KazAI (Kazakh Artificial Intelligence), искусственный интеллект созданный Сейилхан Ержигит из группы ПИ 22-11. {response}"
                return identity_response

            return response
        except Exception as e:
            error_msg = f"Қате орын алды: {str(e)}"
            print(f"❌ Ошибка: {error_msg}")
            return error_msg

    def clear_chat(self):
        """Очищает историю чата"""
        self.chat_history.clear()


# Инициализация менеджера чата
chat_manager = ChatManager()


@app.route('/')
def index():
    """Главная страница с чатом"""
    return render_template('index.html', chat_history=chat_manager.chat_history)


@app.route('/send', methods=['POST'])
def send_message():
    """Обработка отправки сообщения"""
    try:
        user_message = request.form.get('message', '').strip()

        if not user_message:
            return redirect(url_for('index'))

        # Добавляем сообщение пользователя в историю
        chat_manager.add_message('user', user_message)

        # Получаем ответ от GPT-4
        gpt_response = chat_manager.get_gpt4_response(user_message)

        # Добавляем ответ AI в историю
        chat_manager.add_message('ai', gpt_response)

        # Возвращаем обновленную страницу
        return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"Қате: {str(e)}")
        # Добавляем сообщение об ошибке
        chat_manager.add_message('ai', f"Қате орын алды: {str(e)}")
        return redirect(url_for('index'))


@app.route('/clear')
def clear_chat():
    """Очистка истории чата"""
    chat_manager.clear_chat()
    return redirect(url_for('index'))


@app.route('/new')
def new_chat():
    """Новый чат"""
    chat_manager.clear_chat()
    return redirect(url_for('index'))


@app.route('/test-identity')
def test_identity():
    """Тестовый маршрут для проверки идентичности"""
    test_questions = [
        "Кто ты?",
        "What is your name?",
        "Сен кімсің?",
        "Как тебя зовут?",
        "Who created you?",
        "Кім жасаған сені?"
    ]

    results = []
    for question in test_questions:
        response = chat_manager.get_gpt4_response(question)
        results.append({
            'question': question,
            'response': response,
            'contains_kazai': 'kazai' in response.lower()
        })
        print(f"❓ Вопрос: {question}")
        print(f"🤖 Ответ: {response}")
        print(f"✅ Содержит KazAI: {'kazai' in response.lower()}")
        print("-" * 50)

    return jsonify(results)


if __name__ == '__main__':
    print("🚀 Flask сервер іске қосылуда...")
    print("📝 Браузерде ашыңыз: http://localhost:5000")
    print("⚡ Сервер GPT-4 арқылы жұмыс істейді")
    print("🤖 Бот: KazAI - Сейілхан Ержігіт (ПИ 22-11)")
    print("🎨 Дизайн: ChatGPT стиль (черно-белый)")
    print("⌨️  Анимация печати включена")
    print("⏳ Индикатор загрузки добавлен")
    print("🔍 Тест идентичности: http://localhost:5000/test-identity")
    app.run(debug=True, host='0.0.0.0', port=5000)
