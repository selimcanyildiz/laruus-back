import boto3
import random
from app.core.settings import config

SES_SENDER = "selimcantemp@gmail.com"


def generate_code() -> str:
    return str(random.randint(100000, 999999))


def send_verification_email(to_email: str, code: str):
    ses = boto3.client(
        "ses",
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_REGION,
    )

    ses.send_email(
        Source=SES_SENDER,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": "LARUUS - Verify Your Email", "Charset": "UTF-8"},
            "Body": {
                "Html": {
                    "Data": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px;">
                        <h1 style="font-size: 24px; margin-bottom: 8px;">LARUUS</h1>
                        <p style="color: #666; margin-bottom: 32px;">Verify your email address</p>
                        <div style="background: #f5f5f5; border-radius: 12px; padding: 32px; text-align: center; margin-bottom: 24px;">
                            <p style="color: #666; font-size: 14px; margin-bottom: 12px;">Your verification code:</p>
                            <h2 style="font-size: 36px; letter-spacing: 8px; margin: 0; color: #000;">{code}</h2>
                        </div>
                        <p style="color: #999; font-size: 12px;">This code expires in 10 minutes. If you didn't create an account, please ignore this email.</p>
                    </div>
                    """,
                    "Charset": "UTF-8",
                },
            },
        },
    )
