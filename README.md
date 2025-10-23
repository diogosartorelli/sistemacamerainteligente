# Projeto Final - Hardware Architecture (2025.2)
## Sistema de Segurança IoT com Raspberry Pi

Projeto disciplina de Hardware Architecture Semestre 2025.2, ministrada pelo Prof. Me. Fernando P. Pinheiro na Atitus Educação.

---

## 1. Descrição Geral

Este projeto é um protótipo funcional (MVP) de um sistema de segurança IoT que soluciona um problema real de monitoramento patrimonial.

A solução utiliza uma Raspberry Pi para coletar informações do mundo físico (detecção de presença por sensor ultrassônico)e interagir com o ambiente. Ao detectar uma intrusão, o sistema captura uma fotografia, que é processada e transmitida para uma aplicação conectada  e armazenada em um banco de dados local para visualização.

## 2. Funcionalidades do MVP

* Detecção de Movimento:** Utiliza um sensor ultrassônico (HC-SR04) para detectar a proximidade de objetos ou pessoas.
* Registro Visual:** Ao detectar movimento, uma webcam USB conectada à Raspberry Pi captura uma fotografia instantânea.
* Comunicação Hardware-Software:** O script embarcado envia a imagem capturada para o backend Supabase.
* Armazenamento e Visualização:** O backend armazena um registro do evento (timestamp e caminho da imagem) em um banco de dados.

## 3. Tecnologias Utilizadas

### Hardware
* Plataforma Embarcada: Raspberry Pi 4 [cite: 48]
* Sensor: Sensor Ultrassônico HC-SR04 [cite: 48]
* Arduino Uno
* Coleta de Imagem:** Webcam USB genérica

### Software (Aplicação Embarcada)
* **Linguagem:** Python 3
* **Bibliotecas:**
    * `RPi.GPIO`: Para controle do pino do atuador (LED).
    * `pyserial`: Para comunicação com o sensor ultrassônico.
    * `opencv-python`: Para captura de imagem da webcam.
    * `requests`: Para enviar a foto para o backend.
