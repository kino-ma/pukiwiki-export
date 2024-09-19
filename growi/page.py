from growi.date import epoch_iso
from growi.id import Id


class Page:
    def __init__(
        self,
        path: str,
        revisionId: Id | None = None,
        id: Id | None = None,
        createdAt: str = epoch_iso(),
        updatedAt: str = epoch_iso(),
    ):
        if not path.startswith("/"):
            path = f"/{path}"
        self.path = path

        self.revisionId = revisionId
        self.id = id or Id()

        self.createdAt = createdAt
        self.updatedAt = updatedAt

    def json(self):
        data = {
            "parent": None,
            "descendantCount": 0,
            "isEmpty": False,
            "status": "published",
            "grant": 1,
            "grantedUsers": [],
            "liker": [],
            "seenUsers": [],
            "commentCount": 0,
            "grantedGroup": None,
            "__v": 0,
        }

        data["_id"] = str(self.id)
        data["revision"] = str(self.revisionId)
        data["path"] = self.path
        data["createdAt"] = self.createdAt
        data["updatedAt"] = self.updatedAt

        return data
