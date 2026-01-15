import pytest

from entity.product_inventory import create_product_inventory
from value_object.unit import Unit
from value_object.qty_change_type import ChangeType
from error import UnsupportedUnitError, UnsupportedChangeTypeError, InvalidQtyError


kg_to_bskt = 3.6
kg_to_bag = 50

@pytest.fixture
def sample_product_inventory():
	sample_product_inventory = create_product_inventory(sku="test_rice", product_name="Rice (test)", base_unit=Unit.KG)
	sample_product_inventory.add_supported_unit(unit=Unit.BAG, multiply_by = kg_to_bag)
	sample_product_inventory.add_supported_unit(unit=Unit.BSKT, multiply_by = kg_to_bskt)

	return sample_product_inventory


def test_qty_change(sample_product_inventory):
	assert sample_product_inventory.get_qty() == 0
	new_qty = 20
	sample_product_inventory.change_qty(qty=new_qty, change_type=ChangeType.INCREASE)
	assert sample_product_inventory.get_qty() == pytest.approx(new_qty)
	reduce_by = 5
	sample_product_inventory.change_qty(qty=reduce_by, change_type=ChangeType.DECREASE)
	assert sample_product_inventory.get_qty() == pytest.approx(new_qty - reduce_by)
	new_qty = sample_product_inventory.get_qty()
	increase_by = 10
	sample_product_inventory.change_qty(qty=increase_by, change_type=ChangeType.INCREASE)
	assert sample_product_inventory.get_qty() == pytest.approx(new_qty + increase_by)


def test_unit_conversion(sample_product_inventory):
	assert sample_product_inventory.get_qty(unit=Unit.BAG) == 0
	new_value_in_kg = 100
	new_value_in_bags = 2
	sample_product_inventory.change_qty(qty=new_value_in_bags, unit=Unit.BAG, change_type=ChangeType.INCREASE)
	assert  sample_product_inventory.get_qty(unit=Unit.KG) == pytest.approx(new_value_in_kg)
	expected_value_in_bskts = new_value_in_kg / kg_to_bskt
	assert sample_product_inventory.get_qty(unit=Unit.BSKT) == pytest.approx(expected_value_in_bskts)
	new_value_in_kg = sample_product_inventory.get_qty()
	reduce_by_bskts = 3
	sample_product_inventory.change_qty(qty=reduce_by_bskts, unit=Unit.BSKT, change_type=ChangeType.DECREASE)
	expected_value_in_kg = new_value_in_kg - (reduce_by_bskts * kg_to_bskt)
	expected_value_in_bag = expected_value_in_kg / kg_to_bag
	assert sample_product_inventory.get_qty() == pytest.approx(expected_value_in_kg)
	assert sample_product_inventory.get_qty(unit=Unit.BAG) == pytest.approx(expected_value_in_bag)


def test_tiny_values(sample_product_inventory):
	assert sample_product_inventory.get_qty() == 0
	new_value_in_kg = 0.0003
	new_value_in_bags = new_value_in_kg / kg_to_bag
	sample_product_inventory.change_qty(qty=new_value_in_bags, unit=Unit.BAG, change_type=ChangeType.INCREASE)
	assert sample_product_inventory.get_qty(unit=Unit.KG) == pytest.approx(new_value_in_kg)
	expected_value_in_bskts = new_value_in_kg / kg_to_bskt
	assert sample_product_inventory.get_qty(unit=Unit.BSKT) == pytest.approx(expected_value_in_bskts)
	new_value_in_kg = sample_product_inventory.get_qty()
	reduce_by_kg = 0.00009
	sample_product_inventory.change_qty(qty=reduce_by_kg, unit=Unit.KG, change_type=ChangeType.DECREASE)
	expected_value_in_kg = new_value_in_kg - reduce_by_kg
	expected_value_in_bag = expected_value_in_kg / kg_to_bag
	assert sample_product_inventory.get_qty() == pytest.approx(expected_value_in_kg)
	assert sample_product_inventory.get_qty(unit=Unit.BAG) == pytest.approx(expected_value_in_bag)



def test_qty_adjust(sample_product_inventory):
	assert sample_product_inventory.get_qty() == 0
	sample_product_inventory.change_qty(qty=2, unit=Unit.BSKT, change_type=ChangeType.ADJUST)
	new_value_in_bags = 2
	sample_product_inventory.change_qty(qty=new_value_in_bags, unit=Unit.BAG, change_type=ChangeType.ADJUST)
	expected_value_in_kg = new_value_in_bags * kg_to_bag
	assert sample_product_inventory.get_qty() == pytest.approx(expected_value_in_kg)


def test_unsupported_stuff_unsupported(sample_product_inventory):
	assert sample_product_inventory.get_qty() == 0
	with pytest.raises(UnsupportedUnitError):
		sample_product_inventory.change_qty(qty=10, unit=3, change_type=ChangeType.ADJUST)
	
	with pytest.raises(UnsupportedChangeTypeError):
		sample_product_inventory.change_qty(qty=10, change_type="fifty")


def test_qty_limits(sample_product_inventory):	
	with pytest.raises(InvalidQtyError):
		sample_product_inventory.change_qty(qty=50, unit=Unit.BAG, change_type = ChangeType.DECREASE)

	with pytest.raises(InvalidQtyError):
		sample_product_inventory.change_qty(qty=-50, unit=Unit.BAG, change_type = ChangeType.INCREASE)

	with pytest.raises(InvalidQtyError):
		sample_product_inventory.change_qty(qty=-50, unit=Unit.BAG, change_type = ChangeType.DECREASE)
