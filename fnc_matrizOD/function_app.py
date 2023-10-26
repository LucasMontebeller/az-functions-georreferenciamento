import azure.functions as func
import logging
import pickle
from src.api.matrizOD_api import process_matrizOD
from src.api.map_api import generate_az_map

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="get-matrizOD")
def get_matrizOD(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    action = req.params.get('action') # vem da url get-matrizOD?action=''

    # GET
    if req.method == 'GET':
        if action == 'map':
            map = generate_az_map()
            map_html = map.get_root().render()
            return func.HttpResponse(map_html, mimetype="text/html")
    
    # POST
    elif req.method == 'POST':
        # op = req.params.get('op')
        # body = process_matrizOD(op)
        with open('src/mock/graph.pickle', 'rb') as file:
            data = pickle.load(file)
        return func.HttpResponse(pickle.dumps(data), mimetype='application/octet-stream')
        # return func.HttpResponse(body=body, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")  
        
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )