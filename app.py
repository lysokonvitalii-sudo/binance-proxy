from flask import Flask, jsonify
import requests
import hmac
import hashlib
import time
import os

app = Flask(__name__)

API_KEY = os.environ.get("BINANCE_API_KEY")
SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY")

@app.route('/balance')
def get_balance():
    if not API_KEY or not SECRET_KEY:
        return jsonify({"error": "API keys not set"}), 500

    timestamp = int(time.time() * 1000)
    query = f"timestamp={timestamp}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        query.encode(),
        hashlib.sha256
    ).hexdigest()

    url = f"https://api.binance.com/api/v3/account?{query}&signature={signature}"
    headers = {"X-MBX-APIKEY": API_KEY}
    response = requests.get(url, headers=headers)
    
    data = response.json()
    
    # Якщо помилка від Binance — повертаємо її
    if "code" in data:
        return jsonify({"binance_error": data}), 400
    
    balances = [b for b in data["balances"]
                if float(b["free"]) > 0]
    return jsonify(balances)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
