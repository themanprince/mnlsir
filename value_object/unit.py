from uuid import uuid4
from enum import Enum
from dataclasses import dataclass


class Unit(Enum):
	BSKT = uuid4()
	BAG = uuid4()
	KG = uuid4()
	CTN = uuid4()
	PCS = uuid4()
	BTL = uuid4()
	PKT = uuid4()
	TUBER = uuid4()
	BUNCH = uuid4()
	TIN = uuid4()


@dataclass(frozen=True)
class UnitConversion:
	unit: Unit
	conversion_factor: float