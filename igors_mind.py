import igors_prefs
import random

from groq import Groq
import json
import telebot

try:
    with open("msg_count.txt", "r", encoding="utf-8") as f:
        
            igors_prefs.messages_count = int(f.read())
except Exception as e:
    print(e)

history = []

try:
    with open("history.json", "r", encoding="utf-8") as f:
        history = json.loads(f.read())
except Exception as e:
    print(e)

if history == []:
    history = [
        {
            "role": "system",
            "content": igors_prefs.instructions + igors_prefs.base_character
        }
    ]


    
client = Groq(api_key=igors_prefs.API_KEY)

def append_history_with_message(new_message: telebot.types.Message):
    history.append(
        {
            "role": "user",
            "content": new_message.from_user.first_name + ": " + str(new_message.text)
            }
        )
    while len(history) > igors_prefs.memory_limit:
        history.pop(1)
    
def prompt(new_message: telebot.types.Message):
    h = history.copy()
    h[0]["content"] += igors_prefs.modifier
    # print(json.dumps(h, indent=4, ensure_ascii=False))
    completion = client.chat.completions.create(
        model=igors_prefs.model_used,
        messages=h,
        temperature=1.1,
        max_tokens=3000,
        top_p=1,
        stream=True,
        stop=None,
    )
    reply = ""
    for chunk in completion:
        reply = reply + str(chunk.choices[0].delta.content or "")
    history.append(
        {
            "role": "assistant",
            "content": reply
            }
        )

    return reply


def prompt_no_history(prompt:str, token_c):
    completion = client.chat.completions.create(
        model=igors_prefs.model_used,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=1.1,
        max_tokens=token_c,
        top_p=1,
        stream=True,
        stop=None,
    )
    reply = ""
    for chunk in completion:
        reply = reply + str(chunk.choices[0].delta.content or "")
    return reply


def get_summary(history):
    completion = client.chat.completions.create(
        model=igors_prefs.model_used,
        messages=[
            {
                "role": "system",
                "content": "создай сжатое описание истории сообщений, где ты - это assistant, а пользователи с разными именами - это user. выведи результат как бы от второго лица, где ты обращаешься к игорю"
            },
            {
                "role": "user",
                "content": "выведи результат в форме обычного текста очень кратко на русском языке.Укороти максимально сильно " + str(history)
            }
        ],
        temperature=0.9,
        max_tokens=3000,
        top_p=0.9,
        stream=True,
        stop=None
    )
    reply = ""
    for chunk in completion:
        reply = reply + str(chunk.choices[0].delta.content or "")
    return reply
    
    
def update_character(new_mod):
    global history
    print("\n\nCharacter updated\n")
    history[0]["content"] = str(igors_prefs.instructions + prompt_no_history(
                                "скорати и убери повторения, сделай текст от второго лица" 
                                + history[0]["content"]
                                + igors_prefs.base_character.replace("\n", " ")
                                + get_summary(history), 
                                4096
                            ) + new_mod).replace("\n", " ")
    print("from ch upd - " + new_mod)
    save_history()
    with open("msg_count.txt", "w", encoding="utf-8") as f:
        f.write(str(igors_prefs.messages_count))
    
    
def save_history():
    global history
    h = json.dumps(history, indent=4, ensure_ascii=False)
    with open("history.json", "w", encoding='utf-8') as f:
        f.write(h)
        
def should_answer_general(message:telebot.types.Message):
    random.seed(igors_prefs.messages_count)
    cond_b = should_answer_analise(history)
    cond_d = False
    for i in igors_prefs.refer_list:
        if i in message.text.lower():
            cond_d = True
    try:
        cond_c = message.reply_to_message.from_user.is_bot
        if not cond_c:
            return False
    except Exception as e:
        cond_c = False
    
    return cond_b or cond_c or cond_d

def should_answer_analise(history):
    completion = client.chat.completions.create(
        model=igors_prefs.model_used,
        messages=[
            {
                "role": "system",
                "content": "исходя из истории сообщений, где ты - это assistant, а пользователи с разными именами - это user, определи, тебе ли адресовано сообщение. Дай ответ да или нет. Имей в виду, что к тебе обращаются не очень часто"
            },
            {
                "role": "user",
                "content": str(history)
            }
        ],
        temperature=0.1,
        max_tokens=5,
        top_p=0.9,
        stream=True,
        stop=None,
    )
    reply = ""
    for chunk in completion:
        reply = reply + str(chunk.choices[0].delta.content or "")
    
    print("Should ans reply "  + reply)
    
    if "да" in reply.lower() and random.randint(0, 10) != 5:
        return True
    else:  
        return False
    
    
    