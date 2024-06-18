from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
import csv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.decorators.csrf import csrf_protect
import json
import requests
import geopy.distance
from .quad_tress import QNode, QuadTree, Location
import matplotlib.pyplot as plt
import time
import pandas as pd
import csv

@csrf_protect
def login_signup_view(request):
    login_form = AuthenticationForm()
    signup_form = UserCreationForm()

    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = AuthenticationForm(request, request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home_view')  # Redirect to home page after login
        elif 'signup' in request.POST:
            signup_form = UserCreationForm(request.POST)
            if signup_form.is_valid():
                signup_form.save()
                return redirect('login_signup_view')  # Redirect to login page after signup

    return render(request, 'index1.html', {'login_form': login_form, 'signup_form': signup_form})

def home_view(request):
    return render(request,'home1.html')
def get_districts(request):
    state_id = request.GET.get('state_id')
    # Example data for districts of Tamil Nadu, Kerala, and Karnataka
    districts_data = {
        'tamilnadu': ['Chennai', 'Coimbatore', 'Madurai'],
        'kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode'],
        'karnataka': ['Bengaluru', 'Mysuru', 'Hubballi']
    }

    # Map state_id to the corresponding state
    if state_id == '1':
        state = 'tamilnadu'
    elif state_id == '2':
        state = 'kerala'
    elif state_id == '3':
        state = 'karnataka'
    else:
        state = None

    # If state is found, return the districts for that state
    if state:
        districts = districts_data.get(state, [])
        return JsonResponse(districts, safe=False)
    else:
        return JsonResponse([], safe=False)


def select_ward(request):
    if request.method == 'POST':
        district = request.POST.get('district')
        state = request.POST.get('state')
        
        # Assuming the CSV file is located in the same directory as views.py
        csv_file_path = 'myapp\zONE.CSV.csv'
        
        # Read ward data from the CSV file
        wards = []
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                    wards.append(row['Name of the Zone'])
        
        return render(request, 'Zone.html', {'wards': wards})

session = requests.Session()
def get_full_address(latitude, longitude):
    url = 'https://nominatim.openstreetmap.org/reverse'
    params = {
        'format': 'json',
        'lat': latitude,
        'lon': longitude,
        'zoom': 14,  # Adjust zoom level as needed
        'addressdetails': 1
    }
    headers = {
        'User-Agent': 'YourAppName/1.0 (your.email@example.com)'  # Replace with your app name and contact email
    }
    response = session.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    address = data.get('address', {})
    # ward_no = address.get('suburb')  # Adjust this if the ward number is stored differently
    full_address = ', '.join([v for k, v in address.items() if v])
    ward_no=full_address.split(",")[0].split(' ')[-1]
    print(ward_no)
    file_path = 'C:\\Users\\91842\\Desktop\\Atm\\Atmlocator\\myapp\\censuschennaicity.csv'
        
    if ward_no[0] in ('1','2','3','4','5','6','7','8','9','10'):
        population=500
        print('yes')
        with open(file_path, newline='') as csvfile:

            # Create a CSV reader object
            reader = csv.DictReader(csvfile)
            
            # Iterate over each row in the CSV file
            for row in reader:
                # Compare values in two columns (e.g., 'column1' and 'column2')
                if row['Ward Number'] == ward_no:
                    # Add the values from another column (e.g., 'column3') if the condition is met
                    population += int(row['Total Population'])
    else:
        ward_no = 1
        population = 10000
    
    return {
        'full_address': f"Ward {ward_no}, {full_address}",
        'ward_no': ward_no,
        'population': population
    }

def find_address_for_places(places):
    for place in places:
        full_address = get_full_address(place['latitude'], place['longitude'])
        place['full_address'] = full_address  # Sleep to respect Nominatim usage policy
    return places

def overpass_query(query):
    url = "http://overpass-api.de/api/interpreter"
    response = requests.get(url, params={'data': query})
    response.raise_for_status()
    return response.json()

def find_places(location, radius, place_type):
    lat, lon = location
    delta = radius / 111320  # Convert radius to degrees (approximately)
    bbox = [lat - delta, lon - delta, lat + delta, lon + delta]

    query = f"""
    [out:json];
    (
      node["amenity"="{place_type}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      way["amenity"="{place_type}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      relation["amenity"="{place_type}"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out center;
    """

    result = overpass_query(query)

    places = []
    for element in result['elements']:
        name = element['tags'].get('name', 'N/A')
        lat = element['lat'] if 'lat' in element else element['center']['lat']
        lon = element['lon'] if 'lon' in element else element['center']['lon']
        
        # Get the full address
        full_address = get_full_address(lat, lon)
        
        places.append({
            'name': name,
            'latitude': lat,
            'longitude': lon,
            'full_address': full_address
        })
    
    return places

# Location of Kelambakkam (latitude, longitude)
def ward_population(request):
    import os
    file_path = 'myapp\ward_data.json'
    if os.path.exists(file_path):
        with open('ward_data.json', 'r') as json_file:
            main_ward=json.load(json_file)
            if len(main_ward)==0:
                main_ward={}
    else:
        with open('ward_data.json', 'r') as json_file:
            main_ward=json.load(json_file)
    if request.method == 'POST':
        selected_ward = request.POST.get('ward')
    if selected_ward not in main_ward:
        list_zones={"THIRUVOTRIYUR":[13.163510, 80.303180],'Sholinganallur':[12.8742,	80.22433],"MANALI":[13.163740,80.263650],"MADHAVARAM":[13.163130, 80.228400
],"TONDIARPET":[13.132290, 80.286680],"ROYAPURAM":[13.107280, 80.292950],"THIRU-VI-KA NAGAR":[13.123984336853027, 80.20769500732422],"AMBATTUR":[13.0880606, 80.1963757
],"ANNA NAGAR":[13.0872004, 80.2164421],"TEYNAMPET":[13.044979095458984, 80.25179290771484],"KODAMBAKKAM":[13.052735328674316, 80.2206802368164
],"VALASARAVAKKAM":[13.0403, 80.1723],"ALANDUR":[13.0042558, 80.2014525],'ADYAR':[13.006442, 80.2543612],'PERUNGUDI':[ 12.9710239,80.2418051
]}
        latitude=list_zones[selected_ward][0]
        longitude=list_zones[selected_ward][1]
        location =  (latitude,longitude)
        radius = 2000 # Radius in meters

        # Find all required places
        atms = find_places(location, radius, 'atm')
        bus_stops = find_places(location, radius, 'bus_station')
        hospitals = find_places(location, radius, 'hospital')
        colleges = find_places(location, radius, 'college')

        hotspots = bus_stops + hospitals + colleges

        # Create Location objects with full address
        list_hotspots = [Location(loc['name'], loc['latitude'], loc['longitude'], loc['full_address']) for loc in hotspots]
        list_atms = [Location(loc['name'], loc['latitude'], loc['longitude'], loc['full_address']) for loc in atms]

        # Sort ATMs based on latitude
        list_atms.sort(key=lambda x: x.x)

        # Build the QuadTree
        atm_tree=None
        if len(list_atms)!=0:
            atm_tree = QuadTree(list_atms[0])
            for loc in list_atms[1:]:
                atm_tree.insert(loc)



        # Scoring criteria
        def score_location(location, atm_tree=None):
            score = 0
            if atm_tree!=None:
                node, distance = atm_tree.search_closest_node(atm_tree.root, location)
                
                # Proximity to ATM
                if distance <= 0.5:
                    score += 1
                else:
                    score += 2
            
            # Type of hotspot
            if 'bus_station' in location.name.lower():
                score += 3
            else:
                score += 2
            
            # Address and population data
            ward_no = location.full_address['ward_no']
            population = location.full_address['population']
            
            # Same ward points
            same_ward_locations = [loc for loc in list_hotspots if loc.full_address['ward_no'] == ward_no]
            if len(same_ward_locations) > 1:
                score += 3

            # ATM presence in the ward
            atms_in_ward = [atm for atm in list_atms if atm.full_address['ward_no'] == ward_no]
            if atms_in_ward:
                score -= 1

            # Population points
            if population > 10000:
                score += 2
            else:
                score += 1
            
            return score

        # Calculate scores for each hotspot
        if atm_tree:
            scores = {loc: score_location(loc, atm_tree) for loc in list_hotspots}
        else:
            scores = {loc: score_location(loc) for loc in list_hotspots}
            

        # Find the top five locations based on scores
        top_five_locations = sorted(scores, key=scores.get, reverse=True)[:5]

        # Create a dictionary to store information about the best location and the top five locations
        location_info = {}
        # Extract coordinates of the best location
        best_location=top_five_locations[0].name
        latitude = top_five_locations[0].x
        longitude = top_five_locations[0].y
        population=top_five_locations[0].full_address['population']

        # Define a function to count the number of each type of place around a given location
        def count_places_around_location(location, radius, place_type):
            places_around_location = find_places(location, radius, place_type)
            return len(places_around_location)

        # Define the radius around the best location within which to search for places
        search_radius = 2000  # Adjust this radius as needed

        # Calculate counts of each type of place around the best location
        bus_stops_count = count_places_around_location((latitude, longitude), search_radius, 'bus_station')
        hospitals_count = count_places_around_location((latitude, longitude), search_radius, 'hospital')
        colleges_count = count_places_around_location((latitude,longitude), search_radius, 'college')
        atms_count = count_places_around_location((latitude,longitude), search_radius, 'atm')
        statistical_data=[bus_stops_count,hospitals_count,colleges_count,atms_count]
        main_ward[selected_ward]={
                'selected_ward': best_location,
                'latitude': latitude,
                'longitude': longitude,
                'population': population,
                'statistics': statistical_data
            }
        with open('ward_data.json', 'w') as json_file:
            json.dump(main_ward, json_file)

        return JsonResponse({
                'selected_ward': best_location,
                'latitude': latitude,
                'longitude': longitude,
                'population': population,
                'statistics': statistical_data
            })
    else:
            for i,j in main_ward.items():
                if i==selected_ward:
                    return JsonResponse({
                'selected_ward': j['selected_ward'],
                'latitude': j['latitude'],
                'longitude': j['longitude'],
                'population': j['population'],
                'statistics': j['statistics']
            })
                    break
            
