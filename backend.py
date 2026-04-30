from flask import Flask, request, render_template, jsonify, session
import pickle
from threading import Timer
import webbrowser
from database import init_db
from auth import auth
from reports import reports as reports_bp
from admin import admin as admin_bp

# Load model and vectorizer
print("Loading AI model...")
model = pickle.load(open("model.pkl", "rb"))
print("AI model loaded.")

print("Loading TF-IDF vectorizer...")
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
print("TF-IDF vectorizer loaded.")

app = Flask(__name__)
app.secret_key = "scam_detector_secret_key_2024"

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(reports_bp)
app.register_blueprint(admin_bp)

# Initialize database
init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze_sms", methods=["POST"])
def analyze_sms():
    data = request.json
    message = data.get("message", "")

    # Guard: return error if message is empty
    if not message.strip():
        return jsonify({"error": "No message provided"}), 400

    # Transform message into vector
    message_vec = vectorizer.transform([message])

    # Prediction
    prediction_label = model.predict(message_vec)[0]

    # Map numeric labels to human-readable
    label_map = {0.0: "Ham", 1.0: "Spam"}
    prediction_label = label_map.get(float(prediction_label), "Unknown")

    # Confidence using predict_proba
    if hasattr(model, "predict_proba"):
        confidence_score = model.predict_proba(message_vec).max()
    else:
        confidence_score = None

    return jsonify({
        "prediction": prediction_label,
        "confidence": round(float(confidence_score), 2) if confidence_score else "N/A"
    })

# Automatically open browser
url = "http://127.0.0.1:5000/"
Timer(1, lambda: webbrowser.open(url)).start()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
