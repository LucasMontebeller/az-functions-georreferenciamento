import pickle

# Salva grafo em arquivo pickle
def save_graph(G, filename): 
    pickle.dump(G, open(filename, 'wb'))

# Carrega grafo de arquivo pickle
def load_graph(filename): 
    try:
        G = pickle.load(open(filename, 'rb'))
    except IOError:
        print('File not found')
        G = {}
    return G