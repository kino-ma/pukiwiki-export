import random


ID_BITS = 94
ID_MAX = (0b1 << ID_BITS) - 1
ID_MIN = 0b1 << (ID_BITS - 1)


class Id():
    def __init__(self,
                 min: int = ID_MIN,
                 max: int = ID_MAX,
                 intId: int | None = None):
        if not intId:
            intId = random.randint(min, max)

        self.intId = intId

    def __str__(self):
        return f"{self.intId:x}"

    def __repr__(self) -> str:
        return self.__str__()
