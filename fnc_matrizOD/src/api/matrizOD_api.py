import os
import pandas as pd
from io import BytesIO
from src.utils.json_utils import save_dict_json, save_json
from src.geoprocessing.matrixOD import generate_matrix_od
from src.tests.scenarios import read_scen_complete

# Envio de arquivo - matriz OD distância
def process_matrizOD(op):
    if op == 'op3' or op=='op5':
        if op == 'op3':
            route_type = 'shortest'
            msg = 'shortest matrix, info=dist'
        elif op == 'op5':
            route_type = 'fastest'
            msg = 'fastest matrix, info=dist'
        
        # read data
        G, id_talhoes, id_regioes, entrada_regioes = read_scen_complete()
        
        # Criar Matriz OD distância
        matrix_od, path_od = generate_matrix_od(G, id_talhoes, id_regioes, entrada_regioes, route_type)
        print ('OD:', matrix_od)
        save_dict_json(matrix_od, os.path.join('output', 'matrix', route_type, 'matrix_od.json'))
        save_dict_json(path_od, os.path.join('output', 'matrix', route_type, 'path_od.json'))
        save_json(msg, os.path.join('output', 'matrix', route_type, 'info.json'))
        print (f"A matriz OD foi salve na pasta {os.path.join('output', 'matrix', route_type)}!")
        
        # Combinado de salvar matriz completa para melhorar performance
        # Se quiser reduzir espaço de armazenagem, salvar shortest_paths_t_r, shortest_paths_r_r, shortest_paths_r_t

        # Converter as chaves (tuplas) para strings
        matrix_dic_serializavel = {str(key): value for key, value in matrix_od.items()}

        # Em JSON
        # Usando json.dumps() para converter a matriz em JSON
        # matrix_od_json = json.dumps(matrix_dic_serializavel)
        
        # Define os cabeçalhos da resposta
        # headers = {
        #     "Content-Type": "application/json",
        #     "Content-Disposition": "attachment; filename=output/matrix_od.json"
        #     }

        # # Retorna a matriz em JSON e o arquivo Excel como resposta
        # return func.HttpResponse(body=matrix_od_json, headers=headers, mimetype="application/json")

        # Em Excel
        # Processar os dados para criar a estrutura adequada
        origens = []
        destinos = []
        data = {}

        for key, value in matrix_dic_serializavel.items():
            origem, destino = eval(key)  # Converter a chave em tupla de forma segura
            origens.append(origem)
            destinos.append(destino)
            if origem not in data:
                data[origem] = {}
            data[origem][destino] = value

        # Criar um DataFrame pandas diretamente com colunas e índices personalizados
        df = pd.DataFrame(data).T

        # Criar um objeto BytesIO para armazenar os dados do Excel
        excel_bytes_io = BytesIO()

        # Salvar o DataFrame no objeto BytesIO no formato Excel
        df.to_excel(excel_bytes_io, index=True, header=True, engine='openpyxl')

        # Salvar o objeto BytesIO em um arquivo Excel local
        save_bitesIO_to_excel(excel_bytes_io, os.path.join('output','matrix',route_type,'matrix_od.xlsx'))

        # Configure os cabeçalhos da resposta
        excel_headers = {
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Tipo de conteúdo Excel
        "Content-Disposition": "attachment; filename=output/matrix_od.xlsx"  # Nome do arquivo Excel
        }

    return excel_bytes_io.getvalue(), excel_headers        

def save_bitesIO_to_excel(excel_bytes_io, filename):
    with open(filename, 'wb') as f:
        f.write(excel_bytes_io.getvalue())     
