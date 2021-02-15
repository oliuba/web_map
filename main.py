"""
This module works with movie locations database and builds an HTML-page
with the map of movies locations of a certain year.
The map has three layers: the main one, the one with the closest to a user films locations icons
and the one with films locations icons in a chosen country.
"""

import math
import folium
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
geolocator = Nominatim(user_agent = 'web_map')
geocode = RateLimiter(geolocator.geocode, min_delay_seconds = 1)


def year_from_title(title: str) -> str:
    """
    Returns a string of a year of the movie.
    >>> year_from_title('Pain in Seeing (2017)')
    '2017'
    >>> year_from_title('"Beer OClock with Slosh & Buuz" (2014/I)')
    '2014'
    """
    try:
        year = title.split(' (')[1][:4]
    except IndexError:
        year = None
    return year


def distance(first_point: tuple, second_point: tuple) -> float:
    """
    Returns a number - distance between two points in meters.
    >>> distance((49.83826, 24.02324), (45.91234, 27.54962))
    509514.6569293797
    """
    earth_radius = 6371e3
    latitude_1 = first_point[0] * math.pi / 180
    latitude_2 = second_point[0] * math.pi / 180
    longitude_1 = first_point[1] * math.pi / 180
    longitude_2 = second_point[1] * math.pi / 180
    latitude_difference = latitude_2 - latitude_1
    longitude_difference = longitude_2 - longitude_1
    haversine_a = (math.sin(latitude_difference / 2) ** 2) + math.cos(latitude_1) * \
        math.cos(latitude_2) * (math.sin(longitude_difference / 2) ** 2)
    haversine_c = 2 * math.atan2(math.sqrt(haversine_a), math.sqrt(1 - haversine_a))
    haversine_distance = earth_radius * haversine_c
    return haversine_distance


def place_to_coordinates(place: str) -> tuple:
    """
    Returns tuple with coordinates (latitude, longitude) of a place.
    >>> place_to_coordinates('Lviv')
    (49.841952, 24.0315921)
    >>> place_to_coordinates('New York')
    (40.7127281, -74.0060152)
    """
    try:
        location = geolocator.geocode(place)
        coordinates = location.latitude, location.longitude
    except (GeocoderUnavailable, AttributeError):
        coordinates = np.nan
    return coordinates


def add_columns(movie_year: str) -> pd.DataFrame:
    """
    Returns a dataframe of locations.list adapted for the analysis.
    """
    movie_data = pd.read_csv('locations.list', sep = '\t+', header = None, skiprows = 14, \
        names = ['Title', 'Location', 'Additional info'], engine = 'python')
    movie_data = movie_data.iloc[:, 0:2]    # Delete useless column with additional info
    movie_data['Year'] = movie_data['Title'].apply(year_from_title)
    movie_data = movie_data[(movie_data['Year'].str.isdigit()) & (movie_data['Year'] == movie_year)]

    movie_data['Title'] = movie_data['Title'].apply(lambda title: title.split(' (')[0])
    movie_data = movie_data.drop_duplicates()
    movie_data['Country'] = movie_data['Location'].apply(lambda loc: loc.split(', ')[-1])
    movie_data['Coordinates'] = movie_data['Location'].apply(place_to_coordinates)
    movie_data = movie_data[movie_data['Coordinates'].notna()]
    return movie_data


def closest_to_user(user_coordinates: tuple, movie_data: pd.DataFrame) -> list:
    """
    Returns a list of lists: up to 10 closest to a user places and their coordinates.
    """
    dist_to_user = movie_data
    dist_to_user['Distance to user'] = dist_to_user.apply(lambda x: distance(x['Coordinates'], \
        user_coordinates), axis = 1)
    sort_movies = movie_data.sort_values(by = ['Distance to user'])
    df_closest_locations = sort_movies.head(10)
    titles_and_coordinates = df_closest_locations[['Title', 'Coordinates']]
    list_closest_locations = titles_and_coordinates.values.tolist()
    return list_closest_locations


def movies_by_country(country: str, movie_data: pd.DataFrame) -> list:
    """
    Returns a list of lists: up to 10 movies filmed in the country.
    """
    country_movies = movie_data
    country_movies = country_movies[country_movies['Country'] == country].head(10)
    country_movies = country_movies[['Title', 'Coordinates']]
    return country_movies.values.tolist()


def map_closest_to_user(closest_locations: list) -> folium.FeatureGroup:
    """
    Returns the second layer of map with movie locations that are closest to user.
    """
    closest_loc_to_user = folium.FeatureGroup(name = 'Closest movie locations')
    for loc in closest_locations:
        movie_title = loc[0]
        movie_lat = loc[1][0]
        movie_lon = loc[1][1]
        closest_loc_to_user.add_child(folium.Marker(location = [movie_lat, movie_lon], \
            popup = movie_title, icon = folium.Icon(color = 'green')))
    return closest_loc_to_user


def map_country_movies(counrty_movies: list, country: str) -> folium.FeatureGroup:
    """
    Returns the third layer of map with movie locations that are situated in certain country.
    """
    country_locations = folium.FeatureGroup(name = f'{country} movie locations')
    for loc in counrty_movies:
        movie_title = loc[0]
        movie_lat = loc[1][0]
        movie_lon = loc[1][1]
        country_locations.add_child(folium.Marker(location = [movie_lat, movie_lon], \
            popup = movie_title, icon = folium.Icon(color = 'red')))
    return country_locations


def main() -> None:
    """
    This is the main fumction, which takes the needed information from user
    and builds a map depending on it.
    """
    movie_year = input('Please enter a year you would like to have a map for: ')
    user_location = input('Please enter your location (format: lat, long): ')
    movie_country = input('Please enter a country you would like to have a map for: ')
    user_coord = tuple(map(float, user_location.split(', ')))
    map_name = movie_year + '_' + movie_country + '_movies_map.html'

    movie_db = add_columns(movie_year)
    movies_map = folium.Map()
    second_layer = map_closest_to_user(closest_to_user(user_coord, movie_db))
    movies_map.add_child(second_layer)

    third_layer = map_country_movies(movies_by_country(movie_country, movie_db), movie_country)
    movies_map.add_child(third_layer)
    movies_map.add_child(folium.LayerControl())
    movies_map.save(map_name)
    print(f'Map generation is finished. Please have a look at {map_name}')

main()
