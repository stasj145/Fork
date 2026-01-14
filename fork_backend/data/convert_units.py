import csv
import re

def convert_imperial_to_metric(text):
    """
    Convert imperial units to metric units in the given text.
    """
    # Convert mph to km/h (1 mph = 1.60934 km/h)
    # Handle ranges like "12-13.9 mph"
    def mph_to_kmh(match):
        value = match.group(1)
        # Check if it's a range (contains hyphen)
        if '-' in value:
            parts = value.split('-')
            converted_parts = [str(round(float(part) * 1.60934, 1)) for part in parts]
            return f"{'-'.join(converted_parts)} km/h"
        else:
            return f"{round(float(value) * 1.60934, 1)} km/h"
    
    text = re.sub(r'([\d\.\-]+)\s*mph', mph_to_kmh, text)
    
    # Convert miles to kilometers (1 mile = 1.60934 km)
    # Handle ranges like "12-13.9 mile"
    def miles_to_km(match):
        value = match.group(1)
        # Check if it's a range (contains hyphen)
        if '-' in value:
            parts = value.split('-')
            converted_parts = [str(round(float(part) * 1.60934, 1)) for part in parts]
            return f"{'-'.join(converted_parts)} km"
        else:
            return f"{round(float(value) * 1.60934, 1)} km"
    
    text = re.sub(r'([\d\.\-]+)\s*mile', miles_to_km, text)
    
    # Convert lbs to kg (1 lb = 0.453592 kg)
    # Handle ranges like "16-24 lbs"
    def lbs_to_kg(match):
        value = match.group(1)
        # Check if it's a range (contains hyphen)
        if '-' in value:
            parts = value.split('-')
            converted_parts = [str(round(float(part) * 0.453592, 1)) for part in parts]
            return f"{'-'.join(converted_parts)} kg"
        else:
            return f"{round(float(value) * 0.453592, 1)} kg"
    
    text = re.sub(r'([\d\.\-]+)\s*lb', lbs_to_kg, text)
    text = re.sub(r'([\d\.\-]+)\s*lbs', lbs_to_kg, text)
    
    # Convert inches to cm (1 inch = 2.54 cm)
    # Handle ranges like "12-13.9 inches"
    def inches_to_cm(match):
        value = match.group(1)
        # Check if it's a range (contains hyphen)
        if '-' in value:
            parts = value.split('-')
            converted_parts = [str(round(float(part) * 2.54, 1)) for part in parts]
            return f"{'-'.join(converted_parts)} cm"
        else:
            return f"{round(float(value) * 2.54, 1)} cm"
    
    text = re.sub(r'([\d\.\-]+)\s*inch', inches_to_cm, text)
    text = re.sub(r'([\d\.\-]+)\s*inches', inches_to_cm, text)
    
    # Convert feet to meters (1 foot = 0.3048 m)
    # Handle ranges like "12-13.9 feet"
    def feet_to_meters(match):
        value = match.group(1)
        # Check if it's a range (contains hyphen)
        if '-' in value:
            parts = value.split('-')
            converted_parts = [str(round(float(part) * 0.3048, 1)) for part in parts]
            return f"{'-'.join(converted_parts)} m"
        else:
            return f"{round(float(value) * 0.3048, 1)} m"
    
    text = re.sub(r'([\d\.\-]+)\s*foot', feet_to_meters, text)
    text = re.sub(r'([\d\.\-]+)\s*feet', feet_to_meters, text)
    text = re.sub(r'([\d\.\-]+)\s*ft', feet_to_meters, text)
    
    return text

def process_csv(input_file, output_file):
    """
    Process the CSV file and add a new column with metric units.
    """
    rows = []
    
    # Read the input CSV
    with open(input_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header
        
        # Add new column header
        header.append("name metric")
        rows.append(header)
        
        # Process each row
        for row in reader:
            # The first column contains the activity name with possible imperial units
            imperial_name = row[0]
            # Convert to metric
            metric_name = convert_imperial_to_metric(imperial_name)
            # Add to row
            row.append(metric_name)
            rows.append(row)
    
    # Write the output CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

if __name__ == "__main__":
    process_csv('data/exercise_dataset.csv', 'data/exercise_dataset_metric.csv')
    print("Conversion complete. Output saved to data/exercise_dataset_metric.csv")
