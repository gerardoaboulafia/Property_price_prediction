def filter_by_currency_place(data):
    # Filtrar por moneda USD y ubicaciones en Capital Federal
    data = data[(data['property_currency'] == 'USD') & (data['place_l2'] == 'Capital Federal')]
    # Filtrar por tipos de propiedad
    data = data[data['property_type'].isin(['Departamento', 'Casa', 'PH'])]
    data.columns = data.columns.str.replace('property_', '')

    return data
