def test_complete_soil_flow(client, auth):
    field = client.post("/api/v1/fields", headers=auth, json={"name":"North plot","district":"Rajshahi","upazila":"Godagari","area_bigha":1.5}).json()
    response = client.post("/api/v1/soil-tests", headers=auth, json={"field_id":field["id"],"ph":5.2,"nitrogen":"low","phosphorus":"medium","potassium":"medium","texture":"loam","moisture":42})
    assert response.status_code == 201
    result = client.post(f"/api/v1/soil-tests/{response.json()['id']}/analyze", headers=auth)
    assert result.status_code == 201
    assert result.json()["requires_expert"] is True
    assert result.json()["model_version"] == "rules-v1"

def test_login_rejects_wrong_password(client):
    client.post("/api/v1/auth/register", json={"name":"Farmer","email":"f@example.com","password":"strongpass123"})
    response = client.post("/api/v1/auth/login", json={"email":"f@example.com","password":"wrongpass"})
    assert response.status_code == 401

def test_unauthorized_field_creation(client):
    response = client.post("/api/v1/fields", json={"name":"Plot","district":"Khulna","upazila":"Dumuria"})
    assert response.status_code == 401
