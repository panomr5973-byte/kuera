"""
Terabox Uploader for KUERA
Uploads files/folders to Terabox cloud storage.

Usage:
    python upload.py --file "path/to/file" --remote "/remote/folder"
    python upload.py --folder "path/to/folder" --remote "/remote/folder" --pattern "*.gguf"
    python upload.py --batch batch_list.json
"""

import os
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Optional

try:
    import requests
except ImportError:
    print("[ERROR] requests not installed. Run: pip install requests")
    sys.exit(1)

# Configuration
APP_ID = "250528"
BASE_URL = "https://www.terabox.com"
CHUNK_SIZE = 4 * 1024 * 1024  # 4MB chunks for large files


class TeraboxUploader:
    def __init__(self, cookies_file: str = "cookies.json"):
        self.session = requests.Session()
        self.cookies = self._load_cookies(cookies_file)
        self.js_token = self.cookies.get("jsToken", "")
        self._setup_session()

    def _load_cookies(self, cookies_file: str) -> Dict:
        path = Path(cookies_file)
        if not path.exists():
            print(f"[ERROR] Cookies file not found: {cookies_file}")
            print("[INFO] Copy 'cookies.json.template' and fill in your Terabox cookies.")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _setup_session(self):
        """Configure session with cookies and headers."""
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.terabox.com/main",
            "Origin": "https://www.terabox.com",
        })

        # Set cookies from file
        cookie_mapping = {
            "ndus": "ndus",
            "csrfToken": "csrfToken",
            "browserid": "browserid",
            "lang": "lang",
            "ndut_fmt": "ndut_fmt",
        }
        for key, cookie_name in cookie_mapping.items():
            value = self.cookies.get(key)
            if value and not value.startswith("opsional") and not value.startswith("GANTI"):
                self.session.cookies.set(cookie_name, value, domain="terabox.com")

    def _fetch_js_token(self) -> Optional[str]:
        """Extract jsToken from the main page HTML."""
        try:
            resp = self.session.get(f"{BASE_URL}/main", timeout=30)
            resp.raise_for_status()
            import re
            match = re.search(r'"jsToken":"([^"]+)"', resp.text)
            if match:
                return match.group(1)
            # Alternative pattern
            match = re.search(r'jsToken\s*=\s*["\']([^"\']+)', resp.text)
            if match:
                return match.group(1)
        except Exception as e:
            print(f"[WARN] Could not fetch jsToken: {e}")
        return None

    def check_login(self) -> bool:
        """Verify cookies are valid by checking user info/quota."""
        try:
            # Try to get quota info
            params = {
                "app_id": APP_ID,
                "checkexpire": 1,
                "checkfree": 1,
            }
            resp = self.session.get(
                f"{BASE_URL}/api/quota",
                params=params,
                timeout=30
            )
            data = resp.json()
            if data.get("errno") == 0:
                username = data.get("username", "unknown")
                total = data.get("total", 0)
                used = data.get("used", 0)
                free_gb = (total - used) / (1024**3)
                total_gb = total / (1024**3)
                print(f"[OK] Logged in as: {username}")
                print(f"[OK] Storage: {free_gb:.2f} GB free / {total_gb:.2f} GB total")
                return True
            else:
                err_msg = data.get("errmsg", "Unknown error")
                print(f"[ERROR] Login check failed: {err_msg} (errno={data.get('errno')})")
                print("[INFO] Your ndus cookie may be expired. Login again in browser and copy new cookie.")
                return False
        except Exception as e:
            print(f"[ERROR] Network error during login check: {e}")
            return False

    def ensure_folder(self, remote_path: str) -> bool:
        """Create remote folder if it doesn't exist."""
        # Terabox auto-creates folders on upload, so this is optional
        # But we can verify it exists by listing
        return True

    def _calc_md5(self, filepath: Path) -> str:
        """Calculate MD5 hash of file."""
        md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192 * 1024), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def _upload_small_file(self, filepath: Path, remote_path: str) -> bool:
        """Upload file < 4GB using single request."""
        filename = filepath.name
        file_size = filepath.stat().st_size
        remote_file = f"{remote_path}/{filename}".replace("//", "/")

        md5_hash = self._calc_md5(filepath)
        block_list = [md5_hash]

        # Step 1: Precreate
        try:
            precreate_data = {
                "path": remote_file,
                "size": file_size,
                "isdir": 0,
                "autoinit": 1,
                "block_list": json.dumps(block_list),
                "rtype": 3,
                "app_id": APP_ID,
            }
            if self.js_token:
                precreate_data["jsToken"] = self.js_token

            resp = self.session.post(
                f"{BASE_URL}/api/precreate",
                data=precreate_data,
                timeout=60
            )
            precreate_result = resp.json()
            if precreate_result.get("errno") != 0:
                err = precreate_result.get("errmsg", "unknown")
                print(f"[ERROR] Precreate failed: {err}")
                return False

            upload_id = precreate_result.get("uploadid")
            return_type = precreate_result.get("return_type", 1)

            if return_type == 1 or not upload_id:
                # File might already exist or no upload needed
                print(f"[OK] File may already exist or no upload needed: {filename}")
                return True

            # Step 2: Upload file
            upload_url = precreate_result.get("upload_url") or f"{BASE_URL}/api/upload"
            
            with open(filepath, "rb") as f:
                files = {"file": (filename, f, "application/octet-stream")}
                upload_data = {
                    "app_id": APP_ID,
                    "path": remote_file,
                    "uploadid": upload_id,
                    "partseq": 0,
                }
                if self.js_token:
                    upload_data["jsToken"] = self.js_token

                resp = self.session.post(
                    upload_url,
                    data=upload_data,
                    files=files,
                    timeout=300
                )

            upload_result = resp.json()
            if upload_result.get("errno") != 0:
                err = upload_result.get("errmsg", "unknown")
                print(f"[ERROR] Upload failed: {err}")
                return False

            # Step 3: Create (finalize)
            create_data = {
                "path": remote_file,
                "size": file_size,
                "isdir": 0,
                "uploadid": upload_id,
                "block_list": json.dumps(block_list),
                "rtype": 3,
                "app_id": APP_ID,
            }
            if self.js_token:
                create_data["jsToken"] = self.js_token

            resp = self.session.post(
                f"{BASE_URL}/api/create",
                data=create_data,
                timeout=60
            )
            create_result = resp.json()
            if create_result.get("errno") == 0:
                print(f"[OK] Uploaded: {filename} ({file_size / (1024**2):.2f} MB)")
                return True
            else:
                err = create_result.get("errmsg", "unknown")
                print(f"[ERROR] Create/finalize failed: {err}")
                return False

        except Exception as e:
            print(f"[ERROR] Upload exception for {filename}: {e}")
            return False

    def upload_file(self, filepath: Path, remote_dir: str) -> bool:
        """Upload a single file to Terabox."""
        if not filepath.exists():
            print(f"[ERROR] File not found: {filepath}")
            return False

        file_size = filepath.stat().st_size
        filename = filepath.name

        # Ensure remote path starts with /
        remote_dir = remote_dir if remote_dir.startswith("/") else "/" + remote_dir
        remote_dir = remote_dir.rstrip("/")

        print(f"[UPLOAD] {filename} ({file_size / (1024**2):.2f} MB) -> {remote_dir}/")

        # For now, use simple upload for all file sizes
        # Large files (> 2GB) should be split using archive_split.py first
        return self._upload_small_file(filepath, remote_dir)

    def upload_folder(self, folder_path: Path, remote_dir: str, pattern: str = "*") -> Dict:
        """Upload all matching files from a folder."""
        if not folder_path.exists():
            print(f"[ERROR] Folder not found: {folder_path}")
            return {"success": 0, "failed": 0}

        files = sorted(folder_path.glob(pattern))
        files = [f for f in files if f.is_file()]

        if not files:
            print(f"[WARN] No files matching '{pattern}' in {folder_path}")
            return {"success": 0, "failed": 0}

        print(f"[INFO] Found {len(files)} files to upload")
        success = 0
        failed = 0

        for i, filepath in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] ", end="")
            if self.upload_file(filepath, remote_dir):
                success += 1
            else:
                failed += 1
            # Small delay between uploads
            time.sleep(1)

        print(f"\n{'='*50}")
        print(f"[SUMMARY] Success: {success}, Failed: {failed}")
        return {"success": success, "failed": failed}

    def upload_batch(self, batch_file: str) -> None:
        """Upload multiple files/folders from a batch JSON config."""
        with open(batch_file, "r", encoding="utf-8") as f:
            batch = json.load(f)

        total_success = 0
        total_failed = 0

        for item in batch.get("items", []):
            source = item["source"]
            remote = item["remote"]
            item_type = item.get("type", "file")
            pattern = item.get("pattern", "*")

            print(f"\n{'='*50}")
            print(f"[BATCH] {source} -> {remote}")
            print(f"{'='*50}")

            if item_type == "folder":
                result = self.upload_folder(Path(source), remote, pattern)
            else:
                result = {"success": 0, "failed": 0}
                if self.upload_file(Path(source), remote):
                    result["success"] = 1
                else:
                    result["failed"] = 1

            total_success += result["success"]
            total_failed += result["failed"]

        print(f"\n{'='*50}")
        print(f"[FINAL] Total Success: {total_success}, Total Failed: {total_failed}")


def main():
    parser = argparse.ArgumentParser(description="Upload files to Terabox")
    parser.add_argument("--file", "-f", help="Single file to upload")
    parser.add_argument("--folder", "-d", help="Folder to upload")
    parser.add_argument("--remote", "-r", default="/KUERA_Backup", help="Remote destination folder")
    parser.add_argument("--pattern", "-p", default="*", help="File pattern for folder upload")
    parser.add_argument("--batch", "-b", help="Batch config JSON file")
    parser.add_argument("--cookies", "-c", default="cookies.json", help="Path to cookies JSON file")

    args = parser.parse_args()

    if not any([args.file, args.folder, args.batch]):
        parser.print_help()
        print("\n[ERROR] Specify --file, --folder, or --batch")
        sys.exit(1)

    uploader = TeraboxUploader(args.cookies)

    # Fetch jsToken if not provided
    if not uploader.js_token:
        print("[INFO] Fetching jsToken from Terabox...")
        token = uploader._fetch_js_token()
        if token:
            uploader.js_token = token
            print(f"[OK] Got jsToken: {token[:20]}...")
        else:
            print("[WARN] Could not fetch jsToken, upload may still work without it")

    # Check login
    if not uploader.check_login():
        print("[FATAL] Login failed. Please check your cookies.")
        sys.exit(1)

    # Execute upload
    if args.batch:
        uploader.upload_batch(args.batch)
    elif args.file:
        uploader.upload_file(Path(args.file), args.remote)
    elif args.folder:
        uploader.upload_folder(Path(args.folder), args.remote, args.pattern)


if __name__ == "__main__":
    main()
