import requests
import socket
import threading
import time
import random
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import cv2
import numpy as np
import struct

class AdvancedHikvisionTester:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.rtsp_port = 554
        self.http_port = 80
        self.session = requests.Session()
        self.found_credentials = None
        
    def generate_advanced_test_pattern(self, width=1920, height=1080):
        """Generate advanced test pattern with metadata"""
        # Create base image
        img = Image.new('RGB', (width, height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Add timestamp and info
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        draw.rectangle([0, 0, width, 80], fill=(0, 0, 0))
        
        info_text = [
            f"HIKVISION TEST STREAM - {timestamp}",
            f"Resolution: {width}x{height}",
            f"Frame: {random.randint(1000, 9999)}",
            "AUTHORIZED TESTING ONLY"
        ]
        
        for i, text in enumerate(info_text):
            color = (255, 255, 0) if i == 3 else (255, 255, 255)
            draw.text((20, 15 + i*20), text, fill=color)
        
        # Add moving elements
        moving_x = int((time.time() * 50) % (width - 200))
        moving_y = int((time.time() * 30) % (height - 150))
        
        # Draw moving rectangle
        draw.rectangle([moving_x, moving_y, moving_x+200, moving_y+150], 
                      fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        
        # Add grid pattern
        for x in range(0, width, 50):
            draw.line([(x, 0), (x, height)], fill=(100, 100, 100), width=1)
        for y in range(0, height, 50):
            draw.line([(0, y), (width, y)], fill=(100, 100, 100), width=1)
        
        # Add color bars
        colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255)]
        bar_width = width // len(colors)
        for i, color in enumerate(colors):
            draw.rectangle([i*bar_width, height-60, (i+1)*bar_width, height-20], fill=color)
        
        return img
    
    def scan_common_hikvision_paths(self):
        """Scan for common Hikvision endpoints"""
        common_paths = [
            "/ISAPI/System/deviceInfo",
            "/ISAPI/Streaming/channels/101",
            "/ISAPI/Event/notification/alertStream",
            "/doc/page/login.asp",
            "/SDK/webLanguage",
            "/System/configurationFile",
        ]
        
        print("🔍 Scanning Hikvision paths...")
        for path in common_paths:
            url = f"http://{self.target_ip}:{self.http_port}{path}"
            try:
                response = requests.get(url, timeout=3)
                print(f"📁 {path} - Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"   🔓 Found accessible: {url}")
            except Exception as e:
                print(f"📁 {path} - Error: {e}")
    
    def brute_force_common_credentials(self):
        """Try common Hikvision credentials"""
        credentials_list = [
            # Default Hikvision credentials
            ('admin', 'admin'),
            ('admin', '12345'),
            ('admin', '123456'),
            ('admin', '111111'),
            ('admin', '1234567'),
            ('admin', '12345678'),
            ('admin', '123456789'),
            ('admin', '1234567890'),
            ('admin', '888888'),
            ('admin', '666666'),
            # Common variations
            ('admin', 'Admin123'),
            ('admin', 'Hik12345'),
            ('admin', 'hikvision'),
            ('admin', 'Hikvision'),
            ('admin', 'Hik123'),
        ]
        
        print("🔑 Testing common credentials...")
        for username, password in credentials_list:
            try:
                test_url = f"http://{self.target_ip}:{self.http_port}/ISAPI/System/deviceInfo"
                response = requests.get(test_url, auth=(username, password), timeout=5)
                
                if response.status_code == 200:
                    self.found_credentials = (username, password)
                    print(f"✅ CREDENTIALS FOUND: {username}:{password}")
                    return True
                else:
                    print(f"❌ {username}:{password} - Failed")
                    
            except Exception as e:
                print(f"❌ {username}:{password} - Error: {e}")
        
        return False
    
    def simulate_rtsp_stream(self, duration=60):
        """Simulate RTSP stream injection"""
        print("🎥 Simulating RTSP stream injection...")
        
        # Create RTSP-like socket connection
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target_ip, self.rtsp_port))
            print(f"📡 Connected to RTSP port {self.rtsp_port}")
            
            # Send RTSP OPTIONS request
            options_request = f"OPTIONS rtsp://{self.target_ip}:{self.rtsp_port}/ RTSP/1.0\r\nCSeq: 1\r\n\r\n"
            sock.send(options_request.encode())
            response = sock.recv(1024)
            print(f"📨 RTSP Response: {response.decode()}")
            
        except Exception as e:
            print(f"❌ RTSP connection failed: {e}")
        
        finally:
            try:
                sock.close()
            except:
                pass
    
    def generate_mjpeg_stream(self, port=8080):
        """Generate MJPEG stream simulation"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading
        
        class MJPEGHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/stream':
                    self.send_response(200)
                    self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
                    self.end_headers()
                    
                    frame_count = 0
                    while True:
                        try:
                            # Generate test image
                            img = self.generate_test_frame(frame_count)
                            img_bytes = io.BytesIO()
                            img.save(img_bytes, format='JPEG', quality=85)
                            frame_data = img_bytes.getvalue()
                            
                            # Send frame
                            self.wfile.write(b'--frame\r\n')
                            self.send_header('Content-Type', 'image/jpeg')
                            self.send_header('Content-Length', len(frame_data))
                            self.end_headers()
                            self.wfile.write(frame_data)
                            self.wfile.write(b'\r\n')
                            
                            frame_count += 1
                            time.sleep(0.1)  # 10 FPS
                            
                        except Exception as e:
                            break
                
                elif self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    html = """
                    <html>
                    <head><title>Test MJPEG Stream</title></head>
                    <body>
                        <h1>Test CCTV Stream</h1>
                        <img src="/stream" width="640" height="480">
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
            
            def generate_test_frame(self, frame_count):
                img = Image.new('RGB', (640, 480), color=(
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                ))
                draw = ImageDraw.Draw(img)
                
                # Add timestamp and frame info
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                draw.text((10, 10), f"Frame: {frame_count}", fill=(255,255,255))
                draw.text((10, 30), f"Time: {timestamp}", fill=(255,255,255))
                draw.text((10, 50), "SIMULATED STREAM", fill=(255,0,0))
                
                # Add moving object
                x = int((frame_count * 5) % 600)
                draw.ellipse([x, 100, x+40, 140], fill=(0,255,0))
                
                return img
        
        def run_server():
            server = HTTPServer(('0.0.0.0', port), MJPEGHandler)
            print(f"🌐 MJPEG Server running on port {port}")
            server.serve_forever()
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        return server_thread
    
    def comprehensive_test(self):
        """Run comprehensive security test"""
        print("🚀 Starting Comprehensive Hikvision Security Test")
        print("=" * 50)
        
        # Phase 1: Network discovery
        print("\n📍 Phase 1: Network Discovery")
        self.scan_common_hikvision_paths()
        
        # Phase 2: Credential testing
        print("\n🔑 Phase 2: Credential Testing")
        if self.brute_force_common_credentials():
            print("✅ Authentication bypass possible")
        else:
            print("❌ No common credentials worked")
        
        # Phase 3: Stream testing
        print("\n🎥 Phase 3: Stream Testing")
        self.simulate_rtsp_stream()
        
        # Phase 4: Start MJPEG server
        print("\n🌐 Phase 4: MJPEG Stream Server")
        self.generate_mjpeg_stream(8080)
        print("Access the stream at: http://localhost:8080")
        
        print("\n📊 Test completed!")

def main():
    print("""
    🔧 Advanced Hikvision Security Testing Tool
    ⚠️  FOR AUTHORIZED TESTING ONLY ⚠️
    """)
    
    # Replace with your target IP
    target_ip = input("Enter target IP (or press enter for localhost): ").strip()
    if not target_ip:
        target_ip = "127.0.0.1"
    
    tester = AdvancedHikvisionTester(target_ip)
    
    print(f"🎯 Target: {target_ip}")
    print("1. Comprehensive Test")
    print("2. Credential Test Only") 
    print("3. Stream Simulation Only")
    
    choice = input("Select option: ").strip()
    
    if choice == "1":
        tester.comprehensive_test()
    elif choice == "2":
        tester.brute_force_common_credentials()
    elif choice == "3":
        tester.simulate_rtsp_stream()
        tester.generate_mjpeg_stream(8080)
    else:
        print("Invalid option")

if __name__ == "__main__":
    main()
