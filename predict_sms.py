import pickle

# Load trained model and vectorizer
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

print("SMS Scam Detector (type 'exit' to quit)")

while True:
    sms = input("Enter SMS: ")
    if sms.lower() == "exit":
        break
    
    sms_vec = vectorizer.transform([sms])
    prediction = model.predict(sms_vec)[0]
    
    if prediction == 1:
        print("Prediction: SPAM 🚨")
    else:
        print("Prediction: HAM ✅")