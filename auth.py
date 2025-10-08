import firebase_admin
from firebase_admin import credentials, firestore
import bcrypt
from telegram import Update
from telegram.ext import ContextTypes

# Firebase setup
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Register function
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Use: /register email password")
            return

        email = args[0]
        password = args[1]

        user_ref = db.collection("users").document(email)
        if user_ref.get().exists:
            await update.message.reply_text("User already exists. Please /login.")
            return

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user_ref.set({
            "email": email,
            "password_hash": hashed.decode(),
            "balance": 0,
            "kyc_status": False
        })

        await update.message.reply_text("Registration successful ✅ Use /login to access your account.")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Login function
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Use: /login email password")
            return

        email = args[0]
        password = args[1]

        user_ref = db.collection("users").document(email)
        user_doc = user_ref.get()

        if not user_doc.exists:
            await update.message.reply_text("User not found. Please /register first.")
            return

        stored_hash = user_doc.to_dict()["password_hash"]
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            await update.message.reply_text("Login successful ✅")
        else:
            await update.message.reply_text("Invalid password ❌")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Forgot password function (simple version)
async def forgot_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("Use: /forgotpassword email")
            return

        email = args[0]
        user_ref = db.collection("users").document(email)
        if not user_ref.get().exists:
            await update.message.reply_text("User not found.")
            return

        # Simple version: reset password to "123456" (demo only)
        hashed = bcrypt.hashpw("123456".encode(), bcrypt.gensalt())
        user_ref.update({"password_hash": hashed.decode()})

        await update.message.reply_text("Password reset successful. New password: 123456")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
