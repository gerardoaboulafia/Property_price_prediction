import pandas as pd

def flag_outliers(df):
    price_upper_bound = 1500000
    price_lower_bound = 20000

    rooms_upper_bound = 15
    rooms_lower_bound = 1

    surface_upper_bound = 500
    surface_lower_bound = 20

    # --- Precio ---
    mask_price_low = df['price'] < price_lower_bound
    mask_price_high = df['price'] > price_upper_bound
    df.loc[mask_price_low, 'flag'] = df.loc[mask_price_low, 'flag'].fillna('') + 'Price too low; '
    df.loc[mask_price_high, 'flag'] = df.loc[mask_price_high, 'flag'].fillna('') + 'Price too high; '

    # --- Ambientes ---
    mask_rooms_low = df['rooms'] < rooms_lower_bound
    mask_rooms_high = df['rooms'] > rooms_upper_bound
    df.loc[mask_rooms_low, 'flag'] = df.loc[mask_rooms_low, 'flag'].fillna('') + 'Not enough rooms; '
    df.loc[mask_rooms_high, 'flag'] = df.loc[mask_rooms_high, 'flag'].fillna('') + 'Too many rooms; '

    # --- Superficie ---
    mask_surface_low = df['surface'] < surface_lower_bound
    mask_surface_high = df['surface'] > surface_upper_bound
    df.loc[mask_surface_low, 'flag'] = df.loc[mask_surface_low, 'flag'].fillna('') + 'Surface too small; '
    df.loc[mask_surface_high, 'flag'] = df.loc[mask_surface_high, 'flag'].fillna('') + 'Surface too large; '

    # Limpiar separadores y normalizar flags vacíos a None
    df['flag'] = df['flag'].str.rstrip('; ').replace({'': None})

    return df


def clean_data_outliers(data):
    data = flag_outliers(data)
    data['rooms_final'] = data.groupby('l3')['rooms_final'].transform(lambda x: x.fillna(x.mean()))
    data['m2_final'] = data.groupby('l3')['m2_final'].transform(lambda x: x.fillna(x.mean()))
    data['distancia_subte_cercano'] = data.groupby('l3')['distancia_subte_cercano'].transform(lambda x: x.fillna(x.mean()))
    return data
