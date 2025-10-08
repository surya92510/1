from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv("config.env")

BOT_TOKEN = os.getenv("7641165279:AAFzcCax3wcyapdUFNU6rJ2qf_QN36-xBuo")

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Wallet Bot! Use /register to create account.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
from auth import register, login, forgot_password
from telegram.ext import CommandHandler

app.add_handler(CommandHandler("register", register))
app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("forgotpassword", forgot_password))

from payment import add_money, withdraw_money
app.add_handler(CommandHandler("addmoney", add_money))
app.add_handler(CommandHandler("withdraw", withdraw_money))

from kyc import upload_kyc
app.add_handler(CommandHandler("kyc", upload_kyc))

from admin import view_users, view_withdrawals, approve_withdrawal

app.add_handler(CommandHandler("viewusers", view_users))
app.add_handler(CommandHandler("viewwithdrawals", view_withdrawals))
app.add_handler(CommandHandler("approvewithdraw", approve_withdrawal))
