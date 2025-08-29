def filter_by_currency_place(data):
    # Filtrar por moneda USD y ubicaciones en Capital Federal
    data = data[(data['currency'] == 'USD') & (data['l2'] == 'Capital Federal')]
    # Filtrar por tipos de propiedad
    data = data[data['type'].isin(['Departamento', 'Casa', 'PH'])]

    return data
