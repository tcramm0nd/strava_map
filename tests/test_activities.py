import pytest
from strava_map import ActivityDB
import glob
@pytest.fixture
def required_response_fields():
    return set(('name', 'start_date', 'type', 'map'))

@pytest.fixture
def example_activities():
    return ActivityDB(data=[{'name': 'Afternoon Run', 'type': 'Run', 'date': '2021-02-11', 'coordinates': [[40.48681, -79.97101], [40.48686, -79.97073], [40.48685, -79.97048]]},
         {'name': 'Afternoon Ride', 'type': 'Ride', 'date': '2021-02-12', 'coordinates': [[40.46681, -79.97301], [40.4886, -79.9073], [40.124, -79.049]]}])

@pytest.fixture
def strava_client_info():
    return {'client_id': 45784,
            'client_secret':''}

def test_empty_db():
    assert ActivityDB()._data.empty

def test_activity_save(example_activities):
    example_activities.save(path='tests/')
    assert glob.glob('tests/*_strava_activities.json')

def test_activity_load(example_activities):
    assert str(ActivityDB(filename='tests/example.json').data.columns) == str(example_activities.data.columns)

def test_fetch_single_activity(required_response_fields):
    abd = ActivityDB()
    activity = abd.fetch(activity_id=4083992429)
    response_keys = set(activity.keys())
    assert required_response_fields.issubset(response_keys)