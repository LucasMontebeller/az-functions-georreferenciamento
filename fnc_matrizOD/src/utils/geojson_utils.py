import geojson

# Carrega dados de um arquivo GeoJSON
def load_geojson(arquivo):
    with open(arquivo) as f:
        return geojson.load(f)['features']

# Salva lista de pontos em GeoJSON
def save_geojson(points, filename): 

    geojson_data = geojson.FeatureCollection([geojson.Feature(geometry=geojson.Point((p.x, p.y))) for p in points])

    with open(filename, 'w') as f:
        geojson.dump(geojson_data, f)