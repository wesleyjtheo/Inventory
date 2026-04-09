LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sora Warehouse - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#000000">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="/manifest.webmanifest">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
        }
        .login-container {
            background: #fff;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            max-width: 400px;
            width: 100%;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
            background: #000;
            color: #fff;
            padding: 20px;
            border-radius: 8px;
            margin: -40px -40px 30px -40px;
        }
        .logo h1 {
            font-size: 24px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 4px;
            letter-spacing: 0.5px;
        }
        .logo p {
            color: #ccc;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .form-group {
            margin-bottom: 24px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .form-group input {
            width: 100%;
            padding: 14px;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            font-size: 18px;
            transition: all 0.2s;
            text-align: center;
            letter-spacing: 8px;
            font-weight: 600;
            background: #fff;
        }
        .form-group input:focus {
            outline: none;
            border-color: #000;
            box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
        }
        .login-btn {
            width: 100%;
            padding: 16px;
            background: #000;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .login-btn:hover {
            background: #333;
        }
        .login-btn:active {
            transform: scale(0.98);
        }
        .login-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .error-message {
            background: #000;
            color: #fff;
            padding: 14px;
            border-radius: 6px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
            display: none;
            border: 1px solid #000;
        }
        .security-note {
            margin-top: 20px;
            padding: 14px;
            background: #f8f8f8;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        .security-note strong {
            color: #000;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🏭 SORA STUDIO</h1>
            <p>Warehouse Management System</p>
        </div>
        <div class="error-message" id="errorMessage"></div>
        <form id="loginForm">
            <div class="form-group">
                <label for="pin">Enter Security PIN</label>
                <input type="password" id="pin" maxlength="6" pattern="[0-9]{6}" inputmode="numeric" required autocomplete="off">
            </div>
            <button type="submit" class="login-btn" id="loginBtn">Access System</button>
        </form>
        <div class="security-note">
            <strong>🔒 Secure Connection</strong><br>
            This session is protected and will expire after 1 hour of inactivity
        </div>
    </div>
    <script>
        const form = document.getElementById('loginForm');
        const pinInput = document.getElementById('pin');
        const loginBtn = document.getElementById('loginBtn');
        const errorMessage = document.getElementById('errorMessage');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const pin = pinInput.value;
            
            if (pin.length !== 6) {
                showError('PIN must be 6 digits');
                return;
            }
            
            loginBtn.disabled = true;
            loginBtn.textContent = 'Verifying...';
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ pin: pin })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    window.location.href = '/';
                } else {
                    showError(result.message || 'Invalid PIN');
                    pinInput.value = '';
                    loginBtn.disabled = false;
                    loginBtn.textContent = 'Access System';
                }
            } catch (error) {
                showError('Connection error. Please try again.');
                loginBtn.disabled = false;
                loginBtn.textContent = 'Access System';
            }
        });
        
        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 5000);
        }

        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js').catch((error) => {
                    console.error('Service worker registration failed:', error);
                });
            });
        }
        
        pinInput.focus();
    </script>
</body>
</html>
"""

# HTML Template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sora Warehouse Scanner</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#000000">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="/manifest.webmanifest">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
            padding: 16px;
        }
        .header {
            background: #000;
            color: #fff;
            padding: 16px 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }
        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-shrink: 0;
        }
        .session-indicator {
            font-size: 11px;
            color: #4ade80;
            white-space: nowrap;
        }
        .header h1 {
            font-size: 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin: 0;
            flex-grow: 1;
            text-align: center;
        }
        .logout-btn {
            background: #fff;
            color: #000;
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
            flex-shrink: 0;
        }
        .logout-btn:hover {
            background: #f0f0f0;
        }
        .container {
            background: #fff;
            border-radius: 8px;
            padding: 20px;
            max-width: 480px;
            margin: 0 auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .action-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 24px;
        }
        .action-btn {
            padding: 16px;
            border: 2px solid #e0e0e0;
            background: #fff;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
        }
        .action-btn:hover {
            border-color: #666;
        }
        .action-btn.active {
            background: #000;
            color: #fff;
            border-color: #000;
        }
        .form-section {
            margin-bottom: 20px;
        }
        .form-section label {
            display: block;
            margin-bottom: 6px;
            color: #333;
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        select, input[type="text"], input[type="number"] {
            width: 100%;
            padding: 14px;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            font-size: 16px;
            background: #fff;
            transition: all 0.2s;
            -webkit-appearance: none;
            appearance: none;
        }
        select {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23333' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 14px center;
            padding-right: 40px;
        }
        select:focus, input:focus {
            outline: none;
            border-color: #000;
            box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
        }
        input[type="text"]::placeholder {
            color: #999;
        }
        .stock-display {
            background: #f8f8f8;
            border: 1px solid #e0e0e0;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 20px;
            display: none;
        }
        .stock-display.visible {
            display: block;
        }
        .stock-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #666;
            margin-bottom: 4px;
        }
        .stock-value {
            font-size: 28px;
            font-weight: 600;
            color: #000;
        }
        .submit-btn {
            width: 100%;
            padding: 16px;
            background: #000;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .submit-btn:hover {
            background: #333;
        }
        .submit-btn:active {
            transform: scale(0.98);
        }
        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .message {
            padding: 14px;
            border-radius: 6px;
            margin-top: 16px;
            font-size: 14px;
            text-align: center;
            display: none;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .success {
            background: #f0f0f0;
            color: #000;
            border: 1px solid #d0d0d0;
        }
        .error {
            background: #000;
            color: #fff;
            border: 1px solid #000;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 12px;
        }
        .view-stock-btn {
            width: 100%;
            padding: 12px;
            background: #fff;
            color: #000;
            border: 1px solid #000;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.2s;
        }
        .view-stock-btn:hover {
            background: #000;
            color: #fff;
        }
        .button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 16px;
        }
        .secondary-btn {
            padding: 12px;
            background: #fff;
            color: #666;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.2s;
        }
        .secondary-btn:hover {
            border-color: #000;
            color: #000;
        }
        .low-stock-row {
            background: #fff3cd !important;
        }
        .delete-btn {
            background: #000;
            color: #fff;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }
        .delete-btn:hover {
            background: #d32f2f;
        }
        .modal-buttons {
            display: flex;
            gap: 8px;
            justify-content: flex-end;
            margin-top: 16px;
        }
        .modal-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-cancel {
            background: #f0f0f0;
            color: #666;
        }
        .btn-cancel:hover {
            background: #e0e0e0;
        }
        .btn-confirm {
            background: #000;
            color: #fff;
        }
        .btn-confirm:hover {
            background: #d32f2f;
        }
        .delete-modal-content {
            background: #fff;
            border-radius: 8px;
            padding: 24px;
            max-width: 400px;
            width: 100%;
            margin: 20px;
        }
        .delete-input {
            width: 100%;
            padding: 10px;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            font-size: 14px;
            margin-top: 12px;
        }
        .names-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 12px;
            margin-top: 16px;
            max-height: 500px;
            overflow-y: auto;
        }
        .name-item {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }
        .name-item-header {
            font-weight: 700;
            font-size: 13px;
            margin-bottom: 8px;
            color: #000;
        }
        .name-input {
            width: 100%;
            padding: 8px;
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            font-size: 13px;
        }
        .save-name-btn {
            background: #000;
            color: #fff;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            margin-top: 6px;
            font-weight: 600;
        }
        .save-name-btn:hover {
            background: #333;
        }
        .init-names-btn {
            background: #28a745;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            font-weight: 600;
            margin-bottom: 16px;
        }
        .init-names-btn:hover {
            background: #218838;
        }
        .history-btn {
            background: #007bff;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            font-weight: 600;
            margin-bottom: 16px;
            margin-left: 8px;
        }
        .history-btn:hover {
            background: #0056b3;
        }
        .search-box {
            width: 100%;
            padding: 12px;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            font-size: 14px;
            margin-bottom: 16px;
        }
        .search-container {
            padding: 0 20px 10px 20px;
        }
        .type-section {
            margin-bottom: 20px;
        }
        .type-header {
            background: #000;
            color: #fff;
            padding: 8px 12px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 8px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .type-header:hover {
            background: #333;
        }
        .type-items {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 12px;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            overflow-y: auto;
            padding: 20px;
        }
        .modal.active {
            display: flex;
            align-items: flex-start;
            justify-content: center;
        }
        .modal-content {
            background: #fff;
            border-radius: 8px;
            padding: 24px;
            max-width: 600px;
            width: 100%;
            margin: 20px auto;
            position: relative;
        }
        .bulk-modal-content {
            background: #fff;
            border-radius: 8px;
            padding: 24px;
            max-width: 900px;
            width: 100%;
            margin: 20px auto;
            position: relative;
            max-height: 90vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e0e0e0;
        }
        .modal-header h2 {
            font-size: 18px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .close-btn {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .stock-table {
            width: 100%;
            border-collapse: collapse;
        }
        .stock-table th {
            text-align: left;
            padding: 12px 8px;
            border-bottom: 2px solid #000;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }
        .stock-table td {
            padding: 12px 8px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 14px;
        }
        .stock-table tr:hover {
            background: #f8f8f8;
        }
        .low-stock-id-row {
            cursor: pointer;
            font-weight: 600;
        }
        .low-stock-id-row:hover {
            background: #f0f0f0;
        }
        .low-stock-detail-row {
            background: #fafafa;
        }
        .low-stock-detail-row td {
            padding-left: 30px;
            font-size: 13px;
            color: #666;
        }
        .expand-icon {
            display: inline-block;
            margin-right: 8px;
            transition: transform 0.2s;
        }
        .expand-icon.expanded {
            transform: rotate(90deg);
        }
        .stock-qty {
            font-weight: 600;
            color: #000;
        }
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #999;
        }
        .grouped-stock-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            padding: 20px 0;
        }
        .stock-group-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }
        .stock-group-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        .stock-group-card:nth-child(1) {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stock-group-card:nth-child(2) {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .stock-group-card:nth-child(3) {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .stock-group-card:nth-child(4) {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        .stock-group-card:nth-child(5) {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        .stock-group-card:nth-child(6) {
            background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
        }
        .stock-group-card:nth-child(7) {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        }
        .stock-group-header h3 {
            margin: 0 0 12px 0;
            font-size: 18px;
            font-weight: 600;
        }
        .stock-group-total {
            font-size: 32px;
            font-weight: 700;
            margin: 12px 0;
        }
        .stock-group-meta {
            font-size: 14px;
            opacity: 0.9;
            margin-top: 8px;
        }
        .stock-group-arrow {
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 24px;
            opacity: 0.6;
            transition: all 0.3s ease;
        }
        .stock-group-card:hover .stock-group-arrow {
            opacity: 1;
            right: 15px;
        }
        .back-btn {
            background: #2196F3;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 16px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: background 0.2s;
        }
        .back-btn:hover {
            background: #1976D2;
        }
        .loading {
            text-align: center;
            padding: 40px 20px;
        }
        .analysis-container {
            max-height: 600px;
            overflow-y: auto;
            padding: 20px;
        }
        .analysis-section {
            margin-bottom: 30px;
            background: #fafafa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #000;
        }
        .analysis-section h3 {
            margin: 0 0 15px 0;
            font-size: 16px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        .analysis-stat {
            background: #fff;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }
        .analysis-stat-label {
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        .analysis-stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #000;
        }
        .analysis-table {
            width: 100%;
            background: #fff;
            border-collapse: collapse;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .analysis-table th {
            background: #000;
            color: #fff;
            padding: 12px 8px;
            text-align: left;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .analysis-table td {
            padding: 10px 8px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 13px;
        }
        .analysis-table tr:hover {
            background: #f8f8f8;
        }
        .health-score {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
        }
        .health-excellent { background: #d4edda; color: #155724; }
        .health-good { background: #d1ecf1; color: #0c5460; }
        .health-fair { background: #fff3cd; color: #856404; }
        .health-needs-attention { background: #f8d7da; color: #721c24; }
        .download-analysis-btn {
            position: absolute;
            top: 20px;
            right: 60px;
            padding: 10px 20px;
            background: #000;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .download-analysis-btn:hover {
            background: #333;
        }
        .upload-area {
            border: 2px dashed #d0d0d0;
            border-radius: 8px;
            padding: 32px;
            text-align: center;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .upload-area:hover {
            border-color: #000;
            background: #f8f8f8;
        }
        .upload-area.dragover {
            border-color: #000;
            background: #f0f0f0;
        }
        .upload-icon {
            font-size: 48px;
            margin-bottom: 12px;
            color: #999;
        }
        .upload-text {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }
        .file-input {
            display: none;
        }
        .bulk-stats {
            background: #f5f5f5;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 20px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #000;
            margin-bottom: 4px;
        }
        .stat-label {
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .bulk-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 13px;
        }
        .bulk-table th {
            text-align: left;
            padding: 10px 8px;
            border-bottom: 2px solid #000;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }
        .bulk-table td {
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
        }
        .bulk-table tr:hover {
            background: #f8f8f8;
        }
        .duplicate-row {
            background: #fff3cd !important;
            opacity: 0.7;
        }
        .duplicate-row td {
            color: #856404;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-new {
            background: #d4edda;
            color: #155724;
        }
        .badge-duplicate {
            background: #fff3cd;
            color: #856404;
        }
        .confirm-save-btn {
            width: 100%;
            padding: 16px;
            background: #000;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.2s;
        }
        .confirm-save-btn:hover {
            background: #28a745;
        }
        .confirm-save-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .processing {
            display: inline-block;
            margin-left: 8px;
        }
        .remove-row-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 4px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .remove-row-btn:hover {
            background: #c82333;
            transform: scale(1.05);
        }
        .removed-row {
            opacity: 0.3;
            text-decoration: line-through;
            background: #f8d7da !important;
        }
        .removed-row .remove-row-btn {
            display: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <span class="session-indicator">🔒 Secure</span>
        </div>
        <h1>SORA WAREHOUSE</h1>
        <button class="logout-btn" onclick="logout()">Logout</button>
    </div>
    
    <div class="container">
        <div class="action-buttons">
            <button type="button" class="action-btn" data-action="input" onclick="selectAction('input')">
                IN
            </button>
            <button type="button" class="action-btn" data-action="output" onclick="selectAction('output')">
                OUT
            </button>
        </div>
        
        <form id="inventoryForm">
            <input type="hidden" id="action" name="action" value="">
            
            <div class="form-section">
                <label for="nail_type">Type</label>
                <select id="nail_type" name="nail_type" required onchange="handleTypeChange()">
                    <option value="">Select Type</option>
                    <optgroup label="Nail Products">
                        <option value="X">X — 250k</option>
                        <option value="S">S — 200k</option>
                        <option value="C">C — 180k</option>
                        <option value="M">M — 150k</option>
                        <option value="A">A — 130k</option>
                        <option value="B">B — 100k</option>
                    </optgroup>
                    <optgroup label="Supplies">
                        <option value="Glue">Glue</option>
                        <option value="Toolkit">Toolkit</option>
                        <option value="Box">Box</option>
                    </optgroup>
                </select>
            </div>
            
            <div class="form-section" id="identifierSection">
                <label for="identifier">ID</label>
                <input type="text" id="identifier" name="identifier" placeholder="e.g., S1, S2, X1" required onchange="updateStockInfo()" oninput="updateStockInfo()">
            </div>
            
            <div class="grid-2">
                <div class="form-section" id="sizeSection">
                    <label for="size">Size</label>
                    <select id="size" name="size" required onchange="updateStockInfo()">
                        <option value="">Select Size</option>
                        <option value="XS">XS</option>
                        <option value="S">S</option>
                        <option value="M">M</option>
                        <option value="L">L</option>
                    </select>
                </div>
                
                <div class="form-section">
                    <label for="quantity">Qty</label>
                    <input type="number" id="quantity" name="quantity" min="1" placeholder="0" required>
                </div>
            </div>
            
            <div class="stock-display" id="stockDisplay">
                <div class="stock-label">CURRENT STOCK</div>
                <div class="stock-value" id="currentStock">0</div>
            </div>
            
            <button type="submit" class="submit-btn" id="submitBtn" disabled>Select Action</button>
        </form>
        
        <button type="button" class="view-stock-btn" onclick="viewStock()">View All Stock</button>
        
        <div class="button-group">
            <button type="button" class="secondary-btn" onclick="manageNames()">Manage Names</button>
        </div>
        
        <div class="button-group" style="margin-top: 12px;">
            <button type="button" class="secondary-btn" onclick="publishReport()">Publish Report</button>
            <button type="button" class="secondary-btn" onclick="viewAnalysis()">📊 Analysis</button>
            <button type="button" class="secondary-btn" onclick="bulkUpload()">Bulk Upload</button>
        </div>
        
        <div class="message" id="message"></div>
    </div>
    
    <div class="modal" id="stockModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Stock Inventory</h2>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div class="search-container" id="stockSearchContainer" style="display:none;">
                <input type="text" class="search-box" id="stockSearchBox" placeholder="Search by Type, ID, Product Name, or Size..." oninput="filterStockTable()">
            </div>
            <div id="stockTableContainer">
                <div class="loading">Loading...</div>
            </div>
        </div>
    </div>
    
    <!-- Bulk Upload Modal -->
    <div class="modal" id="bulkUploadModal">
        <div class="bulk-modal-content">
            <div class="modal-header">
                <h2>Bulk Upload</h2>
                <button class="close-btn" onclick="closeBulkModal()">&times;</button>
            </div>
            
            <div id="uploadSection">
                <div class="upload-area" id="uploadArea" onclick="document.getElementById('csvFileInput').click()">
                    <div class="upload-icon">📄</div>
                    <div class="upload-text">Click to upload or drag and drop your CSV file</div>
                    <div style="font-size: 12px; color: #999;">CSV format: date, Select IN or OUT, Select TYPE, ID, Size, QTY</div>
                </div>
                <input type="file" id="csvFileInput" class="file-input" accept=".csv" onchange="handleFileSelect(event)">
            </div>
            
            <div id="resultsSection" style="display: none;">
                <div class="bulk-stats">
                    <div class="stat-item">
                        <div class="stat-value" id="totalEntries">0</div>
                        <div class="stat-label">Total Entries</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="newEntries" style="color: #28a745;">0</div>
                        <div class="stat-label">New Entries</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="duplicateEntries" style="color: #856404;">0</div>
                        <div class="stat-label">Duplicates</div>
                    </div>
                </div>
                
                <div style="max-height: 400px; overflow-y: auto; margin-bottom: 20px;">
                    <table class="bulk-table">
                        <thead>
                            <tr>
                                <th>Status</th>
                                <th>Date</th>
                                <th>IN/OUT</th>
                                <th>Type</th>
                                <th>ID</th>
                                <th>Size</th>
                                <th>Qty</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="bulkTableBody">
                        </tbody>
                    </table>
                </div>
                
                <button class="confirm-save-btn" id="confirmSaveBtn" onclick="confirmBulkSave()">
                    Confirm & Save <span id="processing" class="processing" style="display: none;">⏳</span>
                </button>
            </div>
        </div>
    </div>
    
    <!-- Analysis Modal -->
    <div class="modal" id="analysisModal">
        <div class="modal-content" style="max-width: 1200px;">
            <div class="modal-header">
                <h2>📊 Inventory Analysis</h2>
                <button class="download-analysis-btn" onclick="downloadAnalysisReport()">Download Report</button>
                <button class="close-btn" onclick="closeAnalysisModal()">&times;</button>
            </div>
            <div id="analysisContainer" class="analysis-container">
                <div class="loading">Loading analysis...</div>
            </div>
        </div>
    </div>
    
    <!-- Report Preview Modal -->
    <div class="modal" id="reportPreviewModal">
        <div class="modal-content" style="max-width: 1000px;">
            <div class="modal-header">
                <h2>📄 Report Preview</h2>
                <div style="display: flex; gap: 10px;">
                    <button class="download-analysis-btn" onclick="confirmDownloadReport()">Download Report</button>
                    <button class="close-btn" onclick="closeReportPreview()">&times;</button>
                </div>
            </div>
            <div id="reportPreviewContainer" style="max-height: 70vh; overflow-y: auto; background: #f9f9f9; padding: 20px; border-radius: 4px;">
                <div class="loading">Loading report preview...</div>
            </div>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('inventoryForm');
        const message = document.getElementById('message');
        const actionInput = document.getElementById('action');
        const submitBtn = document.getElementById('submitBtn');
        const actionButtons = document.querySelectorAll('.action-btn');
        
        function selectAction(action) {
            actionInput.value = action;
            actionButtons.forEach(btn => {
                if (btn.dataset.action === action) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
            
            submitBtn.disabled = false;
            submitBtn.textContent = action === 'input' ? 'Add Stock' : 'Remove Stock';
        }
        
        function handleTypeChange() {
            const nailType = document.getElementById('nail_type').value;
            const identifierSection = document.getElementById('identifierSection');
            const sizeSection = document.getElementById('sizeSection');
            const identifierInput = document.getElementById('identifier');
            const sizeSelect = document.getElementById('size');
            
            // Check if it's a supply type
            const isSupply = ['Glue', 'Toolkit', 'Box'].includes(nailType);
            
            if (isSupply) {
                // Hide and disable ID and Size fields for supplies
                identifierSection.style.display = 'none';
                sizeSection.style.display = 'none';
                identifierInput.required = false;
                sizeSelect.required = false;
                
                // Auto-fill values
                identifierInput.value = nailType;
                sizeSelect.value = 'UNIT';
            } else {
                // Show and enable ID and Size fields for nail products
                identifierSection.style.display = 'block';
                sizeSection.style.display = 'block';
                identifierInput.required = true;
                sizeSelect.required = true;
                
                // Clear auto-filled values
                if (['Glue', 'Toolkit', 'Box'].includes(identifierInput.value)) {
                    identifierInput.value = '';
                }
                if (sizeSelect.value === 'UNIT') {
                    sizeSelect.value = '';
                }
            }
            
            // Update stock info
            updateStockInfo();
        }
        
        async function updateStockInfo() {
            const nailType = document.getElementById('nail_type').value;
            const identifier = document.getElementById('identifier').value;
            const size = document.getElementById('size').value;
            const stockDisplay = document.getElementById('stockDisplay');
            const currentStock = document.getElementById('currentStock');
            
            // For supply types, use the type as identifier if not set
            const effectiveIdentifier = ['Glue', 'Toolkit', 'Box'].includes(nailType) ? nailType : identifier;
            const effectiveSize = ['Glue', 'Toolkit', 'Box'].includes(nailType) ? 'UNIT' : size;
            
            if (nailType && effectiveIdentifier && effectiveSize) {
                try {
                    const response = await fetch(`/get_stock?nail_type=${nailType}&identifier=${effectiveIdentifier}&size=${effectiveSize}`);
                    const data = await response.json();
                    currentStock.textContent = data.stock;
                    stockDisplay.classList.add('visible');
                } catch (error) {
                    console.error('Error fetching stock:', error);
                }
            } else {
                stockDisplay.classList.remove('visible');
            }
        }
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!actionInput.value) {
                message.style.display = 'block';
                message.className = 'message error';
                message.textContent = 'Please select an action (IN or OUT)';
                setTimeout(() => {
                    message.style.display = 'none';
                }, 3000);
                return;
            }
            
            const formData = new FormData(form);
            const nailType = formData.get('nail_type');
            const isSupply = ['Glue', 'Toolkit', 'Box'].includes(nailType);
            const identifier = isSupply ? nailType : formData.get('identifier');
            const size = isSupply ? 'UNIT' : formData.get('size');
            const data = {
                action: actionInput.value,
                nail_type: nailType,
                identifier: identifier,
                size: size,
                quantity: parseInt(formData.get('quantity'))
            };
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            
            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                message.style.display = 'block';
                if (result.success) {
                    message.className = 'message success';
                    message.textContent = result.message;
                    // Reset only ID, Size, Quantity, and Action (keep Type selected)
                    if (!isSupply) {
                        document.querySelector('input[name="identifier"]').value = '';
                        document.querySelector('select[name="size"]').value = '';
                    }
                    document.querySelector('input[name="quantity"]').value = '';
                    actionInput.value = '';
                    actionButtons.forEach(btn => btn.classList.remove('active'));
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Select Action';
                    document.getElementById('stockDisplay').classList.remove('visible');
                    handleTypeChange();
                    updateStockInfo();
                } else {
                    message.className = 'message error';
                    message.textContent = result.message;
                    submitBtn.disabled = false;
                    submitBtn.textContent = data.action === 'input' ? 'Add Stock' : 'Remove Stock';
                }
                
                setTimeout(() => {
                    message.style.display = 'none';
                }, 4000);
                
            } catch (error) {
                message.style.display = 'block';
                message.className = 'message error';
                message.textContent = 'Error: ' + error.message;
                submitBtn.disabled = false;
                submitBtn.textContent = data.action === 'input' ? 'Add Stock' : 'Remove Stock';
            }
        });
        
        let itemNames = {};
        
        async function logout() {
            if (confirm('Are you sure you want to logout?')) {
                try {
                    await fetch('/logout', { method: 'POST' });
                    window.location.href = '/login';
                } catch (error) {
                    console.error('Logout error:', error);
                    window.location.href = '/login';
                }
            }
        }
        
        async function loadItemNames() {
            try {
                const response = await fetch('/get_item_names');
                const data = await response.json();
                if (data.success) {
                    itemNames = data.names;
                }
            } catch (error) {
                console.error('Error loading item names:', error);
            }
        }
        
        // Load names on page load
        loadItemNames();
        
        function getItemDisplayName(nailType, identifier) {
            // For supply types, don't concatenate (identifier already equals nailType)
            const isSupply = ['Glue', 'Toolkit', 'Box'].includes(nailType);
            const key = isSupply ? identifier : `${nailType}${identifier}`;
            const name = itemNames[key];
            return name ? `${key} - ${name}` : key;
        }
        
        function filterStockTable() {
            const searchTerm = document.getElementById('stockSearchBox').value.toLowerCase().trim();
            const container = document.getElementById('stockTableContainer');
            
            // If in grouped view, don't filter - just show all groups
            if (currentViewMode === 'grouped') {
                if (!searchTerm) {
                    container.innerHTML = renderGroupedStockView(currentStockData);
                } else {
                    // Filter and show detailed table when searching in grouped view
                    const filteredStock = currentStockData.filter(item => {
                        const displayName = getItemDisplayName(item.nail_type, item.identifier);
                        return item.nail_type.toLowerCase().includes(searchTerm) ||
                               item.identifier.toLowerCase().includes(searchTerm) ||
                               item.size.toLowerCase().includes(searchTerm) ||
                               displayName.toLowerCase().includes(searchTerm);
                    });
                    container.innerHTML = '<button class=\"back-btn\" onclick=\"backToGroupedView()\">\u2190 Back to Groups</button>' + 
                                         renderStockTable(filteredStock, currentHighlightLow, currentShowDelete);
                }
                return;
            }
            
            // Detail view filtering
            if (!searchTerm) {
                // Show current group details
                if (currentGroup) {
                    let filteredStock;
                    if (currentGroup === 'Supplies') {
                        filteredStock = currentStockData.filter(item => ['Glue', 'Toolkit', 'Box'].includes(item.nail_type));
                    } else {
                        filteredStock = currentStockData.filter(item => item.nail_type === currentGroup);
                    }
                    container.innerHTML = '<button class=\"back-btn\" onclick=\"backToGroupedView()\">\u2190 Back to Groups</button>' + 
                                         renderStockTable(filteredStock, currentHighlightLow, currentShowDelete);
                } else {
                    container.innerHTML = renderStockTable(currentStockData, currentHighlightLow, currentShowDelete);
                }
                return;
            }
            
            // Apply search filter
            let baseStock = currentStockData;
            if (currentGroup) {
                if (currentGroup === 'Supplies') {
                    baseStock = currentStockData.filter(item => ['Glue', 'Toolkit', 'Box'].includes(item.nail_type));
                } else {
                    baseStock = currentStockData.filter(item => item.nail_type === currentGroup);
                }
            }
            
            const filteredStock = baseStock.filter(item => {
                const displayName = getItemDisplayName(item.nail_type, item.identifier);
                return item.nail_type.toLowerCase().includes(searchTerm) ||
                       item.identifier.toLowerCase().includes(searchTerm) ||
                       item.size.toLowerCase().includes(searchTerm) ||
                       displayName.toLowerCase().includes(searchTerm);
            });
            
            let html = '';
            if (currentGroup) {
                html = '<button class=\"back-btn\" onclick=\"backToGroupedView()\">\u2190 Back to Groups</button>';
            }
            html += renderStockTable(filteredStock, currentHighlightLow, currentShowDelete);
            container.innerHTML = html;
        }
        
        function renderLowStockTable(stock) {
            if (stock && stock.length > 0) {
                let html = '<table class="stock-table">';
                html += '<thead><tr>';
                html += '<th>Type</th>';
                html += '<th>ID</th>';
                html += '<th>Product Name</th>';
                html += '<th>Total Quantity</th>';
                html += '</tr></thead>';
                html += '<tbody>';
                
                stock.forEach((item, index) => {
                    const displayName = getItemDisplayName(item.nail_type, item.identifier);
                    const rowId = `low-stock-${index}`;
                    
                    // Main row with aggregated data
                    html += `<tr class="low-stock-id-row" onclick="toggleLowStockDetails('${rowId}')">`;
                    html += `<td><span class="expand-icon" id="icon-${rowId}">▶</span>${item.nail_type}</td>`;
                    html += `<td>${item.identifier}</td>`;
                    html += `<td>${displayName}</td>`;
                    html += `<td class="stock-qty">${item.total_quantity}</td>`;
                    html += '</tr>';
                    
                    // Hidden detail rows for each size
                    item.sizes.forEach(sizeData => {
                        html += `<tr class="low-stock-detail-row" id="${rowId}-detail" style="display:none;">`;
                        html += `<td></td>`;
                        html += `<td colspan="2">Size: ${sizeData.size}</td>`;
                        html += `<td class="stock-qty">${sizeData.quantity}</td>`;
                        html += '</tr>';
                    });
                });
                
                html += '</tbody></table>';
                return html;
            }
            return '<div class="empty-state">No low stock items</div>';
        }
        
        function toggleLowStockDetails(rowId) {
            const detailRows = document.querySelectorAll(`[id^="${rowId}-detail"]`);
            const icon = document.getElementById(`icon-${rowId}`);
            
            detailRows.forEach(row => {
                if (row.style.display === 'none') {
                    row.style.display = '';
                    icon.classList.add('expanded');
                } else {
                    row.style.display = 'none';
                    icon.classList.remove('expanded');
                }
            });
        }
        
        function renderGroupedStockView(stock) {
            // Group stock by type
            const groups = {
                'X': { name: 'Type X — 250k', items: [], total: 0 },
                'S': { name: 'Type S — 200k', items: [], total: 0 },
                'C': { name: 'Type C — 180k', items: [], total: 0 },
                'M': { name: 'Type M — 150k', items: [], total: 0 },
                'A': { name: 'Type A — 130k', items: [], total: 0 },
                'B': { name: 'Type B — 100k', items: [], total: 0 },
                'Supplies': { name: 'Supplies (Glue, Toolkit, Box)', items: [], total: 0 }
            };
            
            stock.forEach(item => {
                const type = item.nail_type;
                const isSupply = ['Glue', 'Toolkit', 'Box'].includes(type);
                const groupKey = isSupply ? 'Supplies' : type;
                
                if (groups[groupKey]) {
                    groups[groupKey].items.push(item);
                    groups[groupKey].total += item.quantity;
                }
            });
            
            let html = '<div class="grouped-stock-container">';
            
            Object.keys(groups).forEach(groupKey => {
                const group = groups[groupKey];
                if (group.items.length > 0) {
                    html += `<div class="stock-group-card" onclick="showGroupDetails('${groupKey}')">`;
                    html += `<div class="stock-group-header">`;
                    html += `<h3>${group.name}</h3>`;
                    html += `<div class="stock-group-total">${group.total.toLocaleString()} units</div>`;
                    html += `</div>`;
                    html += `<div class="stock-group-meta">${group.items.length} items</div>`;
                    html += `<div class="stock-group-arrow">→</div>`;
                    html += `</div>`;
                }
            });
            
            html += '</div>';
            return html;
        }
        
        function renderStockTable(stock, highlightLow = false, showDelete = false) {
            if (stock && stock.length > 0) {
                let html = '<table class="stock-table">';
                html += '<thead><tr>';
                html += '<th>Type</th>';
                html += '<th>ID</th>';
                html += '<th>Size</th>';
                html += '<th>Quantity</th>';
                if (showDelete) html += '<th>Action</th>';
                html += '</tr></thead>';
                html += '<tbody>';
                
                stock.forEach(item => {
                    const rowClass = (highlightLow && item.quantity < 3) ? ' class="low-stock-row"' : '';
                    const displayName = getItemDisplayName(item.nail_type, item.identifier);
                    html += `<tr${rowClass}>`;
                    html += `<td>${item.nail_type}</td>`;
                    html += `<td>${displayName}</td>`;
                    html += `<td>${item.size}</td>`;
                    html += `<td class="stock-qty">${item.quantity}</td>`;
                    if (showDelete) {
                        html += `<td><button class="delete-btn" onclick="deleteStock('${item.nail_type}', '${item.identifier}', '${item.size}', ${item.quantity})">Delete</button></td>`;
                    }
                    html += '</tr>';
                });
                
                html += '</tbody></table>';
                return html;
            }
            return '<div class="empty-state">No stock available</div>';
        }
        
        let currentStockData = [];
        let currentShowDelete = false;
        let currentHighlightLow = false;
        let currentViewMode = 'grouped'; // 'grouped' or 'detail'
        let currentGroup = null;
        
        async function viewStock() {
            const modal = document.getElementById('stockModal');
            const container = document.getElementById('stockTableContainer');
            const searchContainer = document.getElementById('stockSearchContainer');
            const searchBox = document.getElementById('stockSearchBox');
            const modalHeader = modal.querySelector('.modal-header h2');
            
            modal.classList.add('active');
            container.innerHTML = '<div class="loading">Loading...</div>';
            searchContainer.style.display = 'block';
            searchBox.value = '';
            modalHeader.textContent = 'Stock Inventory';
            
            try {
                const response = await fetch('/view_all_stock');
                const data = await response.json();
                currentStockData = data.stock;
                currentShowDelete = true;
                currentHighlightLow = false;
                currentViewMode = 'grouped';
                currentGroup = null;
                container.innerHTML = renderGroupedStockView(currentStockData);
            } catch (error) {
                container.innerHTML = '<div class="empty-state">Error loading stock</div>';
                console.error('Error:', error);
            }
        }
        
        function showGroupDetails(groupKey) {
            const modal = document.getElementById('stockModal');
            const container = document.getElementById('stockTableContainer');
            const modalHeader = modal.querySelector('.modal-header h2');
            const searchContainer = document.getElementById('stockSearchContainer');
            
            currentViewMode = 'detail';
            currentGroup = groupKey;
            
            // Filter items for this group
            let filteredStock;
            if (groupKey === 'Supplies') {
                filteredStock = currentStockData.filter(item => ['Glue', 'Toolkit', 'Box'].includes(item.nail_type));
                modalHeader.textContent = 'Supplies - Details';
            } else {
                filteredStock = currentStockData.filter(item => item.nail_type === groupKey);
                modalHeader.textContent = `Type ${groupKey} - Details`;
            }
            
            // Add back button
            let html = '<button class="back-btn" onclick="backToGroupedView()">← Back to Groups</button>';
            html += renderStockTable(filteredStock, false, true);
            container.innerHTML = html;
            searchContainer.style.display = 'block';
        }
        
        function backToGroupedView() {
            const modal = document.getElementById('stockModal');
            const container = document.getElementById('stockTableContainer');
            const modalHeader = modal.querySelector('.modal-header h2');
            const searchBox = document.getElementById('stockSearchBox');
            
            currentViewMode = 'grouped';
            currentGroup = null;
            searchBox.value = '';
            modalHeader.textContent = 'Stock Inventory';
            container.innerHTML = renderGroupedStockView(currentStockData);
        }
        
        async function viewLowStock() {
            const modal = document.getElementById('stockModal');
            const container = document.getElementById('stockTableContainer');
            const searchContainer = document.getElementById('stockSearchContainer');
            const searchBox = document.getElementById('stockSearchBox');
            
            modal.classList.add('active');
            container.innerHTML = '<div class="loading">Loading...</div>';
            searchContainer.style.display = 'none';
            searchBox.value = '';
            
            try {
                const response = await fetch('/view_low_stock');
                
                // Check if response is OK
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Low stock data:', data);
                
                if (data.success && data.low_stock && data.low_stock.length > 0) {
                    currentStockData = data.low_stock;
                    currentShowDelete = false;
                    currentHighlightLow = true;
                    searchContainer.style.display = 'none';
                    container.innerHTML = renderLowStockTable(currentStockData);
                } else if (data.success === false) {
                    container.innerHTML = `<div class="empty-state">Error: ${data.error || 'Unknown error'}</div>`;
                } else {
                    container.innerHTML = '<div class="empty-state">No low stock items</div>';
                }
            } catch (error) {
                container.innerHTML = `<div class="empty-state">Error loading stock: ${error.message}</div>`;
                console.error('Error:', error);
            }
        }
        
        async function publishReport() {
            const exportedBy = prompt('Enter your name:');
            if (!exportedBy) return;
            
            // Ask for format
            const format = prompt('Choose format (type "pdf" or "txt"):');
            if (!format || !['pdf', 'txt'].includes(format.toLowerCase())) {
                alert('Invalid format. Please choose "pdf" or "txt"');
                return;
            }
            
            // Store the export info for later download
            window.reportExportInfo = {
                exportedBy: exportedBy,
                format: format.toLowerCase()
            };
            
            // Show preview modal
            const modal = document.getElementById('reportPreviewModal');
            const container = document.getElementById('reportPreviewContainer');
            modal.classList.add('active');
            container.innerHTML = '<div class="loading">Loading report preview...</div>';
            
            try {
                // Get report preview
                const response = await fetch('/preview_report', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({exported_by: exportedBy})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Display the report content in a formatted way
                    container.innerHTML = `<pre style="white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.4; color: #333;">${data.report_content}</pre>`;
                } else {
                    container.innerHTML = '<div class="empty-state">Error loading report preview</div>';
                }
            } catch (error) {
                container.innerHTML = `<div class="empty-state">Error: ${error.message}</div>`;
                console.error('Error:', error);
            }
        }
        
        async function confirmDownloadReport() {
            if (!window.reportExportInfo) {
                alert('Report information not found. Please try again.');
                return;
            }
            
            const { exportedBy, format } = window.reportExportInfo;
            const endpoint = format === 'pdf' ? '/generate_report_pdf' : '/generate_report';
            const fileExtension = format;
            
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({exported_by: exportedBy})
                });
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `inventory_report_${new Date().toISOString().split('T')[0]}.${fileExtension}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                // Close preview modal
                closeReportPreview();
                
                message.style.display = 'block';
                message.className = 'message success';
                message.textContent = `${fileExtension.toUpperCase()} report downloaded successfully!`;
                setTimeout(() => { message.style.display = 'none'; }, 3000);
            } catch (error) {
                message.style.display = 'block';
                message.className = 'message error';
                message.textContent = 'Error generating report';
                setTimeout(() => { message.style.display = 'none'; }, 3000);
            }
        }
        
        function closeReportPreview() {
            document.getElementById('reportPreviewModal').classList.remove('active');
            window.reportExportInfo = null;
        }
        
        async function viewAnalysis() {
            const modal = document.getElementById('analysisModal');
            const container = document.getElementById('analysisContainer');
            
            modal.classList.add('active');
            container.innerHTML = '<div class="loading">Loading analysis...</div>';
            
            try {
                const [analysisResponse, lowStockResponse] = await Promise.all([
                    fetch('/view_analysis'),
                    fetch('/view_low_stock')
                ]);

                const data = await analysisResponse.json();
                const lowStockData = await lowStockResponse.json();
                const lowStockItems = (lowStockData.success && lowStockData.low_stock) ? lowStockData.low_stock : [];
                
                if (data.success && data.analysis) {
                    container.innerHTML = renderAnalysis(data.analysis, lowStockItems);
                } else {
                    container.innerHTML = '<div class="empty-state">Error loading analysis</div>';
                }
            } catch (error) {
                container.innerHTML = `<div class="empty-state">Error: ${error.message}</div>`;
                console.error('Error:', error);
            }
        }
        
        function renderAnalysis(analysis, lowStockItems = []) {
            const health = analysis.health_metrics;
            const sizeDist = analysis.size_distribution;
            const catStats = analysis.category_statistics;
            const itemsBySize = analysis.items_by_size;
            
            let html = '';
            
            // Health Overview
            html += '<div class="analysis-section">';
            html += '<h3>📈 Inventory Health Overview</h3>';
            html += '<div class="analysis-grid">';
            html += `<div class="analysis-stat"><div class="analysis-stat-label">Total Quantity</div><div class="analysis-stat-value">${health.total_quantity.toLocaleString()}</div></div>`;
            html += `<div class="analysis-stat"><div class="analysis-stat-label">Unique Products</div><div class="analysis-stat-value">${health.unique_products}</div></div>`;
            html += `<div class="analysis-stat"><div class="analysis-stat-label">Total Entries</div><div class="analysis-stat-value">${health.total_entries}</div></div>`;
            html += `<div class="analysis-stat"><div class="analysis-stat-label">Avg Stock/Product</div><div class="analysis-stat-value">${health.average_stock_per_product}</div></div>`;
            html += '</div>';
            
            html += '<div class="analysis-grid" style="margin-top: 15px;">';
            html += `<div class="analysis-stat"><div class="analysis-stat-label">Low Stock (<4)</div><div class="analysis-stat-value" style="color: #d32f2f;">${health.low_stock_products} (${health.low_stock_percentage}%)</div></div>`;
            html += `<div class="analysis-stat"><div class="analysis-stat-label">Medium Stock (4-10)</div><div class="analysis-stat-value" style="color: #f57c00;">${health.medium_stock_products}</div></div>`;
            html += `<div class="analysis-stat"><div class="analysis-stat-label">High Stock (>10)</div><div class="analysis-stat-value" style="color: #388e3c;">${health.high_stock_products}</div></div>`;
            
            const healthClass = health.stock_health_score.toLowerCase().replace(' ', '-');
            html += `<div class="analysis-stat"><div class="analysis-stat-label">Health Score</div><div class="health-score health-${healthClass}">${health.stock_health_score}</div></div>`;
            html += '</div>';
            html += '</div>';

            // Low Stock Details
            html += '<div class="analysis-section">';
            html += '<h3>⚠️ Low Stock Details (Total Quantity &lt; 4)</h3>';

            if (lowStockItems.length > 0) {
                html += '<table class="analysis-table">';
                html += '<thead><tr><th>Type</th><th>ID</th><th>Product Name</th><th>Total Quantity</th><th>Size Breakdown</th></tr></thead>';
                html += '<tbody>';

                lowStockItems.forEach(item => {
                    const displayName = getItemDisplayName(item.nail_type, item.identifier);
                    const sizeBreakdown = (item.sizes || []).map(s => `${s.size}: ${s.quantity}`).join(', ');
                    html += `<tr>`;
                    html += `<td><strong>${item.nail_type}</strong></td>`;
                    html += `<td>${item.identifier}</td>`;
                    html += `<td>${displayName}</td>`;
                    html += `<td style="color: #d32f2f; font-weight: 700;">${item.total_quantity}</td>`;
                    html += `<td>${sizeBreakdown || '-'}</td>`;
                    html += `</tr>`;
                });

                html += '</tbody></table>';
            } else {
                html += '<div class="empty-state">No low stock items</div>';
            }

            html += '</div>';
            
            // Size Distribution
            html += '<div class="analysis-section">';
            html += '<h3>📏 Size Distribution - Overall</h3>';
            html += '<table class="analysis-table">';
            html += '<thead><tr><th>Size</th><th>Total Quantity</th><th>Number of Entries</th><th>Percentage</th></tr></thead>';
            html += '<tbody>';
            
            const sizes = ['XS', 'S', 'M', 'L', 'UNIT'];
            const totalQty = Object.values(sizeDist.totals).reduce((a, b) => a + b, 0);
            
            sizes.forEach(size => {
                const qty = sizeDist.totals[size] || 0;
                const count = sizeDist.item_counts[size] || 0;
                const pct = totalQty > 0 ? ((qty / totalQty) * 100).toFixed(1) : 0;
                if (count > 0) {  // Only show sizes that have stock
                    html += `<tr><td><strong>${size}</strong></td><td>${qty.toLocaleString()}</td><td>${count}</td><td>${pct}%</td></tr>`;
                }
            });
            
            html += '</tbody></table>';
            html += '</div>';
            
            // Items by Size - NEW SECTION
            html += '<div class="analysis-section">';
            html += '<h3>🔍 Available Types by Size</h3>';
            html += '<p style="color: #666; font-size: 13px; margin-bottom: 15px;">View what products are available for each size</p>';
            
            Object.keys(itemsBySize).sort().forEach(size => {
                const sizeData = itemsBySize[size];
                html += '<div style="margin-bottom: 20px; border: 1px solid #e0e0e0; border-radius: 6px; padding: 15px;">';
                html += `<h4 style="margin: 0 0 10px 0; color: #1976d2;">Size: ${size} <span style="font-weight: normal; font-size: 13px; color: #666;">(${sizeData.unique_products} products, ${sizeData.total_quantity} units)</span></h4>`;
                html += '<table class="analysis-table" style="margin: 0;">';
                html += '<thead><tr><th>Type</th><th>ID</th><th>Product Name</th><th>Quantity</th></tr></thead>';
                html += '<tbody>';
                
                sizeData.items.forEach(item => {
                    html += `<tr>`;
                    html += `<td><strong>${item.nail_type}</strong></td>`;
                    html += `<td>${item.identifier}</td>`;
                    html += `<td>${item.name}</td>`;
                    html += `<td>${item.quantity}</td>`;
                    html += `</tr>`;
                });
                
                html += '</tbody></table>';
                html += '</div>';
            });
            
            html += '</div>';
            
            // Category Statistics
            html += '<div class="analysis-section">';
            html += '<h3>🗂️ Category Analysis</h3>';
            html += '<table class="analysis-table">';
            html += '<thead><tr><th>Type</th><th>Total Quantity</th><th>Unique Products</th><th>Total Entries</th><th>Sizes Available</th></tr></thead>';
            html += '<tbody>';
            
            Object.keys(catStats).sort().forEach(category => {
                const stats = catStats[category];
                html += `<tr>`;
                html += `<td><strong>${category}</strong></td>`;
                html += `<td>${stats.total_quantity.toLocaleString()}</td>`;
                html += `<td>${stats.unique_products}</td>`;
                html += `<td>${stats.total_entries}</td>`;
                html += `<td>${stats.sizes_available.join(', ')}</td>`;
                html += `</tr>`;
            });
            
            html += '</tbody></table>';
            html += '</div>';
            
            return html;
        }
        
        async function downloadAnalysisReport() {
            const analystName = prompt('Enter your name:');
            if (!analystName) return;
            
            try {
                const response = await fetch('/generate_analysis', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({analyst_name: analystName})
                });
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `inventory_analysis_${new Date().toISOString().split('T')[0]}.txt`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                message.style.display = 'block';
                message.className = 'message success';
                message.textContent = 'Analysis report downloaded successfully!';
                setTimeout(() => { message.style.display = 'none'; }, 3000);
            } catch (error) {
                message.style.display = 'block';
                message.className = 'message error';
                message.textContent = 'Error generating analysis';
                setTimeout(() => { message.style.display = 'none'; }, 3000);
            }
        }
        
        function closeAnalysisModal() {
            document.getElementById('analysisModal').classList.remove('active');
        }
        
        async function deleteStock(nailType, identifier, size, currentQty) {
            const modal = document.getElementById('stockModal');
            const deleteModal = document.createElement('div');
            deleteModal.className = 'modal active';
            deleteModal.innerHTML = `
                <div class="delete-modal-content">
                    <h3 style="margin-bottom: 16px; font-size: 16px;">Delete Stock Item</h3>
                    <p style="margin-bottom: 12px; color: #666; font-size: 14px;">
                        ${nailType}${identifier} - ${size} (Current: ${currentQty})
                    </p>
                    <label style="display: block; margin-bottom: 8px; font-size: 13px; font-weight: 600;">
                        Enter quantity to delete (or leave empty to delete all):
                    </label>
                    <input type="number" id="deleteQty" class="delete-input" 
                           placeholder="Leave empty to delete all" min="1" max="${currentQty}">
                    <div class="modal-buttons">
                        <button class="modal-btn btn-cancel" onclick="this.closest('.modal').remove()">Cancel</button>
                        <button class="modal-btn btn-confirm" onclick="confirmDelete('${nailType}', '${identifier}', '${size}', ${currentQty})">Delete</button>
                    </div>
                </div>
            `;
            document.body.appendChild(deleteModal);
            
            deleteModal.addEventListener('click', function(e) {
                if (e.target === deleteModal) {
                    deleteModal.remove();
                }
            });
        }
        
        async function confirmDelete(nailType, identifier, size, currentQty) {
            const deleteQtyInput = document.getElementById('deleteQty');
            const deleteQty = deleteQtyInput.value ? parseInt(deleteQtyInput.value) : currentQty;
            
            if (deleteQty > currentQty) {
                alert('Cannot delete more than current quantity');
                return;
            }
            
            try {
                const response = await fetch('/delete_stock', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        nail_type: nailType,
                        identifier: identifier,
                        size: size,
                        quantity: deleteQty
                    })
                });
                
                const result = await response.json();
                
                document.querySelector('.delete-modal-content').closest('.modal').remove();
                
                if (result.success) {
                    message.style.display = 'block';
                    message.className = 'message success';
                    message.textContent = result.message;
                    setTimeout(() => { message.style.display = 'none'; }, 3000);
                    
                    viewStock();
                } else {
                    message.style.display = 'block';
                    message.className = 'message error';
                    message.textContent = result.message || 'Error deleting stock';
                    setTimeout(() => { message.style.display = 'none'; }, 3000);
                }
            } catch (error) {
                document.querySelector('.delete-modal-content').closest('.modal').remove();
                message.style.display = 'block';
                message.className = 'message error';
                message.textContent = 'Error deleting stock';
                setTimeout(() => { message.style.display = 'none'; }, 3000);
            }
        }
        
        function closeModal() {
            document.getElementById('stockModal').classList.remove('active');
        }
        
        // Close modal on outside click
        document.getElementById('stockModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        async function manageNames() {
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.id = 'namesModal';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 900px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h3 style="margin: 0; font-size: 18px;">Manage Item Names</h3>
                        <button class="close-btn" onclick="document.getElementById('namesModal').remove()">×</button>
                    </div>
                    <div style="margin-bottom: 16px;">
                        <button class="history-btn" onclick="viewAllHistory()">View Change History</button>
                    </div>
                    <input type="text" class="search-box" id="nameSearchBox" placeholder="Search by ID or name..." oninput="renderNamesGrid(this.value)">
                    <div id="namesContainer" class="names-grid">
                        <div class="loading">Loading...</div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    modal.remove();
                }
            });
            
            await loadItemNames();
            renderNamesGrid();
        }
        
        function renderNamesGrid(searchTerm = '') {
            const container = document.getElementById('namesContainer');
            if (!container) return;
            
            // Sort keys by type (alphabetically) then by number (numerically)
            const sortedKeys = Object.keys(itemNames).sort((a, b) => {
                const typeA = a[0];
                const typeB = b[0];
                
                // First sort by type
                if (typeA !== typeB) {
                    return typeA.localeCompare(typeB);
                }
                
                // Then sort by number
                const numA = parseInt(a.substring(1)) || 0;
                const numB = parseInt(b.substring(1)) || 0;
                return numA - numB;
            });
            
            // Filter by search term
            const filteredKeys = searchTerm 
                ? sortedKeys.filter(key => 
                    key.toLowerCase().includes(searchTerm.toLowerCase()) || 
                    itemNames[key].toLowerCase().includes(searchTerm.toLowerCase())
                  )
                : sortedKeys;
            
            // Group by type
            const grouped = {};
            filteredKeys.forEach(key => {
                const type = key[0];
                if (!grouped[type]) grouped[type] = [];
                grouped[type].push(key);
            });
            
            let html = '';
            
            // Render each type section
            Object.keys(grouped).sort().forEach(type => {
                const typeNames = {
                    'X': 'Type X — 250k',
                    'S': 'Type S — 200k',
                    'C': 'Type C — 180k',
                    'M': 'Type M — 150k',
                    'A': 'Type A — 130k',
                    'B': 'Type B — 100k'
                };
                
                html += `
                    <div class="type-section">
                        <div class="type-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'grid' : 'none'">
                            <span>${typeNames[type] || type}</span>
                            <span>${grouped[type].length} items</span>
                        </div>
                        <div class="type-items">
                `;
                
                grouped[type].forEach(key => {
                    const name = itemNames[key];
                    const nailType = key[0];
                    const identifier = key.substring(1);
                    
                    html += `
                        <div class="name-item">
                            <div class="name-item-header">${key}</div>
                            <input type="text" class="name-input" id="name-${key}" value="${name}" placeholder="Enter name">
                            <div style="display: flex; gap: 4px; margin-top: 6px;">
                                <button class="save-name-btn" onclick="saveItemName('${nailType}', '${identifier}')">Save</button>
                                <button class="save-name-btn" style="background: #007bff;" onclick="viewItemHistory('${key}')">📋</button>
                            </div>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            });
            
            if (filteredKeys.length === 0) {
                html = '<div class="empty-state">No items found</div>';
            }
            
            container.innerHTML = html;
        }
        
        async function saveItemName(nailType, identifier) {
            const key = `${nailType}${identifier}`;
            const nameInput = document.getElementById(`name-${key}`);
            const name = nameInput.value.trim();
            
            if (!name) {
                alert('Please enter a name');
                return;
            }
            
            // Ask for who is making the change
            const changedBy = prompt('Enter your name:');
            if (!changedBy || !changedBy.trim()) {
                alert('Name is required to track changes');
                return;
            }
            
            try {
                const response = await fetch('/update_item_name', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        nail_type: nailType,
                        identifier: identifier,
                        name: name,
                        changed_by: changedBy.trim()
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    itemNames[key] = name;
                    message.style.display = 'block';
                    message.className = 'message success';
                    message.textContent = result.message;
                    setTimeout(() => { message.style.display = 'none'; }, 2000);
                } else {
                    message.style.display = 'block';
                    message.className = 'message error';
                    message.textContent = result.message;
                    setTimeout(() => { message.style.display = 'none'; }, 3000);
                }
            } catch (error) {
                message.style.display = 'block';
                message.className = 'message error';
                message.textContent = 'Error saving name';
                setTimeout(() => { message.style.display = 'none'; }, 3000);
            }
        }
        
        async function initializeDefaultNames() {
            if (!confirm('This will initialize all default item names in the database. Continue?')) {
                return;
            }
            
            try {
                const response = await fetch('/initialize_names', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const result = await response.json();
                
                if (result.success) {
                    message.style.display = 'block';
                    message.className = 'message success';
                    message.textContent = result.message;
                    setTimeout(() => { message.style.display = 'none'; }, 2000);
                    
                    await loadItemNames();
                    renderNamesGrid();
                } else {
                    message.style.display = 'block';
                    message.className = 'message error';
                    message.textContent = result.message;
                    setTimeout(() => { message.style.display = 'none'; }, 3000);
                }
            } catch (error) {
                message.style.display = 'block';
                message.className = 'message error';
                message.textContent = 'Error initializing names';
                setTimeout(() => { message.style.display = 'none'; }, 3000);
            }
        }
        
        async function viewItemHistory(itemKey) {
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 700px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h3 style="margin: 0; font-size: 18px;">Change History for ${itemKey}</h3>
                        <button class="close-btn" onclick="this.closest('.modal').remove()">×</button>
                    </div>
                    <div id="historyContainer" style="max-height: 500px; overflow-y: auto;">
                        <div class="loading">Loading...</div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    modal.remove();
                }
            });
            
            try {
                const response = await fetch(`/get_name_change_log?item_key=${itemKey}`);
                const data = await response.json();
                
                if (data.success && data.logs.length > 0) {
                    let html = '<table class="log-table">';
                    html += '<thead><tr><th>Date & Time</th><th>Old Name</th><th>New Name</th><th>Changed By</th></tr></thead>';
                    html += '<tbody>';
                    
                    data.logs.forEach(log => {
                        const date = new Date(log.changed_at).toLocaleString();
                        html += '<tr>';
                        html += `<td>${date}</td>`;
                        html += `<td>${log.old_name || '<em>N/A</em>'}</td>`;
                        html += `<td>${log.new_name}</td>`;
                        html += `<td>${log.changed_by}</td>`;
                        html += '</tr>';
                    });
                    
                    html += '</tbody></table>';
                    document.getElementById('historyContainer').innerHTML = html;
                } else {
                    document.getElementById('historyContainer').innerHTML = '<div class="empty-state">No change history found</div>';
                }
            } catch (error) {
                document.getElementById('historyContainer').innerHTML = '<div class="empty-state">Error loading history</div>';
            }
        }
        
        async function viewAllHistory() {
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 900px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <h3 style="margin: 0; font-size: 18px;">All Name Changes (Last 100)</h3>
                        <button class="close-btn" onclick="this.closest('.modal').remove()">×</button>
                    </div>
                    <div id="allHistoryContainer" style="max-height: 600px; overflow-y: auto;">
                        <div class="loading">Loading...</div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    modal.remove();
                }
            });
            
            try {
                const response = await fetch('/get_name_change_log');
                const data = await response.json();
                
                if (data.success && data.logs.length > 0) {
                    let html = '<table class="log-table">';
                    html += '<thead><tr><th>Item</th><th>Date & Time</th><th>Old Name</th><th>New Name</th><th>Changed By</th></tr></thead>';
                    html += '<tbody>';
                    
                    data.logs.forEach(log => {
                        const date = new Date(log.changed_at).toLocaleString();
                        html += '<tr>';
                        html += `<td><strong>${log.item_key}</strong></td>`;
                        html += `<td>${date}</td>`;
                        html += `<td>${log.old_name || '<em>N/A</em>'}</td>`;
                        html += `<td>${log.new_name}</td>`;
                        html += `<td>${log.changed_by}</td>`;
                        html += '</tr>';
                    });
                    
                    html += '</tbody></table>';
                    document.getElementById('allHistoryContainer').innerHTML = html;
                } else {
                    document.getElementById('allHistoryContainer').innerHTML = '<div class="empty-state">No change history found</div>';
                }
            } catch (error) {
                document.getElementById('allHistoryContainer').innerHTML = '<div class="empty-state">Error loading history</div>';
            }
        }
        
        // Bulk Upload Functions
        let currentBulkData = null;
        let removedNewEntries = new Set();
        let removedDuplicateEntries = new Set();
        
        function bulkUpload() {
            document.getElementById('bulkUploadModal').classList.add('active');
            // Reset modal state
            document.getElementById('uploadSection').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';
            document.getElementById('csvFileInput').value = '';
            currentBulkData = null;
            removedNewEntries.clear();
            removedDuplicateEntries.clear();
        }
        
        function closeBulkModal() {
            document.getElementById('bulkUploadModal').classList.remove('active');
            // Reset on close
            removedNewEntries.clear();
            removedDuplicateEntries.clear();
        }
        
        // Drag and drop functionality
        const uploadArea = document.getElementById('uploadArea');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            }, false);
        });
        
        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        }, false);
        
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                handleFile(file);
            }
        }
        
        async function handleFile(file) {
            if (!file.name.endsWith('.csv')) {
                alert('Please upload a CSV file');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Show loading
            document.getElementById('uploadSection').innerHTML = '<div class="loading">Processing file...</div>';
            
            try {
                const response = await fetch('/bulk_upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentBulkData = result;
                    displayBulkResults(result);
                } else {
                    alert('Error: ' + (result.error || 'Failed to process file'));
                    // Reset upload section
                    document.getElementById('uploadSection').innerHTML = `
                        <div class="upload-area" id="uploadArea" onclick="document.getElementById('csvFileInput').click()">
                            <div class="upload-icon">📄</div>
                            <div class="upload-text">Click to upload or drag and drop your CSV file</div>
                            <div style="font-size: 12px; color: #999;">CSV format: date, Select IN or OUT, Select TYPE, ID, Size, QTY</div>
                        </div>
                        <input type="file" id="csvFileInput" class="file-input" accept=".csv" onchange="handleFileSelect(event)">
                    `;
                }
            } catch (error) {
                alert('Error uploading file: ' + error.message);
                location.reload();
            }
        }
        
        function displayBulkResults(data) {
            // Hide upload section, show results
            document.getElementById('uploadSection').style.display = 'none';
            document.getElementById('resultsSection').style.display = 'block';
            
            // Update statistics
            document.getElementById('totalEntries').textContent = data.statistics.total_entries;
            document.getElementById('newEntries').textContent = data.statistics.new_entries;
            document.getElementById('duplicateEntries').textContent = data.statistics.duplicate_entries;
            
            // Build table
            const tbody = document.getElementById('bulkTableBody');
            tbody.innerHTML = '';
            
            // Add new entries
            data.new_entries.forEach((entry, index) => {
                const row = tbody.insertRow();
                row.dataset.entryType = 'new';
                row.dataset.entryIndex = index;
                row.innerHTML = `
                    <td><span class="status-badge badge-new">NEW</span></td>
                    <td>${entry.date}</td>
                    <td>${entry['Select IN or OUT']}</td>
                    <td>${entry['Select TYPE']}</td>
                    <td>${entry.ID}</td>
                    <td>${entry.Size}</td>
                    <td>${entry.QTY}</td>
                    <td><button class="remove-row-btn" onclick="removeRow(this, 'new', ${index})">Remove</button></td>
                `;
            });
            
            // Add duplicate entries
            data.duplicate_entries.forEach((entry, index) => {
                const row = tbody.insertRow();
                row.className = 'duplicate-row';
                row.dataset.entryType = 'duplicate';
                row.dataset.entryIndex = index;
                row.innerHTML = `
                    <td><span class="status-badge badge-duplicate">DUPLICATE</span></td>
                    <td>${entry.date}</td>
                    <td>${entry['Select IN or OUT']}</td>
                    <td>${entry['Select TYPE']}</td>
                    <td>${entry.ID}</td>
                    <td>${entry.Size}</td>
                    <td>${entry.QTY}</td>
                    <td><button class="remove-row-btn" onclick="removeRow(this, 'duplicate', ${index})">Remove</button></td>
                `;
            });
            
            // Update count display
            updateEntryCount();
        }
        
        function removeRow(button, entryType, index) {
            const row = button.closest('tr');
            
            // Toggle removed state
            if (row.classList.contains('removed-row')) {
                // Un-remove the row
                row.classList.remove('removed-row');
                button.textContent = 'Remove';
                
                // Remove from removed set
                if (entryType === 'new') {
                    removedNewEntries.delete(index);
                } else {
                    removedDuplicateEntries.delete(index);
                }
            } else {
                // Mark as removed
                row.classList.add('removed-row');
                button.textContent = 'Undo';
                
                // Add to removed set
                if (entryType === 'new') {
                    removedNewEntries.add(index);
                } else {
                    removedDuplicateEntries.add(index);
                }
            }
            
            // Update count display
            updateEntryCount();
        }
        
        function updateEntryCount() {
            if (!currentBulkData) return;
            
            const activeNewCount = currentBulkData.new_entries.length - removedNewEntries.size;
            const activeDuplicateCount = currentBulkData.duplicate_entries.length - removedDuplicateEntries.size;
            const activeTotalCount = activeNewCount + activeDuplicateCount;
            
            document.getElementById('totalEntries').textContent = activeTotalCount;
            document.getElementById('newEntries').textContent = activeNewCount;
            document.getElementById('duplicateEntries').textContent = activeDuplicateCount;
        }
        
        async function confirmBulkSave() {
            if (!currentBulkData || currentBulkData.new_entries.length === 0) {
                alert('No new entries to save');
                return;
            }
            
            // Filter out removed entries
            const entriesToSave = currentBulkData.new_entries.filter((entry, index) => {
                return !removedNewEntries.has(index);
            });
            
            if (entriesToSave.length === 0) {
                alert('No entries to save. All entries have been removed.');
                return;
            }
            
            const confirmMsg = `You are about to save ${entriesToSave.length} entries.\n\n${removedNewEntries.size > 0 ? `(${removedNewEntries.size} entries removed and will not be saved)\n\n` : ''}Continue?`;
            
            if (!confirm(confirmMsg)) {
                return;
            }
            
            const confirmBtn = document.getElementById('confirmSaveBtn');
            const processing = document.getElementById('processing');
            
            confirmBtn.disabled = true;
            processing.style.display = 'inline-block';
            
            try {
                const response = await fetch('/bulk_save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        entries: entriesToSave
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert(`✅ Successfully saved ${result.saved_count} entries!\n\n${result.message}`);
                    closeBulkModal();
                    // Refresh the page to show updated inventory
                    location.reload();
                } else {
                    alert('Error: ' + (result.error || 'Failed to save entries'));
                    confirmBtn.disabled = false;
                    processing.style.display = 'none';
                }
            } catch (error) {
                alert('Error saving entries: ' + error.message);
                confirmBtn.disabled = false;
                processing.style.display = 'none';
            }
        }

        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js').catch((error) => {
                    console.error('Service worker registration failed:', error);
                });
            });
        }
    </script>
</body>
</html>
"""
