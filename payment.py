import razorpay
import os
from telegram import Update
from telegram.ext import ContextTypes
from database import db  # Firebase db connection from database.py

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Add Money function
async def add_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Use: /addmoney email amount")
            return

        email = args[0]
        amount = int(args[1]) * 100  # Razorpay amount in paise

        user_ref = db.collection("users").document(email)
        if not user_ref.get().exists:
            await update.message.reply_text("User not found. Please /register first.")
            return

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        await update.message.reply_text(
            f"Payment order created. Order ID: {order['id']}\nPay using Razorpay checkout."
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Withdraw Money function (request system)
async def withdraw_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Use: /withdraw email amount")
            return

        email = args[0]
        amount = float(args[1])

        user_ref = db.collection("users").document(email)
        user_doc = user_ref.get()

        if not user_doc.exists:
            await update.message.reply_text("User not found.")
            return

        balance = user_doc.to_dict()["balance"]
        if amount > balance:
            await update.message.reply_text("Insufficient balance.")
            return

        # Withdrawal request stored in DB (admin approves later)
        db.collection("withdrawals").add({
            "email": email,
            "amount": amount,
            "status": "pending"
        })

        await update.message.reply_text(
            f"Withdrawal request for ₹{amount} submitted ✅. Waiting for admin approval."
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
