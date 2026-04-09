"""
Sora Warehouse Inventory Analysis
Provides comprehensive analytics and insights on inventory data
"""

from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
from pipeline.core.sora_warehouse import SoraWarehouse

class InventoryAnalyzer:
    def __init__(self):
        self.warehouse = SoraWarehouse()

    @staticmethod
    def _display_name(code: str, name: str) -> str:
        return f"{code} - {name}" if name else code
    
    def get_size_distribution(self) -> Dict:
        """Get total quantity distribution by size across all inventory"""
        stock = self.warehouse.get_all_stock()
        size_totals = defaultdict(int)
        size_counts = defaultdict(int)  # Count of items (not quantity)
        
        for item in stock:
            size = item['size']
            quantity = item.get('quantity', 0)
            size_totals[size] += quantity
            size_counts[size] += 1
        
        return {
            'totals': dict(size_totals),
            'item_counts': dict(size_counts)
        }
    
    def get_size_distribution_by_category(self) -> Dict:
        """Get quantity distribution by size for each nail type category"""
        stock = self.warehouse.get_all_stock()
        category_size_totals = defaultdict(lambda: defaultdict(int))
        category_size_counts = defaultdict(lambda: defaultdict(int))
        
        for item in stock:
            nail_type = item['nail_type']
            size = item['size']
            quantity = item.get('quantity', 0)
            
            category_size_totals[nail_type][size] += quantity
            category_size_counts[nail_type][size] += 1
        
        return {
            'totals': {k: dict(v) for k, v in category_size_totals.items()},
            'item_counts': {k: dict(v) for k, v in category_size_counts.items()}
        }
    
    def get_category_statistics(self) -> Dict:
        """Get comprehensive statistics for each category"""
        stock = self.warehouse.get_all_stock()
        category_stats = defaultdict(lambda: {
            'total_quantity': 0,
            'unique_items': set(),
            'total_item_count': 0,
            'sizes_available': set()
        })
        
        for item in stock:
            nail_type = item['nail_type']
            identifier = item['identifier']
            quantity = item.get('quantity', 0)
            size = item['size']
            
            category_stats[nail_type]['total_quantity'] += quantity
            category_stats[nail_type]['unique_items'].add(identifier)
            category_stats[nail_type]['total_item_count'] += 1
            category_stats[nail_type]['sizes_available'].add(size)
        
        # Convert sets to counts
        result = {}
        for category, stats in category_stats.items():
            result[category] = {
                'total_quantity': stats['total_quantity'],
                'unique_products': len(stats['unique_items']),
                'total_entries': stats['total_item_count'],
                'sizes_available': sorted(list(stats['sizes_available']))
            }
        
        return result
    
    def get_top_stocked_items(self, limit: int = 10) -> List[Dict]:
        """Get top N items by total quantity across all sizes"""
        stock = self.warehouse.get_all_stock()
        item_names = self.warehouse.get_all_item_names()
        
        # Aggregate by identifier
        aggregated = defaultdict(lambda: {
            'total_quantity': 0,
            'sizes': []
        })
        
        for item in stock:
            key = f"{item['nail_type']}_{item['identifier']}"
            aggregated[key]['nail_type'] = item['nail_type']
            aggregated[key]['identifier'] = item['identifier']
            aggregated[key]['total_quantity'] += item.get('quantity', 0)
            aggregated[key]['sizes'].append(item['size'])
        
        # Sort by total quantity
        sorted_items = sorted(
            aggregated.values(), 
            key=lambda x: x['total_quantity'], 
            reverse=True
        )[:limit]
        
        # Add names
        for item in sorted_items:
            is_supply = item['nail_type'] in ['Glue', 'Toolkit', 'Box']
            key = item['identifier'] if is_supply else f"{item['nail_type']}{item['identifier']}"
            item['name'] = self._display_name(key, item_names.get(key, ''))
        
        return sorted_items
    
    def get_least_stocked_items(self, limit: int = 10) -> List[Dict]:
        """Get bottom N items by total quantity across all sizes"""
        stock = self.warehouse.get_all_stock()
        item_names = self.warehouse.get_all_item_names()
        
        # Aggregate by identifier
        aggregated = defaultdict(lambda: {
            'total_quantity': 0,
            'sizes': []
        })
        
        for item in stock:
            key = f"{item['nail_type']}_{item['identifier']}"
            aggregated[key]['nail_type'] = item['nail_type']
            aggregated[key]['identifier'] = item['identifier']
            aggregated[key]['total_quantity'] += item.get('quantity', 0)
            aggregated[key]['sizes'].append(item['size'])
        
        # Sort by total quantity (ascending)
        sorted_items = sorted(
            aggregated.values(), 
            key=lambda x: x['total_quantity']
        )[:limit]
        
        # Add names
        for item in sorted_items:
            is_supply = item['nail_type'] in ['Glue', 'Toolkit', 'Box']
            key = item['identifier'] if is_supply else f"{item['nail_type']}{item['identifier']}"
            item['name'] = self._display_name(key, item_names.get(key, ''))
        
        return sorted_items
    
    def get_stock_health_metrics(self) -> Dict:
        """Get overall inventory health metrics"""
        stock = self.warehouse.get_all_stock()
        item_names = self.warehouse.get_all_item_names()
        
        # Aggregate by identifier
        aggregated = defaultdict(lambda: {'total_quantity': 0})
        for item in stock:
            identifier = item['identifier']
            aggregated[identifier]['total_quantity'] += item.get('quantity', 0)
        
        total_quantity = sum(item.get('quantity', 0) for item in stock)
        total_unique_products = len(aggregated)
        total_entries = len(stock)
        
        # Low stock analysis (< 4)
        low_stock_count = sum(1 for item in aggregated.values() if item['total_quantity'] < 4)
        
        # Medium stock (4-10)
        medium_stock_count = sum(1 for item in aggregated.values() if 4 <= item['total_quantity'] <= 10)
        
        # High stock (> 10)
        high_stock_count = sum(1 for item in aggregated.values() if item['total_quantity'] > 10)
        
        # Average stock per product
        avg_stock = total_quantity / total_unique_products if total_unique_products > 0 else 0
        
        return {
            'total_quantity': total_quantity,
            'unique_products': total_unique_products,
            'total_entries': total_entries,
            'average_stock_per_product': round(avg_stock, 2),
            'low_stock_products': low_stock_count,
            'medium_stock_products': medium_stock_count,
            'high_stock_products': high_stock_count,
            'low_stock_percentage': round((low_stock_count / total_unique_products * 100), 1) if total_unique_products > 0 else 0,
            'stock_health_score': self._calculate_health_score(low_stock_count, medium_stock_count, high_stock_count, total_unique_products)
        }
    
    def _calculate_health_score(self, low: int, medium: int, high: int, total: int) -> str:
        """Calculate a simple health score based on stock distribution"""
        if total == 0:
            return "No Data"
        
        low_pct = (low / total) * 100
        
        if low_pct < 20:
            return "Excellent"
        elif low_pct < 35:
            return "Good"
        elif low_pct < 50:
            return "Fair"
        else:
            return "Needs Attention"
    
    def get_items_by_size(self) -> Dict:
        """Get all items grouped by size - useful to see what types are available for a specific size"""
        stock = self.warehouse.get_all_stock()
        item_names = self.warehouse.get_all_item_names()
        
        # Group items by size
        items_by_size = defaultdict(list)
        
        for item in stock:
            size = item['size']
            nail_type = item['nail_type']
            identifier = item['identifier']
            quantity = item.get('quantity', 0)
            
            # For supply types, identifier is the key; for nail products, nail_type+identifier
            is_supply = nail_type in ['Glue', 'Toolkit', 'Box']
            key = identifier if is_supply else f"{nail_type}{identifier}"
            name = self._display_name(key, item_names.get(key, ''))
            
            items_by_size[size].append({
                'nail_type': nail_type,
                'identifier': identifier,
                'name': name,
                'quantity': quantity
            })
        
        # Sort items within each size group
        for size in items_by_size:
            items_by_size[size].sort(key=lambda x: (x['nail_type'], x['identifier']))
        
        # Return with totals per size
        result = {}
        for size in sorted(items_by_size.keys()):
            items = items_by_size[size]
            result[size] = {
                'items': items,
                'total_quantity': sum(item['quantity'] for item in items),
                'unique_products': len(items)
            }
        
        return result
    
    def get_size_availability_matrix(self) -> Dict:
        """Get which products have which sizes available"""
        stock = self.warehouse.get_all_stock()
        item_names = self.warehouse.get_all_item_names()
        
        # Track sizes per product
        product_sizes = defaultdict(lambda: {
            'nail_type': '',
            'name': '',
            'sizes': set()
        })
        
        for item in stock:
            identifier = item['identifier']
            is_supply = item['nail_type'] in ['Glue', 'Toolkit', 'Box']
            key = identifier if is_supply else f"{item['nail_type']}{identifier}"
            product_sizes[identifier]['nail_type'] = item['nail_type']
            product_sizes[identifier]['name'] = self._display_name(key, item_names.get(key, ''))
            product_sizes[identifier]['sizes'].add(item['size'])
        
        # Analyze completeness
        all_sizes = {'XS', 'S', 'M', 'L'}
        complete_range = []
        partial_range = []
        single_size = []
        
        for identifier, data in product_sizes.items():
            size_count = len(data['sizes'])
            product_info = {
                'identifier': identifier,
                'nail_type': data['nail_type'],
                'name': data['name'],
                'sizes': sorted(list(data['sizes']))
            }
            
            if size_count == 4:
                complete_range.append(product_info)
            elif size_count == 1:
                single_size.append(product_info)
            else:
                partial_range.append(product_info)
        
        return {
            'complete_range_products': complete_range,
            'partial_range_products': partial_range,
            'single_size_products': single_size,
            'summary': {
                'complete_count': len(complete_range),
                'partial_count': len(partial_range),
                'single_size_count': len(single_size)
            }
        }
    
    def generate_analysis_report(self, analyst_name: str = "System") -> str:
        """Generate a comprehensive text-based analysis report"""
        lines = []
        lines.append("=" * 90)
        lines.append(" " * 25 + "INVENTORY ANALYSIS REPORT")
        lines.append("=" * 90)
        lines.append("")
        lines.append(f"  Report Date     : {datetime.now().strftime('%B %d, %Y')}")
        lines.append(f"  Report Time     : {datetime.now().strftime('%H:%M:%S')}")
        lines.append(f"  Analyzed By     : {analyst_name}")
        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        
        # Overall Health Metrics
        health = self.get_stock_health_metrics()
        lines.append("INVENTORY HEALTH OVERVIEW")
        lines.append("-" * 90)
        lines.append(f"  Total Quantity              : {health['total_quantity']:,}")
        lines.append(f"  Unique Products             : {health['unique_products']}")
        lines.append(f"  Total Stock Entries         : {health['total_entries']}")
        lines.append(f"  Average Stock per Product   : {health['average_stock_per_product']:.2f} units")
        lines.append("")
        lines.append(f"  Low Stock Products (<4)     : {health['low_stock_products']} ({health['low_stock_percentage']}%)")
        lines.append(f"  Medium Stock Products (4-10): {health['medium_stock_products']}")
        lines.append(f"  High Stock Products (>10)   : {health['high_stock_products']}")
        lines.append("")
        lines.append(f"  📊 Stock Health Score       : {health['stock_health_score']}")
        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        
        # Size Distribution
        size_dist = self.get_size_distribution()
        lines.append("SIZE DISTRIBUTION - OVERALL")
        lines.append("-" * 90)
        lines.append(f"{'Size':<10} {'Total Quantity':>20} {'Number of Entries':>20}")
        lines.append("-" * 90)
        
        for size in ['XS', 'S', 'M', 'L']:
            qty = size_dist['totals'].get(size, 0)
            count = size_dist['item_counts'].get(size, 0)
            lines.append(f"{size:<10} {qty:>20,} {count:>20}")
        
        total_qty = sum(size_dist['totals'].values())
        total_count = sum(size_dist['item_counts'].values())
        lines.append("-" * 90)
        lines.append(f"{'TOTAL':<10} {total_qty:>20,} {total_count:>20}")
        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        
        # Size Distribution by Category
        category_size_dist = self.get_size_distribution_by_category()
        lines.append("SIZE DISTRIBUTION - BY CATEGORY")
        lines.append("-" * 90)
        
        for category in sorted(category_size_dist['totals'].keys()):
            capacity = self.warehouse.get_nail_type_info(category)
            lines.append(f"\nType {category} — {capacity}k")
            lines.append("-" * 90)
            lines.append(f"{'Size':<10} {'Total Quantity':>20} {'Number of Entries':>20}")
            lines.append("-" * 90)
            
            for size in ['XS', 'S', 'M', 'L']:
                qty = category_size_dist['totals'][category].get(size, 0)
                count = category_size_dist['item_counts'][category].get(size, 0)
                if qty > 0:  # Only show sizes that exist
                    lines.append(f"{size:<10} {qty:>20,} {count:>20}")
            
            cat_total_qty = sum(category_size_dist['totals'][category].values())
            cat_total_count = sum(category_size_dist['item_counts'][category].values())
            lines.append("-" * 90)
            lines.append(f"{'SUBTOTAL':<10} {cat_total_qty:>20,} {cat_total_count:>20}")
        
        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        
        # Category Statistics
        cat_stats = self.get_category_statistics()
        lines.append("CATEGORY ANALYSIS")
        lines.append("-" * 90)
        lines.append(f"{'Type':<8} {'Capacity':>10} {'Quantity':>12} {'Products':>10} {'Entries':>10} {'Sizes':>20}")
        lines.append("-" * 90)
        
        for category in sorted(cat_stats.keys()):
            stats = cat_stats[category]
            capacity = self.warehouse.get_nail_type_info(category)
            sizes_str = ', '.join(stats['sizes_available'])
            lines.append(f"{category:<8} {str(capacity) + 'k':>10} {stats['total_quantity']:>12,} {stats['unique_products']:>10} {stats['total_entries']:>10} {sizes_str:>20}")
        
        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        
        # Top Stocked Items
        top_items = self.get_top_stocked_items(15)
        lines.append("TOP 15 MOST STOCKED ITEMS")
        lines.append("-" * 90)
        lines.append(f"{'Rank':<6} {'Type':<6} {'ID':<10} {'Product Name':<35} {'Quantity':>10}")
        lines.append("-" * 90)
        
        for idx, item in enumerate(top_items, 1):
            lines.append(f"{idx:<6} {item['nail_type']:<6} {item['identifier']:<10} {item['name']:<35} {item['total_quantity']:>10}")
        
        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        
        # Least Stocked Items
        least_items = self.get_least_stocked_items(15)
        lines.append("BOTTOM 15 LEAST STOCKED ITEMS")
        lines.append("-" * 90)
        lines.append(f"{'Rank':<6} {'Type':<6} {'ID':<10} {'Product Name':<35} {'Quantity':>10}")
        lines.append("-" * 90)
        
        for idx, item in enumerate(least_items, 1):
            lines.append(f"{idx:<6} {item['nail_type']:<6} {item['identifier']:<10} {item['name']:<35} {item['total_quantity']:>10}")
        
        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        
        # Size Availability Matrix
        size_matrix = self.get_size_availability_matrix()
        lines.append("SIZE AVAILABILITY ANALYSIS")
        lines.append("-" * 90)
        lines.append(f"  Complete Range (all 4 sizes) : {size_matrix['summary']['complete_count']} products")
        lines.append(f"  Partial Range (2-3 sizes)    : {size_matrix['summary']['partial_count']} products")
        lines.append(f"  Single Size Only             : {size_matrix['summary']['single_size_count']} products")
        lines.append("")
        
        if size_matrix['single_size_products']:
            lines.append("Products with Only One Size Available:")
            lines.append("-" * 90)
            lines.append(f"{'Type':<6} {'ID':<10} {'Product Name':<35} {'Size':>10}")
            lines.append("-" * 90)
            
            for prod in size_matrix['single_size_products'][:20]:  # Limit to 20
                lines.append(f"{prod['nail_type']:<6} {prod['identifier']:<10} {prod['name']:<35} {prod['sizes'][0]:>10}")
            
            if len(size_matrix['single_size_products']) > 20:
                lines.append(f"... and {len(size_matrix['single_size_products']) - 20} more")
        
        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        lines.append("END OF ANALYSIS REPORT")
        lines.append("")
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 90)
        
        return '\n'.join(lines)
    
    def save_analysis_to_file(self, analyst_name: str = "System", filename: str = None) -> str:
        """Save analysis report to a file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"inventory_analysis_{timestamp}.txt"
        
        report_content = self.generate_analysis_report(analyst_name)
        
        with open(filename, 'w') as f:
            f.write(report_content)
        
        return filename
    
    def get_analysis_summary(self) -> Dict:
        """Get a quick summary for API endpoints"""
        health = self.get_stock_health_metrics()
        size_dist = self.get_size_distribution()
        cat_stats = self.get_category_statistics()
        items_by_size = self.get_items_by_size()
        
        return {
            'health_metrics': health,
            'size_distribution': size_dist,
            'category_statistics': cat_stats,
            'items_by_size': items_by_size,
            'generated_at': datetime.now().isoformat()
        }

if __name__ == '__main__':
    # Example usage
    analyzer = InventoryAnalyzer()
    
    analyst_name = input("Enter your name: ")
    filename = analyzer.save_analysis_to_file(analyst_name)
    
    print(f"\n✅ Analysis report generated successfully!")
    print(f"📊 Saved to: {filename}")
    
    # Show quick summary
    health = analyzer.get_stock_health_metrics()
    print(f"\n📈 Quick Summary:")
    print(f"   Total Items: {health['unique_products']}")
    print(f"   Total Quantity: {health['total_quantity']:,}")
    print(f"   Health Score: {health['stock_health_score']}")
