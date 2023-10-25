import pandas as pd

# Calcula velocidade média - observar que será necessário rever de acordo com os dados a tabela speed_df
# speed_df não deve ter valores duplicados para a combinacao highway, surface, lanes, maxspeed, source
def calculate_avg_speed(highway, surface, lanes, maxspeed, source):
    
    # Carregue DataFrame com premissas
    speed_df = pd.read_csv('input/speed_df.csv')

    # Use os parâmetros para filtrar os dados da tabela e retornar a velocidade
    filtro = (speed_df['source'] == source) & \
             (speed_df['highway']=="Nulo" if highway is None else speed_df['highway'] == highway) & \
             (speed_df['maxspeed']=="Nulo" if maxspeed is None else speed_df['maxspeed'] == maxspeed) & \
             (speed_df['surface']=="Nulo" if surface is None else speed_df['surface'] == surface) & \
             (speed_df['lanes']=="Nulo" if lanes is None else speed_df['lanes'] == lanes)
    filtered_data = speed_df.loc[filtro]

    if not filtered_data.empty:
        avg_speed = filtered_data['avg_speed'].values[0]  # Obtém o primeiro valor de avg_speed
        return avg_speed
    else:
        print ('avg = None. Atenção verificar vias sem velocidade!!!!', highway, surface, lanes, maxspeed, source)
        return None