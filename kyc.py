import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
from telegram import Update
from telegram.ext import ContextTypes

# Firebase setup
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    "storageBucket": "your-project-id.appspot.com"
})
db = firestore.client()
bucket = storage.bucket()

async def upload_kyc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        email = None
        if len(context.args) != 1:
            await update.message.reply_text("Use: /kyc email (and attach document as file)")
            return

        email = context.args[0]

        if not update.message.document:
            await update.message.reply_text("Please attach a document file with the command.")
            return

        file_id = update.message.document.file_id
        file = await context.bot.get_file(file_id)
        file_path = f"{email}_{update.message.document.file_name}"

        # Download file locally
        await file.download_to_drive(file_path)

        # Upload to Firebase Storage
        blob = bucket.blob(file_path)
        blob.upload_from_filename(file_path)
        blob.make_public()

        # Save KYC status in Firestore
        db.collection("users").document(email).update({
            "kyc_status": False,
            "kyc_document": blob.public_url
        })

        await update.message.reply_text(
            f"KYC document uploaded successfully ✅\nDocument URL: {blob.public_url}\nAdmin will verify soon."
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
