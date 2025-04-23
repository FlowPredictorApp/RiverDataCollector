from google.cloud import firestore
from GetJavorinka import getJavorinka
import datetime

def collect_and_store(request):  # This is the HTTP entry point for Cloud Function
    db = firestore.Client()
    result = getJavorinka()

    # save result to Firestore
    if result is not None:
        for item in result:
            # Create a unique document ID based on the current timestamp
            doc_id = f"javorinka_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            db.collection("javorinka").document(doc_id).set(item)
    else:
        print("No data to save")

    return f"Saved {len(result)} items"