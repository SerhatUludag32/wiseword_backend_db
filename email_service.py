import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.getenv("GMAIL_EMAIL")
        self.password = os.getenv("GMAIL_APP_PASSWORD")  # App-specific password
    
    def send_verification_email(self, to_email: str, verification_code: str):
        """Send verification email with 6-digit code"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Wise Words <{self.email}>"
            msg['To'] = to_email
            msg['Subject'] = "Wise Words - Email Verification Code"
            msg['Reply-To'] = self.email
            msg['X-Mailer'] = "Wise Words App"
            
            # Email body with verification code
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #333;">Welcome to Wise Words! 🧠</h2>
                    
                    <p>Thank you for registering! Please verify your email address by entering this 6-digit code:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background-color: #f5f5f5; border: 2px dashed #4CAF50; 
                                    border-radius: 8px; padding: 20px; display: inline-block;">
                            <span style="font-size: 32px; font-weight: bold; color: #4CAF50; 
                                         letter-spacing: 5px; font-family: monospace;">
                                {verification_code}
                            </span>
                        </div>
                    </div>
                    
                    <p style="text-align: center; color: #666;">
                        Enter this code in the verification form to complete your registration.
                    </p>
                    
                    <p style="margin-top: 30px; color: #888; font-size: 12px;">
                        ⏰ This verification code will expire in 15 minutes for security.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        You're receiving this email because you registered for Wise Words. 
                        If you didn't register, please ignore this email.
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_body = f"""
Welcome to Wise Words!

Thank you for registering! Please verify your email address by entering this 6-digit code:

{verification_code}

Enter this code in the verification form to complete your registration.

This verification code will expire in 15 minutes for security.

If you didn't register for Wise Words, please ignore this email.
            """
            
            # Attach both plain text and HTML versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to Gmail SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable encryption
            server.login(self.email, self.password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            print(f"✅ Verification code email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, nickname: str):
        """Send welcome email after successful verification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = "Welcome to Wise Words! Start Chatting with History"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #333;">🎉 Welcome to Wise Words, {nickname}!</h2>
                    
                    <p>Your email has been verified successfully! You can now:</p>
                    
                    <ul style="line-height: 1.6;">
                        <li>🧠 Chat with <strong>Albert Einstein</strong> about relativity and physics</li>
                        <li>🍎 Discuss gravity and mathematics with <strong>Isaac Newton</strong></li>
                        <li>🎨 Explore art and inventions with <strong>Leonardo da Vinci</strong></li>
                        <li>⚛️ Learn about radioactivity from <strong>Marie Curie</strong></li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://127.0.0.1:8000/docs" 
                           style="background-color: #2196F3; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 4px; display: inline-block;">
                            Start Chatting Now!
                        </a>
                    </div>
                    
                    <p style="color: #666;">
                        Visit our API documentation to explore all features and start your conversations with history's greatest minds!
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            
            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()
            
            print(f"✅ Welcome email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send welcome email: {str(e)}")
            return False

# Global instance
email_service = EmailService() 