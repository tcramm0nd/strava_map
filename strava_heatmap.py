import requests
import json
import polyline
from loguru import logger
import stravauth
import folium
from folium.plugins import HeatMap
import datetime as dt
import pandas as pd
import webbrowser  
                    
def get_activities(write_csv=True):

    client = stravauth.Client()
    access_token = client.access_token

    page = 1
    url = 'https://www.strava.com/api/v3/athlete/activities'
    activity_list = []

    while True:
        r = requests.get(url + '?access_token=' + access_token + '&per_page=100&page=' + str(page))
        if r.status_code != 200:
            print('Refreshing token')
            client.refresh()
            access_token = client.access_token
            r = requests.get(url + '?access_token=' + access_token + '&per_page=100&page=' + str(page))
        activities = r.json()
        activity_list.extend(activities)

        if len(activities) < 100:
            break

        page += 1
   
    print(f'Retrieved {len(activity_list)} total activities')
    
    df = pd.DataFrame(activity_list)
    df['coords'] = df['map'].apply(lambda x: convert_to_coords(x))
    
    if write_csv:
        filename = str(dt.date.today()) + '_strava_activities.csv'
        df.to_csv(filename)

    return df

def convert_to_coords(map_data):

    p = map_data['summary_polyline']
    if p:
        coords = polyline.decode(p)
        return coords
    
def create_heatmap(activities, activity_type = 'all'):

    if type(activities) != pd.core.frame.DataFrame:
        raise ValueError ('No Activities DataFrame Provided')
    
    with open('config.txt') as f:
        activity_types = f.read()
        activity_types = activity_types.split(', ')    
        
    if activity_type in activity_types:
        types = [activity_type]
    else:
        types = pd.unique(activities['type'])
        
    all_coords = activities['coords'].apply(pd.Series).stack().reset_index(drop=True)
    coords = {}
    for t in types:
        a = activities[activities['type'] == t]
        c = a['coords'].apply(pd.Series).stack().reset_index(drop=True)
        if len(c) > 0:
            coords[t] = c
    
    gradients = {'Run':{0: 'white', .9: 'blue', 1:'cyan'},
                 'Ride': {0: 'white', .9: 'maroon', 1:'red'}}
    start_point = pd.DataFrame(all_coords.to_list()).median(axis=0)
    
    m = folium.Map(location=start_point,
                    tiles='Stamen Toner',
                    zoom_start=14
        )

    for key in coords.keys():
        feature_group = folium.FeatureGroup(name=key, show=True)
        if key in ['Ride', 'Run']:
            gradient = gradients[key]
        else:
            gradient = {0: 'white', 1: 'lawngreen'}
        feature_group.add_child(HeatMap(coords[key], radius=7, blur=5, gradient=gradient))
        m.add_child(feature_group)
        
    m.add_child(folium.map.LayerControl())
    
    filename = str(dt.date.today()) + '_' + activity_type + '_activities.html'
    m.save(filename)
    webbrowser.open(filename)
    
def main():
    a = get_activities()
    create_heatmap(a, activity_type='Run')
    
if __name__ == '__main__':
    main()