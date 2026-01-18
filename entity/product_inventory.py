from value_object.unit import Unit, UnitConversion
from value_object.qty_change_type import ChangeType
from error import UnsupportedUnitError, UnsupportedChangeTypeError, InvalidQtyError


class ProductInventory(object):

	def __init__(self, sku: str, product_name: str, base_unit: Unit, qty:float = 0):
		self.sku = sku
		self.product_name = product_name
		self.base_unit = base_unit
		self._qty = qty or 0
		self._supported_units = [
			UnitConversion(unit=base_unit, conversion_factor=1),
		]
	
	
	def add_supported_unit(self, unit: Unit, conversion_factor: float):
		if conversion_factor < 0:
			raise ValueError(f"conversion_factor cannot be negative... you entered '{conversion_factor}'")
			
		self._supported_units.append(UnitConversion(unit = unit, conversion_factor = conversion_factor))
	
	
	def _get_unit_conv_OR_raise_err(self, unit: Unit):
		is_a_valid_unit = isinstance(unit, Unit)
		is_a_supported_unit = False
		
		#checking if unit is supported
		for unit_conversion in self._supported_units:
			if unit_conversion.unit == unit:
				is_a_supported_unit = True
				break
		
		#if this unit_not_okay variable is true, then the if-statement will execute... raising an error..
		#if unit is_a_valid_unit or is_a_supported_unit, then the unit_not_okay willbe false
		#leading to the error not being raise
		unit_not_okay = not (is_a_valid_unit and is_a_supported_unit)
		
		if unit_not_okay:
			raise UnsupportedUnitError(f"Unit ({unit}) Not supported by Product ({self.product_name})")
		
		unit_conversion = next((unit_conv for unit_conv in self._supported_units if unit_conv.unit == unit), None)
		
		if unit_conversion is None:
			raise UnsupportedUnitError(f"Unit ({unit}) Not supported by Product ({self.product_name})")
		
		return unit_conversion
	
	
	def _convert_to_base_unit(self, qty: float, from_unit: Unit):
		
		unit_conversion = self._get_unit_conv_OR_raise_err(from_unit)
		multiply_by = unit_conversion.conversion_factor
		
		return qty * multiply_by
	
	
	def _convert_from_base_unit(self, qty: float, to_unit: Unit):
		
		unit_conversion = self._get_unit_conv_OR_raise_err(to_unit)
		divide_by = unit_conversion.conversion_factor
		
		return qty / divide_by
		
	
	def get_qty(self, unit: Unit = None):
		
		if unit is None:
			unit = self.base_unit
		
		qty_in_base_unit = self._qty
		qty_in_their_unit = self._convert_from_base_unit(to_unit = unit, qty=qty_in_base_unit)
		
		return qty_in_their_unit
	
	
	
	def _check_change_type_OR_raise_err(self, change_type: ChangeType):
		is_a_valid_change_type = isinstance(change_type, ChangeType)
		
		if not is_a_valid_change_type:
			raise UnsupportedChangeTypeError()
	
	
	
	def change_qty(self, qty: float, change_type: ChangeType, unit:Unit = None):
		self._check_change_type_OR_raise_err(change_type)
		
		if qty < 0:
			raise InvalidQtyError(f"Tried to pass in negative Qty ({qty})")
		
		if unit is None:
			unit = self.base_unit
		
		qty_in_base_unit = self._convert_to_base_unit(from_unit = unit, qty = qty)
		
		if change_type == ChangeType.RECEIVE:
			self._qty = self._qty + qty_in_base_unit
		
		elif change_type == ChangeType.ISSUE:
			if (self._qty - qty_in_base_unit) < 0:
				raise InvalidQtyError("You can't issue more than the qty available")
			
			self._qty = self._qty - qty_in_base_unit
		
		elif change_type == ChangeType.ADJUST:
			self._qty = qty_in_base_unit
		
		else:
			raise UnsupportedChangeTypeError(f"unsupported value entered for change_type ({change_type})")
	
	


async def create_product_inventory(sku: str, product_name: str, base_unit: Unit, qty:float=0):
	return ProductInventory(qty=qty, sku=sku, product_name=product_name, base_unit=base_unit)
