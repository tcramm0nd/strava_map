import pytest
from strava_map import ActivityDB
import glob

data = [{'name': 'Afternoon Run', 'type': 'Run', 'date': '2021-02-11', 'coordinates': [[40.48681, -79.97101], [40.48686, -79.97073], [40.48685, -79.97048]]},
         {'name': 'Afternoon Ride', 'type': 'Ride', 'date': '2021-02-12', 'coordinates': [[40.46681, -79.97301], [40.4886, -79.9073], [40.124, -79.049]]}]
@pytest.fixture
def example_activities():
    return ActivityDB(data=data)

def test_empty_db():
    assert ActivityDB()._data.empty

def test_activity_save(example_activities):
    example_activities.save(path='tests/')
    assert glob.glob('tests/*_strava_activities.json')

def test_activity_load(example_activities):
    assert str(ActivityDB(filename='tests/example.json').data.columns) == str(example_activities.data.columns)

@pytest.fixture
def strava_client_info():
    return {'client_id': 45784,
            'client_secret':''}
# def test_fetch_activities(monkeypatch):
#     def mock_return():
#         # return requests.status_codes
def test_fetch_activities():
    abd = ActivityDB(fetch=True)
    assert not abd.data.empty
