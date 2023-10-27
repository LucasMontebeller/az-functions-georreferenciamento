from haversine import haversine
import osmnx as ox
import geopandas as gpd
import pandas as pd
import networkx as nx
from shapely.geometry import Point, LineString
from src.geoprocessing.distances import find_closest_point_on_line
from src.geoprocessing.speeds import calculate_avg_speed
from src.geoprocessing.routes import process_coordinates

# Extrai coordenadas 'x' e 'y' dos nós do grafo e calcula distância Harversine 
def calculate_harversine_distance (G, start_node, end_node):

    # Extract 'x' and 'y' coordinates from the nodes' attributes
    start_x = G.nodes[start_node]['x']
    start_y = G.nodes[start_node]['y']
    end_x = G.nodes[end_node]['x']
    end_y = G.nodes[end_node]['y']

    # Calculate Haversine distance
    distance = haversine((start_y, start_x), (end_y, end_x))

    return distance

# Adicionar arestas ao grafo, observando os sentidos da via, de acordo com informação do atributo oneway
def add_edge_all_directions(G, start_node, end_node, oneway, highway, surface, lanes, maxspeed, source):

    # Add edge with Haversine distance attribute
    length = calculate_harversine_distance (G, start_node, end_node)
    avg_speed = calculate_avg_speed(highway, surface, lanes, maxspeed, source)

    G.add_edge(start_node, end_node, key=0, length=length, highway=highway, surface=surface, lanes=lanes, maxspeed=maxspeed, avg_speed= avg_speed, time = (length/avg_speed if avg_speed>0 else 999), source=source)

    # Adicionar as arestas ao grafo - sentido contrário
    if oneway != 'yes':
   
         # Add edge with Haversine distance attribute
         G.add_edge(end_node, start_node, key=0, length=length, highway=highway, surface=surface, lanes=lanes, maxspeed=maxspeed, avg_speed= avg_speed, time = (length/avg_speed if avg_speed>0 else 999), source=source)
    
    return G

# Cria um MultiDiGraph a partir de nós e arestas de vias em um GeoDataframe
def create_graph_from_nodes_edges(gdf):

    # Criar um grafo vazio
    G = nx.MultiDiGraph(crs="EPSG:4326")

    # Dicionário para mapear coordenadas para IDs de nós
    coord_to_node = {}

    # Iterar sobre as geometrias das vias no GeoDataFrame
    for index, row in gdf.iterrows():
        geometry = row['geometry']
        oneway = row['oneway']
        highway = row['highway']
        surface = row['surface']
        lanes = row['lanes']
        maxspeed = row['maxspeed']
        source = 'custom' if 'custom_road' in row['path'] else 'osm'

        if geometry.geom_type == 'MultiLineString':
            lines = geometry.geoms # Converte em LineStrings
        else:
            lines = [geometry] # Se LineStrings
        
        # Iterar sobre as geometrias das vias no GeoDataFrame
        for line in lines:
            points = list(line.coords)
            
            # Obter os pontos (nós) da geometria da via e adicioná-los ao grafo
            for point_coords in points:
                if point_coords not in coord_to_node:
                    node_id = len(coord_to_node)
                    x, y = point_coords  # Extract x and y from the coordinates
                    G.add_node(node_id, x=x, y=y) 
                    coord_to_node[point_coords] = node_id
            
            # Adicionar as arestas ao grafo
            for start_coords, end_coords in zip(points[:-1], points[1:]):
                G = add_edge_all_directions(G, coord_to_node[start_coords], coord_to_node[end_coords], oneway, highway, surface, lanes, maxspeed, source)
    return G

# Cria um grafo (NetworkX) a partir de dados geográficos (GeoJSON)
# Merged roads = Custom + OSM roads = Vias internas às regiões 
def create_graph_from_geojson(merged_roads):
    gdf = gpd.GeoDataFrame.from_features(merged_roads)
    return create_graph_from_nodes_edges(gdf)

def visualizar_grafo(G):
    # Visualizar o grafo
    gdf_map = ox.graph_to_gdfs(G)
    ox.graph_to_gdfs(G, nodes=False).explore()

# Dados os vertices, obtem geometria da aresta
def obtem_geometria_aresta(G, edge):
    u, v = edge
    u_coords = (G.nodes[u]['x'], G.nodes[u]['y']) # x,y
    v_coords = (G.nodes[v]['x'], G.nodes[v]['y'])
    
    # Geometria da aresta como um segmento de linha
    geometria_aresta = LineString([u_coords, v_coords]) 
    return geometria_aresta

# Função para verificar se a aresta passa pelo ponto
def check_aresta_contains_node(G, edge, node):

     # Geometria da aresta como um segmento de linha
    geometria_aresta = obtem_geometria_aresta(G, edge) #u,v = edge 

    # Nó para verificar
    no = Point(node)

    # Verificar a distância entre o ponto e a geometria da aresta
    distancia = geometria_aresta.distance(no)

    # Defina uma tolerância para considerar que a aresta passa pelo ponto
    tolerancia = 0.1

    # Verificar se a distância está dentro da tolerância
    if distancia <= tolerancia:
        return True
    else:
        return False
    
def split_and_update_edges(G, id_talhao, edge, new_node, oneway, highway, surface, lanes, maxspeed, source):

    check = check_aresta_contains_node(G, edge, new_node) 
    if check == False:
        print(f'Atenção! O nó {new_node} não está dentro da aresta {edge}')
    else:
        G.remove_edge(*edge)  # Remover a aresta original
        u, v = edge
        G.add_node(id_talhao, x= new_node[0], y= new_node[1])
        G = add_edge_all_directions(G, u, id_talhao, oneway, highway, surface, lanes, maxspeed, source)
        G = add_edge_all_directions(G, id_talhao, v, oneway, highway, surface, lanes, maxspeed, source)
    return G

# Encontra arestas do grafo mais proximas dos centróides e acha os pontos de acesso aos tallhões nas vias.
# Inlui esses pontos de acesso aos talhões no grafo como nós e atualiza as arestas para considerarem esses nós.
def  calculate_area_access_points(G, id_areas, nodes):
# nodes podem ser centroides dos talhoes ou pontos de acesso nas vias (que serão conferidos e inclusos no grafo)
# centroide: (node.x, node.y)
    nearest_edges = []
    nearest_points_on_edges = []

    for id_area, node in zip(id_areas, nodes):

        # Encontre as coordenadas dos nós que definem a aresta mais próxima
        x, y = process_coordinates(node)
        nearest_edge = ox.distance.nearest_edges(G, x, y)

        u, v = nearest_edge
        u_coords = (G.nodes[u]['x'], G.nodes[u]['y']) # x,y
        v_coords = (G.nodes[v]['x'], G.nodes[v]['y'])
        oneway='yes'
        highway = G[u][v][0]['highway']
        surface = G[u][v][0]['surface']
        lanes = G[u][v][0]['lanes']
        maxspeed = G[u][v][0]['maxspeed']
        source = G[u][v][0]['source']
        if G.has_edge(v, u, key=0):
            oneway = 'no'

        # Acha o ponto de acesso das areas na via (aresta) mais próxima
        nearest_point_on_edge = find_closest_point_on_line((x, y), u_coords, v_coords)

        # Inlui o nó no grafo e atualiza as arestas
        G = split_and_update_edges(G, id_area, nearest_edge, nearest_point_on_edge, oneway, highway, surface, lanes, maxspeed, source)

        nearest_edges.append(nearest_edge)
        nearest_points_on_edges.append(nearest_point_on_edge)

    return G, nearest_edges, nearest_points_on_edges

# Verifica se todos os nós estão presentes no Grafo G
def check_nodes_in_graph (G, id_nodes):
    # G.nodes[0]['x'], G.nodes[0]['y'] long, lat
    # entrada_regioes[0]['properties']['x'], entrada_regioes[0]['properties']['y']
    # entrada_talhoes[0][0], entrada_talhoes[0][1]

    all_nodes_ids_present = all(node in G.nodes for node in id_nodes)
    
    if not all_nodes_ids_present:
        return False
    
    return True


def all_data_fields(G):

    all_data_fields = set()

    # Percorra os dicionários contidos na coluna 'data' e adicione suas chaves ao conjunto
    for u, v, data in G.edges(data=True):
        all_data_fields.update(data.keys())

    # Converta o conjunto em uma lista (se preferir)
    all_data_fields_list = list(all_data_fields)

    return all_data_fields_list

# Obtain coordenadas dos nós do caminho
def obtain_coord_path(G, path):
    coords = [[G.nodes[node]['y'], G.nodes[node]['x']] for node in path]
    return coords

# Gera tabelas com informações das arestas e nós dos grafos
def generate_graph_tables(G, fields):
    
    # # # Create a list of edges and nodes and their attributes
    edges_data = [(u, v, data) for u, v, data in G.edges(data=True)]
    nodes_data = [(farm_id, coords['x'], coords['y']) for farm_id, coords in G.nodes(data=True)]
    
    # Create a DataFrame with the edge data
    edges_df = pd.DataFrame(edges_data, columns=['u', 'v', 'data'])
    nodes_df = pd.DataFrame(nodes_data, columns=['farm_id', 'x', 'y'])

    # Adicione colunas específicas do dicionário 'data' como colunas no DataFrame
    for field in fields:
        edges_df[field] = edges_df['data'].apply(lambda data: data.get(field))
        
    return edges_df, nodes_df

# Imprime o comprimento de cada edge
def print_weights_edges(G):
    for u, v, data in G.edges(data=True):
        print(f"Aresta de {u} para {v}, Peso: {data.get('length', 'N/A')}")

# Função para analisar dados relacionados à velocidade das arestas de um grafo
def analyze_graph(G, fields):
    # Gerar tabelas de arestas e nós a partir do grafo
    fields=all_data_fields(G)
    edges_df, nodes_df = generate_graph_tables(G, fields)
    print(edges_df.head())
    osm_df = edges_df[edges_df['source'] == 'osm']
    custom_df = edges_df[edges_df['source'] == 'custom']
    df = edges_df # selecione se quiser analisar dados de uma fonte específica (customizada ou open street map)

    # Imprimir o número de estradas OSM, estradas personalizadas e o total de estradas
    print('Len OSM roads, Custom roads, Total:', len(osm_df), '+', len(custom_df), '=', len(edges_df), '\n')
    # df.describe()
    # df.info()

    print()
    
    # Imprimir contagem de tipos de rodovias e o número de valores nulos
    print(df['highway'].value_counts(), '\n\nHighway Null:', df[df['highway'].isnull()]['u'].count(), '\n')
    print(df['surface'].value_counts(), '\n\nSurface Null:', df[df['surface'].isnull()]['u'].count(), '\n')
    print(df['lanes'].value_counts(), '\n\nLanes Null:', df[df['lanes'].isnull()]['u'].count(), '\n')

    # Calcular o total de linhas na tabela original
    total_rows = df.shape[0]

    # Agrupar por 'source', 'highway', 'maxspeed', 'surface' e 'lanes' e contar as ocorrências
    speed_df = df.groupby(['source', 'highway', 'maxspeed', 'surface', 'lanes'], dropna=False).size().reset_index(name='total')

    # Calcular o total de ocorrências nas combinações únicas
    total_rows_grouped = speed_df['total'].sum()

    # Criar uma DataFrame para a linha de total
    total_row = pd.DataFrame({'highway': ['Total'], 'maxspeed': ['-'], 'surface': ['-'], 'lanes': ['-'],
                             'total': [total_rows_grouped]})

    # Concatenar a linha de total ao DataFrame agrupado
    speed_df_t = pd.concat([speed_df, total_row], ignore_index=True)

    # Verificar se o total agrupado bate com o total de linhas da tabela original
    if total_rows_grouped == total_rows:
        print("Totais batem!")
    else:
        print("Totais não batem!")

    print(speed_df_t)

# Para chamar a função, passe os argumentos apropriados para `generate_graph_tables` e `fields`:
# analyze_graph(G, fields)