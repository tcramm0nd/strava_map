from strava_map import Map, ActivityDB
import pytest
import glob

# pytest --cov-report term-missing:skip-covered --cov=strava_map .


data = [{'name': 'Afternoon Run', 'type': 'Run', 'date': '2021-02-11', 'coordinates': [[40.48681, -79.97101], [40.48686, -79.97073], [40.48685, -79.97048]]},
         {'name': 'Afternoon Ride', 'type': 'Ride', 'date': '2021-02-12', 'coordinates': [[40.46681, -79.97301], [40.4886, -79.9073], [40.124, -79.049]]}]


@pytest.fixture
def example_activities():
    return ActivityDB(data=data)
@pytest.fixture
def example_map(example_activities):
    return Map(example_activities)

def test_Map_columns(example_activities):
    m = Map(example_activities)
    assert str(m.data.columns) == str(example_activities.data.columns)
def test_map_center(example_activities):
    m = Map(example_activities)
    assert m.center == [40.48683, -79.970605]
    
@pytest.mark.parametrize('activity_types,expected',
                         [('All',['Run', 'Ride']),
                          ('Run', ['Run']),
                          (['Run', 'Ride'],['Run', 'Ride'])])
def test_activity_types(activity_types, expected, example_activities):
    m = Map(example_activities, activity_types=activity_types)
    diff = set(m.activity_types) ^ set(expected)
    assert not diff
@pytest.mark.parametrize('split_by_type,expected',[(True,['Ride', 'Run']),
                                                   (False,['All'])])
def test_coords_by_type(split_by_type, expected, example_activities):
    m = Map(example_activities, split_by_type=split_by_type)
    coords = m.coordinates_by_type()
    diff = set(coords.keys()) ^ set(expected)
    assert not diff
    
def test_heatmap(example_map):
    example_map.create_heatmap()
    assert glob.glob('*_activity_heatmap.html')