# Encontrar o Ponto na reta mais próximo a um ponto de interesse
def find_closest_point_on_line(point_of_interest, line_point1, line_point2):
    x0, y0 = point_of_interest
    x1, y1 = line_point1
    x2, y2 = line_point2

    # Vetor da reta
    line_vector = (x2 - x1, y2 - y1)
    
    # Vetor do ponto de interesse para o primeiro ponto da reta
    point_vector = (x0 - x1, y0 - y1)

    line_vector_magnitude_squared = line_vector[0]**2 + line_vector[1]**2

    if line_vector_magnitude_squared == 0:
         # Handle the case where the line vector is a zero vector
        closest_point = point_of_interest
    else:
        # Projeto do ponto de interesse no vetor da reta
        t = (point_vector[0] * line_vector[0] + point_vector[1] * line_vector[1]) / (line_vector[0]**2 + line_vector[1]**2)

        # Limitar o valor de t para garantir que o ponto projetado esteja dentro do segmento
        t = max(0, min(t, 1))
        
        # Coordenadas do ponto mais próximo na reta
        closest_point = (x1 + t * line_vector[0], y1 + t * line_vector[1])
    
    return closest_point