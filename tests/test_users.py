from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class TestUserRoutes:
    def test_create_user(self, db_session):
        data = {"username": "newuser", "password": "password123", "balance": 100.0}
        response = client.post("/api/v1/users/create", json=data)
        assert response.status_code == 200
        assert response.json() == {"message": "User created successfully"}

    def test_create_existing_user(self, db_session):
        data = {"username": "existinguser", "password": "password123", "balance": 50.0}
        client.post("/api/v1/users/create", json=data)

        response = client.post("/api/v1/users/create", json=data)
        assert response.status_code == 409

    def test_login_user(self, db_session):
        data = {"username": "user1", "password": "password123", "balance": 50.0}
        client.post("/api/v1/users/create", json=data)

        response = client.post("/api/v1/users/login", json=data)
        assert response.status_code == 200
        token_data = response.json()["data"]
        assert "access_token" in token_data

    def test_login_user_with_wrong_creds(self, db_session):
        data = {"username": "user1", "password": "password123", "balance": 50.0}

        response = client.post("/api/v1/users/login", json=data)
        assert response.status_code == 400

    def test_get_user_data(self, db_session):
        data = {"username": "user2", "password": "password123", "balance": 200.0}
        client.post("/api/v1/users/create", json=data)

        response = client.get("/api/v1/users/user2")
        assert response.status_code == 200
        user_data = response.json()["data"]
        assert user_data["username"] == "user2"
        assert "balance" in user_data

    def test_get_user_data_not_found(self, db_session):
        response = client.get("/api/v1/users/nonexistentuser")
        assert response.status_code == 404
