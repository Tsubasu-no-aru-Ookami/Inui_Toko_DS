from functools import partial
import websockets
import asyncio
import json
import logging
import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class VoiceTracker:
    def __init__(self):
        self.active_users = {}
        self.token = "NDEzNzkwODU4MDMxMTM2Nzc5.Gurys9.5lZDm4q90PlYe6l95JsglULxmMYtSaFCCUwf0I"  # ЗАМЕНИТЕ
        self.user_id = "413790858031136779"      # ЗАМЕНИТЕ
        self.ws = None
        self.session = None
        self.ws_server = None

    async def initialize(self):
        """Инициализация асинхронных компонентов"""
        self.session = aiohttp.ClientSession()
        self.ws_server = await websockets.serve(
            self.handle_ws_client,
            "localhost",
            8765
        )
        logger.info("WebSocket server started")

    async def authenticate(self, ws):
        """Аутентификация в Discord"""
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": 3276543,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                }
            }
        }
        await ws.send(json.dumps(payload))

    async def handle_ws_client(self, websocket):
        """Обработчик соединений Electron"""
        try:
            while True:
                await websocket.send(json.dumps({
                    "users": list(self.active_users.values())
                }))
                await asyncio.sleep(1)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")

    async def connect_to_discord(self):
        """Подключение к Discord Gateway"""
        while True:
            try:
                async with websockets.connect(
                    "wss://gateway.discord.gg/?v=9&encoding=json",
                    max_size=None
                ) as self.ws:
                    await self.authenticate(self.ws)
                    
                    # Heartbeat
                    async def send_heartbeat(interval):
                        while True:
                            await asyncio.sleep(interval)
                            await self.ws.send(json.dumps({"op": 1, "d": None}))

                    # Обработка сообщений
                    async for message in self.ws:
                        data = json.loads(message)
                        if data.get('t') == 'VOICE_STATE_UPDATE':
                            await self.process_voice_state(data['d'])

            except Exception as e:
                logger.error(f"Connection error: {e}")
                await asyncio.sleep(5)

    async def process_voice_state(self, state):
        """Обработка голосового статуса"""
        user_id = str(state.get('user_id'))
        if user_id == self.user_id:
            if state.get('channel_id'):
                await self.update_channel_users(
                    state['guild_id'],
                    state['channel_id']
                )
            else:
                self.active_users = {}

    async def update_channel_users(self, guild_id, channel_id):
        """Обновление списка пользователей канала"""
        try:
            async with self.session.get(
                f"https://discord.com/api/v9/guilds/{guild_id}/voice-states",
                headers={"Authorization": self.token}
            ) as resp:
                if resp.status == 200:
                    states = await resp.json()
                    self.active_users = {
                        str(s['user']['id']): {
                            "id": str(s['user']['id']),
                            "name": s['user'].get('username', 'Unknown'),
                            "speaking": s.get('speaking', False)
                        }
                        for s in states
                        if s.get('channel_id') == channel_id
                    }
        except Exception as e:
            logger.error(f"Failed to update users: {e}")

    async def cleanup(self):
        """Очистка ресурсов"""
        if self.session:
            await self.session.close()
        if self.ws_server:
            self.ws_server.close()
            await self.ws_server.wait_closed()

async def main():
    tracker = VoiceTracker()
    await tracker.initialize()
    try:
        await tracker.connect_to_discord()
    finally:
        await tracker.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")