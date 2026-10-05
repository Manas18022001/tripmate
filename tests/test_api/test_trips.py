def test_get_trips_empty(test_client):
    response = test_client.get("/api/trips/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_trip_not_found(test_client):
    response = test_client.get("/api/trips/999")
    assert response.status_code == 404

def test_delete_trip_not_found(test_client):
    response = test_client.delete("/api/trips/999")
    assert response.status_code == 404
