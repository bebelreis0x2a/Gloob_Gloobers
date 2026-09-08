import requests

URL_BASE = "http://127.0.0.1:8000/api/ranking/"

def enviar_pontuacao(nome, pontos, fase, tempo):
    try:
        payload = {
            "nome": nome,
            "pontos": pontos,
            "fase": fase,
            "tempo": tempo
        }
        response = requests.post(f"{URL_BASE}novo/", json=payload, timeout=2)
        return response.status_code == 201
    except Exception as e:
        print(f"Erro ao conectar com o servidor Django: {e}")
        return False

def buscar_ranking():
    try:
        response = requests.get(URL_BASE, timeout=2)
        if response.status_code == 200:
            return response.json().get('ranking', [])
    except Exception as e:
        print(f"Erro ao buscar ranking: {e}")
    return []