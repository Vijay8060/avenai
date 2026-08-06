from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from groq import Groq
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database setup
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aven_chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Get API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Groq Client
client = Groq(api_key=GROQ_API_KEY)

system_instruction = """
You are Aven AI.

You were created by Vijay Saradhi.

You are a helpful, friendly and intelligent AI assistant.

You help with:
- Coding
- Learning
- Productivity
- General knowledge
If someone asks who is mother of vijay, always reply:

"Mother of Vijay is Swetha."
If someone asks who is father of vijay, always reply:

"Mother of Vijay is Kiran Prasad."
If someone asks who is brother of vijay, always reply:

"Mother of Vijay is Rajesh."

If someone asks who created you, always reply:

"I was created by Vijay Saradhi. I am Aven AI."
"""

# ---------------- Database ---------------- #

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String(500))
    ai_message = db.Column(db.Text)

with app.app_context():
    db.create_all()

# ---------------- Routes ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_text = data.get("message", "").strip()

    if not user_text:
        return jsonify({"reply": "Please enter a message."})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            temperature=0.7,
            max_tokens=1024
        )

        reply = response.choices[0].message.content

    except Exception as e:
        reply = f"⚠️ Error: {str(e)}"

    # Save chat
    chat_data = Chat(
        user_message=user_text,
        ai_message=reply
    )

    db.session.add(chat_data)
    db.session.commit()

    return jsonify({
        "reply": reply
    })


@app.route("/history")
def history():
    chats = Chat.query.order_by(Chat.id).all()

    history = []

    for chat in chats:
        history.append({
            "user": chat.user_message,
            "bot": chat.ai_message
        })

    return jsonify(history)


@app.route("/new_chat")
def new_chat():
    Chat.query.delete()
    db.session.commit()

    return jsonify({
        "status": "deleted"
    })


if __name__ == "__main__":
    app.run(debug=True)