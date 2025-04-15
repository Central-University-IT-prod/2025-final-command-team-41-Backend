from passlib.context import CryptContext

from src.modules.auth.domain.services import PasswordHasher

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


class ArgonPasswordHasher(PasswordHasher):
    async def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
