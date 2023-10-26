from src.geoprocessing.maps import create_map
from src.tests.scenarios import read_scen_data

def generate_az_map():
    talhoes, regioes, entrada_regioes, oficina_central, merged_roads = read_scen_data()
    map = create_map(talhoes, regioes, entrada_regioes, oficina_central, merged_roads)
    return map