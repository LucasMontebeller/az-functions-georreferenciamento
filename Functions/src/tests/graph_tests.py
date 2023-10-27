import networkx as nx

# Teste para simular locais não conexos na rede
def test_and_simulate_unconnected_network_locations(G, source_node = 'R003_T003', target_node = 'R003'):
    if nx.has_path(G, source_node, target_node):
        print(f"There is a path from {source_node} to {target_node}.")
    else:
        print(f"No path from {source_node} to {target_node} found.")
    # id = source_node
    # folium.Marker(location=[G.nodes[id]['y'], G.nodes[id]['x']], popup=f"{id}", icon=folium.Icon(color="red",icon="home")).add_to(my_map)
    # if source_node in G:
    #     sucessores = list(G.successors(source_node))
    #     print(sucessores)
    # for s in sucessores:
    #     print(s)
    #     folium.Marker(location=[G.nodes[s]['y'], G.nodes[s]['x']], popup=f"{s}", icon=folium.Icon(color="blue",icon="home")).add_to(my_map) 
    #     n=0
    #     id = sucessores[n] # selecione o sucessor da direcao que voce quer analisar o, 1...etc
    #     print(f'next id[{n}] = {id}')
    #     my_map