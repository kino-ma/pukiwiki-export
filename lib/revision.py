from .date import epoch_iso
from .id import Id


class Revision:
    def __init__(
        self,
        pageId: Id,
        body: str,
        authorId: Id,
        id: Id | None = None,
        format: str = "markdown",
        createdAt: str | None = None,
    ):
        self.id = id or Id()
        self.pageId = pageId
        self.body = body
        self.authorId = authorId
        self.format = format

        if createdAt is None:
            createdAt = epoch_iso()
        self.createdAt = createdAt

    def json(self):
        data = {
            "__v": 0,
        }

        data["_id"] = str(self.id)
        data["format"] = str(self.format)
        data["createdAt"] = self.createdAt
        data["pageId"] = str(self.pageId)
        data["author"] = str(self.authorId)
        data["body"] = self.body

        return data
