import pytest
import pytest_asyncio

from datetime import datetime
from aggregrate.store import create_store
from value_object.unit import Unit
from error import UnsupportedUnitError, InvalidQtyError



kg_to_bskt = 2.451
kg_to_bag = 50
tins_to_ctn = 24

product1_sku = "test_rice"
product2_sku = "test_coconut_milk"


@pytest_asyncio.fixture
async def sample_store():
	store = await create_store(store_id="test_store", store_name="Store (test)")
	await store.create_product_inventory(sku=product1_sku, product_name="Rice (test)", base_unit=Unit.KG)
	store.add_supported_unit(sku=product1_sku, unit=Unit.BAG, conversion_factor = kg_to_bag)
	store.add_supported_unit(sku=product1_sku, unit=Unit.BSKT, conversion_factor = kg_to_bskt)

	await store.create_product_inventory(sku=product2_sku, product_name="Coconut Milk (test)", base_unit=Unit.TIN)
	store.add_supported_unit(sku=product2_sku, unit=Unit.CTN, conversion_factor = tins_to_ctn)

	return store


@pytest.mark.asyncio
async def test_store_receiving(sample_store):
	
	qty_to_receive_product1 = 2
	qty_to_receive_product2 = 3
	
	await sample_store.receive({
		"received_entry_id": "test_receive",
	    "created_at": str(datetime.now()),
	    "received_at": str(datetime.now()),
	    "received_from": "RD Enterprises",
	    "received_by": "Prince Adigwe",
	    "purpose": None,
	    "store_id": sample_store.store_id,
	    "received_products": [
			{
				"sku": product1_sku,
				"qty": qty_to_receive_product1,
				"unit": Unit.BSKT
			},
			{
				"sku": product2_sku,
				"qty": qty_to_receive_product2,
				"unit": Unit.CTN
			}
		]
	})
	
	expected_base_unit_qty_product1 = kg_to_bskt * qty_to_receive_product1
	expected_base_unit_qty_product2 = tins_to_ctn * qty_to_receive_product2
	
	store_inventory_snapshot = await sample_store.get_inventory_snapshot()

	assert store_inventory_snapshot[product1_sku]["qty"] == expected_base_unit_qty_product1
	assert store_inventory_snapshot[product1_sku]["unit"] == Unit.KG

	assert store_inventory_snapshot[product2_sku]["qty"] == expected_base_unit_qty_product2
	assert store_inventory_snapshot[product2_sku]["unit"] == Unit.TIN
	
	
	expected_qty_in_bags_product1 = expected_base_unit_qty_product1 / kg_to_bag
	actual_qty_in_bags_product1 = await sample_store.get_stock_level(sku=product1_sku, unit=Unit.BAG)
	assert actual_qty_in_bags_product1 == pytest.approx(expected_qty_in_bags_product1)
	
	
@pytest.mark.asyncio
async def test_receive_fails_on_invalid_unit(sample_store):
	with pytest.raises(UnsupportedUnitError):
		await sample_store.receive({
		"received_entry_id": "test_receive",
	    "created_at": str(datetime.now()),
	    "received_at": str(datetime.now()),
	    "received_from": "RD Enterprises",
	    "received_by": "Prince Adigwe",
	    "purpose": None,
	    "store_id": sample_store.store_id,
	    "received_products": [
			{
				"sku": product1_sku,
				"qty": 10,
				"unit": Unit.CTN #invalid unit for product1
			},
			{
				"sku": product2_sku,
				"qty": 212,
				"unit": Unit.BSKT  #invalid unit for product2
			}
		]
	})
			

@pytest.mark.asyncio
async def test_receive_fails_on_negative_qty(sample_store):
	with pytest.raises(InvalidQtyError):	
		await sample_store.receive({
			"received_entry_id": "test_receive",
		    "created_at": str(datetime.now()),
		    "received_at": str(datetime.now()),
		    "received_from": "RD Enterprises",
		    "received_by": "Prince Adigwe",
		    "purpose": None,
		    "store_id": sample_store.store_id,
		    "received_products": [
				{
					"sku": product1_sku,
					"qty": -10,
					"unit": Unit.BSKT
				}
			]
		})
			
@pytest.mark.asyncio
async def test_fails_on_invalid_store_id(sample_store):
	with pytest.raises(ValueError):
		await sample_store.receive({
		    "store_id": "random",
			"received_entry_id": "test_receive",
		    "created_at": str(datetime.now()),
		    "received_at": str(datetime.now()),
		    "received_from": "RD Enterprises",
		    "received_by": "Prince Adigwe",
		    "purpose": None,
		    "received_products": [
				{
					"sku": product1_sku,
					"qty": 2,
					"unit": Unit.BSKT
				},
				{
					"sku": product2_sku,
					"qty": 4,
					"unit": Unit.CTN
				}
			]
		})


@pytest.mark.asyncio
async def test_receiving_works_wthout_specifying_store_id(sample_store):
	qty_to_receive_product1 = 3
	
	await sample_store.receive({
		"received_entry_id": "test_receive",
	    "created_at": str(datetime.now()),
	    "received_at": str(datetime.now()),
	    "received_from": "RD Enterprises",
	    "received_by": "Prince Adigwe",
	    "purpose": None,
	    "store_id": sample_store.store_id,
	    "received_products": [
			{
				"sku": product1_sku,
				"qty": qty_to_receive_product1,
				"unit": Unit.BSKT
			}
		]
	})

	expected_base_unit_qty_product1 = kg_to_bskt * qty_to_receive_product1
	expected_qty_in_bags_product1 = expected_base_unit_qty_product1 / kg_to_bag
	actual_qty_in_bags_product1 = await sample_store.get_stock_level(sku=product1_sku, unit=Unit.BAG)
	assert actual_qty_in_bags_product1 == pytest.approx(expected_qty_in_bags_product1)
