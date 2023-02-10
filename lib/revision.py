from datetime import datetime

from .id import Id


class Revision:
    def __init__(
        self,
        pageId: Id,
        body: str,
        id: Id = Id(),
        format: str = "markdown",
        createdAt: str = datetime.now().isoformat(),
    ):
        self.id = id
        self.pageId = pageId
        self.body = body
        self.format = format
        self.createdAt = createdAt

    def json(self):
        data = {
            "__v": 0,
        }

        data["_id"] = str(self.id)
        data["format"] = str(self.format)
        data["createdAt"] = self.createdAt
        data["pageId"] = str(self.pageId)
        data["body"] = self.body

        return data
