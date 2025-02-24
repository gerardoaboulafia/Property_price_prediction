import pandas as pd

def eliminar_outliers(df, columna):
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    rango_inferior = Q1 - 1.5 * IQR
    rango_superior = Q3 + 1.5 * IQR * 1.1
    return df[(df[columna] >= rango_inferior) & (df[columna] <= rango_superior)]

def clean_data_outliers(data):
    casas = data[data['type'] == 'Casa']
    departamentos = data[data['type'] == 'Departamento']
    ph = data[data['type'] == 'PH']

    casas_limpio = eliminar_outliers(casas, 'price')
    departamentos_limpio = eliminar_outliers(departamentos, 'price')
    ph_limpio = eliminar_outliers(ph, 'price')

    data = pd.concat([casas_limpio, departamentos_limpio, ph_limpio], ignore_index=True)

    data = data[data['price'] >= 10000]
    data = data[~((data['type'] == 'Departamento') & (data['surface_total'] > 800))]
    data = data[~((data['bedrooms'] > 15) & (data['title'].str.contains('hotel', case=False)))]
    data = data[~(data['bedrooms'] > data['rooms_final'])]

    data = data[(data['price'] > 0) & (data['m2_final'] > 0) & (data['rooms_final'] > 0)]

    data['rooms_final'] = data.groupby('place_l3')['rooms_final'].transform(lambda x: x.fillna(x.mean()))
    data['m2_final'] = data.groupby('place_l3')['m2_final'].transform(lambda x: x.fillna(x.mean()))
    data['price'] = data.groupby('place_l3')['price'].transform(lambda x: x.fillna(x.mean()))
    data['distancia_subte_cercano'] = data.groupby('place_l3')['distancia_subte_cercano'].transform(lambda x: x.fillna(x.mean()))

    data = data.dropna(subset=['place_l3', 'type'])

    data = data.drop(['id', 'start_date', 'end_date', 'created_on', 'latitud', 'longitud', 'place_l2', 
                  'operation','rooms', 'bedrooms', 'surface_total', 'surface_covered', 
                  'title', 'm2_descripcion', 'rooms_total'], axis=1)



    return data
