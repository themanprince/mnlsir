import pytest
import pytest_asyncio
from aggregrate.store import create_store
from value_object.unit import Unit
from error import AlreadyExistingProduct


@pytest.mark.asyncio
async def test_multiple_entrance_of_same_sku_causes_error():
	store = await create_store(store_id="test_store", store_name="Store (test)")
	product_sku = "test_rice"

	with pytest.raises(AlreadyExistingProduct):
		await store.create_product_inventory(sku=product_sku, product_name="Rice (test)", base_unit=Unit.KG)
		await store.create_product_inventory(sku=product_sku, product_name="Rice (test)", base_unit=Unit.KG)
	