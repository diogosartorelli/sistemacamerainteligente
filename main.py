import time
import os
import cv2
from imagekitio import ImageKit
from mailersend import MailerSendClient, EmailBuilder
from supabase import create_client, Client
import serial

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

# MailerSend (substitua pela sua chave real)
ms = MailerSendClient(api_key='SUA_CHAVE_MAILERSEND_AQUI')

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

def upload_imagekit(nome_arquivo):
    """Faz upload da imagem para ImageKit.io e retorna a URL pública"""
    with open(nome_arquivo, "rb") as f:
        response = imagekit.upload_file(
            file=f,
            file_name=os.path.basename(nome_arquivo),
            options={}
        )
    if response.response_metadata.status == 200:
        url_da_imagem = response.result.url
        print("☁️ Upload concluído com sucesso!")
        print("🌐 URL da imagem:", url_da_imagem)
        return url_da_imagem
    else:
        print("❌ Falha no upload:", response.response_metadata)
        return None

def enviar_email(imagem_url):
    """Envia e-mail de alerta com a imagem do evento"""
    email = (EmailBuilder()
             .from_email("sender@domain.com", "Sistema de Monitoramento")
             .to_many([{"email": "recipient@domain.com", "name": "Destinatário"}])
             .subject("🚨 Alerta: Evento Detectado!")
             .html(f"<p>Um evento foi detectado. Veja a imagem abaixo:</p><img src='{imagem_url}' width='400'>")
             .text(f"Um evento foi detectado. Veja a imagem: {imagem_url}")
             .build())
    response = ms.emails.send(email)
    if response.status_code == 200:
        print("📧 E-mail enviado com sucesso!")
        return True
    else:
        print("❌ Erro ao enviar e-mail:", response.status_code, response.text)
        return False

def inserir_supabase(imagem_url, descricao="Alerta de teste"):
    """Insere registro do alerta no Supabase"""
    data = {
        "ds_link_image": imagem_url,
        "ds_alerta": descricao,
        "dt_alerta": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    response = supabase.table("alerta").insert(data).execute()
    if hasattr(response, "status_code") and response.status_code != 201:
        print(f"❌ Erro ao inserir no Supabase: {response}")
    else:
        print("✅ Registro inserido no Supabase com sucesso.")

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

            pasta = Path("/home/cueca/Pictures/Webcam")
fotos = list(pasta.glob("*.jpg"))
fotos = [f for f in fotos if f.is_file()]

if not fotos:
    raise Exception("Nenhuma foto JPG encontrada na pasta.")

foto_mais_recente = max(fotos, key=lambda f: f.stat().st_mtime)
print(f"📸 Foto selecionada: {foto_mais_recente.name}")

imagekit = ImageKit(
    private_key='private_ve3sPwA7RWYR7H9qfoSgFFOjXUk=',
    public_key='public_HdyowsYZElEPTc0ggT+ZAuhfviA=',
    url_endpoint='https://ik.imagekit.io/project1134814'
)

with open(foto_mais_recente, "rb") as f:
    response = imagekit.upload_file(
        file=f,
        file_name=foto_mais_recente.name,
        options={}
    )

image_url = response.url
print("✅ URL da imagem:", image_url)

url_supabase = "https://rakwwwahnloapodnvbsv.supabase.co"
key_supabase = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJha3d3d2FobmxvYXBvZG52YnN2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5ODMwNTMsImV4cCI6MjA3NjU1OTA1M30.BnN-wXkpYrFQYXYLw7jneoaCjcqCz5ro4AHSJQckS5E"
supabase: Client = create_client(url_supabase, key_supabase)

data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

data = {
    "ds_link_image": image_url,
    "ds_alerta": "Cuidado! Sua casa está sendo invadida",
    "dt_alerta": data_hora_atual
}

response = supabase.table("alerta").insert(data).execute()

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

phone_number = "555493310936"
api_key = "5932002"   

mensagem_whats = f"🚨 {mensagem_alerta}\n📅 {data_alerta}\n📸 {link_imagem}"

encoded_message = urllib.parse.quote(mensagem_whats)
url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={encoded_message}&apikey={api_key}"

        
        time.sleep(1)  # Aguarda 1 segundo antes da próxima leitura

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
        arduino.cloc
