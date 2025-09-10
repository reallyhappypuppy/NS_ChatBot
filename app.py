from flask import Flask, render_template, request, session
import os
from dotenv import load_dotenv
from openai import OpenAI
import random

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# OpenAI API 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def chat():
    if "conversation_history" not in session:
        session["conversation_history"] = []

    bot_response = ""

    if request.method == "POST":

        # 버튼 클릭으로 들어온 경우 (keyword)
        keyword = request.form.get("keyword")
        if keyword:
            response_map = {
                "밥": "🍚 밥은 꼭 챙겨 드세요! 배가 불러야 집중도 잘 됩니다.",
                "공부": "📖 하기 싫은 날도 있지만, 조금만 더 힘내봐요! 미래의 나를 위해!",
                "피곤": "😌 지금은 쉬어야 할 때일 수도 있어요. 잠깐 눈을 감고 깊게 숨 쉬어보세요.",
                "칭찬": "🎉 대단해요! 여기까지 온 것만으로도 충분히 잘하고 있어요!",
                "격려": "💪 힘내세요! 당신은 생각보다 훨씬 더 강한 사람이에요!",
                "낙생고": "🏫 낙생고등학교는 대한민국 경기도 성남시 분당구 판교동에 있는 사립 고등학교입니다! 아마 여러분들의 현재 위치와 같을거에요!^^",
                "운세": "👍 미래는 스스로 개척하는것! 오늘의 운세 따위는 중요하지 않습니다!",
                "명언": [
                    "🌟 '실수해도 인정하고 다음에 만회하면 되는것, 그것이 진정한 어른이다.'",
                    "💡 '미래를 위해서 우리는 앞으로 나아가야만 한다.'",
                    "🔥 '어떤 것의 이름은 그 존재를 나타내는 지표이다. 그 지표 너머에 무엇이 있는지는 그 존재가 정하는 것이다.'",
                    "💫 '선택하지 않은 길은 존재하지 않았던 길과 같다.'",
                    "🔑 '싸우지 않으면 지킬 수 없는 것들이 있다.'",
                    "🌳 '세상이 어떻게 되든 간에, 우리는 살아가는 수밖에 없다.'",
                    "🧩 '사람은 죽으면 끝이다. 하지만 살아있는 한 뭔가를 할 수 있다.'",
                    "🛎️ '무언가를 잃는 건 괴로운 일이다. 하지만 그 슬픔을 안고 나아가는 것이 인간이다.'",
                    "☀️ '인류만이 신을 가지고 있다. 현재를 초월하는 힘, ‘가능성’이라 불리는 내면의 신.'",
                    "🕰️ '아무리 과거를 되돌아봐도, 우리는 절대 돌아갈 수 없다. 이미 일어난 일은 지나갔기 때문이다.'",
                    "🔭 '천재는 만능이 아니다. 그저 경쟁이 낳은 슬픈 별종일 뿐일지도 모른다.'",
                    "⛔️ '멈추지 마라. 멈추지 않으면 언젠가 다다를 것이다.'",
                ],
                "메뉴": [
                    "🍜 오늘은 따뜻한 라멘 어때요?",
                    "🍕 피자 한 조각에 행복을!",
                    "🥗 상큼한 샐러드로 몸도 마음도 리프레시!",
                    "🍱 든든한 도시락 한 판 추천!",
                    "🍖 고기 먹고 힘내새요!",
                    "🍣 신선한 초밥은 어떤가요?",
                    "🌶️ 오늘은 매운게 끌리는데요?",
                    "🍛 맛있는 카레 한 그릇!",
                ],
            }
            raw_response = response_map.get(keyword, "🙂 준비된 응답이 없어요!")
            if isinstance(raw_response, list):
                bot_response = random.choice(raw_response)
            else:
                bot_response = raw_response

            session["conversation_history"].append({"role": "assistant", "content": bot_response})
            return render_template("chat.html", conversation=session["conversation_history"], bot_response=bot_response)

        # 일반 입력 (message)
        user_input = request.form.get("message")
        if user_input:  # message가 있을 때만 실행
            conversation_history = session["conversation_history"]
            conversation_history.append({"role": "user", "content": user_input})

            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=conversation_history,
                    max_tokens=300,
                    temperature=0.7,
                )
                bot_reply = response.choices[0].message.content.strip()
                conversation_history.append({"role": "assistant", "content": bot_reply})
                bot_response = bot_reply
            except Exception as e:
                print("❌ 오류:", str(e))
                bot_response = f"⚠️ 오류 발생: {str(e)}"

            session["conversation_history"] = conversation_history

    return render_template("chat.html", conversation=session["conversation_history"], bot_response=bot_response)

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("conversation_history", None)
    return "", 204

if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi
    port = int(os.environ.get("PORT", 10000))  
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', port)), app)
