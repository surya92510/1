from telegram import Update
from telegram.ext import ContextTypes
from database import db  # Firebase db connection

# अपना Telegram ID यहाँ डालो
ADMIN_ID = 123456789  

def is_admin(update: Update):
    return update.effective_user.id == ADMIN_ID

# View all users
async def view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("🚫 You are not authorized.")
        return

    users = db.collection("users").stream()
    msg = "📋 Users List:\n"
    for user in users:
        data = user.to_dict()
        msg += f"- {data['email']} | Balance: ₹{data['balance']} | KYC: {data['kyc_status']}\n"
    await update.message.reply_text(msg)

# View withdraw requests
async def view_withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("🚫 You are not authorized.")
        return

    requests = db.collection("withdrawals").where("status", "==", "pending").stream()
    msg = "💰 Pending Withdrawals:\n"
    for req in requests:
        data = req.to_dict()
        msg += f"- {data['email']} | Amount: ₹{data['amount']} | ID: {req.id}\n"
    await update.message.reply_text(msg)

# Approve withdraw request
async def approve_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("🚫 You are not authorized.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Use: /approvewithdraw withdrawal_id")
        return

    withdrawal_id = context.args[0]
    withdrawal_ref = db.collection("withdrawals").document(withdrawal_id)
    withdrawal_doc = withdrawal_ref.get()

    if not withdrawal_doc.exists:
        await update.message.reply_text("Withdrawal request not found.")
        return

    withdrawal_data = withdrawal_doc.to_dict()
    email = withdrawal_data["email"]
    amount = withdrawal_data["amount"]

    user_ref = db.collection("users").document(email)
    user_doc = user_ref.get()
    balance = user_doc.to_dict()["balance"]

    if amount > balance:
        await update.message.reply_text("User has insufficient balance.")
        return

    user_ref.update({"balance": balance - amount})
    withdrawal_ref.update({"status": "approved"})

    await update.message.reply_text(f"✅ Withdrawal approved for {email} amount ₹{amount}")
