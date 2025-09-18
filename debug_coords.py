#!/usr/bin/env python3
"""
Debug script to test coordinate transformation
"""

import pandas as pd
import sys
from pathlib import Path

# Add the Pipeline directory to the Python path
pipeline_dir = Path(__file__).parent / "Pipeline"
sys.path.append(str(pipeline_dir))

from preprocess.filter_data import filter_by_currency_place
from preprocess.regex_extraction import extract_features_regex
from preprocess.geo_validation_fixed import validate_geo

# Test coordinates for Palermo
print("Testing coordinate transformations...")
print("=" * 50)

# Original coordinates (before swap)
original_lat = -58.35675489807129  # This will be lon after swap
original_lon = -34.59189141419116  # This will be lat after swap

print(f"Original input: lat={original_lat}, lon={original_lon}")

# Create test data
data = pd.DataFrame([{
    'lat': original_lat,
    'lon': original_lon,
    'l1': 'Argentina',
    'l2': 'Capital Federal',
    'l3': 'Palermo',
    'rooms': 2.0,
    'surface_total': 65.0,
    'currency': 'USD',
    'title': 'Departamento 2 ambientes 65m2 Palermo',
    'description': 'Hermoso departamento de 2 ambientes en Palermo, 65 metros cuadrados',
    'property_type': 'Departamento',
    'operation_type': 'Venta',
    'price': 185000.0
}])

print(f"Before swap: lat={data['lat'].iloc[0]}, lon={data['lon'].iloc[0]}")

# Apply lat/lon swap (as in notebook)
data = data.rename(columns={'lat': 'temp_lat', 'lon': 'lat'})
data = data.rename(columns={'temp_lat': 'lon'})

print(f"After swap: lat={data['lat'].iloc[0]}, lon={data['lon'].iloc[0]}")

# Apply filter
data = filter_by_currency_place(data)
print(f"After filter_by_currency_place: flag='{data['flag'].iloc[0]}'")

# Apply geo validation
data = validate_geo(data)
print(f"After validate_geo: flag='{data['flag'].iloc[0]}'")

print("Final coordinates for validation:")
print(f"  lat (should be longitude): {data['lat'].iloc[0]}")
print(f"  lon (should be latitude): {data['lon'].iloc[0]}")

# Test if these coordinates are actually in Buenos Aires
from shapely.geometry import Point
import geopandas as gpd
import shapely.wkt

barrios_path = 'Pipeline/barrios copy.csv'
barrios = gpd.read_file(barrios_path)
barrios['geometry'] = barrios['WKT'].apply(lambda x: shapely.wkt.loads(x))
from shapely.ops import unary_union
combined_polygon = unary_union(barrios['geometry'])

test_point = Point(data['lon'].iloc[0], data['lat'].iloc[0])
is_inside = combined_polygon.contains(test_point) or combined_polygon.touches(test_point)

print(f"Point {test_point} is inside CABA polygon: {is_inside}")

# Show some neighborhood names for reference
print("\nAvailable neighborhoods in barrios file:")
print(barrios['BARRIO'].head(10).tolist())
