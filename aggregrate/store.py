feom typing import Dict
from uuid import uuid4
from value_object.unit import Unit
from entity.product_inventory import ProductInventory
from error import UnexistingProduct


class Store(object):
	def __init__(self, store_id: str, store_name: str):
		self.store_id = store_id
		self.store_name = store_name
		self._inventory_list = []
	
	
	def create_product_inventory(self, sku: str, product_name: str, base_unit: Unit):
		self._inventory_list.append(ProductInventory(qty=0, sku=sku, product_name=product_name, base_unit=base_unit))
	
	
	def _get_product_inventory_by_sku(self, sku: str):
		product_inventory = next((product_inventory for product_inventory in self._inventory_list if product_inventory.sku == sku), None)
		
		if product_inventory is None:
			raise UnexistingProduct(f"Product does not exist in this inventory with sku={sku}")
		
		return product_inventory
	
	
	def add_supported_unit(self, sku: str, unit: Unit, conversion_factor: float):
		product_inventory = self._get_product_inventory_by_sku(sku)
		product_inventory.add_supported_unit(unit = unit, conversion_factor = conversion_factor)
	
	
	def receive(self, received_entry: Dict):
		id_of_store_to_receive = received_entry["store_id"]
		if not id_of_store_to_receive == self.store_id:
			raise ValueError(f"Invalid Store ID entered? Tried to receive goods for Store with id ({id_of_store_to_receive}) into Store with id ({self.store_id})")
		
		for product in received_entry["received_products"]:
			product_inventory = self._get_product_inventory_by_sku(product["sku"])
			product_inventory.change_qty(qty=product["qty"], unit=product["unit"], change_type=ChangeType.RECEIVE)
	
	
	def get_inventory_snapshot(self):
		inventory_snapshot = {}
		
		for product_inventory in self._inventory_list:
			sku = product_inventory.sku
			base_unit = product_inventory.base_unit
			qty = product_inventory.get_qty()
			
			inventory_snapshot[sku] = {
				"unit": base_unit,
				"qty": qty
			}
		
		return inventory_snapshot
	
	
	def get_stock_level(self, sku: str, unit: Unit):
		product_inventory = self._get_product_inventory_by_sku(sku)
		return product_inventory.get_qty(unit=unit)



async def create_store(store_id:str=uuid4(), store_name:str):
	return Store(store_id = store_id, store_name = store_name)