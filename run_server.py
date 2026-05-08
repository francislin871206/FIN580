"""
Local development server for the FIN580 Brent Crude Dashboard.
Serves static files and provides an API endpoint to run the Python pipeline.
"""
import http.server
import socketserver
import subprocess
import json
import os

PORT = 8080

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/run_pipeline':
            print("\n[Server] Received request to run pipeline...")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                # Run the pipeline script
                process = subprocess.run(
                    ['python', 'scripts/run_pipeline.py'], 
                    capture_output=True, text=True
                )
                if process.returncode == 0:
                    print("[Server] Pipeline finished successfully.")
                    response = {"status": "success", "output": process.stdout}
                else:
                    print("[Server] Pipeline failed.")
                    response = {"status": "error", "output": process.stderr}
                    
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                print(f"[Server] Error: {str(e)}")
                self.wfile.write(json.dumps({"status": "error", "output": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # Ensure we are in the project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print("="*60)
        print(">>> BRENT CRUDE COMMAND CENTER - LOCAL SERVER <<<")
        print("="*60)
        print(f"Server is running at: http://localhost:{PORT}")
        print("Press Ctrl+C to stop.")
        print("="*60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
