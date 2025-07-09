from flask import Flask, render_template, request, session
import openai
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.urandom(24) 
load_dotenv()

# OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def chat():
    if "conversation_history" not in session:
        session["conversation_history"] = []
    bot_response = ""

    if request.method == "POST":
        user_input = request.form["message"]
        conversation_history = session["conversation_history"]
        conversation_history.append({"role": "user", "content": user_input})

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=conversation_history,
                max_tokens=300,
                temperature=0.7,
            )
            bot_reply = response.choices[0].message.content.strip()
            conversation_history.append({"role": "assistant", "content": bot_reply})
            bot_response = bot_reply
        except Exception as e:
            bot_response = f"⚠️ 오류 발생: {str(e)}"

        session["conversation_history"] = conversation_history 

    return render_template("chat.html", conversation=session.get("conversation_history", []), bot_response=bot_response)

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("conversation_history", None)
    return "", 204

if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi
    port = int(os.environ.get("PORT", 5000))
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', port)), app)