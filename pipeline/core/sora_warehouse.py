"""
Sora Warehouse Management System
Handles data storage and retrieval for nail inventory using Supabase
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SoraWarehouse:
    # Class-level constants
    NAIL_TYPES = {'X': 250000, 'S': 200000, 'C': 180000, 'M': 150000, 'A': 130000, 'B': 100000}
    SUPPLY_TYPES = {'Glue': 0, 'Toolkit': 0, 'Box': 0}  # Supplies don't have pricing
    SIZES = ['XS', 'S', 'M', 'L']
    SUPPLY_SIZE = 'UNIT'  # Standard size for supplies
    PRODUCT_NAME_CSV = Path(__file__).resolve().parents[2] / 'product_code_names.csv'
    _product_name_cache: Optional[dict] = None
    _product_name_cache_mtime: float = 0.0
    
    DEFAULT_ITEM_NAMES = {
        'X1': 'Forever Red', 'S1': 'ECLIPSE', 'S2': 'LORREN', 'S3': 'BLUE FIRE',
        'S4': 'CHERRY ME', 'S5': 'ECSTASY', 'S6': 'BLOSSOM REFLECTION',
        'S7': 'LUNAR ROSE QIPAO', 'S8': 'LOTUS LUNAR', 'S9': 'PROSPER LUNAR',
        'S10': 'SAGE JASMINE', 'S11': 'AQUA REFLECTION', 'S12': 'WHIMSICAL LOVELY',
        'S13': 'BEARY JOY', 'S14': 'THE BAHAMAZ', 'S15': 'EMERALD LEOPARD',
        'S16': 'OCEAN WAVE', 'S17': 'DREAM POP', 'S18': 'MARGARETH',
        'S19': 'PINK BEACH', 'S20': 'VELOURA', 'C1': 'LETHAL', 'C2': 'PICO DOTS',
        'C3': 'OVAL BLUSH DREAMS', 'C5': 'MINI MINTS', 'C6': 'HOT CHIC',
        'C7': 'REGALIA', 'C8': 'CALISTA', 'C9': 'LONG PICO DOTS',
        'C10': 'SQUOVAL BLUSH DREAMS', 'C11': 'BLUSH DREAMS', 'C12': 'BERRY BUN',
        'C13': 'BROWNIE KITTY', 'C14': 'JAZZY', 'C15': 'MIRROR SHELLS',
        'C16': 'POLAROISE', 'C17': 'NALLCE', 'C18': 'POCHACCO', 'C19': 'OPPETTE',
        'C20': 'SUGAR RUSH', 'C21': 'GLASS TOUCH', 'C22': 'GOLDEN MIDNIGHT',
        'C23': 'PINK MIRAGE', 'C24': 'GOLDEN WINE', 'C25': 'RED UP',
        'C26': 'MISTY BLUE', 'C27': 'ALICE', 'C28': 'MATHEA',
        'M1': 'GEISHA', 'M2': 'HEIDI', 'M3': 'DONT BLINK', 'M4': 'PURPLE GALAXY',
        'M5': 'COTTON', 'M6': 'ROYALE BLUE', 'M7': 'ROSSIE FRENCH',
        'M8': 'THE BALLERINA', 'M9': 'FUTURISTIC ICY BLUE', 'M10': 'SIMPLE NELLY',
        'M11': 'LETTY', 'M12': 'TIRAMISU', 'M13': 'LUX COCO', 'M14': 'MACAU JADE',
        'M15': 'WINDY', 'M16': 'No name', 'M17': 'No name',
        'A1': 'CREME', 'A2': 'SWEETTIE', 'A3': 'ELEGANCE', 'A4': 'RIBBONING',
        'A5': 'MOCCACHINO', 'A6': 'BRIGHT DAY', 'A7': 'GRACIE', 'A8': 'NOMA',
        'A9': 'LADY LACE', 'B1': 'LEATHER', 'B2': 'ROXELLA', 'B3': 'CATHEISSE',
        'B4': 'PEARLING WHITE', 'B5': 'NARA', 'B6': 'No name', 'B7': 'no name'
    }
    
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self._verify_connection()

    @classmethod
    def _item_name_key(cls, nail_type: str, identifier: str) -> str:
        """Create the canonical key used by the product name CSV."""
        return identifier if nail_type in cls.SUPPLY_TYPES else f"{nail_type}{identifier}"

    @classmethod
    def _load_product_names(cls, force_refresh: bool = False) -> dict:
        """Load the product name map from the CSV file."""
        try:
            current_mtime = cls.PRODUCT_NAME_CSV.stat().st_mtime
        except FileNotFoundError:
            current_mtime = 0.0

        if (
            cls._product_name_cache is not None and
            not force_refresh and
            cls._product_name_cache_mtime == current_mtime
        ):
            return cls._product_name_cache.copy()

        names: dict = {}
        try:
            with cls.PRODUCT_NAME_CSV.open('r', encoding='utf-8-sig', newline='') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    code = (row.get('product_code') or row.get('item_key') or '').strip()
                    name = (row.get('product_name') or row.get('name') or '').strip()
                    if code:
                        names[code] = name
            cls._product_name_cache = names
            cls._product_name_cache_mtime = current_mtime
        except FileNotFoundError:
            print(f"Warning: product name CSV not found at {cls.PRODUCT_NAME_CSV}")
            cls._product_name_cache = {}
            cls._product_name_cache_mtime = 0.0
        except Exception as e:
            print(f"Error loading product names from CSV: {e}")
            cls._product_name_cache = {}
            cls._product_name_cache_mtime = 0.0

        return cls._product_name_cache.copy()
    
    def _verify_connection(self):
        """Verify database connection"""
        try:
            self.supabase.table('inventory').select('*').limit(1).execute()
        except Exception as e:
            print(f"Warning: Could not verify database. Ensure tables exist in Supabase.")
            print(f"Error: {e}")
    
    def _validate_input(self, nail_type: str, identifier: str, size: str, quantity: int) -> bool:
        """Validate input parameters"""
        # Check if it's a supply type (Glue, Toolkit, Box)
        if nail_type in self.SUPPLY_TYPES:
            return quantity > 0 and bool(identifier)
        
        # Regular nail type validation
        return (nail_type in self.NAIL_TYPES and 
                size in self.SIZES and 
                quantity > 0 and 
                bool(identifier))
    
    def _create_key(self, nail_type: str, identifier: str, size: str) -> str:
        """Create unique item key"""
        return f"{nail_type}_{identifier}_{size}"
    
    def add_stock(self, nail_type: str, identifier: str, size: str, quantity: int) -> bool:
        """Add stock to inventory"""
        if not self._validate_input(nail_type, identifier, size, quantity):
            return False
        
        try:
            key = self._create_key(nail_type, identifier, size)
            result = self.supabase.table('inventory').select('*').eq('item_key', key).execute()
            
            if result.data:
                current_quantity = result.data[0]['quantity']
                new_quantity = current_quantity + quantity
                self.supabase.table('inventory').update({
                    'quantity': new_quantity,
                    'updated_at': datetime.now().isoformat()
                }).eq('item_key', key).execute()
            else:
                new_quantity = quantity
                self.supabase.table('inventory').insert({
                    'item_key': key,
                    'nail_type': nail_type,
                    'identifier': identifier,
                    'size': size,
                    'quantity': new_quantity,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }).execute()
            
            self._log_transaction('INPUT', nail_type, identifier, size, quantity, new_quantity)
            return True
        except Exception as e:
            print(f"Error adding stock: {e}")
            return False
    
    def remove_stock(self, nail_type: str, identifier: str, size: str, quantity: int) -> bool:
        """Remove stock from inventory"""
        if not self._validate_input(nail_type, identifier, size, quantity):
            return False
        
        try:
            key = self._create_key(nail_type, identifier, size)
            result = self.supabase.table('inventory').select('*').eq('item_key', key).execute()
            
            if not result.data:
                return False
            
            current_quantity = result.data[0]['quantity']
            if current_quantity < quantity:
                return False
            
            new_quantity = current_quantity - quantity
            self.supabase.table('inventory').update({
                'quantity': new_quantity,
                'updated_at': datetime.now().isoformat()
            }).eq('item_key', key).execute()
            
            self._log_transaction('OUTPUT', nail_type, identifier, size, quantity, new_quantity)
            return True
        except Exception as e:
            print(f"Error removing stock: {e}")
            return False
    
    def delete_item(self, nail_type: str, identifier: str, size: str, quantity: int = None) -> bool:
        """Delete stock item or reduce quantity"""
        if not self._validate_input(nail_type, identifier, size, 1):
            return False
        
        try:
            key = self._create_key(nail_type, identifier, size)
            result = self.supabase.table('inventory').select('*').eq('item_key', key).execute()
            
            if not result.data:
                return False
            
            current_quantity = result.data[0]['quantity']
            
            if quantity is None or quantity >= current_quantity:
                # Delete the entire item
                self.supabase.table('inventory').delete().eq('item_key', key).execute()
                self._log_transaction('DELETE', nail_type, identifier, size, current_quantity, 0)
            else:
                # Reduce quantity
                new_quantity = current_quantity - quantity
                self.supabase.table('inventory').update({
                    'quantity': new_quantity,
                    'updated_at': datetime.now().isoformat()
                }).eq('item_key', key).execute()
                self._log_transaction('DELETE', nail_type, identifier, size, quantity, new_quantity)
            
            return True
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False
    
    def get_item_name(self, nail_type: str, identifier: str) -> str:
        """Get the name for a specific item"""
        try:
            key = self._item_name_key(nail_type, identifier)
            return self._load_product_names().get(key, '')
        except Exception as e:
            print(f"Error getting item name: {e}")
            return ''
    
    def get_all_item_names(self) -> dict:
        """Get all item names"""
        try:
            return self._load_product_names()
        except Exception as e:
            print(f"Error getting all names: {e}")
            return {}
    
    def update_item_name(self, nail_type: str, identifier: str, name: str, changed_by: str = 'System') -> bool:
        """Name editing is disabled; edit product_code_names.csv instead."""
        print("Name editing is disabled. Update product_code_names.csv instead.")
        return False
    
    def initialize_default_names(self) -> bool:
        """Legacy compatibility hook; refreshes the CSV cache only."""
        try:
            self._load_product_names(force_refresh=True)
            return True
        except Exception as e:
            print(f"Error refreshing product names: {e}")
            return False
    
    def _log_name_change(self, nail_type: str, identifier: str, old_name: str, new_name: str, changed_by: str):
        """Log name change to audit table"""
        try:
            key = f"{nail_type}{identifier}"
            self.supabase.table('name_change_log').insert({
                'item_key': key,
                'nail_type': nail_type,
                'identifier': identifier,
                'old_name': old_name,
                'new_name': new_name,
                'changed_by': changed_by,
                'changed_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error logging name change: {e}")
    
    def get_name_change_log(self, item_key: str = None) -> List:
        """Get name change history"""
        try:
            if item_key:
                result = self.supabase.table('name_change_log').select('*').eq('item_key', item_key).order('changed_at', desc=True).execute()
            else:
                result = self.supabase.table('name_change_log').select('*').order('changed_at', desc=True).limit(100).execute()
            return result.data
        except Exception as e:
            print(f"Error getting name change log: {e}")
            return []
    
    def _log_transaction(self, transaction_type: str, nail_type: str, identifier: str, 
                         size: str, quantity: int, new_balance: int):
        """Log transaction to database"""
        try:
            self.supabase.table('transactions').insert({
                'transaction_type': transaction_type,
                'nail_type': nail_type,
                'identifier': identifier,
                'size': size,
                'quantity': quantity,
                'new_balance': new_balance,
                'created_at': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error logging transaction: {e}")
    
    def get_stock(self, nail_type: str, identifier: str, size: str) -> int:
        """Get current stock level"""
        try:
            key = self._create_key(nail_type, identifier, size)
            result = self.supabase.table('inventory').select('quantity').eq('item_key', key).execute()
            return result.data[0]['quantity'] if result.data else 0
        except Exception:
            return 0
    
    def get_all_stock(self) -> List[dict]:
        """Get all inventory levels"""
        try:
            result = self.supabase.table('inventory').select('*').order('nail_type').execute()
            return result.data or []
        except Exception:
            return []
    
    def get_recent_transactions(self, limit: int = 10) -> List[dict]:
        """Get recent transactions"""
        try:
            result = self.supabase.table('transactions').select('*').order('created_at', desc=True).limit(limit).execute()
            return result.data or []
        except Exception:
            return []
    
    def get_nail_type_info(self, nail_type: str) -> Optional[int]:
        """Get nail type capacity"""
        return self.NAIL_TYPES.get(nail_type)
