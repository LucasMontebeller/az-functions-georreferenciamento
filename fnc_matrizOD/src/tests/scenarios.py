import os
from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
import geojson
from src.geoprocessing.graphs import create_graph_from_geojson, calculate_area_access_points
from src.geoprocessing.maps import add_centroides_map, add_area_access_point_map
from src.utils.geojson_utils import load_geojson
from src.utils.json_utils import load_json
from src.utils.pickle_utils import load_graph

# Lê dados do cenário
# Dados dos talhões, das regiões e seus pontos de entrada, do ponto da oficinal central e vias (open street maps + vias customizadas)
# Não inclui as vias do Azure Maps, apenas as do open street maps slecionadas e as customizadas
def read_scen_data():
    
    # Lê dados dos talhões, das regiões e seus pontos de entrada, do ponto da oficinal central e vias (open street maps + vias customizadas)
    talhoes = load_geojson('../cenario/talhoes.geojson')
    regioes = load_geojson('../cenario/regioes.geojson')
    entrada_regioes = load_geojson('../cenario/entrada_regioes.geojson')
    oficina_central = load_geojson('../cenario/oficina_central.geojson')
    merged_roads = load_geojson('../cenario/merged_roads.geojson')

    return (talhoes, regioes, entrada_regioes, oficina_central, merged_roads)

# Lê dados do cenário original e os dados processados
def read_scen_complete():
    talhoes, regioes, entrada_regioes, oficina_central, merged_roads = read_scen_data()
    id_talhoes = load_json(os.path.join('output','cenario','id_talhoes.json'))
    id_regioes = load_json(os.path.join('output','cenario','id_regioes.json'))
    G = load_graph(os.path.join('output','cenario','graph.pickle'))
    # entrada_talhoes = load_geojson(os.path.join('output','cenario','entrada_talhoes.geojson'))
    # centroides = load_geojson(os.path.join('output','cenario','centroides.geojson'))
    return G, id_talhoes, id_regioes, entrada_regioes # entrada_talhoes, oficina_central, merged_roads

# Gera id para talhões e regiões
def generate_ids_talhoes_and_regioes(talhoes, entrada_regioes):

    id_talhoes = [(t["properties"]["layer"][:-4]) for t in talhoes] #'T_'+ '{:0>3}'.format
    id_regioes = ['R'+ '{:0>3}'.format(e["properties"]["id"]) for e in entrada_regioes]

    return id_talhoes, id_regioes

# Função para gerar centroides para representar talhões
def generate_centroides_talhoes(id_talhoes, talhoes):
    
    # Cria lista para armazenar as geometrias
    geometrias = []

    # Extrai geometrias dos talhoes
    for t in talhoes:
        coordinates = t["geometry"]["coordinates"][0][0]
        polygon = Polygon(coordinates)
        geometrias.append(polygon)

    # Cria uma GeoDataFrame com as geometrias
    gdf_data = pd.DataFrame({"Name": id_talhoes})
    gdf = gpd.GeoDataFrame(gdf_data, geometry=geometrias, crs='EPSG:4326')
    
    # Reprojeta as geometrias para a zona UTM 22 (EPSG:32722
    gdf = gdf.to_crs(epsg=32722)

    # Calcula os centroides em UTM 22
    centroides = gdf.geometry.centroid

    # Converte centroides para latitude e longitude em EPSG:4326 (CRS geográfico)
    centroides = centroides.to_crs(epsg=4326)

    return centroides

# Salva pontos de acesso aos talhões em GeoJSON
def save_area_access_point_to_geojson(id, entrada, filename):
    
    entrada_geojson = []

    for id, point in zip(id, entrada):
        longitude, latitude = point
        properties = {
            "id": id, 
        }
        feature = geojson.Feature(
            geometry=geojson.Point((longitude, latitude)),
            properties=properties
        )
        entrada_geojson.append(feature)

    feature_collection = geojson.FeatureCollection(entrada_geojson)

    with open(filename, "w") as f:
        geojson.dump(feature_collection, f)

# Calcula e adiciona os pontos de acesso aos talhoes e às regiões ao grafo.
def generate_graph_with_access_points(talhoes, regioes, entrada_regioes, oficina_central, merged_roads):

    # Cria um grafo (NetworkX) a partir de dados geográficos (GeoJSON)
    # Merged roads = Custom + OSM roads = Vias internas às regiões 
    G = create_graph_from_geojson(merged_roads)
    # visualizar_grafo(G)

    # Gera id para os talhoes e regioes
    id_talhoes, id_regioes = generate_ids_talhoes_and_regioes(talhoes, entrada_regioes)
    
    # Gera centroides para representar os talhões
    centroides = generate_centroides_talhoes(id_talhoes, talhoes)
 
    # Acha arestas do grafo mais proximas dos centroides e os pontos da vias de acesso aos talhões. Inclui pontos de acesso dos talhoes no grafo e atualiza arestas.
    G, nearest_edges, entrada_talhoes = calculate_area_access_points(G, id_talhoes, centroides)

    # Plota os nós das arestas mais próximas dos centroides no mapa (se for talhao) ou nós de acesso às regioes(se for regiao), caso precise validar algo.
    # add_nearest_edges_map(G, nearest_edges, my_map)

    # Acha arestas do grafo mais proximas dos acessos às regioes. Pontos acesso às regiões já informados. Inclui pontos de acesso das regiões no grafo e atualiza arestas.
    G, nearest_edges, entrada_regioes_simp = calculate_area_access_points(G, id_regioes, entrada_regioes)
 
    return G, id_talhoes, id_regioes, centroides, entrada_talhoes, entrada_regioes_simp

# Inclui dados dos centróides dos talhões e pontos de acesso aos talhoes e às regiões ao grafo mapa.
def add_centroides_and_access_points_map(id_talhoes, id_regioes, centroides, entrada_talhoes, entrada_regioes_simp, my_map):
    
    # Adiciona os centroides ao mapa
    my_map = add_centroides_map(my_map, id_talhoes, centroides)

    # Plota os nós das vias mais próximas no mapa
    my_map = add_area_access_point_map(id_talhoes, entrada_talhoes, my_map, "green")
    my_map = add_area_access_point_map(id_regioes, entrada_regioes_simp, my_map, "gray")

    return my_map