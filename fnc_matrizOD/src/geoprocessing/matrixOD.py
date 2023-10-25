### Matriz OD Distancia
import networkx as nx
from src.geoprocessing.graphs import obtain_coord_path, check_nodes_in_graph
from src.geoprocessing.routes import get_directions_route

# Obtem informações de geradas das rotas entre 2 pontos.
def obtain_route_matrix(od, o, d, directions):
    od[(o, d)]={}
    od[(o, d)]['distance'] = directions['distance'] # distância em metros
    od[(o, d)]['time'] = directions['time'] # tempo em segundos
    od[(o, d)]['path'] = directions['coordinates'] 
    # print ('coords', directions['coordinates'])
    return od[(o, d)]

# Gera matriz OD menor distância, route_type = 'shortest', weight = 'length' ou 
# Gera matriz OD menor tempo, route_type = 'fastest', weight = 'time'
# Utilizando Network x e Grafo (no nossa caso, bases OSM  ou customizada)
def create_shortest_or_fastest_paths (G, nodes_origem, nodes_destino, route_type):

    if route_type=='shortest':
        weight='length'
        type_info = 'shortest matrix, info=dist'
    elif route_type=='fastest':
        weight='time'
        type_info = 'fastest matrix, info=time'

    shortest_or_fastest_paths = {} 

    # Calculate shortest paths and distances for all pairs of nodes within the subset
    for origem, destino in zip(nodes_origem, nodes_destino):
        coords_path=[]
        print ('origem -destino', origem, '-', destino)
        info, path = nx.single_source_dijkstra(G, origem, target=destino, weight=weight) #info = distance if shortest, time if fastest
        coords_path = obtain_coord_path(G, path)
        shortest_or_fastest_paths[(origem, destino)] = {'info': info, 'path': coords_path, 'type info':type_info}
    return shortest_or_fastest_paths 

# Gera matriz OD de distância entre regioes
# Utilizando informações do Azure Maps
def generate_matrix_od_btw_regions(id_regioes, entrada_regioes, route_type='fastest'):

    # Nesse caso, geraremos rotas de todos os pontos para todos os pontos. 
    # Porém nao há necessidade de gerar tudo para tudo, dependerá do plano de rotas.

    r_origins =  r_destinations = id_regioes

    coord_regioes = [(e["properties"]["y"],e["properties"]["x"]) for e in entrada_regioes]
    coord_r_origins = coord_r_destinations = coord_regioes

    od = {}
    for o, coord_o in zip(r_origins, coord_r_origins):
        for d, coord_d in zip(r_destinations, coord_r_destinations):
            if o != d:
                coords_od = [coord_o, coord_d]
                directions = get_directions_route(coords_od, client = 1, route_type=route_type)
                od[(o, d)] = obtain_route_matrix(od, o, d, directions)
    return od

# Gera matriz OD entre cada talhão e o ponto de entrada da sua região (e vice-versa) 
# Utilizando OpenStreetMaps + Vias customizadas
def generate_matrix_od_btw_plots_and_regions(G, id_talhoes, id_regioes, route_type):

    # Check se todos os nós estão presentes no grapho
    check_nodes_in_graph (G, id_regioes) #'R001_T001'
    check_nodes_in_graph (G, id_talhoes) #'R001'

    #  Na matriz os talhoes sao origens e destinos
    t_origens = t_destinos = id_talhoes

    # Sao identificadas as regioes referentes aos talhoes de origens e dos destinos
    r_origens = [t_o[:4] for t_o in t_origens] # A região de cada talhao é identificada nos 4 primeiros caracteres do id do talhao (ex. R001_T001)
    r_destinos = [t_d[:4] for t_d in t_destinos] # 

    # Create matrix od talhões - regioes 
    paths_t_r = create_shortest_or_fastest_paths (G, t_origens, r_origens, route_type)
    paths_t_r

    # Create matrix od regiões - talhões
    paths_r_t = create_shortest_or_fastest_paths (G, r_destinos, t_destinos, route_type)
    paths_r_t

    return paths_t_r, paths_r_t

# Gera matriz OD entre talhões da mesma região 
# Utilizando OpenStreetMaps + Vias customizadas

def generate_matrix_od_btw_plots_inside_regions(G, id_talhoes, route_type='fastest'): # route_type = shortest or fastest
 
    #  Na matriz os talhoes sao origens e destinos
    t_origens = []
    t_destinos = []

    for t1 in id_talhoes:
        for t2 in id_talhoes:
            if t1[:4]==t2[:4] and t1!=t2:
                t_origens.append(t1)
                t_destinos.append(t2)
    
    # Adicionar pares onde t1 é igual a t2 com o valor zero
    for t in id_talhoes:
        t_origens.append(t)
        t_destinos.append(t)

    # Create matrix od talhões - talhões
    paths_t_t_inside_regions = create_shortest_or_fastest_paths (G, t_origens, t_destinos, route_type) 

    return paths_t_t_inside_regions

# Gera matriz OD completa: entre talhão - região(OSM + Custom), região - região(Azure) - região - talhão(OSM + Custom) 
# Função utilizada para:
#    shortest path, retornando matriz distância
#    fastest path, retornando matriz tempo
def generate_matrix_od_complete(G, id_talhoes, paths_t_r, paths_r_r, paths_r_t, paths_t_t_inside_regions, route_type='fastest'): # route_type = shortest or fastest

   #  Na matriz os talhoes sao origens e destinos
    t_origens = t_destinos = id_talhoes
    
    if route_type=='shortest':
        info_r_r = 'distance'
    elif route_type=='fastest':
        info_r_r = 'time'

    matrix_od={}
    path_od={}
    matrix_od_intern={}
    path_od_intern={}
    matrix_od_extern={}
    path_od_extern={}
    
    for t_origem in t_origens:
        for t_destino in t_destinos: 
            matrix_od[(t_origem, t_destino)]={}
            path_od[(t_origem, t_destino)]={}
            # Se regiao de origem = regiao de destino, matriz interna
            if t_origem[:4]==t_destino[:4]:
                print (t_origem, '->',t_destino)
                matrix_od_intern[(t_origem, t_destino)] = paths_t_t_inside_regions[(t_origem, t_destino)]['info']
                path_od_intern[(t_origem, t_destino)] = paths_t_t_inside_regions[(t_origem, t_destino)]['path']
                
            # Caso contrario, matriz externa
            else:
                r_origem = t_origem[:4]
                r_destino = t_destino[:4]
                print (t_origem, '->',r_origem, '->',r_destino, '->',t_destino)
                matrix_od_extern[(t_origem, t_destino)] = paths_t_r[(t_origem, r_origem)]['info']+ paths_r_r[(r_origem, r_destino)][info_r_r]+paths_r_t[(r_destino, t_destino)]['info'] # info = 'distance' se shortes_path ou 'time' se fastest_path
                path_od_extern[(t_origem, t_destino)] = paths_t_r[(t_origem, r_origem)]['path']+ paths_r_r[(r_origem, r_destino)]['path']+ paths_r_t[(r_destino, t_destino)]['path'] 
    
    matrix_od = {**matrix_od_intern, **matrix_od_extern}
    # print ('Matrix OD:', matrix_od)
    path_od = {**path_od_intern, **path_od_extern}
    # print ('Path OD:', path_od)

    return matrix_od, path_od

def generate_matrix_od(G, id_talhoes, id_regioes, entrada_regioes, route_type):

    # Check se todos os nós estão presentes no grapho
    check_nodes_in_graph (G, id_regioes) #'R001_T001'
    check_nodes_in_graph (G, id_talhoes) #'R001'
    
    # test_and_simulate_unconnected_network_locations(G, source_node = 'R003_T003', target_node = 'R003_T002')

    paths_r_r = generate_matrix_od_btw_regions(id_regioes, entrada_regioes, route_type)
    paths_t_r, paths_r_t = generate_matrix_od_btw_plots_and_regions(G, id_talhoes, id_regioes, route_type)
    paths_t_t_inside_regions = generate_matrix_od_btw_plots_inside_regions(G, id_talhoes, route_type)
    matrix_od, path_od = generate_matrix_od_complete(G, id_talhoes, paths_t_r, paths_r_r, paths_r_t, paths_t_t_inside_regions, route_type)
    return matrix_od, path_od

# Raschunho, caso seja necessário:
# def calculate_time_shortest_path(shortest_path):
# # Inicializa a variável para armazenar o tempo total
#     total_time = 0

#     # Inicializa uma lista para armazenar informações de tempo ao longo do caminho
#     time_info = []

#     # Itera pelas arestas no caminho mais curto
#     for i in range(len(shortest_path) - 1):
#         origem = shortest_path[i]
#         destino = shortest_path[i + 1]

#         # Obtém o tempo associado a esta aresta (substitua 'tempo' pelo nome correto do atributo)
#         edge_time = graph[origem][destino]['tempo']

#         # Adiciona o tempo desta aresta ao tempo total
#         total_time += edge_time

#         # # Adiciona informações de tempo ao longo do caminho
#         # time_info.append({
#         #     'origem': origem,
#         #     'destino': destino,
#         #     'tempo': edge_time
#         # })

#     # Retorna o caminho mais curto e informações de tempo
#     return {
#         'caminho_mais_curto': shortest_path,
#         'tempo_total': total_time,
#         # 'informacoes_tempo': time_info
#     }

# def calculate_distance_fastest_path(fastest_path):
#     # Inicializa a variável para armazenar a distância total
#     total_distance = 0

#     # Itera pelas arestas no caminho mais rápido
#     for i in range(len(fastest_path) - 1):
#         origem = fastest_path[i]
#         destino = fastest_path[i + 1]

#         # Obtém a distância associada a esta aresta (substitua 'distancia' pelo nome correto do atributo)
#         edge_distance = graph[origem][destino]['distancia']

#         # Adiciona a distância desta aresta à distância total
#         total_distance += edge_distance

#     # Retorna o caminho mais rápido e a distância total
#     return {
#         'caminho_mais_rapido': fastest_path,
#         'distancia_total': total_distance
#     }