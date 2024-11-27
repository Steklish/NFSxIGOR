import igors_prefs
from igors_prefs import chat_to_interact, NFS_chat_id
from igors_mind import *
import time

import json

bot = telebot.TeleBot(igors_prefs.TG_API)

bot.send_message(chat_to_interact, "☢️" + prompt_no_history("придумай нелепый факт про связь и опиши кратко", 300) + "\n" + time.asctime() + " host started")

@bot.message_handler(commands=["start",])
def start(message:telebot.types.Message):
    bot.send_message(chat_to_interact, "☢️Связист запущен\n" + time.asctime() + "\nзапустил " + message.from_user.full_name)
    igors_prefs.allowed_to_reply = True
    
@bot.message_handler(commands=["shutup", ])
def reply(message:telebot.types.Message):
    bot.send_message(chat_to_interact, "☢️ Связист заткнут \n" + time.asctime() + "\nОтправил " + message.from_user.full_name)
    igors_prefs.allowed_to_reply = False


@bot.message_handler(commands=["amnesia", ])
def reply(message:telebot.types.Message):
    bot.send_message(chat_to_interact, "☢️ Amnesia...")
    igors_prefs.history = [
        {
            "role": "system",
            "content": igors_prefs.base_character
        }
    ]


@bot.message_handler(commands=["die",])
def reply(message:telebot.types.Message):
    bot.send_message(chat_to_interact, "☢️ history saved\n")
    h = json.dumps(history, indent=4, ensure_ascii=False)
    with open("history.json", "w", encoding='utf-8') as f:
        f.write(h)
    bot.send_message(chat_to_interact, "☢️ Связист умер \n" + time.asctime() + "\nОтправил " + message.from_user.full_name)
    bot.stop_polling()
    exit(0)

@bot.message_handler(commands=["gethistory",])
def reply(message:telebot.types.Message):
    h = json.dumps(history, indent=4, ensure_ascii=False)
    bot.reply_to(message, "☢️☢️☢️☢️☢️☢️\n" + h[0: min(len(h), 5000)])


@bot.message_handler(commands=["summary",])
def reply(message:telebot.types.Message):
    bot.reply_to(message, "☢️" + get_summary(history))



@bot.message_handler(commands=["savehistory",])
def reply(message:telebot.types.Message):
    bot.send_message(chat_to_interact, "☢️ history saved\n")
    save_history()
        

@bot.message_handler(commands=["character",])
def reply(message:telebot.types.Message):
    if len(history) > 0:
        bot.send_message(chat_to_interact, "☢️" + history[0]["content"])


@bot.message_handler(commands=["modifier",])
def reply(message:telebot.types.Message):
    bot.reply_to(
            message,
            "☢️ текущий модификатор:" + igors_prefs.modifier
        )
    
@bot.message_handler(commands=["change_modifier",])
def reply(message:telebot.types.Message):
    bot.send_message(
            message.chat.id,
            "☢️ старый модификатор: " + igors_prefs.modifier
        )
    
    igors_prefs.modifier = "".join(message.text.split(" ")[1:])
    
    print(igors_prefs.modifier)
    bot.send_message(
            message.chat.id,
            "☢️ новый модификатор: " + igors_prefs.modifier
        )
    update_character(igors_prefs.modifier)

@bot.message_handler(func=lambda message: message.chat.id != NFS_chat_id)
def reply(message:telebot.types.Message):
    try:
        igors_prefs.messages_count += 1
        if igors_prefs.messages_count % 10 == 0:
            update_character(igors_prefs.modifier)
            save_history()
        append_history_with_message(message)
        if igors_prefs.allowed_to_reply and should_answer_general(message):
            bot.reply_to(message, prompt(message))
    except Exception as e: 
        print(e)
        bot.send_message(
                chat_to_interact,
                "🚨🚨🚨PIZDA HE'S DYING🚨🚨🚨\n" + str(e)
            )
        
bot.polling()