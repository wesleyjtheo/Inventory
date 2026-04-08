"""
Inventory Report Generator
Generates formatted inventory reports for Sora Warehouse
"""

from datetime import datetime
from typing import List, Dict
from pipeline.core.sora_warehouse import SoraWarehouse
from pipeline.reporting.analysis import InventoryAnalyzer

class ReportGenerator:
    def __init__(self):
        self.warehouse = SoraWarehouse()
    
    def generate_text_report(self, exported_by: str) -> str:
        """Generate a text-based inventory report"""
        stock = self.warehouse.get_all_stock()
        
        # Separate supplies from nail products
        nail_products = [item for item in stock if item.get('nail_type', '') not in ['Glue', 'Toolkit', 'Box']]
        supplies = [item for item in stock if item.get('nail_type', '') in ['Glue', 'Toolkit', 'Box']]
        
        # Sort nail products: alphabetically by type, then numerically by identifier, then by size
        def sort_key_stock(x):
            nail_type = x.get('nail_type', '')
            identifier = x.get('identifier', '')
            size = x.get('size', '')
            # Extract numeric part from identifier
            num_part = ''.join(filter(str.isdigit, identifier))
            num = int(num_part) if num_part else 0
            return (nail_type, num, size)
        
        sorted_nail_products = sorted(nail_products, key=sort_key_stock)
        sorted_supplies = sorted(supplies, key=lambda x: (x.get('nail_type', ''), x.get('size', '')))
        
        # Combine: nail products first, then supplies
        sorted_stock = sorted_nail_products + sorted_supplies
        
        # Aggregate by ID for low stock calculation
        aggregated = {}
        for item in stock:
            key = f"{item['nail_type']}_{item['identifier']}"
            if key not in aggregated:
                aggregated[key] = {
                    'nail_type': item['nail_type'],
                    'identifier': item['identifier'],
                    'total_quantity': 0,
                    'sizes': []
                }
            aggregated[key]['total_quantity'] += item.get('quantity', 0)
            aggregated[key]['sizes'].append({
                'size': item['size'],
                'quantity': item.get('quantity', 0)
            })
        
        # Filter for low stock (total < 4)
        low_stock_items = [item for item in aggregated.values() if item['total_quantity'] < 4]
        
        # Sort low stock: nail products first, then supplies
        def sort_key_low(x):
            nail_type = x['nail_type']
            identifier = x['identifier']
            is_supply = nail_type in ['Glue', 'Toolkit', 'Box']
            # Extract numeric part from identifier
            num_part = ''.join(filter(str.isdigit, identifier))
            num = int(num_part) if num_part else 0
            # Supplies go to the end (add 'Z' prefix to sort after other types)
            sort_type = 'ZZZZZ_' + nail_type if is_supply else nail_type
            return (sort_type, num)
        
        low_stock_sorted = sorted(low_stock_items, key=sort_key_low)
        
        # Get all item names
        item_names = self.warehouse.get_all_item_names()
        
        report_lines = []
        report_lines.append("=" * 90)
        report_lines.append(" " * 20 + "SORA STUDIO WAREHOUSE REPORT")
        report_lines.append("=" * 90)
        report_lines.append("")
        report_lines.append(f"  Report Date     : {datetime.now().strftime('%B %d, %Y')}")
        report_lines.append(f"  Report Time     : {datetime.now().strftime('%H:%M:%S')}")
        report_lines.append(f"  Prepared By     : {exported_by}")
        report_lines.append("")
        report_lines.append("=" * 90)
        report_lines.append("")
        
        # Calculate totals
        total_quantity = sum(item.get('quantity', 0) for item in sorted_stock)
        
        report_lines.append("INVENTORY SUMMARY")
        report_lines.append("-" * 90)
        report_lines.append(f"  Total Items         : {len(sorted_stock)}")
        report_lines.append(f"  Total Quantity      : {total_quantity:,}")
        report_lines.append(f"  Low Stock IDs       : {len(low_stock_sorted)}")
        report_lines.append("")
        report_lines.append("=" * 90)
        report_lines.append("")
        
        # All Stock Section
        report_lines.append("COMPLETE STOCK INVENTORY")
        report_lines.append("-" * 90)
        
        # Group by type and identifier
        current_type = None
        current_id = None
        in_supplies_section = False
        
        for item in sorted_stock:
            # For supply types, identifier is the key; for nail products, nail_type+identifier
            is_supply = item['nail_type'] in ['Glue', 'Toolkit', 'Box']
            key = item['identifier'] if is_supply else f"{item['nail_type']}{item['identifier']}"
            name = item_names.get(key, 'Unknown')
            qty = item.get('quantity', 0)
            
            # Handle supplies as one group
            if is_supply and not in_supplies_section:
                if current_type is not None:
                    report_lines.append("")  # Space before supplies section
                report_lines.append("SUPPLIES (Glue, Toolkit, Box)")
                report_lines.append("-" * 90)
                report_lines.append(f"{'Type':<10} {'Product Name':<35} {'Size':<10} {'Quantity':>10}")
                report_lines.append("-" * 90)
                in_supplies_section = True
                current_type = 'Supplies'
                current_id = None
            # Add type header when type changes (for nail products only)
            elif not is_supply and item['nail_type'] != current_type:
                if current_type is not None:
                    report_lines.append("")  # Space before new type
                current_type = item['nail_type']
                type_capacity = self.warehouse.get_nail_type_info(current_type)
                report_lines.append(f"Type {current_type} — {type_capacity}k")
                report_lines.append("-" * 90)
                report_lines.append(f"{'ID':<10} {'Product Name':<35} {'Size':<10} {'Quantity':>10}")
                report_lines.append("-" * 90)
                current_id = None
                in_supplies_section = False
            
            # Add space between different IDs (only for nail products)
            if not is_supply and item['identifier'] != current_id and current_id is not None:
                report_lines.append("")
            
            current_id = item['identifier']
            # For supplies, show the type (Glue/Toolkit/Box) in the first column
            display_id = item['nail_type'] if is_supply else item['identifier']
            report_lines.append(f"{display_id:<10} {name:<35} {item['size']:<10} {qty:>10}")
        
        report_lines.append("")
        report_lines.append("=" * 90)
        report_lines.append("")
        
        # Low Stock Section
        report_lines.append("LOW STOCK ALERT (Total Quantity < 4 per ID)")
        report_lines.append("-" * 90)
        
        if low_stock_sorted:
            current_type = None
            in_supplies_section = False
            
            for item in low_stock_sorted:
                # For supply types, identifier is the key; for nail products, nail_type+identifier
                is_supply = item['nail_type'] in ['Glue', 'Toolkit', 'Box']
                key = item['identifier'] if is_supply else f"{item['nail_type']}{item['identifier']}"
                name = item_names.get(key, 'Unknown')
                
                # Handle supplies as one group
                if is_supply and not in_supplies_section:
                    if current_type is not None:
                        report_lines.append("")  # Space before supplies section
                    report_lines.append("SUPPLIES (Glue, Toolkit, Box)")
                    report_lines.append("-" * 90)
                    report_lines.append(f"{'Type':<10} {'Product Name':<35} {'Size':<10} {'Quantity':>10}")
                    report_lines.append("-" * 90)
                    in_supplies_section = True
                    current_type = 'Supplies'
                # Add type header when type changes (for nail products only)
                elif not is_supply and item['nail_type'] != current_type:
                    if current_type is not None:
                        report_lines.append("")  # Space before new type
                    current_type = item['nail_type']
                    type_capacity = self.warehouse.get_nail_type_info(current_type)
                    report_lines.append(f"Type {current_type} — {type_capacity}k")
                    report_lines.append("-" * 90)
                    report_lines.append(f"{'ID':<10} {'Product Name':<35} {'Size':<10} {'Quantity':>10}")
                    report_lines.append("-" * 90)
                    in_supplies_section = False
                
                # Display ID with total quantity
                display_id = item['nail_type'] if is_supply else item['identifier']
                report_lines.append(f"{display_id:<10} {name:<35} {'ALL':<10} {item['total_quantity']:>10}")
                
                # Display size breakdown
                for size_data in item['sizes']:
                    report_lines.append(f"{'':<10} {'':<35} {size_data['size']:<10} {size_data['quantity']:>10}")
                
                report_lines.append("")  # Space after each ID
        else:
            report_lines.append("  No items with low stock - All items are well stocked.")
        
        report_lines.append("")
        report_lines.append("=" * 90)
        report_lines.append("")
        
        # Add Analysis Section
        report_lines.append("INVENTORY ANALYSIS")
        report_lines.append("-" * 90)
        analyzer = InventoryAnalyzer()
        summary = analyzer.get_analysis_summary()
        health = summary['health_metrics']
        size_dist = summary['size_distribution']
        cat_stats = summary['category_statistics']
        
        report_lines.append("")
        report_lines.append("Health Overview:")
        report_lines.append(f"  Total Quantity              : {health['total_quantity']:,}")
        report_lines.append(f"  Unique Products             : {health['unique_products']}")
        report_lines.append(f"  Average Stock per Product   : {health['average_stock_per_product']:.2f}")
        report_lines.append(f"  Low Stock Products (<4)     : {health['low_stock_products']} ({health['low_stock_percentage']}%)")
        report_lines.append(f"  Medium Stock Products (4-10): {health['medium_stock_products']}")
        report_lines.append(f"  High Stock Products (>10)   : {health['high_stock_products']}")
        report_lines.append(f"  Stock Health Score          : {health['stock_health_score']}")
        
        report_lines.append("")
        report_lines.append("Size Distribution:")
        report_lines.append(f"{'Size':<10} {'Quantity':>15}")
        report_lines.append("-" * 30)
        for size in ['XS', 'S', 'M', 'L']:
            qty = size_dist['totals'].get(size, 0)
            report_lines.append(f"{size:<10} {qty:>15,}")

        report_lines.append("")
        report_lines.append("AVAILABLE TYPES BY SIZE:")
        size_type_map = {}
        for item in sorted_stock:
            item_size = item.get('size', '')
            item_type = item.get('nail_type', '')
            if item_size and item_type:
                if item_size not in size_type_map:
                    size_type_map[item_size] = set()
                size_type_map[item_size].add(item_type)

        report_lines.append(f"{'Size':<10} {'Unique Types':>15} {'Types':<60}")
        report_lines.append("-" * 90)
        for size in sorted(size_type_map.keys()):
            available_types = sorted(size_type_map[size])
            types_text = ', '.join(available_types)
            report_lines.append(f"{size:<10} {len(available_types):>15} {types_text:<60}")

        report_lines.append("")
        report_lines.append("INVENTORY BY SIZE (DETAILED)")
        report_lines.append("-" * 90)

        size_groups = {}
        for item in sorted_stock:
            item_size = item.get('size', '')
            if item_size not in size_groups:
                size_groups[item_size] = []
            size_groups[item_size].append(item)

        for size in sorted(size_groups.keys()):
            items = size_groups[size]
            total_units = sum(i.get('quantity', 0) for i in items)
            report_lines.append("")
            report_lines.append(f"Size: {size} ({len(items)} products, {total_units} units)")
            report_lines.append("")
            report_lines.append(f"{'TYPE':<8}{'ID':<10}{'PRODUCT NAME':<40}{'QUANTITY':>10}")
            report_lines.append("-" * 90)

            for item in items:
                is_supply = item['nail_type'] in ['Glue', 'Toolkit', 'Box']
                key = item['identifier'] if is_supply else f"{item['nail_type']}{item['identifier']}"
                name = item_names.get(key, 'Unknown')
                report_lines.append(
                    f"{item['nail_type']:<8}{item['identifier']:<10}{name:<40}{item.get('quantity', 0):>10}"
                )
        
        report_lines.append("")
        report_lines.append("=" * 90)
        report_lines.append("")
        report_lines.append("END OF REPORT")
        report_lines.append("")
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 90)
        
        return '\n'.join(report_lines)
    
    def save_report_to_file(self, exported_by: str, filename: str = None) -> str:
        """Save report to a file and return the filename"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"inventory_report_{timestamp}.txt"
        
        report_content = self.generate_text_report(exported_by)
        
        with open(filename, 'w') as f:
            f.write(report_content)
        
        return filename
    
    def get_low_stock_summary(self) -> Dict:
        """Get summary of low stock items"""
        stock = self.warehouse.get_all_stock()
        
        # Aggregate by ID
        aggregated = {}
        for item in stock:
            identifier = item['identifier']
            if identifier not in aggregated:
                aggregated[identifier] = {
                    'identifier': identifier,
                    'total_quantity': 0
                }
            aggregated[identifier]['total_quantity'] += item.get('quantity', 0)
        
        # Filter for low stock (total < 4)
        low_stock = [item for item in aggregated.values() if item['total_quantity'] < 4]
        
        return {
            'count': len(low_stock),
            'items': low_stock,
            'total_items': len(aggregated)
        }

if __name__ == '__main__':
    # Example usage
    generator = ReportGenerator()
    
    exported_by = input("Enter your name: ")
    filename = generator.save_report_to_file(exported_by)
    
    print(f"\n✅ Report generated successfully!")
    print(f"📄 Saved to: {filename}")
    
    # Print low stock summary
    low_stock = generator.get_low_stock_summary()
    print(f"\n⚠️  Low Stock Items: {low_stock['count']}/{low_stock['total_items']}")
