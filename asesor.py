import os
import time
import requests
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

# --- 🔐 CREDENCIALES ---
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# --- PORTAFOLIO ---
portfolio = [
    {"ticker": "NVDA", "peso": "15%"},
    {"ticker": "HOOD", "peso": "13.35%"},
    {"ticker": "VOO", "peso": "10.91%"},
    {"ticker": "ANET", "peso": "10.67%"},
    {"ticker": "GLD", "peso": "7.68%"},
    {"ticker": "PHO", "peso": "4.72%"},
    {"ticker": "MCHI", "peso": "4.08%"},
    {"ticker": "CQQQ", "peso": "2.90%"},
    {"ticker": "GPUS", "peso": "2.16%"}
]

# --- FUNCIONES ---
def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error Telegram: {e}")

def obtener_datos(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1d")
        
        if df.empty or 'Close' not in df.columns: return None

        # Indicadores
        rsi_ind = RSIIndicator(close=df["Close"], window=14)
        df["RSI"] = rsi_ind.rsi()
        
        ema50_ind = EMAIndicator(close=df["Close"], window=50)
        ema200_ind = EMAIndicator(close=df["Close"], window=200)
        df["EMA_50"] = ema50_ind.ema_indicator()
        df["EMA_200"] = ema200_ind.ema_indicator()
        
        ultimo = df.iloc[-1]
        tendencia = "📈 Alcista" if ultimo['EMA_50'] > ultimo['EMA_200'] else "📉 Bajista"

        return {
            "precio": round(float(ultimo['Close']), 2),
            "rsi": round(float(ultimo['RSI']), 2),
            "tendencia": tendencia
        }
    except:
        return None

def consultar_gemini_directo(ticker, datos, peso):
    # --- CONEXIÓN DIRECTA (SIN LIBRERÍA) ---
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
    
    prompt = f"""
    Eres un asesor financiero experto. Activo: {ticker} (Peso: {peso}).
    Datos: Precio ${datos['precio']}, RSI {datos['rsi']}, Tendencia {datos['tendencia']}.
    En 3 líneas cortas y didácticas:
    1. Interpretación técnica (con emojis).
    2. Qué vigilar.
    3. Opinión educativa (Acumular/Mantener/Recortar).
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error API ({response.status_code}): {response.text[:100]}"
            
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def main():
    enviar_telegram("🚀 **Iniciando análisis (Modo Directo)...**")
    exito = False
    
    for activo in portfolio:
        ticker = activo["ticker"]
        datos = obtener_datos(ticker)
        if datos:
            analisis = consultar_gemini_directo(ticker, datos, activo["peso"])
            msg = f"📌 *{ticker}*\nPrecio: ${datos['precio']} | RSI: {datos['rsi']}\n\n{analisis}"
            enviar_telegram(msg)
            exito = True
            time.sleep(40)
    
    if not exito:
        enviar_telegram("⚠️ No se pudieron obtener datos.")
    else:
        enviar_telegram("✅ **Reporte finalizado.**")

if __name__ == "__main__":
    main()
