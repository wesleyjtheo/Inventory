"""
Main Application File - Streamlined
Imports modules and initializes the Flask app
"""
import json
import os

from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, make_response, Response, send_file
import secrets
import qrcode
import re
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Import local modules
from pipeline.core.auth import (
    require_auth, get_security_pin, check_rate_limit, 
    record_login_attempt, verify_pin, ACCESS_TOKEN, SECURITY_PIN_HASH
)
from pipeline.core.helpers import get_local_ip
from pipeline.core.sora_warehouse import SoraWarehouse
from pipeline.reporting.analysis import InventoryAnalyzer

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Ensure PIN hash is initialized for WSGI servers (e.g., Gunicorn).
get_security_pin()


@app.after_request
def add_security_headers(response):
        """Add baseline security headers for public deployments."""
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'no-referrer')
        response.headers.setdefault('Content-Security-Policy', "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; img-src 'self' data: blob:; connect-src 'self';")
        return response


def _build_pwa_icon(size):
        """Generate a simple monochrome icon in-memory for PWA installs."""
        img = Image.new('RGB', (size, size), color='black')
        draw = ImageDraw.Draw(img)

        margin = int(size * 0.12)
        draw.rounded_rectangle(
                [(margin, margin), (size - margin, size - margin)],
                radius=int(size * 0.08),
                outline='white',
                width=max(2, int(size * 0.03)),
        )

        bar_width = max(3, int(size * 0.06))
        center_x = size // 2
        top = int(size * 0.3)
        bottom = int(size * 0.7)
        draw.rectangle([(center_x - bar_width // 2, top), (center_x + bar_width // 2, bottom)], fill='white')

        left = int(size * 0.28)
        right = int(size * 0.72)
        mid_y = size // 2
        draw.rectangle([(left, mid_y - bar_width // 2), (right, mid_y + bar_width // 2)], fill='white')

        icon_bytes = BytesIO()
        img.save(icon_bytes, format='PNG')
        icon_bytes.seek(0)
        return icon_bytes


@app.route('/manifest.webmanifest')
def pwa_manifest():
        """Serve install manifest for mobile home-screen install."""
        manifest = {
                'name': 'Sora Warehouse',
                'short_name': 'Sora',
                'description': 'Sora Inventory and Warehouse Management',
                'start_url': '/',
                'scope': '/',
                'display': 'standalone',
                'background_color': '#000000',
                'theme_color': '#000000',
                'icons': [
                        {
                                'src': '/icon-192.png',
                                'sizes': '192x192',
                                'type': 'image/png',
                                'purpose': 'any maskable',
                        },
                        {
                                'src': '/icon-512.png',
                                'sizes': '512x512',
                                'type': 'image/png',
                                'purpose': 'any maskable',
                        },
                ],
        }

        response = Response(json.dumps(manifest), mimetype='application/manifest+json')
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response


@app.route('/sw.js')
def service_worker():
        """Serve service worker at root scope for app installability."""
        sw_content = """
const CACHE_NAME = 'sora-inventory-v1';
const APP_SHELL = ['/', '/login', '/manifest.webmanifest', '/icon-192.png', '/icon-512.png', '/apple-touch-icon.png'];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    if (event.request.method !== 'GET' || url.origin !== self.location.origin) {
        return;
    }

    // Keep dynamic API traffic network-first to avoid stale inventory state.
    if (url.pathname.startsWith('/submit') ||
            url.pathname.startsWith('/bulk_') ||
            url.pathname.startsWith('/generate_') ||
            url.pathname.startsWith('/preview_report') ||
            url.pathname.startsWith('/view_') ||
            url.pathname.startsWith('/get_') ||
            url.pathname.startsWith('/update_') ||
            url.pathname.startsWith('/delete_') ||
            url.pathname.startsWith('/initialize_') ||
            url.pathname.startsWith('/logout') ||
            url.pathname.startsWith('/login')) {
        event.respondWith(fetch(event.request).catch(() => caches.match('/login')));
        return;
    }

    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) {
                return cached;
            }

            return fetch(event.request).then((response) => {
                const copy = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
                return response;
            });
        })
    );
});
"""

        response = Response(sw_content.strip(), mimetype='application/javascript')
        response.headers['Cache-Control'] = 'no-cache'
        return response


@app.route('/icon-192.png')
def icon_192():
        """PWA icon endpoint (192px)."""
        return send_file(_build_pwa_icon(192), mimetype='image/png')


@app.route('/icon-512.png')
def icon_512():
        """PWA icon endpoint (512px)."""
        return send_file(_build_pwa_icon(512), mimetype='image/png')


@app.route('/apple-touch-icon.png')
def apple_touch_icon():
        """Apple touch icon endpoint for iOS home-screen shortcut."""
        return send_file(_build_pwa_icon(180), mimetype='image/png')

# Initialize warehouse
warehouse = SoraWarehouse()

# Import HTML templates (keep inline for now for simplicity)
from pipeline.web.input_system_templates import LOGIN_TEMPLATE, HTML_TEMPLATE

# Register bulk upload routes
from pipeline.web.bulk_routes import register_bulk_routes
register_bulk_routes(app, warehouse)

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET'])
def login_page():
    """Show login page"""
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    """Handle login"""
    ip = request.remote_addr
    
    # Check rate limiting
    if not check_rate_limit(ip):
        from pipeline.core.auth import login_attempts, LOCKOUT_TIME
        import time
        remaining = LOCKOUT_TIME - (time.time() - login_attempts[ip][1])
        return jsonify({
            'success': False, 
            'message': f'Too many failed attempts. Try again in {int(remaining)} seconds.'
        }), 429
    
    data = request.json
    pin = data.get('pin', '')
    
    # Verify PIN
    if verify_pin(pin):
        session['authenticated'] = True
        session.permanent = True
        record_login_attempt(ip, success=True)
        return jsonify({'success': True})
    else:
        record_login_attempt(ip, success=False)
        from pipeline.core.auth import login_attempts, MAX_LOGIN_ATTEMPTS
        attempts_left = MAX_LOGIN_ATTEMPTS - login_attempts.get(ip, (0, 0))[0]
        return jsonify({
            'success': False, 
            'message': f'Invalid PIN. {attempts_left} attempts remaining.'
        })

@app.route('/logout', methods=['POST'])
def logout():
    """Handle logout"""
    session.clear()
    return jsonify({'success': True})

# ============================================================================
# MAIN APPLICATION ROUTES
# ============================================================================

@app.route('/')
@require_auth
def index():
    """Main page with the form"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_stock')
@require_auth
def get_stock():
    """Get current stock level"""
    nail_type = request.args.get('nail_type')
    identifier = request.args.get('identifier')
    size = request.args.get('size')
    
    if not nail_type or not identifier or not size:
        return jsonify({'error': 'Missing parameters'}), 400
    
    stock = warehouse.get_stock(nail_type, identifier, size)
    return jsonify({'stock': stock})

@app.route('/submit', methods=['POST'])
@require_auth
def submit():
    """Handle form submission"""
    data = request.json
    action = data.get('action')
    nail_type = data.get('nail_type')
    identifier = data.get('identifier')
    size = data.get('size')
    quantity = data.get('quantity')

    # Check if it's a supply type
    is_supply = nail_type in ['Glue', 'Toolkit', 'Box']

    # Normalize supply values (ID and size are hidden in UI for supplies)
    if is_supply:
        identifier = identifier or nail_type
        size = size or 'UNIT'

    if not all([action, nail_type, identifier, size, quantity]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    # Validate ID format only for nail products
    if not is_supply and not re.match(r'^[XSCMAB]\d+$', identifier):
        return jsonify({
            'success': False, 
            'message': f'⚠️ Invalid ID format: "{identifier}". ID must start with X, S, C, M, A, or B followed by a number (e.g., S1, X12, M5). Please check for typos.'
        })
    
    if action == 'input':
        success = warehouse.add_stock(nail_type, identifier, size, quantity)
        message_prefix = 'added'
        error_message = 'Failed to add stock. Please check your inputs.'
    elif action == 'output':
        success = warehouse.remove_stock(nail_type, identifier, size, quantity)
        message_prefix = 'removed'
        error_message = 'Failed to remove stock. Check if sufficient stock is available.'
    else:
        return jsonify({'success': False, 'message': 'Invalid action'})
    
    if success:
        new_stock = warehouse.get_stock(nail_type, identifier, size)
        # For supply types, don't concatenate type and identifier
        is_supply = nail_type in ['Glue', 'Toolkit', 'Box']
        display_id = identifier if is_supply else f'{nail_type}{identifier}'
        return jsonify({
            'success': True,
            'message': f'Successfully {message_prefix} {quantity} units of {display_id}-{size}. New stock: {new_stock}'
        })
    
    return jsonify({'success': False, 'message': error_message})

@app.route('/view_all_stock')
@require_auth
def view_all_stock():
    """Get all stock inventory"""
    try:
        stock = warehouse.get_all_stock()
        def sort_key(x):
            nail_type = x.get('nail_type', '')
            identifier = x.get('identifier', '')
            size = x.get('size', '')
            num_part = ''.join(filter(str.isdigit, identifier))
            num = int(num_part) if num_part else 0
            return (nail_type, num, size)
        
        sorted_stock = sorted(stock, key=sort_key)
        return jsonify({'success': True, 'stock': sorted_stock})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/view_low_stock')
@require_auth
def view_low_stock():
    """Get items with low stock (total quantity < 4 across all sizes for an ID)"""
    try:
        stock = warehouse.get_all_stock()
        LOW_STOCK_THRESHOLD = 4
        
        # First, aggregate all items by identifier
        aggregated = {}
        for item in stock:
            identifier = item['identifier']
            if identifier not in aggregated:
                aggregated[identifier] = {
                    'identifier': identifier,
                    'nail_type': item['nail_type'],
                    'sizes': [],
                    'total_quantity': 0
                }
            
            aggregated[identifier]['sizes'].append({
                'size': item['size'],
                'quantity': item['quantity']
            })
            aggregated[identifier]['total_quantity'] += item['quantity']
        
        # Filter only items where total quantity < threshold
        low_stock = {k: v for k, v in aggregated.items() if v['total_quantity'] < LOW_STOCK_THRESHOLD}
        
        def sort_key(x):
            nail_type = x['nail_type']
            identifier = x['identifier']
            num_part = ''.join(filter(str.isdigit, identifier))
            num = int(num_part) if num_part else 0
            return (nail_type, num)
        
        low_stock_sorted = sorted(low_stock.values(), key=sort_key)
        return jsonify({'success': True, 'low_stock': low_stock_sorted})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# REPORT GENERATION ROUTES
# ============================================================================

@app.route('/generate_report', methods=['POST'])
@require_auth
def generate_report():
    """Generate CSV report"""
    try:
        data = request.json
        report_type = data.get('type', 'all')
        exported_by = data.get('exported_by', 'Unknown')
        
        stock = warehouse.get_all_stock()
        
        csv_content = "Type,ID,Product Name,Size,Quantity\n"
        
        item_names = warehouse.get_all_item_names()
        
        def sort_key(x):
            nail_type = x.get('nail_type', '')
            identifier = x.get('identifier', '')
            size = x.get('size', '')
            num_part = ''.join(filter(str.isdigit, identifier))
            num = int(num_part) if num_part else 0
            return (nail_type, num, size)
        
        sorted_stock = sorted(stock, key=sort_key)
        
        for item in sorted_stock:
            # For supply types, identifier is the key; for nail products, nail_type+identifier
            is_supply = item['nail_type'] in ['Glue', 'Toolkit', 'Box']
            key = item['identifier'] if is_supply else f"{item['nail_type']}{item['identifier']}"
            name = item_names.get(key, 'Unknown')
            csv_content += f"{item['nail_type']},{item['identifier']},{name},{item['size']},{item['quantity']}\n"

        # Available types by size summary
        size_type_map = {}
        for item in sorted_stock:
            item_size = item.get('size', '')
            item_type = item.get('nail_type', '')
            if item_size and item_type:
                if item_size not in size_type_map:
                    size_type_map[item_size] = set()
                size_type_map[item_size].add(item_type)

        csv_content += "\n"
        csv_content += "AVAILABLE TYPES BY SIZE\n"
        csv_content += "Size,Unique Types,Types\n"
        for size in sorted(size_type_map.keys()):
            types = sorted(size_type_map[size])
            csv_content += f"{size},{len(types)},\"{', '.join(types)}\"\n"

        # Detailed inventory by size
        size_groups = {}
        for item in sorted_stock:
            item_size = item.get('size', '')
            if item_size not in size_groups:
                size_groups[item_size] = []
            size_groups[item_size].append(item)

        csv_content += "\n"
        csv_content += "INVENTORY BY SIZE (DETAILED)\n"
        for size in sorted(size_groups.keys()):
            items = size_groups[size]
            total_units = sum(i.get('quantity', 0) for i in items)
            csv_content += f"\nSize: {size} ({len(items)} products, {total_units} units)\n"
            csv_content += "TYPE,ID,PRODUCT NAME,QUANTITY\n"
            for item in items:
                is_supply = item['nail_type'] in ['Glue', 'Toolkit', 'Box']
                key = item['identifier'] if is_supply else f"{item['nail_type']}{item['identifier']}"
                name = item_names.get(key, 'Unknown')
                csv_content += f"{item['nail_type']},{item['identifier']},\"{name}\",{item.get('quantity', 0)}\n"
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=sora_inventory_report.csv'
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/preview_report', methods=['POST'])
@require_auth
def preview_report():
    """Generate report preview as text"""
    try:
        data = request.json
        exported_by = data.get('exported_by', 'Unknown')
        
        # Use the report generator to create text report
        from pipeline.reporting.report_generator import ReportGenerator
        generator = ReportGenerator()
        report_content = generator.generate_text_report(exported_by)
        
        return jsonify({'success': True, 'report_content': report_content})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate_report_pdf', methods=['POST'])
@require_auth
def generate_report_pdf():
    """Generate PDF report"""
    try:
        data = request.json
        exported_by = data.get('exported_by', 'Unknown')
        
        stock = warehouse.get_all_stock()
        item_names = warehouse.get_all_item_names()
        
        def sort_key(x):
            nail_type = x.get('nail_type', '')
            identifier = x.get('identifier', '')
            size = x.get('size', '')
            num_part = ''.join(filter(str.isdigit, identifier))
            num = int(num_part) if num_part else 0
            return (nail_type, num, size)
        
        sorted_stock = sorted(stock, key=sort_key)
        
        # Low stock analysis - aggregate all items by ID first
        LOW_STOCK_THRESHOLD = 4
        aggregated = {}
        for item in stock:
            identifier = item['identifier']
            if identifier not in aggregated:
                aggregated[identifier] = {
                    'identifier': identifier,
                    'nail_type': item['nail_type'],
                    'items': [],
                    'total_quantity': 0
                }
            aggregated[identifier]['items'].append({
                'size': item['size'],
                'quantity': item['quantity']
            })
            aggregated[identifier]['total_quantity'] += item['quantity']
        
        # Filter only items with total_quantity < threshold
        low_stock = {k: v for k, v in aggregated.items() if v['total_quantity'] < LOW_STOCK_THRESHOLD}
        
        def low_stock_sort_key(x):
            nail_type = x['nail_type']
            identifier = x['identifier']
            num_part = ''.join(filter(str.isdigit, identifier))
            num = int(num_part) if num_part else 0
            return (nail_type, num)
        
        low_stock_sorted = sorted(low_stock.values(), key=low_stock_sort_key)
        
        # Create PDF
        BODY_FONT_SIZE = 12
        BODY_LEADING = 15

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.black,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=BODY_FONT_SIZE,
            leading=BODY_LEADING,
            textColor=colors.black
        )
        
        # Title
        elements.append(Paragraph("SORA STUDIO WAREHOUSE REPORT", title_style))
        elements.append(Spacer(1, 12))
        
        # Report info
        info_data = [
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
            ['Report Time:', datetime.now().strftime('%H:%M:%S')],
            ['Prepared By:', exported_by]
        ]
        info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), BODY_FONT_SIZE),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Summary
        total_quantity = sum(item.get('quantity', 0) for item in sorted_stock)
        elements.append(Paragraph("INVENTORY SUMMARY", heading_style))
        summary_data = [
            ['Total Items:', str(len(sorted_stock))],
            ['Total Quantity:', f"{total_quantity:,}"],
            ['Low Stock IDs:', str(len(low_stock_sorted))]
        ]
        summary_table = Table(summary_data, colWidths=[1.5*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), BODY_FONT_SIZE),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        elements.append(PageBreak())
        
        # Complete Stock Inventory
        elements.append(Paragraph("COMPLETE STOCK INVENTORY", heading_style))
        
        # Group by type
        current_type = None
        stock_data = None
        
        for item in sorted_stock:
            key = item['identifier']
            name = item_names.get(key, 'Unknown')
            
            if item['nail_type'] != current_type:
                # Create table for previous type
                if stock_data and len(stock_data) > 1:
                    stock_table = Table(stock_data, colWidths=[1*inch, 3*inch, 0.8*inch, 1*inch], repeatRows=1)
                    stock_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), BODY_FONT_SIZE),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    elements.append(stock_table)
                    elements.append(Spacer(1, 12))
                
                # Start new type
                current_type = item['nail_type']
                type_capacity = warehouse.get_nail_type_info(current_type)
                elements.append(Paragraph(f"Type {current_type} — {type_capacity}k", heading_style))
                
                # Table header
                stock_data = [['ID', 'Product Name', 'Size', 'Quantity']]
            
            # Add item to current table
            stock_data.append([item['identifier'], name, item['size'], str(item['quantity'])])
        
        # Create table for last type
        if stock_data and len(stock_data) > 1:
            stock_table = Table(stock_data, colWidths=[1*inch, 3*inch, 0.8*inch, 1*inch], repeatRows=1)
            stock_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), BODY_FONT_SIZE),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(stock_table)
            elements.append(Spacer(1, 20))
        elements.append(PageBreak())
        
        # Low Stock Section
        elements.append(Paragraph("LOW STOCK ITEMS", heading_style))
        
        if low_stock_sorted:
            low_stock_data = [['Type', 'ID', 'Total Quantity', 'Sizes Available']]
            for item in low_stock_sorted:
                sizes_str = ', '.join([f"{i['size']}({i['quantity']})" for i in item['items']])
                low_stock_data.append([
                    item['nail_type'],
                    item['identifier'],
                    str(item['total_quantity']),
                    sizes_str
                ])
            
            low_table = Table(low_stock_data, colWidths=[0.7*inch, 1*inch, 1.2*inch, 3.5*inch], repeatRows=1)
            low_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), BODY_FONT_SIZE),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(low_table)
        else:
            elements.append(Paragraph("No items with low stock - All items are well stocked.", body_style))
        
        elements.append(Spacer(1, 20))
        elements.append(PageBreak())
        
        # Analysis Section
        elements.append(Paragraph("INVENTORY ANALYSIS", heading_style))
        
        analyzer = InventoryAnalyzer()
        summary = analyzer.get_analysis_summary()
        health = summary['health_metrics']
        size_dist = summary['size_distribution']
        
        # Health metrics
        health_data = [
            ['Metric', 'Value'],
            ['Total Quantity', f"{health['total_quantity']:,}"],
            ['Unique Products', str(health['unique_products'])],
            ['Avg Stock/Product', f"{health['average_stock_per_product']:.2f}"],
            ['Low Stock (<4)', f"{health['low_stock_products']} ({health['low_stock_percentage']}%)"],
            ['Medium Stock (4-10)', str(health['medium_stock_products'])],
            ['High Stock (>10)', str(health['high_stock_products'])],
            ['Health Score', health['stock_health_score']]
        ]
        
        health_table = Table(health_data, colWidths=[2.5*inch, 2*inch])
        health_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), BODY_FONT_SIZE),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(health_table)
        elements.append(Spacer(1, 12))
        
        # Size distribution
        size_data = [['Size', 'Total Quantity']]
        for size in ['XS', 'S', 'M', 'L']:
            qty = size_dist['totals'].get(size, 0)
            size_data.append([size, f"{qty:,}"])
        
        size_table = Table(size_data, colWidths=[1*inch, 1.5*inch])
        size_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), BODY_FONT_SIZE),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(size_table)

        elements.append(Spacer(1, 12))

        # Available types by size
        elements.append(Paragraph("AVAILABLE TYPES BY SIZE", heading_style))

        size_type_map = {}
        for item in sorted_stock:
            item_size = item.get('size', '')
            item_type = item.get('nail_type', '')
            if item_size and item_type:
                if item_size not in size_type_map:
                    size_type_map[item_size] = set()
                size_type_map[item_size].add(item_type)

        available_types_data = [['Size', 'Unique Types', 'Types']]
        for size in sorted(size_type_map.keys()):
            types = sorted(size_type_map[size])
            available_types_data.append([size, str(len(types)), ', '.join(types)])

        available_types_table = Table(available_types_data, colWidths=[1*inch, 1.2*inch, 3.3*inch], repeatRows=1)
        available_types_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), BODY_FONT_SIZE),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(available_types_table)

        elements.append(Spacer(1, 12))

        # Detailed inventory by size
        elements.append(Paragraph("INVENTORY BY SIZE (DETAILED)", heading_style))
        size_groups = {}
        for item in sorted_stock:
            item_size = item.get('size', '')
            if item_size not in size_groups:
                size_groups[item_size] = []
            size_groups[item_size].append(item)

        for size in sorted(size_groups.keys()):
            items = size_groups[size]
            total_units = sum(i.get('quantity', 0) for i in items)
            elements.append(Paragraph(f"Size: {size} ({len(items)} products, {total_units} units)", body_style))

            size_detail_data = [['Type', 'ID', 'Product Name', 'Quantity']]
            for item in items:
                is_supply = item['nail_type'] in ['Glue', 'Toolkit', 'Box']
                key = item['identifier'] if is_supply else f"{item['nail_type']}{item['identifier']}"
                name = item_names.get(key, 'Unknown')
                size_detail_data.append([
                    item['nail_type'],
                    item['identifier'],
                    name,
                    str(item.get('quantity', 0))
                ])

            size_detail_table = Table(size_detail_data, colWidths=[0.8*inch, 1*inch, 3.0*inch, 0.9*inch], repeatRows=1)
            size_detail_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), BODY_FONT_SIZE),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(size_detail_table)
            elements.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(elements)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=sora_inventory_report.pdf'
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ANALYSIS ROUTES
# ============================================================================

@app.route('/view_analysis')
@require_auth
def view_analysis():
    """Get inventory analysis summary"""
    try:
        analyzer = InventoryAnalyzer()
        summary = analyzer.get_analysis_summary()
        return jsonify({'success': True, 'analysis': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate_analysis', methods=['POST'])
@require_auth
def generate_analysis():
    """Generate and download analysis report"""
    try:
        data = request.json
        analyst_name = data.get('analyst_name', 'Unknown')
        
        analyzer = InventoryAnalyzer()
        report_content = analyzer.generate_analysis_report(analyst_name)
        
        response = make_response(report_content)
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Content-Disposition'] = 'attachment; filename=inventory_analysis.txt'
        return response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ITEM MANAGEMENT ROUTES
# ============================================================================

@app.route('/delete_stock', methods=['POST'])
@require_auth
def delete_stock():
    """Delete stock item or reduce quantity"""
    try:
        data = request.json
        nail_type = data.get('nail_type')
        identifier = data.get('identifier')
        size = data.get('size')
        quantity = data.get('quantity')
        
        if not all([nail_type, identifier, size]):
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        success = warehouse.delete_item(nail_type, identifier, size, quantity)
        
        # For supply types, don't concatenate type and identifier
        is_supply = nail_type in ['Glue', 'Toolkit', 'Box']
        display_id = identifier if is_supply else f'{nail_type}{identifier}'
        
        if success:
            if quantity:
                remaining = warehouse.get_stock(nail_type, identifier, size)
                if remaining == 0:
                    message = f'Deleted all {display_id}-{size}'
                else:
                    message = f'Deleted {quantity} units of {display_id}-{size}. Remaining: {remaining}'
            else:
                message = f'Deleted item {display_id}-{size} completely'
            
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete stock'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/get_item_names', methods=['GET'])
@require_auth
def get_item_names():
    """Get all item names"""
    try:
        names = warehouse.get_all_item_names()
        return jsonify({'success': True, 'names': names})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/update_item_name', methods=['POST'])
@require_auth
def update_item_name():
    """Update item name"""
    try:
        data = request.json
        nail_type = data.get('nail_type')
        identifier = data.get('identifier')
        name = data.get('name')
        changed_by = data.get('changed_by', 'Unknown')
        
        if not all([nail_type, identifier, name]):
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        success = warehouse.update_item_name(nail_type, identifier, name, changed_by)
        
        # For supply types, don't concatenate type and identifier
        is_supply = nail_type in ['Glue', 'Toolkit', 'Box']
        display_id = identifier if is_supply else f'{nail_type}{identifier}'
        
        if success:
            return jsonify({'success': True, 'message': f'Updated {display_id} to "{name}"'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update name'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/initialize_names', methods=['POST'])
@require_auth
def initialize_names():
    """Initialize default item names in database"""
    try:
        success = warehouse.initialize_default_names()
        if success:
            return jsonify({'success': True, 'message': 'Default names initialized'})
        else:
            return jsonify({'success': False, 'message': 'Failed to initialize names'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/get_name_change_log', methods=['GET'])
@require_auth
def get_name_change_log():
    """Get name change history"""
    try:
        item_key = request.args.get('item_key')
        logs = warehouse.get_name_change_log(item_key)
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# SERVER STARTUP
# ============================================================================

def start_server(port=5000):
    """Start the Flask server and display QR code"""
    def is_private_ipv4(ip: str) -> bool:
        """Return True if IP is in RFC1918 private ranges."""
        return (
            ip.startswith('10.') or
            ip.startswith('192.168.') or
            (ip.startswith('172.') and ip.split('.')[1].isdigit() and 16 <= int(ip.split('.')[1]) <= 31)
        )

    # Generate or load security PIN
    security_pin = get_security_pin()
    
    local_ip = get_local_ip()
    localhost_url = f"http://127.0.0.1:{port}"
    host_alias_url = f"http://localhost:{port}"
    network_url = f"http://{local_ip}:{port}"
    qr_url = network_url if is_private_ipv4(local_ip) else localhost_url
    
    print("\n" + "="*60)
    print("🏭 SORA WAREHOUSE MANAGEMENT SYSTEM")
    print("="*60)
    print(f"\n🔒 SECURITY ENABLED")
    print(f"   Access PIN: {security_pin}")
    print(f"   Session Token: {ACCESS_TOKEN[:16]}...")
    print("\n💻 Open from this computer:")
    print(f"   • {localhost_url}")
    print(f"   • {host_alias_url}")
    print("\n📱 Phone / network URL:")
    print(f"   • {network_url}")
    if not is_private_ipv4(local_ip):
        print("   • Note: detected IP is not a private WiFi LAN address; use localhost on this computer or switch to WiFi LAN IP.")
    print("\n📱 Scan this QR code with your phone:")
    print(f"\n   QR URL: {qr_url}\n")
    
    qr = qrcode.QRCode()
    qr.add_data(qr_url)
    qr.make()
    qr.print_ascii(invert=True)
    
    print(f"\n💡 Security Features:")
    print(f"   • PIN authentication required")
    print(f"   • Rate limiting (5 attempts per 5 minutes)")
    print(f"   • Session expires after 1 hour of inactivity")
    print(f"   • QR code changes with your IP address")
    print(f"\n🌐 Network:")
    print(f"   • Local IP: {local_ip}")
    print(f"   • Port: {port}")
    print(f"   • Make sure your phone is on the same WiFi network!")
    print(f"\n💾 Database: Supabase (credentials in .env)")
    print("\n" + "="*60)
    print("⚠️  IMPORTANT: Keep your PIN and .env file secure!")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    start_server(8080)
