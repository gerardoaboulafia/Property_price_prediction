import re
import pandas as pd
import numpy as np

# Función que utiliza RegEx para encontrar el número de ambientes.
def find_numbers(x_column, x_word, data):
    """ La función busca en la columna especificada de df la
        palabra deseada y toma el número que la precede. La idea es utilizar
        title|description como columnas y amb|dorm|hab como palabras.
    """
    fix_dict = {
        'un':'1', 'Un':'1', 'UN':'1',
        'mono':'1', 'Mono':'1', 'MONO':'1',
        'dos':'2', 'Dos':'2', 'DOS':'2',
        'tres':'3', 'Tres':'3', 'TRES':'3',
        'cuatro':'4', 'Cuatro':'4', 'CUATRO':'4',
        'cinco':'5', 'Cinco':'5', 'CINCO':'5',
        'seis':'6', 'Seis':'6', 'SEIS':'6',
        'siete':'7', 'Siete':'7', 'SIETE':'7',
        'ocho':'8', 'Ocho':'8', 'OCHO':'8',
        'nueve':'9', 'Nueve':'9', 'NUEVE':'9'
    }

    # Ajustar patrón para que busque también números y el término completo (ej. "3 ambientes")
    pattern = re.compile(r'(?i)(?P<amb>(\w+|\d+))\s*' + x_word)

    re_amb = data[x_column].apply(lambda x: pattern.search(str(x)))
    match_amb = re_amb.apply(lambda x: x.group('amb') if x else None)

    # Reemplazo de palabras por números
    match_amb.replace(fix_dict, inplace=True)
    match_amb.fillna('', inplace=True)
    mask_numeric = match_amb.apply(lambda x: x.isnumeric())
    match_amb[~mask_numeric] = np.nan
    return match_amb

# Función para llenar rooms_total
def fill_rooms_total(x_rooms_total, x_column, x_word, data):
    """ Llenado del totalizador 'rooms_total' con la combinación correcta de
        title|description como columnas y amb|dorm|hab como palabras.
    """
    rooms_partial = find_numbers(x_column, x_word, data)

    if x_word == 'ambientes':
        # Convertir directamente a números, reemplazando valores no numéricos con NaN
        rooms_partial = pd.to_numeric(rooms_partial, errors='coerce')
    else:
        # Convertir directamente a números y sumar 1, reemplazando valores no numéricos con NaN
        rooms_partial = pd.to_numeric(rooms_partial, errors='coerce') + 1

    x_rooms_total.fillna(rooms_partial, inplace=True)
    return x_rooms_total

# Función principal para extraer características usando RegEx
def extract_features_regex(data):
    # Inicialización del contador de rooms_total
    rooms_total = pd.Series([np.nan for _ in data.rooms])

    # Llamados con las diferentes combinaciones con la función mejorada
    rooms_total = fill_rooms_total(rooms_total, 'title', 'ambientes', data)
    rooms_total = fill_rooms_total(rooms_total, 'title', 'dorm', data)
    rooms_total = fill_rooms_total(rooms_total, 'title', 'hab', data)

    # Búsqueda de monoambientes
    pattern_mono = re.compile('(?i)monoambiente')
    re_amb_mono = data['title'].astype(str).apply(lambda x: pattern_mono.search(x))
    rooms_partial_mono = re_amb_mono.apply(lambda x: 1 if x is not None else None)
    rooms_total.fillna(pd.Series(rooms_partial_mono), inplace=True)

    # Guardar el resultado final en el DataFrame
    data.loc[:, 'rooms_total'] = rooms_total

    # Crear una nueva columna 'rooms_final' que sea igual a 'rooms'
    data.loc[:, 'rooms_final'] = data['rooms']

    # Reemplazar los valores nulos en 'rooms_final' con los valores de 'rooms_total'
    data.loc[:, 'rooms_final'] = data['rooms_final'].fillna(data['rooms_total'])

    # Creamos un patrón para encontrar los metros cuadrados en la columna de descripción.
    patron_m2 = r"(\d{2,5})(\s)?(m|mt|mts|metros)(\s)?(2)?"
    patron_m2_regex = re.compile(patron_m2, re.IGNORECASE)

    # Convertimos la columna 'title' a tipo string si no lo es ya.
    title_series = data['title'].astype(str)

    # Utilizamos una función lambda para buscar el patrón en cada título.
    # Extraemos solo el número (grupo 1)
    m2_totales = title_series.apply(lambda x: patron_m2_regex.search(x))

    # Extraemos los valores encontrados que no son nulos y aplicamos una función lambda para obtener el número (grupo 1).
    m2_totales = m2_totales[m2_totales.notnull()].apply(lambda x: x.group(1))

    # Asignamos los valores extraídos a una nueva columna 'm2_descripcion' en el DataFrame, y convertimos a tipo numérico.
    data.loc[:, 'm2_descripcion'] = m2_totales.astype(float)

    # Crear una nueva columna 'm2_final' que sea igual a surface_total
    data.loc[:, 'm2_final'] = data['surface_total']

    # Reemplazar los valores nulos en 'm2_final' con los valores de 'm2_descripcion'
    data.loc[:, 'm2_final'] = data['m2_final'].fillna(data['m2_descripcion'])

    return data