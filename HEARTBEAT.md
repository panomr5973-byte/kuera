# KUERA Heartbeat Tasks

Check these periodically (every ~30 min during active hours):

1. **Database Health** — Run `python scripts/db_maintenance.py --dry-run` to check DB bloat
2. **Log Rotation** — Check `logs/` directory size; compress if > 500MB
3. **Service Health** — Check if critical services (API, dashboard) are running
4. **Backup Status** — Verify Terabox backup scripts are ready; run if needed
5. **Audit Workflow** — Check `data/uploads/` for unprocessed files

Run full maintenance weekly:
```bash
python scripts/db_maintenance.py --archive-days 90
```
