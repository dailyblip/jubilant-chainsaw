from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['ok'] is True


def test_state_mock():
    r = client.get('/api/state')
    assert r.status_code == 200
    data = r.json()
    assert len(data['devices']) == 9


def test_normal_scene():
    r = client.post('/api/scenes', json={'scene':'normal'})
    assert r.status_code == 200
    assert r.json()['mode'] == 'normal'
