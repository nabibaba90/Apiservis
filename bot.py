from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Buraya yukarıdaki apis sözlüğünü koy

@app.route("/api/<api_name>", methods=["GET"])
def api_proxy(api_name):
    if api_name not in apis:
        return jsonify({
            "success": False,
            "description": "API bulunamadı"
        }), 404

    api = apis[api_name]
    query_params = {}

    for p in api["params"]:
        val = request.args.get(p)
        if val is None:
            return jsonify({
                "success": False,
                "description": f"'{p}' parametresi eksik"
            }), 400
        query_params[p] = val

    try:
        headers = {
            "User-Agent": request.headers.get(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(api["url"], params=query_params, headers=headers, timeout=15)
        response.raise_for_status()

        if 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
        else:
            data = response.text

        if isinstance(data, dict) and "info" in data:
            del data["info"]

        return jsonify({
            "success": True,
            "description": api["desc"],
            "data": data
        })

    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "description": f"API isteği başarısız: {str(e)}"
        }), 500

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5040)
