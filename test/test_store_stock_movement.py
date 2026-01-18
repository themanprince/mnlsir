import pytest
import pytest_asyncio

from datetime import datetime
from aggregrate.store import create_store
from value_object.unit import Unit
from error import UnsupportedUnitError, InvalidQtyError



product_sku = "test_rice"
opening_bal = 10
base_unit = Unit.KG
kg_to_bskt = 0.05
kg_to_bag = 50



@pytest_asyncio.fixture
async def sample_store():
	store = await create_store(store_id="test_store", store_name="Store (test)")
	await store.create_product_inventory(opening_bal=opening_bal, sku=product_sku, product_name="Rice (test)", base_unit=base_unit)
	store.add_supported_unit(sku=product_sku, unit=Unit.BAG, conversion_factor = kg_to_bag)
	store.add_supported_unit(sku=product_sku, unit=Unit.BSKT, conversion_factor = kg_to_bskt)

	return store


@pytest.mark.asyncio
async def test_opening_bal_of_inventory_greater_than_zero_is_recorded_in_stock_movement(sample_store):
	stock_movement_snapshot = await sample_store.get_product_stock_movement_snapshot(sku=product_sku)
	first_stock_movement = stock_movement_snapshot[0]
	assert first_stock_movement["location"].split(" ")[0].lower() == "balance"
	assert first_stock_movement["bal"] == opening_bal
	assert first_stock_movement["base_unit"] == base_unit


@pytest.mark.asyncio
async def test_received_in_same_unit_BUT_bal_in_base_unit(sample_store):
	qty_to_receive = 3
	unit = Unit.BSKT
	supplier = "RD Enterprises"
	
	await sample_store.receive({
		"received_entry_id": "test_receive",
	    "created_at": str(datetime.now()),
	    "received_at": str(datetime.now()),
	    "received_from": supplier,
	    "received_by": "Prince Adigwe",
	    "purpose": "For Usage, lol",
	    "store_id": sample_store.store_id,
	    "received_products": [
			{
				"sku": product_sku,
				"qty": qty_to_receive,
				"unit": unit
			}
		]
	})

	expected_base_unit_qty = opening_bal + (kg_to_bskt * qty_to_receive)
	
	stock_movement_snapshot = await sample_store.get_product_stock_movement_snapshot(sku=product_sku)
	
	latest_stock_movement = stock_movement_snapshot[-1]
	assert latest_stock_movement["location"].lower() == supplier.lower()
	assert latest_stock_movement["received"] == pytest.approx(qty_to_receive)
	assert latest_stock_movement["unit"] == unit
	assert latest_stock_movement["issued"] is None
	assert latest_stock_movement["bal"] == expected_base_unit_qty
	assert latest_stock_movement["base_unit"] == base_unit
