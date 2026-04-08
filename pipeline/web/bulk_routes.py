"""
Bulk Upload Routes Module
Handles CSV processing and bulk operations
"""
from flask import request, jsonify
from pipeline.core.auth import require_auth
import re

def register_bulk_routes(app, warehouse):
    """Register bulk upload routes"""
    
    @app.route('/bulk_upload', methods=['POST'])
    @require_auth
    def bulk_upload():
        """Process bulk CSV upload"""
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Read file content
            csv_content = file.read().decode('utf-8')
            
            # Import BulkFlow processor
            from pipeline.bulk.BulkFlow import process_csv_content
            from pipeline.bulk.BulkFlowFirewall import BulkFlowFirewall
            
            # Process CSV
            entries = process_csv_content(csv_content)
            
            if not entries:
                return jsonify({'success': False, 'error': 'No valid entries found in CSV'}), 400
            
            # Use firewall to detect duplicates
            firewall = BulkFlowFirewall()
            new_entries, duplicate_entries, statistics = firewall.filter_entries(entries)
            
            return jsonify({
                'success': True,
                'new_entries': new_entries,
                'duplicate_entries': duplicate_entries,
                'statistics': statistics
            })
        except Exception as e:
            import traceback
            print("Bulk upload error:", traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/bulk_save', methods=['POST'])
    @require_auth
    def bulk_save():
        """Save bulk entries to database"""
        try:
            data = request.json
            entries = data.get('entries', [])
            
            if not entries:
                return jsonify({'success': False, 'error': 'No entries to save'}), 400
            
            from pipeline.bulk.BulkFlowFirewall import BulkFlowFirewall
            
            saved_count = 0
            failed_count = 0
            errors = []
            
            for entry in entries:
                try:
                    action = entry.get('Select IN or OUT', '').strip().upper()
                    nail_type = entry.get('Select TYPE', '').strip()
                    identifier = entry.get('ID', '').strip()
                    size = entry.get('Size', '').strip()
                    
                    # Parse quantity carefully
                    qty_value = entry.get('QTY', '').strip()
                    if not qty_value:
                        errors.append(f"Missing quantity for {nail_type} {identifier}")
                        failed_count += 1
                        continue
                    
                    try:
                        quantity = int(qty_value)
                    except ValueError:
                        errors.append(f"Invalid quantity '{qty_value}' for {nail_type} {identifier}")
                        failed_count += 1
                        continue
                    
                    # Check if this is a supply type (Glue, Toolkit, Box)
                    is_supply = nail_type in ['Glue', 'Toolkit', 'Box']
                    
                    # Validate ID format (skip for supplies)
                    if not is_supply and not re.match(r'^[XSCMAB]\d+$', identifier):
                        errors.append(f"Invalid ID format: {identifier}")
                        failed_count += 1
                        continue
                    
                    # Validate action
                    if action not in ['IN', 'OUT']:
                        errors.append(f"Invalid action for {identifier}: {action}")
                        failed_count += 1
                        continue
                    
                    # Validate required fields
                    if not nail_type or not identifier or not size:
                        errors.append(f"Missing required fields for {identifier}")
                        failed_count += 1
                        continue
                    
                    # Validate quantity is positive
                    if quantity <= 0:
                        errors.append(f"Quantity must be positive for {identifier}, got: {quantity}")
                        failed_count += 1
                        continue
                    
                    # Process based on action
                    if action == 'IN':
                        success = warehouse.add_stock(nail_type, identifier, size, quantity)
                    elif action == 'OUT':
                        success = warehouse.remove_stock(nail_type, identifier, size, quantity)
                    else:
                        success = False
                    
                    if success:
                        saved_count += 1
                    else:
                        # For supply types, don't concatenate type and identifier
                        is_supply = nail_type in ['Glue', 'Toolkit', 'Box']
                        display_id = identifier if is_supply else f'{nail_type}{identifier}'
                        errors.append(f"Failed to process {display_id}-{size}")
                        failed_count += 1
                        
                except Exception as e:
                    errors.append(f"Error processing entry: {str(e)}")
                    failed_count += 1
            
            # Mark successfully saved entries as processed in firewall
            if saved_count > 0:
                firewall = BulkFlowFirewall()
                firewall.mark_as_processed(entries[:saved_count])
            
            # Build response message
            message_parts = []
            if saved_count > 0:
                message_parts.append(f"✅ Saved: {saved_count} entries")
            if failed_count > 0:
                message_parts.append(f"❌ Failed: {failed_count} entries")
            if errors:
                message_parts.append(f"\nErrors: {', '.join(errors[:5])}")
                if len(errors) > 5:
                    message_parts.append(f"... and {len(errors) - 5} more")
            
            return jsonify({
                'success': saved_count > 0,
                'saved_count': saved_count,
                'failed_count': failed_count,
                'message': '\n'.join(message_parts),
                'errors': errors
            })
            
        except Exception as e:
            import traceback
            print("Bulk save error:", traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500
