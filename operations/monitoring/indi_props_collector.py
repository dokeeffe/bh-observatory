#!/usr/bin/env python3
import subprocess
import json

def get_indi_properties():
    """Call indi_getprop and return the text output."""
    try:
        result = subprocess.run(
            ['indi_getprop'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print(f"Error: indi_getprop returned code {result.returncode}")
            print(f"stderr: {result.stderr}")
            return None
        return result.stdout
    except FileNotFoundError:
        print("Error: indi_getprop command not found")
        return None
    except subprocess.TimeoutExpired:
        print("Error: indi_getprop timed out")
        return None

def parse_indi_text(text_output):
    """Parse INDI text output and convert to JSON structure.
    
    Format: device.property.element=value
    Example: iOptronV3.GPS_STATUS.On=Off
    """
    devices = {}
    
    for line in text_output.strip().split('\n'):
        line = line.strip()
        if not line or '=' not in line:
            continue
        
        # Split into path and value
        path, value = line.split('=', 1)
        parts = path.split('.')
        
        if len(parts) < 3:
            continue
        
        device = parts[0]
        property_name = parts[1]
        element = '.'.join(parts[2:])  # Handle elements with dots in name
        
        # Initialize device if not exists
        if device not in devices:
            devices[device] = {}
        
        # Initialize property if not exists
        if property_name not in devices[device]:
            devices[device][property_name] = {}
        
        # Try to convert value to appropriate type
        converted_value = convert_value(value)
        devices[device][property_name][element] = converted_value
    
    return devices

def convert_value(value):
    """Convert string value to appropriate type (number, boolean, or string)."""
    value = value.strip()
    
    # Try to convert to number
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        pass
    
    # Check for boolean-like values
    if value.lower() in ['on', 'off']:
        return value == 'On' or value == 'on'
    
    # Return as string
    return value

def main():
    # Get INDI properties
    text_output = get_indi_properties()
    if not text_output:
        return
    
    # Parse and convert to JSON
    json_data = parse_indi_text(text_output)
    if not json_data:
        print("No data parsed")
        return
    
    # Save to file
    output_file = '/tmp/indi_properties.json'
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"INDI properties saved to {output_file}")
    print(f"Found {len(json_data)} devices")

if __name__ == "__main__":
    main()

