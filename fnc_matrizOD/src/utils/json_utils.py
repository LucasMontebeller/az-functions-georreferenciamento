import json 

# Salve string ou lista em arquivo JSON
def save_json(info, filename):
    with open(filename, 'w') as f:
        json.dump(info, f)

# Salve dicionário em arquivo JSON
def save_dict_json(dict, filename):

    # Convertendo as chaves para strings (necessário quando houver tuplas)
    dict_str_keys = {str(key): value for key, value in dict.items()}

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dict_str_keys, f, ensure_ascii=False, indent=4)

# Carregue dicionário ou lista de um arquivo JSON
def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

    except IOError:
        print('File not found')
        data = {}
    return data