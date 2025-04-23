from google.cloud import firestore
from DataCollector import collect_data
import datetime

def collect_and_store(request):  # This is the HTTP entry point for Cloud Function
    db = firestore.Client()
    result = collect_data()

    doc_ref = db.collection('yourCollection').document()
    doc_ref.set({
        'timestamp': datetime.datetime.utcnow(),
        'data': result
    })

    return f"Saved {len(result)} items"