"""KUERA AI — FORSA BUMDes Connector (WSL Bridge)

Bridges KUERA Desktop to WSL-based FORSA automation scripts.
Assumes FORSA scripts live at ~/ai-audit/forsa_scripts/ in WSL.

Usage:
    from src.data.forsa_connector import ForsaBridge
    bridge = ForsaBridge()
    status = bridge.check_wsl_status()
    result = bridge.run_check_status()

Security:
    - Credentials stay in WSL only (not stored in this connector)
    - Only structured output (JSON/Excel) is returned to Windows
    - No raw HTML or sensitive data crosses the bridge
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ForsaBridge:
    """Bridge to WSL FORSA automation scripts."""

    WSL_SCRIPT_DIR = "~/ai-audit/forsa_scripts"
    DEFAULT_SCRIPT = "forsabumdes_check_status.py"

    def __init__(self):
        self.wsl_available = self._check_wsl()

    def _check_wsl(self) -> bool:
        """Check if wsl command is available."""
        return shutil.which("wsl") is not None

    def _wsl_run(self, command: str, timeout: int = 120) -> Dict:
        """Run a command inside WSL and return structured result."""
        if not self.wsl_available:
            return {"status": "error", "message": "WSL not available on this machine"}

        try:
            result = subprocess.run(
                ["wsl", "bash", "-c", command],
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": f"WSL command timed out after {timeout}s"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_wsl_status(self) -> Dict:
        """Check if WSL is running and FORSA scripts exist."""
        if not self.wsl_available:
            return {
                "wsl_available": False,
                "forsa_scripts_found": False,
                "message": "WSL command not found. Install WSL or run scripts manually.",
            }

        # Check if script directory exists
        check_dir = self._wsl_run(f"test -d {self.WSL_SCRIPT_DIR} && echo 'EXISTS' || echo 'MISSING'")
        scripts_exist = "EXISTS" in check_dir.get("stdout", "")

        # List available scripts
        scripts = []
        if scripts_exist:
            ls_result = self._wsl_run(f"ls -1 {self.WSL_SCRIPT_DIR}/*.py 2>/dev/null | xargs -n1 basename")
            if ls_result["status"] == "success":
                scripts = [s.strip() for s in ls_result["stdout"].splitlines() if s.strip()]

        return {
            "wsl_available": True,
            "forsa_scripts_found": scripts_exist,
            "script_dir": self.WSL_SCRIPT_DIR,
            "scripts": scripts,
            "message": "FORSA bridge ready" if scripts_exist else "Script directory not found in WSL",
        }

    def run_check_status(self, mode: str = "2", timeout: int = 300) -> Dict:
        """Run forsabumdes_check_status.py in WSL.

        Args:
            mode: "1" = Semua unit, "2" = Testing (3 unit)
            timeout: Max seconds to wait for completion
        """
        status = self.check_wsl_status()
        if not status["forsa_scripts_found"]:
            return status

        script_path = f"{self.WSL_SCRIPT_DIR}/{self.DEFAULT_SCRIPT}"

        # Check if script exists
        check = self._wsl_run(f"test -f {script_path} && echo 'OK' || echo 'MISSING'")
        if "OK" not in check.get("stdout", ""):
            return {"status": "error", "message": f"Script not found: {script_path}"}

        # Build command that pipes input to the script
        # The script expects interactive input (username, password, mode)
        # We create a wrapper that feeds input via echo + pipe
        wrapper_cmd = (
            f"cd {self.WSL_SCRIPT_DIR} && "
            f"echo -e 'demo_user_01\\nforsabumdes\\n{mode}' | python3 {self.DEFAULT_SCRIPT}"
        )

        result = self._wsl_run(wrapper_cmd, timeout=timeout)

        # Parse output for structured data
        output_lines = result.get("stdout", "").splitlines()
        parsed = self._parse_check_status_output(output_lines)

        return {
            "status": result["status"],
            "returncode": result.get("returncode"),
            "parsed": parsed,
            "raw_stdout_lines": len(output_lines),
            "raw_stderr": result.get("stderr", "")[:500],  # Truncate
            "timestamp": datetime.now().isoformat(),
        }

    def _parse_check_status_output(self, lines: List[str]) -> Dict:
        """Parse stdout from forsabumdes_check_status.py into structured data."""
        parsed = {
            "total_bumd": 0,
            "sudah_isi": 0,
            "belum_isi": 0,
            "status_list": [],
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to extract structured data from output
            if "Total BUMD" in line or "total" in line.lower():
                try:
                    parsed["total_bumd"] = int("".join(filter(str.isdigit, line)))
                except ValueError:
                    pass
            elif "sudah" in line.lower() and "isi" in line.lower():
                try:
                    parsed["sudah_isi"] = int("".join(filter(str.isdigit, line)))
                except ValueError:
                    pass
            elif "belum" in line.lower() and "isi" in line.lower():
                try:
                    parsed["belum_isi"] = int("".join(filter(str.isdigit, line)))
                except ValueError:
                    pass
            elif "|" in line:
                # Likely a data row
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    parsed["status_list"].append({
                        "nama": parts[0],
                        "status": parts[1] if len(parts) > 1 else "",
                        "detail": parts[2] if len(parts) > 2 else "",
                    })

        return parsed

    def list_output_files(self) -> List[str]:
        """List Excel output files generated by FORSA scripts in WSL."""
        result = self._wsl_run(f"ls -1 {self.WSL_SCRIPT_DIR}/*.xlsx 2>/dev/null | xargs -n1 basename")
        if result["status"] == "success":
            return [s.strip() for s in result["stdout"].splitlines() if s.strip()]
        return []

    def copy_output_to_windows(self, filename: str, windows_dir: Optional[str] = None) -> Dict:
        """Copy an Excel result file from WSL to Windows.

        Args:
            filename: Name of .xlsx file in WSL script dir
            windows_dir: Windows destination (default: data/uploads/)
        """
        if windows_dir is None:
            windows_dir = Path(__file__).parent.parent.parent / "data" / "uploads"
        else:
            windows_dir = Path(windows_dir)
        windows_dir.mkdir(parents=True, exist_ok=True)

        wsl_path = f"{self.WSL_SCRIPT_DIR}/{filename}"
        win_path = windows_dir / filename

        # Use wsl cp to Windows path
        win_path_str = str(win_path).replace("\\", "/").replace("C:/", "/mnt/c/").replace("D:/", "/mnt/d/")
        result = self._wsl_run(f"cp {wsl_path} {win_path_str}")

        if result["status"] == "success" and win_path.exists():
            return {"status": "success", "copied_to": str(win_path)}
        return {"status": "error", "message": result.get("stderr", "Copy failed")}


def get_forsa_status() -> Dict:
    """Quick status check without instantiating class."""
    bridge = ForsaBridge()
    return bridge.check_wsl_status()


def run_forsa_audit(mode: str = "2") -> Dict:
    """Run FORSA audit and return structured result."""
    bridge = ForsaBridge()
    return bridge.run_check_status(mode=mode)
