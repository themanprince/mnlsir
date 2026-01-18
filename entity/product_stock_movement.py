from datetime import datetime
from value_object.stock_movement import StockMovement
from value_object.unit import Unit
from value_object.qty_change_type import ChangeType
from error import InvalidQtyError



class ProductStockMovement:
	def __init__(self, sku, opening_bal: float, base_unit: Unit):
		self.sku = sku
		
		timestamp = datetime.now()
		date_str = str(timestamp).split(" ")[0]
		self._stock_movement = [
			StockMovement(
				timestamp = timestamp,
				location = f"Balance as at {date_str}",
				received = None,
				issued = None,
				unit = None,
				bal = opening_bal,
				base_unit = base_unit
			)
		]
	
	
	def record(self, location:str, qty: float, change_type: ChangeType, unit:Unit, bal: float, base_unit: Unit):
		if qty < 0:
			raise InvalidQtyError(f"Tried to pass in negative Qty ({qty})")
		
		self._stock_movement.append(
			StockMovement(
				timestamp = datetime.now(),
				location = location,
				received = qty if (change_type == ChangeType.RECEIVE) else None,
				issued = qty if (change_type == ChangeType.ISSUE) else None,
				unit = unit,
				bal = bal,
				base_unit = base_unit
			)
		)
	
	def get_snapshot(self):
		stock_movement = []
		for movement in self._stock_movement:
			stock_movement.append({
				"timestamp": movement.timestamp,
				"location": movement.location,
				"received": movement.received,
				"issued": movement.issued,
				"unit": movement.unit,
				"bal": movement.bal,
				"base_unit": movement.base_unit
			})
		
		return stock_movement