"""
Disk Space Monitoring Dashboard
Monitor penggunaan space di C: dan D: drive
"""

import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.paths import get_paths


class DiskMonitor:
    """Monitor disk space untuk AI Project"""
    
    def __init__(self):
        self.paths = get_paths()
        self.log_file = self.paths.logs / "disk_monitor.json"
        self.threshold_warning = 10 * 1024 * 1024 * 1024  # 10 GB
        self.threshold_critical = 5 * 1024 * 1024 * 1024  # 5 GB
        
    def get_disk_usage(self, drive: str) -> Dict:
        """Get disk usage untuk drive tertentu"""
        try:
            usage = shutil.disk_usage(drive)
            return {
                "drive": drive,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent_used": round((usage.used / usage.total) * 100, 1),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "drive": drive,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_folder_size(self, path: Path) -> Dict:
        """Get size dari folder"""
        if not path.exists():
            return {"path": str(path), "size_gb": 0, "files": 0}
        
        try:
            total_size = 0
            file_count = 0
            
            for file in path.rglob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
                    file_count += 1
            
            return {
                "path": str(path),
                "size_gb": round(total_size / (1024**3), 2),
                "files": file_count
            }
        except Exception as e:
            return {"path": str(path), "error": str(e)}
    
    def analyze_project_space(self) -> Dict:
        """Analyze space usage untuk seluruh project"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "disks": {},
            "folders": {}
        }
        
        # Disk usage
        report["disks"]["C"] = self.get_disk_usage("C:/")
        report["disks"]["D"] = self.get_disk_usage("D:/")
        
        # Key folders
        report["folders"]["active_models"] = self.get_folder_size(self.paths.active_models)
        report["folders"]["model_backup"] = self.get_folder_size(self.paths.model_backup)
        report["folders"]["model_archive"] = self.get_folder_size(self.paths.model_archive)
        report["folders"]["logs"] = self.get_folder_size(self.paths.logs)
        report["folders"]["data"] = self.get_folder_size(self.paths.data)
        
        return report
    
    def check_alerts(self, report: Dict) -> List[Dict]:
        """Check untuk alerts"""
        alerts = []
        
        for drive, info in report["disks"].items():
            if "free_gb" in info:
                free_bytes = info["free_gb"] * 1024**3
                
                if free_bytes < self.threshold_critical:
                    alerts.append({
                        "level": "CRITICAL",
                        "drive": drive,
                        "message": f"Drive {drive}: Hanya {info['free_gb']:.1f} GB tersisa!",
                        "free_gb": info["free_gb"]
                    })
                elif free_bytes < self.threshold_warning:
                    alerts.append({
                        "level": "WARNING",
                        "drive": drive,
                        "message": f"Drive {drive}: {info['free_gb']:.1f} GB tersisa (dibawah 10GB)",
                        "free_gb": info["free_gb"]
                    })
        
        return alerts
    
    def save_report(self, report: Dict):
        """Save report ke log file"""
        logs = []
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(report)
        
        # Keep only last 30 days
        logs = logs[-100:]
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def print_dashboard(self, report: Dict, alerts: List[Dict]):
        """Print dashboard ke console"""
        print("=" * 70)
        print("[DISK SPACE MONITORING DASHBOARD]")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Alerts
        if alerts:
            print("\n[!] ALERTS:")
            print("-" * 70)
            for alert in alerts:
                level_marker = "[CRITICAL]" if alert["level"] == "CRITICAL" else "[WARNING]"
                print(f"  {level_marker} {alert['message']}")
        else:
            print("\n[OK] All drives healthy")
        
        # Disk usage
        print("\n[DISK USAGE]")
        print("-" * 70)
        for drive, info in report["disks"].items():
            if "error" not in info:
                used_pct = info["percent_used"]
                
                print(f"\n  Drive {drive}:")
                print(f"    Usage: {used_pct}%")
                print(f"    Total: {info['total_gb']:.1f} GB")
                print(f"    Used:  {info['used_gb']:.1f} GB")
                print(f"    Free:  {info['free_gb']:.1f} GB")
        
        # Folder sizes
        print("\n[FOLDER SIZES]")
        print("-" * 70)
        for name, info in report["folders"].items():
            if "error" not in info:
                print(f"  {name:20s}: {info['size_gb']:>8.2f} GB ({info['files']} files)")
            else:
                print(f"  {name:20s}: [ERROR] {info['error']}")
        
        # Recommendations
        print("\n[RECOMMENDATIONS]")
        print("-" * 70)
        c_free = report["disks"]["C"].get("free_gb", 0)
        
        if c_free < 20:
            print("  1. Archive old models to D: drive")
            print("  2. Clean up logs folder")
            print("  3. Remove temporary files")
        elif c_free < 50:
            print("  1. Monitor space usage weekly")
            print("  2. Archive models older than 30 days")
        else:
            print("  1. Space is healthy, no action needed")
            print("  2. Continue regular monitoring")
        
        print("=" * 70)
    
    def generate_html_report(self, report: Dict) -> str:
        """Generate HTML report untuk dashboard"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Project - Disk Monitor</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007acc; padding-bottom: 10px; }}
        .alert {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .alert-critical {{ background: #ffebee; color: #c62828; border-left: 4px solid #c62828; }}
        .alert-warning {{ background: #fff3e0; color: #ef6c00; border-left: 4px solid #ef6c00; }}
        .disk-card {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #4caf50, #8bc34a); transition: width 0.3s; }}
        .progress-fill.warning {{ background: linear-gradient(90deg, #ff9800, #ffc107); }}
        .progress-fill.critical {{ background: linear-gradient(90deg, #f44336, #ff5722); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #007acc; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Project - Disk Space Monitoring</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Alerts</h2>
"""
        
        alerts = self.check_alerts(report)
        if alerts:
            for alert in alerts:
                css_class = "alert-critical" if alert["level"] == "CRITICAL" else "alert-warning"
                html += f'<div class="alert {css_class}">{alert["message"]}</div>'
        else:
            html += '<div class="alert" style="background: #e8f5e9; color: #2e7d32; border-left: 4px solid #4caf50;">All drives healthy!</div>'
        
        html += "<h2>Disk Usage</h2>"
        
        for drive, info in report["disks"].items():
            if "error" not in info:
                pct = info["percent_used"]
                fill_class = "progress-fill"
                if pct > 90:
                    fill_class += " critical"
                elif pct > 80:
                    fill_class += " warning"
                
                html += f"""
        <div class="disk-card">
            <h3>Drive {drive}: - {info["free_gb"]:.1f} GB free</h3>
            <div class="progress-bar">
                <div class="{fill_class}" style="width: {pct}%"></div>
            </div>
            <p>Total: {info["total_gb"]:.1f} GB | Used: {info["used_gb"]:.1f} GB ({pct}%)</p>
        </div>
"""
        
        html += """
        <h2>Folder Sizes</h2>
        <table>
            <tr>
                <th>Folder</th>
                <th>Size (GB)</th>
                <th>Files</th>
            </tr>
"""
        
        for name, info in report["folders"].items():
            if "error" not in info:
                html += f"""
            <tr>
                <td>{name}</td>
                <td>{info["size_gb"]:.2f}</td>
                <td>{info["files"]}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
</body>
</html>
"""
        return html
    
    def save_html_report(self, report: Dict):
        """Save HTML report"""
        html = self.generate_html_report(report)
        html_path = self.paths.project_root / "monitoring" / "dashboard.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n[OK] HTML report saved: {html_path}")
    
    def run(self, save_html: bool = True):
        """Run full monitoring"""
        report = self.analyze_project_space()
        alerts = self.check_alerts(report)
        
        self.print_dashboard(report, alerts)
        self.save_report(report)
        
        if save_html:
            self.save_html_report(report)
        
        return report, alerts


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Disk Space Monitor")
    parser.add_argument("--no-html", action="store_true", help="Skip HTML report")
    
    args = parser.parse_args()
    
    monitor = DiskMonitor()
    monitor.run(save_html=not args.no_html)


if __name__ == "__main__":
    main()
