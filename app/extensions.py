from app.config import Config
import razorpay

# Razorpay Client
razorpay_client = razorpay.Client(auth=(
    Config.RAZORPAY_KEY_ID,
    Config.RAZORPAY_KEY_SECRET
)) if Config.RAZORPAY_KEY_ID and Config.RAZORPAY_KEY_SECRET else None
