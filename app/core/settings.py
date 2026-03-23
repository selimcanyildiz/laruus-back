from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )

    # AWS S3
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "eu-central-1")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "")

    def validate(self):
        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set")
        if not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY is not set")

config = Config()
config.validate()
