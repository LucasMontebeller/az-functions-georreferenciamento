import azure.functions as func
import logging
from src.api.matrizOD_api import process_matrizOD

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="get-matrizOD")
def get_matrizOD(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    
    # Teste de funcionamento
    elif req.method == 'POST':
        op = req.params.get('op')
        body = process_matrizOD(op)
        return func.HttpResponse(body=body, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")  
        
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )