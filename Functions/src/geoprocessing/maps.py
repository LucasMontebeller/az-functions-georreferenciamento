import os
import folium

# Função para criar um mapa com camadas de talhões, regiões, entrada de regiões, oficina central e merged_roads
def create_map(talhoes, regioes, entrada_regioes, oficina_central, merged_roads):

    lat = talhoes[0]['geometry']['coordinates'][0][0][0][1]
    long = talhoes[0]['geometry']['coordinates'][0][0][0][0]
    
    my_map = folium.Map(location=[lat, long], zoom_start=12)
    azure_subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
    tile_url = f'https://atlas.microsoft.com/map/tile?subscription-key={azure_subscription_key}&api-version=2.0&layer=basic&style=main'
    attribution = 'Azure Maps | © 2023 Microsoft Corporation © 1987-2023 HERE'
    folium.TileLayer(tile_url, attr=attribution).add_to(my_map)

    style_function1 = lambda x: {
        'fillColor': 'blue',
        'color': '',
        'weight': 0.0001,
        'fillOpacity': 0.7
    }

    style_function2 = lambda x: {
        'fillColor': 'light_gray',
        'color': '',
        'weight': 0.00001,
        'fillOpacity': 0.1
    }

    style_function3 = lambda x: {
        'fillColor': 'green',
        'color': 'green',
        'weight': 1,
        'fillOpacity': 0.7
    }

    for t in talhoes:
        folium.GeoJson(t, style_function=style_function1).add_to(my_map)

    for r in regioes:
        folium.GeoJson(r, style_function=style_function2).add_to(my_map)

    for o in oficina_central:
        folium.Marker([o['geometry']['coordinates'][1], o['geometry']['coordinates'][0]], popup="Oficina Central", icon=folium.Icon(color="red", icon="info-sign")).add_to(my_map)

    for e in entrada_regioes:
        folium.Marker([e['properties']['y'], e['properties']['x']], popup=f"Região {e['properties']['id']}", icon=folium.Icon(color="gray", icon="info-sign")).add_to(my_map)

    for mr in merged_roads:
        folium.GeoJson(mr, style_function=style_function3).add_to(my_map)

    return my_map

# Adiciona os centroides ao mapa
def add_centroides_map(my_map, id_talhoes, centroides):
    for t, c in zip(id_talhoes, centroides):
        folium.Marker((c.y, c.x), popup=f"Talhão {t}", icon=folium.Icon(color="blue",icon="leaf")).add_to(my_map) # icons: "cloud", "envelope", "flag", "home", "leaf", "info-sign"

    return my_map

# Adiciona/plota os nós das arestas mais próximas dos centroides no mapa
# def add_nearest_edges_map(G, nearest_edges, my_map): # Função utilizada apenas para debug
#     for e in nearest_edges:
#         print(G.nodes[e[1]]['x'], G.nodes[e[1]]['y'])
#         folium.Marker(location=[ G.nodes[e[0]]['y'], G.nodes[e[0]]['x'] ], popup=f"Talhão {t}", icon=folium.Icon(color="green",icon="leaf")).add_to(my_map) # icons: "cloud", "envelope", "flag", "home", "leaf", "info-sign"
#         folium.Marker(location=[ G.nodes[e[1]]['y'], G.nodes[e[1]]['x'] ], popup=f"Talhão {t}", icon=folium.Icon(color="green",icon="leaf")).add_to(my_map) # icons: "cloud", "envelope", "flag", "home", "leaf", "info-sign"

# Adiciona os pontos de acessos às áreas ao mapa 
def add_area_access_point_map(id, entrada, my_map, icon_color= "green"):
    for i, e in zip(id, entrada):
        folium.Marker(location=[e[1], e[0]], popup=f"ID {i}", icon=folium.Icon(color=icon_color,icon="leaf")).add_to(my_map)
    return my_map
