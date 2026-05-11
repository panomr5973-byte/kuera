#!/usr/bin/env python
"""
Web Interface Sederhana - HTML form untuk interaksi dengan AI
Buka di browser: http://localhost:8080
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests

API_URL = "http://localhost:8000"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Interaction Interface</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .section h2 { margin-top: 0; color: #555; }
        button { background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
        button:disabled { background: #ccc; }
        .btn-red { background: #f44336; }
        .btn-red:hover { background: #da190b; }
        .btn-blue { background: #2196F3; }
        .btn-blue:hover { background: #0b7dda; }
        .result { background: #f9f9f9; padding: 15px; margin-top: 15px; border-radius: 5px; border-left: 4px solid #4CAF50; }
        .error { border-left-color: #f44336; background: #ffebee; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
        .stat-box { background: #e3f2fd; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-box h3 { margin: 0; font-size: 24px; color: #1976d2; }
        .stat-box p { margin: 5px 0 0; color: #555; }
        input[type="number"] { padding: 8px; width: 100px; border: 1px solid #ddd; border-radius: 4px; }
        .feedback-btns { display: flex; gap: 10px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Interaction Interface</h1>
        
        <div class="section">
            <h2>📊 Status</h2>
            <div id="status">Loading...</div>
        </div>
        
        <div class="section">
            <h2>🎯 Single Prediction</h2>
            <p>AI akan membuat prediksi dari sample data</p>
            <button onclick="makePrediction()">Make Prediction</button>
            <div id="prediction-result"></div>
        </div>
        
        <div class="section">
            <h2>🔄 Auto Generate Interactions</h2>
            <p>Generate multiple interactions automatically</p>
            <label>Count: <input type="number" id="auto-count" value="10" min="1" max="100"></label>
            <button class="btn-blue" onclick="autoGenerate()">Start Auto Generate</button>
            <div id="auto-result"></div>
        </div>
        
        <div class="section">
            <h2>⚙️ Manual API Test</h2>
            <button class="btn-blue" onclick="testSample()">Get Sample Data</button>
            <button class="btn-blue" onclick="listModels()">List Models</button>
            <div id="manual-result"></div>
        </div>
    </div>
    
    <script>
        let currentInteractionId = null;
        
        // Check status on load
        checkStatus();
        
        function checkStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').innerHTML = `
                        <div class="stats">
                            <div class="stat-box">
                                <h3>${data.models || 0}</h3>
                                <p>Models</p>
                            </div>
                            <div class="stat-box">
                                <h3>${data.interactions || 0}</h3>
                                <p>Interactions</p>
                            </div>
                            <div class="stat-box">
                                <h3>${data.status || 'Unknown'}</h3>
                                <p>Status</p>
                            </div>
                        </div>
                    `;
                })
                .catch(e => {
                    document.getElementById('status').innerHTML = 
                        '<div class="result error"><strong>Error:</strong> Cannot connect to AI API. Make sure it is running on port 8000.</div>';
                });
        }
        
        function makePrediction() {
            document.getElementById('prediction-result').innerHTML = '<p>Loading...</p>';
            
            fetch('/api/predict', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    currentInteractionId = data.interaction_id;
                    document.getElementById('prediction-result').innerHTML = `
                        <div class="result">
                            <strong>Prediction:</strong> ${data.prediction}<br>
                            <strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%<br>
                            <strong>Model:</strong> ${data.model_used}<br>
                            <strong>Interaction ID:</strong> ${data.interaction_id}<br>
                            <strong>Time:</strong> ${data.timestamp}
                            <div class="feedback-btns">
                                <button onclick="giveFeedback(1)">✓ Correct</button>
                                <button class="btn-red" onclick="giveFeedback(0)">✗ Incorrect</button>
                            </div>
                        </div>
                    `;
                    checkStatus();
                })
                .catch(e => {
                    document.getElementById('prediction-result').innerHTML = 
                        '<div class="result error"><strong>Error:</strong> ' + e.message + '</div>';
                });
        }
        
        function giveFeedback(feedback) {
            if (!currentInteractionId) return;
            
            fetch('/api/feedback', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    interaction_id: currentInteractionId,
                    feedback: feedback
                })
            })
            .then(r => r.json())
            .then(data => {
                alert('Feedback saved: ' + (feedback === 1 ? 'Correct' : 'Incorrect'));
                checkStatus();
            })
            .catch(e => alert('Error: ' + e.message));
        }
        
        function autoGenerate() {
            const count = document.getElementById('auto-count').value;
            document.getElementById('auto-result').innerHTML = '<p>Generating ' + count + ' interactions...</p>';
            
            fetch('/api/auto?count=' + count, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('auto-result').innerHTML = `
                        <div class="result">
                            <strong>Generated:</strong> ${data.generated}<br>
                            <strong>Success:</strong> ${data.success}<br>
                            <strong>Time:</strong> ${data.time}s
                        </div>
                    `;
                    checkStatus();
                })
                .catch(e => {
                    document.getElementById('auto-result').innerHTML = 
                        '<div class="result error"><strong>Error:</strong> ' + e.message + '</div>';
                });
        }
        
        function testSample() {
            fetch('/api/sample')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('manual-result').innerHTML = 
                        '<div class="result"><pre>' + JSON.stringify(data, null, 2) + '</pre></div>';
                })
                .catch(e => alert('Error: ' + e.message));
        }
        
        function listModels() {
            fetch('/api/models')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('manual-result').innerHTML = 
                        '<div class="result"><pre>' + JSON.stringify(data, null, 2) + '</pre></div>';
                })
                .catch(e => alert('Error: ' + e.message));
        }
    </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_html(HTML_PAGE)
        elif self.path == '/api/status':
            self.proxy_to_api('/health')
        elif self.path == '/api/sample':
            self.proxy_to_api('/sample')
        elif self.path == '/api/models':
            self.proxy_to_api('/models')
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/predict':
            self.proxy_to_api('/predict', method='POST', 
                data={'model_id': 'best_model_logistic_regression'})
        elif self.path == '/api/feedback':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.proxy_to_api('/feedback', method='POST', raw_data=body)
        elif self.path.startswith('/api/auto'):
            self.handle_auto_generate()
        else:
            self.send_error(404)
    
    def send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def proxy_to_api(self, path, method='GET', data=None, raw_data=None):
        try:
            url = f"{API_URL}{path}"
            if method == 'GET':
                r = requests.get(url, timeout=5)
            else:
                if raw_data:
                    r = requests.post(url, data=raw_data, 
                        headers={'Content-Type': 'application/json'}, timeout=5)
                else:
                    r = requests.post(url, json=data, timeout=5)
            
            self.send_response(r.status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(r.content)
        except Exception as e:
            self.send_json({'error': str(e)})
    
    def handle_auto_generate(self):
        """Handle auto generation"""
        import time
        start = time.time()
        
        count = 10  # default
        if '?' in self.path:
            params = self.path.split('?')[1]
            for param in params.split('&'):
                if param.startswith('count='):
                    count = int(param.split('=')[1])
        
        success = 0
        for i in range(count):
            try:
                # Predict
                r = requests.post(f"{API_URL}/predict", json={
                    'model_id': 'best_model_logistic_regression'
                }, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    interaction_id = data.get('interaction_id')
                    
                    # Feedback
                    if interaction_id:
                        fb = 1 if i % 3 != 0 else 0  # 66% positive
                        requests.post(f"{API_URL}/feedback", json={
                            'interaction_id': interaction_id,
                            'feedback': fb
                        }, timeout=3)
                    success += 1
            except:
                pass
        
        elapsed = time.time() - start
        self.send_json({
            'generated': count,
            'success': success,
            'time': round(elapsed, 2)
        })
    
    def log_message(self, format, *args):
        pass  # Suppress logs

def run_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    print(f"="*60)
    print(f"  Web Interface Running!")
    print(f"="*60)
    print(f"  Open: http://localhost:{port}")
    print(f"="*60)
    print(f"  Tekan Ctrl+C untuk berhenti")
    print(f"="*60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped")

if __name__ == '__main__':
    run_server()
