from uuid import uuid4
from enum import Enum


class ChangeType(Enum):
	INCREASE = uuid4()
	DECREASE = uuid4()
	ADJUST = uuid4()
