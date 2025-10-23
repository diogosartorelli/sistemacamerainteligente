import time
import os
import cv2
import serial
import urllib.parse
from datetime import datetime
from pathlib import Path
from imagekitio import ImageKit
from supabase import create_client, Client
import requests


# from mailersend import MailerSendClient, EmailBuilder  # Descomente se for usar

# -----------------------------
# 1️⃣ Configurações e inicialização
# -----------------------------

# Pasta para fotos temporárias
PASTA_FOTOS = "/home/cueca/Pictures/Webcam"
os.makedirs(PASTA_FOTOS, exist_ok=True)

# Webcam USB
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise Exception("❌ Não foi possível acessar a câmera USB (/dev/video0).")

# Arduino (sensor ultrassônico)
PORTA_SERIAL = "/dev/ttyACM0"
arduino = serial.Serial(PORTA_SERIAL, 9600, timeout=1)

# ImageKit.io
imagekit = ImageKit(
    private_key='private_ve3sPwA7RWYR7H9qfoSgFFOjXUk=',
    public_key='public_HdyowsYZElEPTc0ggT+ZAuhfviA=',
    url_endpoint='https://ik.imagekit.io/project1134814'
)

# Supabase
SUPABASE_URL = "https://rakwwwahnloapodnvbsv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJha3d3d2FobmxvYXBvZG52YnN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODMwNTMsImV4cCI6MjA3NjU1OTA1M30.BnN-wXkpYrFQYXYLw7jneoaCjcqCz5ro4AHSJQckS5E"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# 2️⃣ Funções
# -----------------------------

def capturar_imagem():
    """Captura imagem da webcam e salva na pasta definida"""
    ret, frame = camera.read()
    if not ret:
        raise Exception("❌ Erro ao capturar imagem da webcam.")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    nome_arquivo = os.path.join(PASTA_FOTOS, f"evento_{timestamp}.jpg")
    cv2.imwrite(nome_arquivo, frame)
    print(f"📸 Imagem capturada: {nome_arquivo}")
    return nome_arquivo

def obter_distancia():
    """Solicita leitura do Arduino via Serial"""
    arduino.write(b"1")
    distancia = arduino.readline().decode("utf-8").strip()
    try:
        return float(distancia)
    except:
        return None

# -----------------------------
# 3️⃣ Loop principal
# -----------------------------

def main():
    print("🚀 Sistema iniciado. Monitorando distância...")

    while True:
        distancia = obter_distancia()
        if distancia and distancia < 50.0:
            print(f"📏 Distância detectada: {distancia:.2f} cm")

            # Captura a imagem
            nome_imagem = capturar_imagem()
            print(nome_imagem)

            # Seleciona a foto mais recente
            pasta = Path(PASTA_FOTOS)
            fotos = list(pasta.glob("*.jpg"))
            fotos = [f for f in fotos if f.is_file()]

            if not fotos:
                raise Exception("Nenhuma foto JPG encontrada na pasta.")

            foto_mais_recente = max(fotos, key=lambda f: f.stat().st_mtime)
            print(f"📸 Foto selecionada: {foto_mais_recente.name}")

            # Upload para o ImageKit
            with open(foto_mais_recente, "rb") as f:
                response = imagekit.upload_file(
                    file=f,
                    file_name=foto_mais_recente.name,
                    options={}
                )

            image_url = response.url
            print("✅ URL da imagem:", image_url)

            # Envio para Supabase
            data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {
                "ds_link_image": image_url,
                "ds_alerta": "Cuidado! Sua casa está sendo invadida",
                "dt_alerta": data_hora_atual
            }
            response = supabase.table("alerta").insert(data).execute()

            # Busca último registro inserido
            ultimo_registro = (
                supabase.table("alerta")
                .select("*")
                .order("cd_alerta", desc=True)
                .limit(1)
                .execute()
            )

            registro = ultimo_registro.data[0]
            link_imagem = registro["ds_link_image"]
            mensagem_alerta = registro["ds_alerta"]
            data_alerta = registro["dt_alerta"]

            print(f"Link da imagem: {link_imagem}")
            print(f"Alerta: {mensagem_alerta}")
            print(f"Data do alerta: {data_alerta}")

            # Envio WhatsApp (CallMeBot)
            phone_number = "555497063721"
            api_key = "4957744"
            mensagem_whats = f"🚨 {mensagem_alerta}\n📅 {data_alerta}\n📸 {link_imagem}"
            encoded_message = urllib.parse.quote(mensagem_whats)
            url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={encoded_message}&apikey={api_key}"
            responde_whats = requests.get(url)
            print(f"📲 Mensagem WhatsApp enviada: {url}")

            time.sleep(1)  # evita capturas múltiplas

        time.sleep(0.5)  # loop de leitura do sensor

# -----------------------------
# 4️⃣ Inicialização do script
# -----------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("🛑 Encerrando o sistema...")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        arduino.close()
