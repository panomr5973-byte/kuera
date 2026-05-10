#!/usr/bin/env python3
"""
KUERA Gateway Server v1.0
WebSocket + HTTP health-check gateway untuk KUERA Desktop/Wallpaper
Jalankan: python gateway_server.py
Port: 18789 (WS + HTTP same port)
"""

import asyncio
import json
import logging
import sys
from datetime import datetime

import aiohttp
from aiohttp import web

# ===== KONFIGURASI =====
PORT = 18789
GATEWAY_TOKEN = "5e79175f87a126aced23edaebe38938cc018916e958029a0"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("KUERA-Gateway")

# ===== STATE =====
connected_clients = set()
gateway_start_time = datetime.now()
message_history = []
MAX_HISTORY = 50


# ===== ROOT HANDLER (auto-detect WS vs HTTP) =====
async def root_handler(request):
    """Handle both HTTP and WebSocket on root path '/' """
    if request.headers.get("Upgrade", "").lower() == "websocket":
        return await websocket_handler(request)
    return await health_check(request)


# ===== HTTP HANDLERS =====
async def health_check(request):
    """HTTP GET / — Health check endpoint"""
    uptime = datetime.now() - gateway_start_time
    status = {
        "status": "online",
        "service": "KUERA Gateway",
        "version": "1.0",
        "uptime": str(uptime).split(".")[0],
        "clients_connected": len(connected_clients),
        "timestamp": datetime.now().isoformat()
    }
    return web.json_response(status, headers={
        "Access-Control-Allow-Origin": "*"
    })


async def cors_preflight(request):
    """Handle CORS preflight requests"""
    return web.Response(
        status=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


# ===== WEBSOCKET HANDLER =====
async def websocket_handler(request):
    """WebSocket /?token=..."""
    # Validasi token dari query string
    token = request.query.get("token", "")
    client_ip = request.remote or "unknown"

    if token != GATEWAY_TOKEN:
        logger.warning(f"[WS] Invalid token from {client_ip} — rejecting")
        raise web.HTTPForbidden(text="Invalid token")

    ws = web.WebSocketResponse(
        heartbeat=20.0,
        autoping=True,
    )
    await ws.prepare(request)

    connected_clients.add(ws)
    logger.info(f"[WS] Client {client_ip} connected. Total: {len(connected_clients)}")

    # Kirim welcome
    welcome = {
        "type": "system",
        "text": "🟢 KUERA Gateway terhubung. Selamat datang!",
        "timestamp": datetime.now().isoformat()
    }
    try:
        await ws.send_json(welcome)
    except Exception as e:
        logger.warning(f"[WS] Failed to send welcome: {e}")

    # Kirim history
    for msg in message_history[-10:]:
        try:
            await ws.send_json(msg)
        except:
            pass

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    msg_type = data.get("type", "unknown")
                    text = data.get("text", "")
                    sender = data.get("from", "anonymous")

                    logger.info(f"[WS] Received [{msg_type}] from {sender}: {text[:80]}")

                    # Simpan ke history
                    broadcast_msg = {
                        "type": msg_type,
                        "text": text,
                        "from": sender,
                        "timestamp": datetime.now().isoformat()
                    }
                    message_history.append(broadcast_msg)
                    if len(message_history) > MAX_HISTORY:
                        message_history.pop(0)

                    # Handle berbagai tipe pesan
                    if msg_type == "chat":
                        reply = {
                            "type": "ai",
                            "text": f"KUERA menerima: \"{text}\". Pesan sedang diproses...",
                            "timestamp": datetime.now().isoformat()
                        }
                        message_history.append(reply)
                        await broadcast(reply)

                    elif msg_type == "voice":
                        reply = {
                            "type": "ai",
                            "text": f"🎤 Voice command diterima: \"{text}\"",
                            "timestamp": datetime.now().isoformat()
                        }
                        await broadcast(reply)

                    elif msg_type == "heartbeat":
                        await ws.send_json({
                            "type": "heartbeat",
                            "timestamp": datetime.now().isoformat()
                        })

                except json.JSONDecodeError:
                    logger.warning(f"[WS] Invalid JSON from {client_ip}")
                except Exception as e:
                    logger.error(f"[WS] Error handling message: {e}")

            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"[WS] Connection error: {ws.exception()}")

    except Exception as e:
        logger.error(f"[WS] Unexpected error: {e}")
    finally:
        connected_clients.discard(ws)
        logger.info(f"[WS] Client {client_ip} disconnected. Total: {len(connected_clients)}")

    return ws


async def broadcast(message):
    """Kirim pesan ke semua client yang terhubung."""
    dead = []
    for client in connected_clients:
        try:
            await client.send_json(message)
        except Exception:
            dead.append(client)
    for d in dead:
        connected_clients.discard(d)


# ===== APP SETUP =====
def create_app():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_options("/", cors_preflight)
    app.router.add_get("/ws", websocket_handler)  # Alternative path for WS
    # Also allow WS on root with token query
    app.router.add_get("/", websocket_handler, name="ws_root")
    return app


async def main():
    logger.info("=" * 50)
    logger.info("  KUERA Gateway Server v1.0")
    logger.info("=" * 50)

    app = web.Application()
    app.router.add_options("/", cors_preflight)
    # Single handler untuk "/" — deteksi otomatis WS vs HTTP
    app.router.add_get("/", root_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)

    try:
        await site.start()
        logger.info(f"[HTTP] Health check : http://0.0.0.0:{PORT}/")
        logger.info(f"[WS]   WebSocket    : ws://0.0.0.0:{PORT}/?token=...")
        logger.info(f"[INFO] Tekan Ctrl+C untuk stop\n")

        # Run forever
        while True:
            await asyncio.sleep(3600)
    except OSError as e:
        logger.error(f"[ERROR] Port {PORT} sudah dipakai: {e}")
        logger.info("[INFO] Coba tutup aplikasi lain yang pakai port 18789, lalu jalankan ulang.")
        sys.exit(1)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n[INFO] Gateway server dimatikan.")
        sys.exit(0)
