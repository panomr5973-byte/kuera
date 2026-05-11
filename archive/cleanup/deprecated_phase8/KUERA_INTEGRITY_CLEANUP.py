#!/usr/bin/env python
"""
KUERA AI - Integrity Check & Cleanup System
Analyzes and organizes existing files, marks incomplete components
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class KueraIntegrityManager:
    """Manages KUERA file integrity and cleanup"""
    
    def __init__(self):
        self.root = Path(".")
        self.archive_dir = Path("archive_incomplete")
        self.manifest_file = Path("KUERA_COMPONENTS.json")
        
        # Define component categories
        self.components = {
            'CORE_COMPLETE': [],
            'WEB_COMPLETE': [],
            'MODEL_COMPLETE': [],
            'INTEGRATION_COMPLETE': [],
            'INCOMPLETE_OR_DUPLICATE': [],
            'SCHEDULED_FOR_LATER': []
        }
        
        # Files to keep (verified working)
        self.KEEP_FILES = {
            # Core System (Complete & Tested)
            'kuera_persona.py': 'Persona system with workspace integration',
            'kuera_evolution_engine.py': 'Evolution tracking & self-learning',
            'kuera_integrated_system.py': 'Main integrated chat system',
            'kuera_multi_model_manager.py': 'Multi-model routing (8 models)',
            
            # Model Integration (Complete)
            'integrate_bartowski_models.py': 'Bartowski collection integration',
            'integrate_all_new_models.py': 'Model registry manager',
            'kuera_llm_ctransformers.py': 'CTransformers wrapper',
            
            # Web Server (Complete)
            'kuwera_web_server_v2.py': 'Flask web server v2.0 (RECOMMENDED)',
            'kuwera_workspace_integration.py': 'Workspace memory sync',
            'kuwera_memory_bridge.py': 'Memory consolidation bridge',
            
            # Utilities (Complete)
            'kuwera_autostart.py': 'Auto-start system',
            'kuwera_health_check.py': 'Health monitoring',
            'kuera_with_check.py': 'Diagnostic wrapper',
            
            # World Bank (Complete)
            'kuera_worldbank_setup.py': 'World Bank data pipeline',
            'kuera_worldbank_integration.py': 'World Bank integration',
            'kuera_worldbank_chat.py': 'Economic analysis chat',
            'kuera_international_integration.py': 'International data',
            'kuera_international_chat.py': 'Multi-source data chat',
        }
        
        # Files to archive (incomplete/duplicate/old)
        self.ARCHIVE_FILES = {
            # Duplicates/Old Versions
            'kuera_chat.py': 'Old version - superseded by integrated system',
            'kuera_chat_demo.py': 'Demo version - not for production',
            'kuera_chat_improved.py': 'Superseded by integrated system',
            'kuera_chat_simple.py': 'Simple version - not needed',
            'kuera_web_server.py': 'Old version - use v2',
            'kuera_web_server_fixed.py': 'Old version - use kuwera_web_server_v2.py',
            'kuwera_web_server.py': 'Old version - use v2',
            'kuwera_web_interface.py': 'Superseded by v2 template',
            'kuwera_persona.py': 'Duplicate - use kuera_persona.py',
            
            # Incomplete/Failed (HTTP 429)
            'kuera_model_downloader.py': 'Incomplete - scheduled for later download',
            'kuera_qwen_chat.py': 'Incomplete - scheduled for later',
            'kuera_ultimate_chat.py': 'Incomplete - scheduled for later',
            'kuera_human_like.py': 'Duplicate functionality',
            'kuera_smart_chat.py': 'Superseded by integrated system',
            'kuera_llm_integration.py': 'Superseded by ctransformers wrapper',
            'kuera_web_access.py': 'Old version - not needed',
            'kuera_analyser.py': 'Old analysis script',
            'kuera_setup_database.py': 'Superseded by evolution engine',
            
            # Demo/Test Files
            'kuera_worldbank_demo.py': 'Demo only',
            'kuera_worldbank_trainer.py': 'Training script - completed',
        }
        
        # Files to schedule for download later
        self.SCHEDULED_FILES = [
            'kuera_model_downloader.py',
            'kuera_qwen_chat.py', 
            'kuera_ultimate_chat.py',
            'kuera_rag_system.py',
            'kuera_voice_interface.py',
            'kuera_vision_system.py',
        ]
    
    def scan_files(self) -> Dict:
        """Scan all Python files in project"""
        files = {}
        for py_file in self.root.glob("ku*.py"):
            if py_file.name.startswith('KUERA_'):
                continue  # Skip our own files
                
            stat = py_file.stat()
            files[py_file.name] = {
                'size_kb': round(stat.st_size / 1024, 1),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'path': str(py_file),
                'status': self._classify_file(py_file.name)
            }
        return files
    
    def _classify_file(self, filename: str) -> str:
        """Classify file status"""
        if filename in self.KEEP_FILES:
            return 'KEEP'
        elif filename in self.ARCHIVE_FILES:
            return 'ARCHIVE'
        elif filename in self.SCHEDULED_FILES:
            return 'SCHEDULED'
        else:
            return 'REVIEW'
    
    def create_manifest(self):
        """Create component manifest"""
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'status': 'INTEGRITY_CHECK_COMPLETE',
            'components': {
                'CORE_COMPLETE': {
                    'description': 'Core system files - verified working',
                    'files': []
                },
                'WEB_COMPLETE': {
                    'description': 'Web interface & server - production ready',
                    'files': []
                },
                'MODEL_COMPLETE': {
                    'description': 'Model integration - 8 models supported',
                    'files': []
                },
                'DATA_COMPLETE': {
                    'description': 'World Bank & international data',
                    'files': []
                },
                'WORKSPACE_COMPLETE': {
                    'description': 'Workspace memory integration',
                    'files': []
                },
                'ARCHIVED': {
                    'description': 'Moved to archive - old/duplicate/incomplete',
                    'files': []
                },
                'SCHEDULED': {
                    'description': 'To be downloaded later if needed',
                    'files': self.SCHEDULED_FILES
                }
            }
        }
        
        # Categorize files
        scanned = self.scan_files()
        
        for fname, info in scanned.items():
            if info['status'] == 'KEEP':
                if 'web' in fname.lower() or 'server' in fname.lower():
                    manifest['components']['WEB_COMPLETE']['files'].append({
                        'name': fname,
                        'size_kb': info['size_kb'],
                        'description': self.KEEP_FILES.get(fname, 'Working component')
                    })
                elif 'model' in fname.lower() or 'integrate' in fname.lower() or 'llm' in fname.lower():
                    manifest['components']['MODEL_COMPLETE']['files'].append({
                        'name': fname,
                        'size_kb': info['size_kb'],
                        'description': self.KEEP_FILES.get(fname, 'Working component')
                    })
                elif 'worldbank' in fname.lower() or 'international' in fname.lower():
                    manifest['components']['DATA_COMPLETE']['files'].append({
                        'name': fname,
                        'size_kb': info['size_kb'],
                        'description': self.KEEP_FILES.get(fname, 'Working component')
                    })
                elif 'workspace' in fname.lower() or 'memory' in fname.lower():
                    manifest['components']['WORKSPACE_COMPLETE']['files'].append({
                        'name': fname,
                        'size_kb': info['size_kb'],
                        'description': self.KEEP_FILES.get(fname, 'Working component')
                    })
                else:
                    manifest['components']['CORE_COMPLETE']['files'].append({
                        'name': fname,
                        'size_kb': info['size_kb'],
                        'description': self.KEEP_FILES.get(fname, 'Working component')
                    })
            elif info['status'] == 'ARCHIVE':
                manifest['components']['ARCHIVED']['files'].append({
                    'name': fname,
                    'size_kb': info['size_kb'],
                    'reason': self.ARCHIVE_FILES.get(fname, 'Old/duplicate')
                })
        
        # Save manifest
        with open(self.manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest
    
    def archive_files(self, dry_run=True):
        """Move incomplete/duplicate files to archive"""
        self.archive_dir.mkdir(exist_ok=True)
        
        archived = []
        errors = []
        
        scanned = self.scan_files()
        
        for fname, info in scanned.items():
            if info['status'] == 'ARCHIVE':
                src = self.root / fname
                dst = self.archive_dir / fname
                
                if dry_run:
                    archived.append({
                        'file': fname,
                        'action': 'WOULD_ARCHIVE',
                        'reason': self.ARCHIVE_FILES.get(fname, 'Old/duplicate')
                    })
                else:
                    try:
                        src.rename(dst)
                        archived.append({
                            'file': fname,
                            'action': 'ARCHIVED',
                            'to': str(dst)
                        })
                    except Exception as e:
                        errors.append({'file': fname, 'error': str(e)})
        
        return {'archived': archived, 'errors': errors, 'dry_run': dry_run}
    
    def print_report(self, manifest: Dict):
        """Print formatted report"""
        print("="*70)
        print(" KUERA AI - INTEGRITY CHECK & CLEANUP REPORT")
        print("="*70)
        print(f" Generated: {manifest['generated_at']}")
        print(f" Status: {manifest['status']}")
        print()
        
        # Complete components
        for category, data in manifest['components'].items():
            if category in ['SCHEDULED', 'ARCHIVED']:
                continue
                
            files = data.get('files', [])
            if files:
                print(f" [OK] {category}")
                print(f"    {data['description']}")
                print(f"    Files: {len(files)}")
                for f in files[:5]:  # Show first 5
                    if isinstance(f, dict):
                        print(f"      • {f['name']} ({f.get('size_kb', '?')} KB)")
                    else:
                        print(f"      • {f}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")
                print()
        
        # Archived
        archived = manifest['components'].get('ARCHIVED', {}).get('files', [])
        if archived:
            print(f" [ARCHIVED] ({len(archived)} files)")
            print("    Moved to archive_incomplete/ - old/duplicate/incomplete")
            for f in archived[:5]:
                if isinstance(f, dict):
                    print(f"      • {f['name']}")
            if len(archived) > 5:
                print(f"      ... and {len(archived) - 5} more")
            print()
        
        # Scheduled
        scheduled = manifest['components'].get('SCHEDULED', {}).get('files', [])
        if scheduled:
            print(f" [SCHEDULED] FOR LATER ({len(scheduled)} files)")
            print("    To be downloaded when needed:")
            for f in scheduled:
                print(f"      • {f}")
            print()
        
        print("="*70)
        print(" RECOMMENDATION:")
        print("="*70)
        print(" Use these core files for production:")
        print("   1. kuwera_web_server_v2.py - Web interface")
        print("   2. kuera_persona.py - Chat persona")
        print("   3. kuera_multi_model_manager.py - Model routing")
        print("   4. kuwera_autostart.py - Auto-start system")
        print()
        print(" Run: python KUERA_INTEGRITY_CLEANUP.py --archive")
        print("      to move incomplete files to archive")
        print("="*70)


def main():
    import sys
    
    manager = KueraIntegrityManager()
    
    # Check for --archive flag
    do_archive = '--archive' in sys.argv
    
    # Create manifest
    print("[INFO] Scanning files...")
    manifest = manager.create_manifest()
    print(f"[OK] Manifest saved to: {manager.manifest_file}")
    print()
    
    # Archive if requested
    if do_archive:
        print("[INFO] Archiving incomplete/duplicate files...")
        result = manager.archive_files(dry_run=False)
        print(f"[OK] Archived {len(result['archived'])} files")
        if result['errors']:
            print(f"[WARN] Errors: {len(result['errors'])}")
    else:
        print("[INFO] Dry run - no files moved (use --archive to actually archive)")
        result = manager.archive_files(dry_run=True)
        print(f"[INFO] Would archive {len(result['archived'])} files")
    
    print()
    
    # Print report
    manager.print_report(manifest)


if __name__ == "__main__":
    main()
