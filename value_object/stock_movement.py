from dataclasses import dataclass
from datetime import datetime
from value_object.unit import Unit


@dataclass(frozen=True)
class StockMovement:
	timestamp: datetime
	location: str #where/who was the product concerned, received from or supplied to
	received: float | None
	issued: float | None
	unit: Unit | None #unit used in receiving/issuing. Nullable in case of opening bal where there is neither received/issued qty
	bal: float
	base_unit: Unit
