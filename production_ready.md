# KUERA AI Production Ready - Windows Native (Simple/Dynamic/Modern)

## 🚀 One-Command Production
```
# Native Windows (no Docker)
start_production.bat  # All deps, services, dashboards
```

## Services:
| Port | Service | URL |
|------|---------|-----|
| 8001 | FastAPI + Nusantara Guard | http://localhost:8001/docs |
| 8265 | Ray Dashboard (dynamic scale) | http://localhost:8265 |
| Redis | Cache/Feedback | localhost:6379 |

## Scale Commands:
```
python infrastructure/scalable_compute.py --distributed  # Multi-GPU/CPU
ray status  # Dynamic workers
wandb login  # Energy logs (optional)
```

## Ethical Production Logs:
- `logs/bias_reports.json`
- `logs/privacy_reports.json`
- `models/*_card.json`

**Modern Stack:** Ray dynamic, accelerate DDP, Redis, WandB, ethical auto-checks. Continuous: Feedback → Retrain.

**Test Production Ethical Cycle:**
```
curl -X POST http://localhost:8001/v1/chat/completions -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Test PII: email@example.com\"}]}"
# Expect: PII redacted, reasoning ethical
```

KUERA AI: Production - Aligned, Safe, Scalable! 🌾

