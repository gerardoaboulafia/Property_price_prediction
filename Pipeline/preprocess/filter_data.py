def filter_by_currency_place(data):
    # Initialize flag column
    data['flag'] = ''
    
    # Create separate flag conditions
    currency_flag = data['currency'] != 'USD'
    location_flag = data['l2'] != 'Capital Federal'
    property_type_flag = ~data['type'].isin(['Departamento', 'Casa', 'PH'])
    
    # Build flag messages by combining conditions
    data.loc[currency_flag, 'flag'] += 'Non-USD currency; '
    data.loc[location_flag, 'flag'] += 'Not in Capital Federal; '
    data.loc[property_type_flag, 'flag'] += 'Invalid property type; '
    
    # Remove trailing semicolon and space
    data['flag'] = data['flag'].str.rstrip('; ')
    
    # Set empty strings to None for rows with no flags
    data.loc[data['flag'] == '', 'flag'] = None
    
    return data
