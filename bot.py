import telebot
from cryptography.fernet import Fernet
import openai


bot = telebot.TeleBot("Enter you telegram key from BotFather")
key = Fernet.generate_key()
fernet = Fernet(key)

openai.api_key = "Open AI Key"
messages = [ {"role": "system", "content": 
              "Take the persona of valorant agent Cypher and answer within 50 words."} ]

markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
agent = telebot.types.KeyboardButton("/agent")
encrypt_btn = telebot.types.KeyboardButton("/encrypt")
decrypt_btn = telebot.types.KeyboardButton("/decrypt")
encrypt_img_btn = telebot.types.KeyboardButton("/encrypt_image")
decrypt_img_btn = telebot.types.KeyboardButton("/decrypt_image")
markup.add(agent,encrypt_btn,decrypt_btn,encrypt_img_btn,decrypt_img_btn)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, "I can do these for your:", reply_markup=markup)


@bot.message_handler(func=lambda m: True)
def agent(message):
    if message.text:
        messages.append(
            {"role": "user", "content": message.text},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    bot.send_message(message.chat.id, reply)
    messages.append({"role": "assistant", "content": reply})

@bot.message_handler(commands=['encrypt'])
def encrypter(message):
    text = "Write message to encrypt:"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, encrypt)

def encrypt(message):
    encrypted_msg = fernet.encrypt(message.text.encode())
    bot.reply_to(message, encrypted_msg)

def encryptimg(message):
    file = bot.get_file(message.photo[-1].file_id)
    filebytes = bot.download_file(file.file_path)
    encrypted_img = fernet.encrypt(filebytes)
    file = open("code.txt",'w')
    file.write(encrypted_img.decode())
    file.close()
    bot.send_document(message.chat.id,open("code.txt",'r'))

def decryptimg(message):
    file = bot.get_file(message.document.file_id)
    filebytes = bot.download_file(file.file_path)
    decrypted_img = fernet.decrypt(filebytes.decode())
    file = open("code.png",'wb')
    file.write(decrypted_img)
    file.close()
    bot.send_document(message.chat.id,open("code.png",'rb'))

@bot.message_handler(commands=['decrypt'])
def decrypter(message):
    text = "Write encrypted message to decrypt:"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, decrypt)

def decrypt(message):
    decrypted_msg = fernet.decrypt(message.text.encode()).decode()
    bot.reply_to(message, decrypted_msg)

@bot.message_handler(commands=['encrypt_image'])
def recphoto(message):
    text = "Send photo to encrypt:"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, encryptimg)

@bot.message_handler(commands=['decrypt_image'])
def recdoc(message):
    text = "Send code.txt to decrypt:"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, decryptimg)
    
bot.infinity_polling()
