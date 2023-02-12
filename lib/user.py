from .id import Id
from .date import now_iso, epoch_iso
from .password import random_password, hash_password


class User:
    def __init(
        self,
        name: str,
        password_seed: str,
        raw_password: str = random_password(),
        username: str | None = None,
        email: str | None = None,
        isAdmin: bool = False,
        id: Id = Id(),
        createdAt: str = now_iso(),
    ):
        self.name = name

        hashed_password = hash_password(password_seed, raw_password)
        self.password = hashed_password

        self.username = username or self.name

        email = email or f"{self.name}@growi.example.com"
        self.email = email

        self.isAdmin = isAdmin
        self.id = id
        self.createdAt = createdAt

    def json(self):
        d = {
            "isGravatarEnabled": False,
            "isEmailPublished": True,
            "lang": "ja_JP",
            "status": 2,
            "isInvitationEmailSended": False,
            "__v": 0,
            "imageUrlCached": "/images/icons/user.svg",
            "lastLoginAt": epoch_iso(),
        }

        d["_id"] = self.id
        d["admin"] = self.isAdmin
        d["rceatedAt"] = self.createdAt
        d["name"] = self.name
        d["username"] = self.username
        d["email"] = self.email
        d["password"] = self.password

        return d
