import requests

def enviar_telegram(mensagem):
    token = "7765478794:AAHAtyPoeY5fa6QIR3cv1zHfz55En4B9PTI"
    chat_id = "5657759813"
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"❌ Erro ao enviar mensagem: {response.text}")
    except Exception as e:
        print(f"❌ Falha na requisição Telegram: {e}")