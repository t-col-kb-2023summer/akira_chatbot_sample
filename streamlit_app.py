import streamlit as st
import openai

# Streamlit Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key
role_system = st.secrets.ChatSettings.role_system
message_max = st.secrets.ChatSettings.message_max


# 現在のやりとりに対するコスト表示
def display_tokens():
    len = str(st.session_state["messages_len"])
    total = str(st.session_state["total_tokens"])
    all = str(st.session_state["all_tokens"])
    st.write("messeage数 "+len+", 今回消費token "+total+", 累計消費token "+all+"です")


# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "messages_len" not in st.session_state:
    st.session_state["messages_len"] = 0
if "total_tokens" not in st.session_state:
    st.session_state["total_tokens"] = 0
if "all_tokens" not in st.session_state:
    st.session_state["all_tokens"] = 0


# UIの構築
st.title("My AI Assistant")
st.write("ChatGPT APIを使ったチャットボットです。")
display_tokens()


# チャットボットとやりとりする関数
def communicate():
    system_message_text = st.session_state["system_role_input"]
    system_message = {"role": "system", "content": system_message_text}
    user_message = {"role": "user", "content": st.session_state["user_input"]}
    initial_all_messages = st.session_state["messages"]
    rest_messages = initial_all_messages[1:] if len(initial_all_messages) > 1 else []
    all_messages = [system_message, *rest_messages, user_message]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=all_messages
    )

    assistant_message = response["choices"][0]["message"]
    all_messages.append(assistant_message)

    if len(all_messages) >= message_max:
        del all_messages[1:3] # 最も古いやり取り(質問+応答)を削除(先頭はrole:systemなので削除せず)

    st.session_state["messages"] = all_messages
    st.session_state["messages_len"] = len(all_messages)
    st.session_state["total_tokens"] = response["usage"]["total_tokens"]
    st.session_state["all_tokens"] += response["usage"]["total_tokens"]
    st.session_state["user_input"] = ""  # 入力欄を消去


system_role_input = st.text_area("チャットAIに適用させる設定を入力してください", key="system_role_input", on_change=communicate, value=(st.session_state["system_role_input"] if "system_role_input" in st.session_state else role_system))


user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    all_messages = st.session_state["messages"]

    for message in reversed(all_messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂"
        if message["role"]=="assistant":
            speaker="🤖"

        st.write(speaker + ": " + message["content"])
