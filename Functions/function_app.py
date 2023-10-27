import azure.functions as func
import logging
from src.api.matrizOD_api import process_matrizOD
from src.api.map_api import generate_az_map

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="function")
def get_matrizOD(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        action = req.params.get('action') # vem da url por query string function?action=''

        # GET
        if req.method == 'GET':
            if action == 'map':
                map = generate_az_map()
                map_html = map.get_root().render()
                return func.HttpResponse(map_html, mimetype="text/html")
        
        # POST
        elif req.method == 'POST':
            # req_body = req.get_body()

            if action == 'matrizOD':
                tipo = req.headers.get("tipo")
                resp_body = process_matrizOD(tipo)
                # dando ruim no generate_matrix_od_btw_regions
                if resp_body is None:
                    return func.HttpResponse("Não foi possível processar a matriz OD, verifique o tipo passado no cabeçalho da requisição.", status_code=400)

                return func.HttpResponse(body=resp_body, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
    except:
        # Registrar auditoria aqui
        return func.HttpResponse(
                "Falha ao processar rota, verifique a url especificada ou tente novamente mais tarde.",
                status_code=400
            )