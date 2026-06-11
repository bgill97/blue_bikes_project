import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from math import radians, cos, sin, asin, sqrt
import numpy as np
from datetime import datetime

# show all columns and prevent wrapping in results
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

df = pd.read_csv('/Users/benjamingillingham/Desktop/blue_bikes_project/202505-bluebikes-tripdata.csv', sep=',')
df['started_at'] = pd.to_datetime(df['started_at'])
df['ended_at'] = pd.to_datetime(df['ended_at'])
df['time_length'] = df['ended_at'] - df['started_at']

df = df[df['end_station_name'].notna()]

#important definitions
salem_station_ids = ['T32002', 'T32016', 'T32001', 'T32008', 'T32005', 'T32018', 'T32003', 'T32004', 'T32015', 'T32014',
                     'T32019', 'T32011', 'T32006', 'T32010', 'T32009', 'T32007', 'T32007 ', 'T32017', 'T32012',
                     'T32013']
encore_station_ids = ['V32004', 'V32011', 'V32005']
encore_docks = df[df['end_station_id'].isin(encore_station_ids) & ~df['start_station_id'].isin(encore_station_ids)]
common_rides = df.groupby(['start_station_name', 'start_lat', 'start_lng', 'end_station_name', 'end_lat', 'end_lng'])[
        'member_casual'].count().reset_index()
common_rides.columns = [*common_rides.columns[:-1], 'ride_count']
top10_common = common_rides.sort_values('ride_count', ascending=False).head(10)
hour_started = pd.to_datetime(df.started_at).dt.hour

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


def columns(df):
    for col in df.columns:
        print(col)


def find_max_value():
    while True:
        field = input('What field do you want to see the maximum value of? ')
        if field not in df.columns:
            print('Please enter a valid field.')
            continue
        else:
            print(df.loc[df[field].idxmax()])
            break


def find_min_value():
    while True:
        field = input('What field do you want to see the minimum value of? ')
        if field not in df.columns:
            print('Please enter a valid field.')
            continue
        else:
            print(df.loc[df[field].idxmin()])
            break


def find_longest_ride():
    pass

def question_break():
    print('---------------------------------------------------')

df['distance'] = haversine(df['start_lng'],df['start_lat'],df['end_lng'],df['end_lat'])
time = pd.to_timedelta(df['time_length'], errors='raise').dt.total_seconds() / 3600
df['kph'] = df['distance'] / time

print('This is the data we have!')
columns(df)
question_break()

# most common rides

def common_routes():
    print(f"What are the 10 most common routes in May 2025?\n{top10_common}")
    question_break()

# longest rides time-wise

def longest_duration_rides():
    long_rides = df.sort_values(by=['time_length'], ascending=False)
    top10_duration = long_rides.head(10)
    print('What are the longest duration rides in May 2025?')
    print(top10_duration[['ride_id', 'started_at', 'ended_at', 'start_station_name', 'end_station_name', 'time_length']])
    question_break()

# trying to find most common hour of the day to ride
def common_hours():
    print('What is the most common hour of the day to start a bike ride in May 2025?')
    common_hours = df.groupby([hour_started])['member_casual'].count().sort_values(ascending=False)
    print(common_hours)
    question_break()

# where are encore riders coming from?
def encore_origin():
    print('Where are Encore riders coming from?')
    # Encore station IDs: V32004, V32011, V32005
    encore_docks_grouped = encore_docks.groupby(['start_station_name'])['member_casual'].count().sort_values(
        ascending=False)
    print(encore_docks_grouped)
    question_break()

# what encore riders are taking the longest?
def encore_slow():
    print('What Encore riders are taking the longest?')
    undedicated_gamblers = encore_docks.sort_values(by=['time_length'], ascending=False)
    print(undedicated_gamblers)
    question_break()

# what encore riders are taking the shortest?
def encore_fast():
    print('What Encore riders are getting there quickly?')
    dedicated_gamblers = encore_docks.sort_values(by=['time_length'], ascending=True)
    print(dedicated_gamblers)
    question_break()

# Boston to Salem
def salem_rides():
    salem_docks = df[df['end_station_id'].isin(salem_station_ids) & ~df['start_station_id'].isin(salem_station_ids)]
    salem_docks_grouped = salem_docks.groupby(['start_station_name'])['member_casual'].count().sort_values(ascending=False)
    print('Salem rides:')
    print(salem_docks)
    #print('Most common origin stations for Salem rides:')
    #print(salem_docks_grouped)
    avg_time_length = salem_docks['time_length'].mean()
    print(f"Average time length for a Salem ride: {avg_time_length}")
    question_break()

# Routes with the longest average duration
def longest_avg_duration_routes():
    remove_rare_routes = df[
        df.groupby(['start_station_name', 'end_station_name'])['start_station_name'].transform('count') >= 20]
    remove_rare_routes = remove_rare_routes.groupby(['start_station_name', 'end_station_name'])['time_length'].agg(
        ['mean', 'count']).sort_values(by=['mean'], ascending=False)
    top10_avg_duration = remove_rare_routes.head(10)
    print(f"What are the 10 longest routes by average duration in May 2025? (at least 20 rides)\n{top10_avg_duration}")
    question_break()


# plotting most common rides
def common_routes_map():
    fig_start = px.scatter_map(data_frame=top10_common, lat="start_lat", lon="start_lng", text="start_station_name",
                               zoom=15, height=800, width=800,hover_data=['start_station_name'])

    fig_end = px.scatter_map(data_frame=top10_common, lat="end_lat", lon="end_lng", text="end_station_name",
                             zoom=15, height=800, width=800,hover_data=['end_station_name'])

    fig_all = go.Figure(data=fig_start.data + fig_end.data)

    max_count = top10_common["ride_count"].max()

    for _, row in top10_common.iterrows():
        opacity = row["ride_count"] / max_count
        fig_all.add_trace(go.Scattermap(
            lat=[row["start_lat"], row["end_lat"]],
            lon=[row["start_lng"], row["end_lng"]],
            mode="lines",
            line=dict(width=1 + 4*opacity, color="blue"),
            showlegend=False,
            hovertext=f"{row['start_station_name']} --> {row['end_station_name']}<br>Total rides: {row['ride_count']}"
        ))

    fig_all.update_layout(title='Top 10 common routes in May 2025', map=dict(zoom=1),
                          height=1200,
                          width=2000)
    #fig_all.show()

#Most common routes starting from our nearest station
def union_square_destination():
    print('Where are Union Square riders going to?')
    # Union Sq station IDs: V32004, V32011, V32005
    union_station_ids = ['S32002']
    union_rides = df[df['start_station_id'].isin(union_station_ids) & ~df['end_station_id'].isin(union_station_ids)]
    union_rides = union_rides.groupby(['start_station_name', 'start_lat', 'start_lng', 'end_station_name', 'end_lat', 'end_lng'])[
        'member_casual'].count().reset_index()
    union_rides.columns = [*union_rides.columns[:-1], 'ride_count']
    union_rides = union_rides.sort_values('ride_count', ascending=False).head(50)
    print(union_rides)
    question_break()

    fig_start = px.scatter_map(data_frame=union_rides, lat="start_lat", lon="start_lng", text="start_station_name",
                               zoom=15, height=800, width=800,hover_data=['start_station_name'])

    fig_end = px.scatter_map(data_frame=union_rides, lat="end_lat", lon="end_lng", text="end_station_name",
                             zoom=15, height=800, width=800,hover_data=['end_station_name'])

    fig_all = go.Figure(data=fig_start.data + fig_end.data)

    max_count = union_rides["ride_count"].max()

    for _, row in union_rides.iterrows():
        opacity = row["ride_count"] / max_count
        fig_all.add_trace(go.Scattermap(
            lat=[row["start_lat"], row["end_lat"]],
            lon=[row["start_lng"], row["end_lng"]],
            mode="lines",
            line=dict(width=1 + 4*opacity, color="blue"),
            showlegend=False,
            hovertext=f"{row['start_station_name']} --> {row['end_station_name']}<br>Total rides: {row['ride_count']}"
        ))

    fig_all.update_layout(title='Most Common Routes Originating in Union Square- May 2025', map=dict(zoom=1),
                          height=1200,
                          width=2000)
    #fig_all.show()

#highest speed rides
def fastest_rides():
    fastest_rides = df.sort_values('kph', ascending=False).head(10)
    print(f"What are the 10 fastest rides by kph in May 2025?\n{fastest_rides}")
    question_break()

#what are the most common stations to dock at each hour of the day
def common_end_stations():
    common_end_stations = df.groupby(['end_station_name','end_lat','end_lng'])['member_casual'].count().sort_values(ascending=False).head(5)
    print(common_end_stations)
    question_break()

def common_end_stations_by_hour():
    for x in range(24):
        common_end_stations = df[df['ended_at'].dt.hour == x]
        common_end_stations = common_end_stations.groupby(['end_station_name','end_lat','end_lng'])['member_casual'].count().sort_values(ascending=False).head(5).reset_index()
        print(f"Most common end stations for Hour {x}:\n{common_end_stations}")
        question_break()
        fig = px.scatter_map(data_frame=common_end_stations,
                             lat="end_lat",
                             lon="end_lng",
                             color="member_casual",
                             text="end_station_name",
                             hover_name="end_station_name",
                             zoom=8,
                             height=800,
                             width=800,
                             title=f"Most Common End Stations for Hour {x}")
        # https://plotly.com/python-api-reference/generated/plotly.express.scatter_map.html
        #fig.show()
'''
geo_center_latitudes = []
geo_center_longitudes = []
hour = []
#geographical center of all bike docks
for x in range(24):
    end_docking_hour = df[df['ended_at'].dt.hour == x]
    avg_lat = end_docking_hour['end_lat'].mean()
    avg_lng = end_docking_hour['end_lng'].mean()
    geo_center_latitudes.append(avg_lat)
    geo_center_longitudes.append(avg_lng)
    hour.append(x)
    print(f"Average docking coordinates for hour {x}: {avg_lat}, {avg_lng}")

geo_center_coordinates = pd.DataFrame({'hour':hour, 'geo_center_latitudes':geo_center_latitudes, 'geo_center_longitudes':geo_center_longitudes})

fig = px.scatter_map(data_frame=geo_center_coordinates,
                     lat="geo_center_latitudes",
                     lon="geo_center_longitudes",
                     text="hour",
                     hover_name="hour",
                     zoom=8,
                     height=800,
                     width=800,
                     title=f"Geographical Center for All Hours")

fig.show()
'''
#Classic vs electric speeds
def classic_vs_electric():
    question_break()
    print('What is the average speed for classic versus electric bikes?')
    classic_rides = df[df['rideable_type'] == 'classic_bike']
    avg_classic_speed = classic_rides['kph'].mean()
    electric_rides = df[df['rideable_type'] == 'electric_bike']
    avg_electric_speed = electric_rides['kph'].mean()
    print(f"The average speed for a classic bike is {avg_classic_speed} kph")
    print(f"The average speed for an electric bike is {avg_electric_speed} kph")

#Popular long distance rides- map these
def common_long_distance_routes():
    question_break()
    print('What are the most popular routes that are at least 6km?')
    long_distance_rides = df[df['distance'] >= 6]
    long_distance_rides = long_distance_rides.groupby(['start_station_name','end_station_name','distance'])['member_casual'].count().sort_values(ascending=False).head(5).reset_index()
    print(long_distance_rides)

#Popular short distance rides- map these
def common_short_distance_routes():
    question_break()
    print('What are the most popular routes that are at most 1/10 km?')
    short_distance_rides = df[df['distance'] <= 0.1]
    short_distance_rides = short_distance_rides[short_distance_rides['start_station_name'] != short_distance_rides['end_station_name']]
    short_distance_rides = short_distance_rides.groupby(['start_station_name','end_station_name','distance'])['member_casual'].count().sort_values(ascending=False).head(5).reset_index()
    print(short_distance_rides)

#highest avg kph for each time of day
def kph_by_hour():
    question_break()
    day_name = df['started_at'].dt.day_name()
    fastest_hours = df.groupby([hour_started,day_name])['kph'].agg(['mean','count']).sort_values(by=['mean'], ascending=False)
    print('What hours of the week are riders traveling the fastest?')
    print(fastest_hours)

#fastest moving bikes routes
def fastest_routes():
    question_break()
    remove_rare_routes_kph = df[
        df.groupby(['start_station_name', 'end_station_name'])['start_station_name'].transform('count') >= 20]
    remove_rare_routes_kph = remove_rare_routes_kph.groupby(['start_station_name', 'end_station_name'])['kph'].agg(
        ['mean', 'count']).sort_values(by=['mean'], ascending=False)
    top10_avg_duration = remove_rare_routes_kph.head(10)
    print(f"What are the 10 fastest routes by average kph in May 2025? (at least 20 rides)\n{top10_avg_duration}")

func_map = {
    'classic_vs_electric': classic_vs_electric,
    'common_long_distance_routes': common_long_distance_routes,
    'common_short_distance_routes': common_short_distance_routes,
    'kph_by_hour': kph_by_hour,
    'fastest_routes': fastest_routes,
    'common_routes': common_routes,
    'longest_duration_rides': longest_duration_rides,
    'common_hours': common_hours,
    'encore_origin': encore_origin,
    'encore_slow': encore_slow,
    'encore_fast': encore_fast,
    'salem_rides': salem_rides,
    'longest_avg_duration_routes': longest_avg_duration_routes,
    'common_routes_map': common_routes_map,
    'union_square_destination': union_square_destination,
    'fastest_rides': fastest_rides,
    'common_end_stations': common_end_stations,
    'common_end_stations_by_hour': common_end_stations_by_hour
}

def show_functions():
    print(list(func_map.keys()))

def run_functions():
    while True:
        func_input = input('Enter one of the functions listed above, or type "exit" to end: ')

        if func_input.strip() == 'exit':
            print('See ya! ')
            exit()

        elif func_input.strip() in func_map.keys():
            func_map[func_input]()
        else:
            print("Sorry no function for that!")


show_functions()
run_functions()

# find_max_value()
# find_min_value()

# color_continuous_scale=px.colors.cyclical.IceFire

#future ideas
#do same map for rides originating in Fenway, Somerville, etc
#do people ride faster at certain times of the day? on certain days of the week?
#what stations need more docks based on demand?