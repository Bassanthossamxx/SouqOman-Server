import asyncio
from googletrans import Translator
import requests
import os
from dotenv import load_dotenv

translator = Translator()

def arabic_to_english(text: str) -> str:
    """Translate Arabic text into English using Google Translate."""
    try:
        result = translator.translate(text, src='ar', dest='en')
        if asyncio.iscoroutine(result):
            result = asyncio.run(result)
        return result.text
    except Exception:
        return text


# --- Akedly OTP Integration ---
load_dotenv()

AKEDLY_API_URL = os.getenv("AKEDLY_API_URL", "https://api.akedly.com/otp")
AKEDLY_API_KEY = os.getenv("AKEDLY_API_KEY")
AKEDLY_PIPELINE_ID = os.getenv("AKEDLY_PIPELINE_ID")


def create_otp_transaction(phone: str):
    """Start Akedly OTP transaction."""
    payload = {
        "APIKey": AKEDLY_API_KEY,
        "pipelineID": AKEDLY_PIPELINE_ID,
        "verificationAddress": {"phoneNumber": phone},
    }

    response = requests.post(AKEDLY_API_URL, json=payload)
    data = response.json()

    if data.get("status") == "success":
        return data["data"]["transactionID"]
    raise Exception(f"Akedly OTP error: {data.get('message', response.text)}")


def activate_otp_transaction(transactionID: str):
    """Trigger OTP SMS to user."""
    res = requests.post(f"{AKEDLY_API_URL}/activate/{transactionID}")
    data = res.json()

    if data.get("status") == "success":
        return data["data"]["_id"]
    raise Exception(f"Akedly OTP error: {data.get('message', res.text)}")


def verify_otp(request_id: str, otp: str):
    """Verify OTP entered by user."""
    try:
        res = requests.post(
            f"{AKEDLY_API_URL}/verify/{request_id}",
            json={"otp": otp},
            headers={"Content-Type": "application/json"},
        )
        data = res.json()
        if data.get("status") == "success":
            return True, data
        return False, data.get("message", "OTP verification failed")
    except requests.RequestException as e:
        return False, f"Request error: {str(e)}"
    except ValueError:
        return False, "Invalid response from Akedly"
