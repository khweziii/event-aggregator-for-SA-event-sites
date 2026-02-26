
from src.logger import logging 
from firebase_admin import credentials, firestore, initialize_app

# Initialize Firebase
def initialize_firebase():
    logging.info("Started initializing firebase admin SDK")

    """Initialize Firebase Admin SDK."""
    try:
        logging.info("Checking if Firebase admin sdk is already initialized")
        # Check if already initialized
        from firebase_admin import get_app
        app = get_app()
        logging.info("Firebase admin SDK is already initalized")
        return firestore.client()

    except ValueError:
        logging.info("Not initialized, initializing firebase admin sdk")
        # Not initialized, so initialize it
        cred = credentials.Certificate("wtp.json")
        initialize_app(cred, {
            "storageBucket": "whatstheplan-ab453.firebasestorage.app"
        })
        logging.info("Successfully initialized Firebase admin SDK")
        return firestore.client()