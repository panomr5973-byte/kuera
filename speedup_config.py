#!/usr/bin/env python
"""
Speedup Config - Mempercepat evolusi untuk demo
Edit config untuk mempercepat waktu (1 jam = 1 minggu)
"""

import json
from pathlib import Path

def apply_speedup():
    """
    Apply speedup configuration:
    - check_interval: 0.1 hours (6 menit) bukannya 24 jam
    - min_samples: 10 bukannya 50
    """
    print("="*60)
    print("  SPEEDUP MODE - Fast Evolution Demo")
    print("="*60)
    
    # Create speedup config
    config = {
        'mode': 'speedup',
        'check_interval_hours': 0.1,  # 6 menit
        'min_samples': 10,  # Hanya 10 feedback untuk trigger
        'performance_threshold': 0.05,
        'note': '1 jam = 1 minggu demo'
    }
    
    # Save config
    with open('logs/speedup_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n  [OK] Speedup config applied!")
    print(f"\n  Settings:")
    print(f"    Check interval: {config['check_interval_hours']} jam ({int(config['check_interval_hours']*60)} menit)")
    print(f"    Min samples: {config['min_samples']}")
    print(f"    Performance threshold: {config['performance_threshold']}")
    
    print("\n  Next steps:")
    print("    1. Restart scheduler dengan config baru")
    print("    2. Jalankan: python demo_7day_evolusi.py --mode fast")
    
    return config

def apply_normal():
    """Reset ke mode normal (24 jam)"""
    config = {
        'mode': 'normal',
        'check_interval_hours': 24,
        'min_samples': 50,
        'performance_threshold': 0.05
    }
    
    with open('logs/speedup_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("[OK] Normal mode applied (24h check, 50 min samples)")
    return config

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "normal":
        apply_normal()
    else:
        apply_speedup()
