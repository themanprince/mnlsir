from uuid import uuid4
from enum import Enum


class ChangeType(Enum):
	RECEIVE = uuid4()
	ISSUE = uuid4()
	ADJUST = uuid4()
