# strava_map
[![PyPI](https://img.shields.io/pypi/v/strava-map)](https://pypi.org/project/strava-map/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/strava-map)](https://pypi.org/project/strava-map/)
[![GitHub License](https://img.shields.io/github/license/tcramm0nd/strava_map)](https://github.com/tcramm0nd/strava_map/blob/main/LICENSE)

Downloads strava activities and generates a heatmap for each activity type. View all your Strava activity data in one map, or just download and save your activity data to edit as you choose.

## Installation
`strava_map` can be installed via pip using:

```bash 
pip install strava-map
```
or run directly from a cloned repo

```bash
git clone https://github.com/tcramm0nd/strava_map.git
```


## Example

```python
from strava_map import Map
m = Map()
```

On the initial run you will be prompted for your Client ID and Client Secret. This is to authorize the App to retrieve activity data from Strava. All Strava keys are stored locally in a `.credntials.json` file.

You can find your Client ID and Client Secret by navigating to `Settings > My API Application`. If you have not set up Strava for API applications, you can find directions on how to do so [here](https://developers.strava.com/docs/getting-started/#account).

![Strava Cient information](https://developers.strava.com/images/getting-started-1.png)

Once the Strava Client has been authorized it will proceed to retrieve activity data, stored in `Map.activity_database`.

### Create a Heatmap of all activities
You can create a heatmap of all activiies by simply running
```python
m.create_heatmap()
```
This will generate a map with different activity types coded as different colors.

### Saving activity data
```python
m.save_activities(path='path/to/directory/')
```

## To Do
- [ ] add KML support
- [ ] add colorization options
- [ ] assign gradients to activities
