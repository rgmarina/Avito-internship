import pytest
import requests
import random

class TestAvitoAPI:
    BASE_URL = "https://qa-internship.avito.com"

    def generate_seller_id(self):
        return random.randint(111111, 999999)

    def get_valid_item_data(self, seller_id=None):
        if seller_id is None:
            seller_id = self.generate_seller_id()
        return {
            "sellerID": seller_id,
            "name": f"Test Item {random.randint(1000, 9999)}",
            "price": random.randint(100, 10000),
            "statistics": {
                "likes": random.randint(0, 100),
                "viewCount": random.randint(0, 1000),
                "contacts": random.randint(0, 50)
            }
        }

    def setup_method(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.created_items = []

    def teardown_method(self):
        for item_id in self.created_items:
            try:
                self.session.delete(f"{self.BASE_URL}/api/2/item/{item_id}")
            except:
                pass

    def test_tc001_create_item_success(self):
        """TC001: Создание объявления с валидными данными."""
        item_data = self.get_valid_item_data()

        response = self.session.post(
            f"{self.BASE_URL}/api/1/item",
            json=item_data
        )

        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        response_data = response.json()

        assert 'id' in response_data, "В ответе отсутствует поле id"
        assert response_data['sellerId'] == item_data['sellerID'], "sellerId не совпадает"
        assert response_data['name'] == item_data['name'], "name не совпадает"
        assert response_data['price'] == item_data['price'], "price не совпадает"
        assert 'createdAt' in response_data, "В ответе отсутствует поле createdAt"

        self.created_items.append(response_data['id'])
        print(f"Создано объявление с ID: {response_data['id']}")

    def test_tc002_create_item_minimal_data(self):
        """TC002: Создание объявления только с обязательными полями."""
        minimal_data = {
            "sellerID": self.generate_seller_id(),
            "name": "Minimal Item",
            "price": 500
        }

        response = self.session.post(
            f"{self.BASE_URL}/api/1/item",
            json=minimal_data
        )

        if response.status_code == 200:
            response_data = response.json()
            assert 'id' in response_data
            self.created_items.append(response_data['id'])

    def test_tc003_create_item_missing_required_fields(self):
        """TC003: Создание объявления без обязательных полей."""
        invalid_data = {
            "name": "Test Item",
            "price": 1000
        }

        response = self.session.post(
            f"{self.BASE_URL}/api/1/item",
            json=invalid_data
        )

        assert response.status_code in [400, 422], f"Ожидалась ошибка 400/422, получен {response.status_code}"

    def test_tc004_create_item_invalid_data_types(self):
        """TC004: Создание объявления с невалидным типом данных."""
        invalid_data = {
            "sellerID": "not_a_number",
            "name": "Test Item",
            "price": 1000,
            "statistics": {
                "likes": "should_be_number",
                "viewCount": 100,
                "contacts": 5
            }
        }

        response = self.session.post(
            f"{self.BASE_URL}/api/1/item",
            json=invalid_data
        )

        assert response.status_code in [400, 422], f"Ожидалась ошибка 400/422, получен {response.status_code}"

    def test_tc005_create_item_negative_price(self):
        """TC005: Создание объявления с отрицательной ценой."""
        item_data = self.get_valid_item_data()
        item_data["price"] = -100

        response = self.session.post(
            f"{self.BASE_URL}/api/1/item",
            json=item_data
        )

        if response.status_code == 200:
            print("API принимает отрицательные цены - возможный баг")
        elif response.status_code in [400, 422]:
            print("API корректно отвергает отрицательные цены")


    def test_tc006_get_existing_item(self):
        """TC006: Получение существующего объявления."""
        item_data = self.get_valid_item_data()
        create_response = self.session.post(f"{self.BASE_URL}/api/1/item", json=item_data)
        assert create_response.status_code == 200
        item_id = create_response.json()['id']
        self.created_items.append(item_id)

        response = self.session.get(f"{self.BASE_URL}/api/1/item/{item_id}")

        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        items_list = response.json()

        assert isinstance(items_list, list), "Ответ должен быть списком"
        assert len(items_list) > 0, "Список объявлений не должен быть пустым"

        item = items_list[0]
        assert item['id'] == item_id, "ID объявления не совпадает"
        assert item['name'] == item_data['name'], "Название не совпадает"

    def test_tc007_get_nonexistent_item(self):
        """TC007: Получение несуществующего объявления."""
        nonexistent_id = "nonexistent_id_12345"

        response = self.session.get(f"{self.BASE_URL}/api/1/item/{nonexistent_id}")

        assert response.status_code == 404, f"Ожидалась ошибка 404, получен {response.status_code}"

    def test_tc008_get_item_invalid_id_format(self):
        """TC008: Получение с не верным ID."""
        invalid_id = "invalid@id!format"

        response = self.session.get(f"{self.BASE_URL}/api/1/item/{invalid_id}")

        assert response.status_code in [400, 404], f"Ожидалась ошибка 400/404, получен {response.status_code}"


    def test_tc009_get_seller_items_existing_seller(self):
        """TC009: Получение объявлений существующего продавца."""
        seller_id = self.generate_seller_id()

        for i in range(2):
            item_data = self.get_valid_item_data(seller_id)
            item_data["name"] = f"Seller Item {i + 1}"
            create_response = self.session.post(f"{self.BASE_URL}/api/1/item", json=item_data)
            if create_response.status_code == 200:
                self.created_items.append(create_response.json()['id'])

        response = self.session.get(f"{self.BASE_URL}/api/1/{seller_id}/item")

        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        seller_items = response.json()

        assert isinstance(seller_items, list), "Ответ должен быть списком"

    def test_tc010_get_seller_without_items(self):
        """TC010: Получение объявлений продавца без объявлений."""
        new_seller_id = self.generate_seller_id()

        response = self.session.get(f"{self.BASE_URL}/api/1/{new_seller_id}/item")

        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        seller_items = response.json()

        assert isinstance(seller_items, list), "Ответ должен быть списком"

    def test_tc011_get_seller_invalid_id(self):
        """TC011: Получение данных по не верному sellerID."""
        invalid_seller_id = "invalid_seller"

        response = self.session.get(f"{self.BASE_URL}/api/1/{invalid_seller_id}/item")

        assert response.status_code in [400, 404], f"Ожидалась ошибка 400/404, получен {response.status_code}"


    def test_tc012_get_existing_item_statistics(self):
        """TC012: Получение статистики существующего объявления."""
        item_data = self.get_valid_item_data()
        create_response = self.session.post(f"{self.BASE_URL}/api/1/item", json=item_data)

        if create_response.status_code == 200:
            item_id = create_response.json()['id']
            self.created_items.append(item_id)

            response = self.session.get(f"{self.BASE_URL}/api/1/statistic/{item_id}")

            if response.status_code == 200:
                stats_data = response.json()
                assert isinstance(stats_data, list), "Статистика должна быть списком"
                if len(stats_data) > 0:
                    stat_item = stats_data[0]
                    assert 'likes' in stat_item
                    assert 'viewCount' in stat_item
                    assert 'contacts' in stat_item
            elif response.status_code == 404:
                print("Статистика для объявления не найдена")

    def test_tc013_get_nonexistent_item_statistics(self):
        """TC013: Получение статистики несуществующего объявления."""
        nonexistent_id = "nonexistent_stat_id_123"

        response = self.session.get(f"{self.BASE_URL}/api/1/statistic/{nonexistent_id}")

        assert response.status_code == 404, f"Ожидалась ошибка 404, получен {response.status_code}"


    def test_tc014_full_cycle_create_get_verify(self):
        """TC014: Полный цикл: создание -> получение -> проверка данных."""
        original_data = self.get_valid_item_data()
        create_response = self.session.post(f"{self.BASE_URL}/api/1/item", json=original_data)
        assert create_response.status_code == 200
        created_item = create_response.json()
        item_id = created_item['id']
        self.created_items.append(item_id)

        get_response = self.session.get(f"{self.BASE_URL}/api/1/item/{item_id}")
        assert get_response.status_code == 200
        retrieved_items = get_response.json()

        assert len(retrieved_items) > 0, "Не найдено созданное объявление"
        retrieved_item = retrieved_items[0]

        assert retrieved_item['id'] == item_id
        assert retrieved_item['sellerId'] == original_data['sellerID']
        assert retrieved_item['name'] == original_data['name']
        assert retrieved_item['price'] == original_data['price']

    def test_tc015_multiple_items_same_seller_integration(self):
        """TC015: Создание нескольких объявлений одного продавца -> проверка списка"""
        seller_id = self.generate_seller_id()
        created_ids = []

        for i in range(3):
            item_data = self.get_valid_item_data(seller_id)
            item_data["name"] = f"Integration Test Item {i + 1}"
            create_response = self.session.post(f"{self.BASE_URL}/api/1/item", json=item_data)

            if create_response.status_code == 200:
                item_id = create_response.json()['id']
                created_ids.append(item_id)
                self.created_items.append(item_id)

        response = self.session.get(f"{self.BASE_URL}/api/1/{seller_id}/item")
        assert response.status_code == 200

        seller_items = response.json()
        assert isinstance(seller_items, list)

        seller_item_ids = [item['id'] for item in seller_items]
        for created_id in created_ids:
            assert created_id in seller_item_ids, f"Созданное объявление {created_id} не найдено в списке продавца"

    def test_tc016_seller_id_boundary_values(self):
        """TC016: Проверка граничных значений для sellerID."""
        boundary_cases = [
            111110,
            111111,
            555555,
            999999,
            1000000
        ]

        for seller_id in boundary_cases:
            item_data = self.get_valid_item_data()
            item_data["sellerID"] = seller_id

            response = self.session.post(f"{self.BASE_URL}/api/1/item", json=item_data)

            if seller_id in [111111, 555555, 999999]:
                if response.status_code == 200:
                    item_id = response.json()['id']
                    self.created_items.append(item_id)
            else:
                if response.status_code == 200:
                    print(f"Возможный баг: API принял sellerID {seller_id} за пределами диапазона")
                    item_id = response.json()['id']
                    self.created_items.append(item_id)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])