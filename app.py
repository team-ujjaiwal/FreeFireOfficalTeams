from flask import Flask, request, send_file, jsonify
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

# Fixed background image
DEFAULT_BG_URL = "https://iili.io/3e5Wzsj.jpg"
VALID_KEY = "1weekkeysforujjaiwal"  # your required key

def get_outfit_image(uid, region):
    try:
        # DO NOT pass 'key' to external API
        outfit_url = f"https://aditya-outfit-v6op.onrender.com/outfit-image?uid={uid}&region={region}&bg={DEFAULT_BG_URL}"
        response = requests.get(outfit_url)

        # Check if response is a valid image
        if response.status_code != 200:
            print("External API failed:", response.text)
            return None

        img = Image.open(BytesIO(response.content)).convert("RGBA")
        return img
    except Exception as e:
        print(f"Error fetching outfit: {e}")
        return None

@app.route("/outfit-image", methods=["GET"])
def outfit_image():
    uid = request.args.get("uid")
    region = request.args.get("region")
    key = request.args.get("key")

    if not uid or not region or not key:
        return jsonify({"error": "Missing uid, region, or key parameter"}), 400

    if key != VALID_KEY:
        return jsonify({"error": "Invalid API key"}), 403

    try:
        # Load background image
        bg_response = requests.get(DEFAULT_BG_URL)
        bg_image = Image.open(BytesIO(bg_response.content)).convert("RGBA")

        # Load outfit image
        outfit_img = get_outfit_image(uid, region)
        if not outfit_img:
            return jsonify({"error": "Failed to fetch outfit image"}), 500

        # Resize to match background
        outfit_img = outfit_img.resize(bg_image.size)

        # Combine both images
        final_image = Image.alpha_composite(bg_image, outfit_img)

        output = BytesIO()
        final_image.save(output, format="PNG")
        output.seek(0)
        return send_file(output, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)