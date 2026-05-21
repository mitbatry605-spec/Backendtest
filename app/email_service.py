import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# ============================================
# 📧 GMAIL SMTP CONFIGURATION
# ============================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "mitbatry605@gmail.com"        # Your Gmail
SMTP_PASSWORD = "dogy gbpb scjf wmht"          # Your 16-digit App Password
FROM_EMAIL = "mitbatry605@gmail.com"           # Your Gmail
# ============================================

def generate_verification_code():
    """Generate 6-digit verification code"""
    return str(random.randint(100000, 999999))

def send_verification_email(to_email, code):
    """Send verification code via email automatically"""
    try:
        print(f"\n{'='*60}")
        print(f"📧 Sending verification email to: {to_email}")
        print(f"🔐 Verification code: {code}")
        print(f"{'='*60}\n")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = "🔐 Email Verification - E.Shop"
        
        # Email body with HTML
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; padding: 0; margin: 0; background-color: #f4f4f4;">
            <div style="max-width: 550px; margin: 40px auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
                
                <!-- Header with Gradient -->
                <div style="background: linear-gradient(135deg, #004d2c 0%, #00a86b 100%); padding: 35px 20px; text-align: center;">
                    <div style="font-size: 50px; margin-bottom: 10px;">🛍️</div>
                    <h1 style="color: white; margin: 0; font-size: 28px; font-weight: bold;">E.Shop</h1>
                    <p style="color: #a5d6a7; margin: 10px 0 0;">Your Trusted Online Store</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 35px 30px;">
                    <h2 style="color: #333; margin-top: 0; font-size: 24px;">Email Verification</h2>
                    <p style="color: #666; line-height: 1.6; font-size: 16px;">Hello,</p>
                    <p style="color: #666; line-height: 1.6; font-size: 16px;">Thank you for signing up with <strong>E.Shop</strong>! Please use the verification code below to complete your registration:</p>
                    
                    <!-- Code Box -->
                    <div style="background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%); border-radius: 15px; padding: 25px; text-align: center; margin: 30px 0; border: 2px dashed #004d2c;">
                        <div style="font-size: 48px; font-weight: bold; letter-spacing: 10px; color: #004d2c; font-family: monospace;">{code}</div>
                        <p style="color: #999; font-size: 13px; margin: 15px 0 0;">⏰ This code will expire in <strong>10 minutes</strong></p>
                    </div>
                    
                    <p style="color: #666; line-height: 1.6;">If you didn't create an account with E.Shop, please ignore this email.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0 20px;">
                    
                    <p style="color: #999; font-size: 12px; text-align: center; line-height: 1.5;">
                        This is an automated message, please do not reply.<br>
                        &copy; 2026 E.Shop. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to Gmail SMTP server
        print("📡 Connecting to Gmail SMTP server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        
        print(f"🔐 Logging in as: {SMTP_USERNAME}")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        print("📤 Sending email...")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}!")
        print(f"📧 Please check your inbox or SPAM folder.\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Email sending failed!")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify SMTP_USERNAME is correct")
        print("3. Verify SMTP_PASSWORD is correct (16-digit app password)")
        print("4. Make sure 2FA is enabled on your Gmail")
        print("5. Check your SPAM folder if email was sent\n")
        return False

def send_verification_sms(phone_number, code):
    """Send verification code via SMS (optional - for future use)"""
    print(f"📱 SMS to {phone_number}: Your verification code is {code}")
    return True