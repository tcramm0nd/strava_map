# strava_map
Downloads strava activities and generates a heatmap for each activity type.

## Installation
`pip install strava-map`

## Example

Navigate to the strava_heatmap directory and run the strava_heatmap python file

```python
python3 strava_heatmap.py
```

On the initial run you will be prompted for your Client ID and Client Secret. This is to authorize the App to retrieve activity data from Strava. All Strava keys are stored locally in a `.credntials.json` file.

You can find your Client ID and Client Secret by navigating to `Settings > My API Application`. If you have not set up Strava for API applications, you can find directions on how to do so [here](https://developers.strava.com/docs/getting-started/#account).

![Strava Cient information](https://developers.strava.com/images/getting-started-1.png)

