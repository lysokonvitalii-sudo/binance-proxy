from flask import Flask, jsonify
import requests
import hmac
import hashlib
import time
import os

app = Flask(__name__)

API_KEY = os.environ.get("BYBIT_API_KEY")
SECRET_KEY = os.environ.get("BYBIT_SECRET_KEY")

@app.route('/balance')
def get_balance():
    if not API_KEY or not SECRET_KEY:
        return jsonify({"error": "API keys not set"}), 500

    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"
    query = "accountType=UNIFIED"

    # Правильний порядок для Bybit v5
    param_str = timestamp + API_KEY + recv_window + query
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        param_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    url = f"https://api.bybit.com/v5/account/wallet-balance?{query}"
    headers = {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-RECV-WINDOW": recv_window,
        "X-BAPI-SIGN": signature,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    
    # Логуємо відповідь для дебагу
    try:
        data = response.json()
    except Exception:
        return jsonify({
            "error": "Invalid response from Bybit",
            "status_code": response.status_code,
            "raw": response.text[:500]
        }), 400

    if data.get("retCode") != 0:
        return jsonify({"bybit_error": data}), 400

    coins = data["result"]["list"][0]["coin"]
    balances = [c for c in coins if float(c["walletBalance"]) > 0]
    return jsonify(balances)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
