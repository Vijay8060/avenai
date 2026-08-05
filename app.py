from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from google import genai
from dotenv import load_dotenv
import os


load_dotenv()


app = Flask(__name__)


# Database setup

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///aven_chat.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)



client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)



system_instruction = """
You are Aven AI.

You were created by Vijay Saradhi.

You are a personal AI assistant for coding,
learning and productivity.

If asked who created you:
Say:
"I was created by Vijay Saradhi. I am Aven AI."
"""





# Chat Database Model

class Chat(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_message = db.Column(
        db.String(500)
    )


    ai_message = db.Column(
        db.Text
    )





with app.app_context():

    db.create_all()







@app.route("/")
def home():

    return render_template("index.html")








@app.route("/chat",methods=["POST"])
def chat():


    data=request.get_json()


    user_text=data["message"]




    response = client.models.generate_content(

        model="gemini-3.6-flash",

        contents=[
            {
                "role":"user",
                "parts":[
                    {
                        "text":system_instruction
                    }
                ]
            },
            {
                "role":"user",
                "parts":[
                    {
                        "text":user_text
                    }
                ]
            }
        ]

    )



    reply=response.text




    # Save to database

    new_chat = Chat(

        user_message=user_text,

        ai_message=reply

    )


    db.session.add(new_chat)

    db.session.commit()





    return jsonify({

        "reply":reply

    })









# Get Chat History

@app.route("/history")

def history():


    chats = Chat.query.all()



    data=[]


    for chat in chats:

        data.append({

            "user":chat.user_message,

            "bot":chat.ai_message

        })



    return jsonify(data)







@app.route("/new_chat")

def new_chat():


    Chat.query.delete()

    db.session.commit()


    return jsonify({

        "status":"deleted"

    })






if __name__=="__main__":

    app.run(debug=True)