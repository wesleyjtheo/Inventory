"""
BulkFlow Firewall - Duplicate Detection System
Detects which entries are new and which have already been processed
Uses a hash-based tracking system to identify duplicate submissions
"""

import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple

class BulkFlowFirewall:
    def __init__(self, tracking_file='bulk_flow_tracking.json'):
        """Initialize the firewall with a tracking file"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.tracking_file = os.path.join(self.base_dir, tracking_file)
        self.processed_hashes = self.load_tracking_data()
    
    def load_tracking_data(self) -> set:
        """Load previously processed entry hashes from tracking file"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_hashes', []))
            except Exception as e:
                print(f"Warning: Could not load tracking file: {e}")
                return set()
        return set()
    
    def save_tracking_data(self):
        """Save processed entry hashes to tracking file"""
        try:
            data = {
                'processed_hashes': list(self.processed_hashes),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving tracking file: {e}")
    
    def generate_entry_hash(self, entry: Dict) -> str:
        """
        Generate a unique hash for an entry based on its content
        Uses: timestamp, date, IN/OUT, TYPE, ID, Size, QTY
        Timestamp is critical to distinguish multiple entries of same item on same day
        """
        # Create a string representation of the entry including timestamp
        timestamp = entry.get('timestamp', '')
        hash_string = f"{timestamp}|{entry['date']}|{entry['Select IN or OUT']}|{entry['Select TYPE']}|{entry['ID']}|{entry['Size']}|{entry['QTY']}"
        
        # Generate SHA-256 hash
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def filter_entries(self, entries: List[Dict]) -> Tuple[List[Dict], List[Dict], Dict]:
        """
        Filter entries into new and duplicate lists
        
        Args:
            entries: List of processed entries from CSV
            
        Returns:
            Tuple of (new_entries, duplicate_entries, statistics)
        """
        new_entries = []
        duplicate_entries = []
        
        for entry in entries:
            entry_hash = self.generate_entry_hash(entry)
            
            if entry_hash in self.processed_hashes:
                # This entry has been processed before
                duplicate_entries.append({
                    **entry,
                    'hash': entry_hash,
                    'status': 'duplicate'
                })
            else:
                # This is a new entry
                new_entries.append({
                    **entry,
                    'hash': entry_hash,
                    'status': 'new'
                })
        
        statistics = {
            'total_entries': len(entries),
            'new_entries': len(new_entries),
            'duplicate_entries': len(duplicate_entries),
            'new_percentage': round((len(new_entries) / len(entries) * 100) if entries else 0, 2),
            'duplicate_percentage': round((len(duplicate_entries) / len(entries) * 100) if entries else 0, 2)
        }
        
        return new_entries, duplicate_entries, statistics
    
    def mark_as_processed(self, entries: List[Dict]):
        """
        Mark entries as processed by adding their hashes to the tracking set
        
        Args:
            entries: List of entries to mark as processed
        """
        for entry in entries:
            if 'hash' in entry:
                self.processed_hashes.add(entry['hash'])
            else:
                # Generate hash if not present
                entry_hash = self.generate_entry_hash(entry)
                self.processed_hashes.add(entry_hash)
        
        # Save to file
        self.save_tracking_data()
    
    def get_statistics(self) -> Dict:
        """Get statistics about processed entries"""
        return {
            'total_processed': len(self.processed_hashes),
            'tracking_file': self.tracking_file,
            'tracking_file_exists': os.path.exists(self.tracking_file)
        }
    
    def reset_tracking(self):
        """Reset all tracking data (use with caution!)"""
        self.processed_hashes = set()
        if os.path.exists(self.tracking_file):
            os.remove(self.tracking_file)
        print("⚠️  Tracking data has been reset")

def test_firewall():
    """Test the firewall functionality"""
    print("="*80)
    print("Testing BulkFlow Firewall")
    print("="*80)
    
    # Create firewall instance
    firewall = BulkFlowFirewall('test_tracking.json')
    
    # Sample test data
    test_entries = [
        {'date': '06/02/2026', 'Select IN or OUT': 'IN', 'Select TYPE': 'X', 'ID': 'X1', 'Size': 'M', 'QTY': '2'},
        {'date': '06/02/2026', 'Select IN or OUT': 'IN', 'Select TYPE': 'X', 'ID': 'X2', 'Size': 'S', 'QTY': '5'},
        {'date': '06/02/2026', 'Select IN or OUT': 'OUT', 'Select TYPE': 'S', 'ID': 'S1', 'Size': 'L', 'QTY': '3'},
    ]
    
    # First run - all should be new
    print("\n1st Run: Processing entries for the first time")
    new, duplicates, stats = firewall.filter_entries(test_entries)
    print(f"   New: {len(new)}, Duplicates: {len(duplicates)}")
    print(f"   Statistics: {stats}")
    
    # Mark as processed
    firewall.mark_as_processed(new)
    print("   Marked entries as processed")
    
    # Second run - all should be duplicates
    print("\n2nd Run: Processing same entries again")
    new, duplicates, stats = firewall.filter_entries(test_entries)
    print(f"   New: {len(new)}, Duplicates: {len(duplicates)}")
    print(f"   Statistics: {stats}")
    
    # Third run - mix of new and old
    mixed_entries = test_entries + [
        {'date': '06/02/2026', 'Select IN or OUT': 'IN', 'Select TYPE': 'C', 'ID': 'C5', 'Size': 'XS', 'QTY': '10'},
    ]
    print("\n3rd Run: Processing with one new entry added")
    new, duplicates, stats = firewall.filter_entries(mixed_entries)
    print(f"   New: {len(new)}, Duplicates: {len(duplicates)}")
    print(f"   Statistics: {stats}")
    
    # Clean up test file
    if os.path.exists('test_tracking.json'):
        os.remove('test_tracking.json')
    
    print("\n" + "="*80)
    print("✅ Firewall test complete")
    print("="*80)

if __name__ == "__main__":
    test_firewall()
