import requests
import os
from src.utils.json_utils import save_dict_json, load_json

directions_dir = '../bd_directions' # receio que isso aqui não vai funcionar !

# Processa diferentes formatos de pontos e retorna x, y
def process_coordinates(node):

# Diferentes formatos
# node[0], node[1] # x, y
# node['x'], node['y'] 
# node['properties']['x'], entrada_regioes[0]['properties']['y'] # node= entrada_regioes[0]
# node.x, node.y
    
    if isinstance(node, dict):
        if 'x' in node and 'y' in node:
            x = node['x']
            y = node['y']
        elif 0 in node and 1 in node:
            x = node[0]
            y = node[1]
        elif 'properties' in node:
            x = node['properties']['x']
            y = node['properties']['y']
        else:
            raise ValueError("Formato de dicionário inválido para coordenadas")
    elif isinstance(node, list):
        if len(node) >= 2:
            x = node[0]
            y = node[1]
        else:
            raise ValueError("Formato de lista inválido para coordenadas")
    elif isinstance(node, tuple):
        if len(node) >= 2:
            x = node[0]
            y = node[1]
        else:
            raise ValueError("Formato de tupla inválido para coordenadas")
    elif hasattr(node, 'x') and hasattr(node, 'y'):
        x = node.x
        y = node.y
    else:
        raise ValueError("Formato de entrada não suportado para coordenadas")

    # Aqui você pode realizar o processamento necessário com as coordenadas x e y
    return x, y

# Obtenha dados de rota entre dois pontos utilizando o serviço de API do Azure e salve em um arquivo JSON
def get_directions_response_azure(lat1, long1, lat2, long2, route_type = 'fastest', mode='car'):
# route_type = 'fastest' or 'shortest'
# https://learn.microsoft.com/en-us/rest/api/maps/route/get-route-directions?tabs=HTTP 

    key = os.getenv('AZURE_SUBSCRIPTION_KEY') # terá que configurar como variãvel de ambiente na nuvem !
    base_url = 'https://atlas.microsoft.com/route/directions/json'

    params = {
            'subscription-key': key,
            'api-version': '1.0',
            'query': f'{lat1},{long1}:{lat2},{long2}',
            'travelMode': 'car',
            'routeType': route_type,
            'computeTravelTimeFor': 'all',
            'traffic': False # não observei diferença considerando traffic = False ou false or True ou true
             # To ignore the current traffic, set traffic to false in your API request (https://learn.microsoft.com/en-us/azure/azure-maps/how-to-use-best-practices-for-routing)
             # A API do Azure Maps Routing Service fornece estimativas de tempo de viagem 
             # com base nas condições de tráfego atuais e históricas, 
             # mas não oferece uma opção direta para retornar um tempo estimado que seja independente do dia e da hora. 
             # As estimativas de tempo de viagem geralmente levam em consideração as condições de tráfego em tempo real 
             # e histórico para fornecer uma estimativa precisa para o momento da solicitação.
        }       
    response = requests.get(base_url, params=params)
    print ('\nResponse:', response.json())

    d={}
    print ('response', response.json())
    d['distance'] = response.json()['routes'][0]['summary']['lengthInMeters'] # meters, 
    d['time'] = response.json()['routes'][0]['summary']['travelTimeInSeconds'] # seconds
    print ('\nCoordinates:', [coord for coord in (response.json()['routes'][0]['legs'][0]['points'])])
    d['coordinates'] = [[coord['latitude'], coord['longitude']] for coord in (response.json()['routes'][0]['legs'][0]['points'])] # lat, long

    save_dict_json(d, os.path.join(directions_dir, route_type, str(lat1)+'_'+str(long1)+'_'+str(lat2)+'_'+str(long2)+'.json'))

# Obtenha dados de rota entre dois pontos utilizando o serviço de API do  Route and Directions e salve em um arquivo JSON
def get_directions_response_rapid(lat1, long1, lat2, long2, route_type='fastest', mode='drive'):
# optimize = "fastestRoute" or "shortestRoute"
# https://rapidapi.com/geoapify-gmbh-geoapify/api/route-and-directions/details

    if route_type=='fastest':
        optimize = "fastestRoute"
    elif route_type=='shortest':
        optimize = "shortestRoute"
    key = os.getenv('ROUTE_AND_DIRECTIONS_SUBSCRIPTION_KEY')
    url = 'https://route-and-directions.p.rapidapi.com/v1/routing'
    host = 'route-and-directions.p.rapidapi.com'
    headers = {'X-RapidAPI-Key': key, 'X-RapidAPI-Host': host}
    querystring = {'waypoints':f'{str(lat1)},{str(long1)}|{str(lat2)},{str(long2)}','mode':'drive', 'optimize': optimize}
    
    response = requests.request('GET', url, headers=headers, params=querystring)
    
    d={}
    d['distance'] = response.json()['features'][0]['properties']['distance'] # meters, 
    d['time'] = response.json()['features'][0]['properties']['time'] # seconds
    d['coordinates'] = response.json()['features'][0]['geometry']['coordinates'] # lat, long
    
    save_dict_json(d, os.path.join(directions_dir, route_type, str(lat1)+'_'+str(long1)+'_'+str(lat2)+'_'+str(long2)+'.json'))

# Obtenha dados de rota entre dois pontos 
def get_directions_route(coords_od, client = 1, route_type = 'fastest', directions_dir = '../bd_directions'):
    # Formato:
        # lat_longs = [[(lat1, long1), (lat2, long2)]], 
        # client = 1 Azure, 2 Route and directions (rapidapi)

    [(lat1, long1), (lat2, long2)] = coords_od
    filename = os.path.join(directions_dir, route_type, str(lat1)+'_'+str(long1) +'_'+str(lat2) +'_'+str(long2)+'.json')
    directions =  load_json(filename)
    # if not directions: # Por favor, remova os comentários para acessar informações do serviço de API.
    #     directions = get_directions_response_azure(lat1, long1, lat2, long2, route_type)
    #     directions =  load_json(filename)
    return directions