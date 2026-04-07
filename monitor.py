import feedparser
import requests
import json
import time
import os

# ─── CONFIGURACIÓN ───────────────────────────────────────────────
TELEGRAM_TOKEN = "8619230632:AAE6XjxR_i2L_gz0JWgXCaU_Jx2CuNC4qMs"
CHAT_ID = "-1003431483057"
INTERVALO_MINUTOS = 15
ARCHIVO_VISTOS = "posts_vistos.json"

PAGINAS = [
    {"nombre": "Alerta AMBER Guanajuato",           "url": "https://www.facebook.com/aambergto"},
    {"nombre": "Atención Ciudadana León",            "url": "https://www.facebook.com/atencion.ciudadana.leon/"},
    {"nombre": "León COMUDE",                        "url": "https://www.facebook.com/LeonCOMUDE/"},
    {"nombre": "Contraloría León",                   "url": "https://www.facebook.com/ContraloriaLeon/"},
    {"nombre": "Desarrollo Urbano León",             "url": "https://www.facebook.com/desarrollourbano.leon/"},
    {"nombre": "León DIF",                           "url": "https://www.facebook.com/leondif/"},
    {"nombre": "Desarrollo Rural León",              "url": "https://www.facebook.com/DireccionGeneralDesarrolloRuralLeon/"},
    {"nombre": "Dirección de Educación Municipal",   "url": "https://www.facebook.com/direcciondeeducacion.municipal/"},
    {"nombre": "Obra Pública León",                  "url": "https://www.facebook.com/DireccionGeneraldeObraPublicaLeon/"},
    {"nombre": "Centro de Ciencias Explora",         "url": "https://www.facebook.com/CentroDeCienciasExplora/"},
    {"nombre": "Feria de León",                      "url": "https://www.facebook.com/FeriaDeLeon/"},
    {"nombre": "IMJU León",                          "url": "https://www.facebook.com/IMJULeon/"},
    {"nombre": "IMPLAN León",                        "url": "https://www.facebook.com/InstitutoMunicipalDePlaneacionLeon/"},
    {"nombre": "León IMUVI",                         "url": "https://www.facebook.com/LeonIMUVI/"},
    {"nombre": "Instituto Cultural León",            "url": "https://www.facebook.com/InstitutoCulturalLeon/"},
    {"nombre": "León Desarrollo Social",             "url": "https://www.facebook.com/LeonDesarrolloSocial/"},
    {"nombre": "Municipio de León",                  "url": "https://www.facebook.com/municipio.leon/"},
    {"nombre": "Parkmetro León",                     "url": "https://www.facebook.com/parkmetroleon/"},
    {"nombre": "Plaza Efraín Huerta",                "url": "https://www.facebook.com/PLAZAEFRAINHUERTA/"},
    {"nombre": "Plaza Griselda Álvarez",             "url": "https://www.facebook.com/PlazaGriseldaAlvarez/"},
    {"nombre": "Plaza Praxedis",                     "url": "https://www.facebook.com/PlazaPraxedis/"},
    {"nombre": "Protección Civil León",              "url": "https://www.facebook.com/proteccion.leon/"},
    {"nombre": "Dirección de Salud León",            "url": "https://www.facebook.com/DireccionSaludLeon/"},
    {"nombre": "SAPAL León",                         "url": "https://www.facebook.com/SapalLeon/"},
    {"nombre": "SSPL León",                          "url": "https://www.facebook.com/LeonSSPL/"},
    {"nombre": "Ayuntamiento de León",               "url": "https://www.facebook.com/AyuntamientoLeon/"},
    {"nombre": "Fortalecimiento Social León",        "url": "https://www.facebook.com/FortalecimientoSocialLeon/"},
    {"nombre": "SIAP León",                          "url": "https://www.facebook.com/SIAPLeon/"},
    {"nombre": "Tesorería León",                     "url": "https://www.facebook.com/tesorerialeon/"},
    {"nombre": "Visita León",                        "url": "https://www.facebook.com/visitaleongto/"},
    {"nombre": "Zoológico de León",                  "url": "https://www.facebook.com/ZoologicodeLeon/"},
]

# ─── FUNCIONES ───────────────────────────────────────────────────

def cargar_vistos():
    if os.path.exists(ARCHIVO_VISTOS):
        with open(ARCHIVO_VISTOS, "r") as f:
            return json.load(f)
    return {}

def guardar_vistos(vistos):
    with open(ARCHIVO_VISTOS, "w") as f:
        json.dump(vistos, f)

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def rss_url(facebook_url):
    # Limpia la URL y arma el feed de rss.app
    slug = facebook_url.rstrip("/").split("/")[-1]
    return f"https://rss.app/feeds/_t{slug}.xml"

def revisar_pagina(pagina, vistos):
    nombre = pagina["nombre"]
    feed_url = rss_url(pagina["url"])

    try:
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            return

        for entry in feed.entries[:3]:  # revisa los 3 más recientes
            post_id = entry.get("id") or entry.get("link")
            if not post_id:
                continue

            if post_id not in vistos:
                vistos[post_id] = True
                titulo = entry.get("title", "Sin título")
                link = entry.get("link", pagina["url"])

                mensaje = (
                    f"📣 <b>Nueva publicación</b>\n\n"
                    f"📌 <b>Página:</b> {nombre}\n"
                    f"📝 <b>Título:</b> {titulo}\n"
                    f"🔗 {link}"
                )
                enviar_telegram(mensaje)
                print(f"✅ Enviado: {nombre} - {titulo}")

    except Exception as e:
        print(f"❌ Error en {nombre}: {e}")

def ciclo_principal():
    print("🚀 Monitor iniciado...")
    enviar_telegram("🚀 Monitor de páginas de Facebook iniciado correctamente.")

    vistos = cargar_vistos()

    # Primera corrida: marcar todos los posts actuales como vistos (sin enviar)
    print("📋 Registrando posts existentes (no se enviarán)...")
    for pagina in PAGINAS:
        feed_url = rss_url(pagina["url"])
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                post_id = entry.get("id") or entry.get("link")
                if post_id:
                    vistos[post_id] = True
        except:
            pass
    guardar_vistos(vistos)
    print("✅ Listo. Esperando posts nuevos...\n")

    while True:
        print(f"🔍 Revisando {len(PAGINAS)} páginas...")
        for pagina in PAGINAS:
            revisar_pagina(pagina, vistos)
            time.sleep(2)  # pequeña pausa entre páginas para no saturar

        guardar_vistos(vistos)
        print(f"⏱ Esperando {INTERVALO_MINUTOS} minutos...\n")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    ciclo_principal()
