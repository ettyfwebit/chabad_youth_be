import requests

TOKEN = 'cfe0c211c2c24a0f9ecf831b046438794323dcaae1e54b3aa2'

def send_message(message, chat_id) -> str:
    url = f"https://7103.api.greenapi.com/cteen/sendMessage/{TOKEN}"
    payload = {"chatId": f'{chat_id}@c.us', "message": message }
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, json=payload, headers=headers)

