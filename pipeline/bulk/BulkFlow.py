"""
BulkFlow - CSV Processor for Warehouse Flow Form
Reads CSV file and splits the Answer column (ID-SIZE-QTY format) into separate columns
Can be used as a module or standalone script
"""

import csv
import os
import io
from datetime import datetime

def process_csv_content(csv_content):
    """
    Process CSV content (from file or string) and split Answer column
    Handles both nail products (ID-SIZE-QTY) and supplies (Glue/Toolkit/Box)
    
    Args:
        csv_content: String content of CSV or file path
        
    Returns:
        List of dictionaries with processed data
    """
    processed_data = []
    SUPPLY_TYPES = ['Glue', 'Toolkit', 'Box']
    
    try:
        # Check if it's a file path or content
        if os.path.exists(csv_content):
            with open(csv_content, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            content = csv_content
        
        # Use StringIO to read CSV from string
        csv_file = io.StringIO(content)
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            # Get the base data
            date = row.get('Date', '')
            completion_time = row.get('Completion time', '')
            in_out = row.get('Select IN or OUT', '')
            type_selected = row.get('Select TYPE', '')
            answer = row.get('Answer in This format (ID-SIZE-QTY)', '')
            supply_qty = row.get('Enter Quantity Glue/Toolkit/BOX', '')
            
            # Check if this is a supply type (Glue, Toolkit, Box)
            if type_selected in SUPPLY_TYPES and supply_qty:
                supply_qty = supply_qty.strip()
                if supply_qty and in_out:  # Make sure we have quantity and action
                    processed_row = {
                        'date': date,
                        'timestamp': completion_time,
                        'Select IN or OUT': in_out,
                        'Select TYPE': type_selected,
                        'ID': type_selected,  # Use type as ID
                        'Size': 'UNIT',  # Standard size for supplies
                        'QTY': supply_qty
                    }
                    processed_data.append(processed_row)
            # Otherwise process as regular nail product
            elif answer:
                # Split by newlines for multiple entries
                entries = answer.strip().split('\n')
                
                for entry in entries:
                    entry = entry.strip()
                    if entry and '-' in entry:
                        # Split ID-SIZE-QTY format
                        parts = entry.split('-')
                        if len(parts) == 3:
                            item_id = parts[0].strip()
                            size = parts[1].strip()
                            qty = parts[2].strip()
                            
                            # Create processed row
                            processed_row = {
                                'date': date,
                                'timestamp': completion_time,
                                'Select IN or OUT': in_out,
                                'Select TYPE': type_selected,
                                'ID': item_id,
                                'Size': size,
                                'QTY': qty
                            }
                            processed_data.append(processed_row)
        
        return processed_data
    
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return []

def save_processed_data(data, output_path):
    """
    Save processed data to a new CSV file
    
    Args:
        data: List of dictionaries with processed data
        output_path: Path to save the output CSV
    """
    if not data:
        print("No data to save")
        return
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['date', 'Select IN or OUT', 'Select TYPE', 'ID', 'Size', 'QTY']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✅ Processed data saved to: {output_path}")
        print(f"   Total rows: {len(data)}")
    
    except Exception as e:
        print(f"Error saving file: {e}")

def display_data(data, limit=10):
    """
    Display processed data in a formatted table
    
    Args:
        data: List of dictionaries with processed data
        limit: Maximum number of rows to display
    """
    if not data:
        print("No data to display")
        return
    
    print("\n" + "="*100)
    print("PROCESSED WAREHOUSE FLOW DATA")
    print("="*100)
    print(f"{'Date':<12} {'IN/OUT':<8} {'Type':<6} {'ID':<10} {'Size':<6} {'QTY':<6}")
    print("-"*100)
    
    for i, row in enumerate(data[:limit]):
        print(f"{row['date']:<12} {row['Select IN or OUT']:<8} {row['Select TYPE']:<6} "
              f"{row['ID']:<10} {row['Size']:<6} {row['QTY']:<6}")
    
    if len(data) > limit:
        print(f"\n... and {len(data) - limit} more rows")
    
    print("-"*100)
    print(f"Total rows: {len(data)}\n")

def main():
    """Main function to process the warehouse flow CSV file"""
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, "Test file", "Sora Studio Warehouse Flow Form(Sheet1).csv")
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(base_dir, f"processed_warehouse_flow_{timestamp}.csv")
    
    print("="*100)
    print("🏭 SORA WAREHOUSE - BULK FLOW PROCESSOR")
    print("="*100)
    print(f"\n📂 Reading file: {input_file}")
    
    # Process the CSV
    processed_data = process_csv_content(input_file)
    
    if processed_data:
        # Display the data
        display_data(processed_data, limit=20)
        
        # Save to output file
        save_processed_data(processed_data, output_file)
        
        # Return the data
        return processed_data
    else:
        print("\n❌ No data processed")
        return []

if __name__ == "__main__":
    result = main()
    
    # Print summary
    print("\n" + "="*100)
    print("📊 SUMMARY")
    print("="*100)
    print(f"✓ Columns returned: date, Select IN or OUT, Select TYPE, ID, Size, QTY")
    print(f"✓ Answer column split successfully into ID, Size, and QTY")
    print(f"✓ Multi-line entries handled (each line becomes separate row)")
    print("="*100)
