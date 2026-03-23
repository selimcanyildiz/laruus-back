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

    def validate(self):
        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set")
        if not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY is not set")

config = Config()
config.validate()
