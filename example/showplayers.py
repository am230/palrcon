import asyncio
from typing import Dict, TypedDict

from palrcon.executor import Executor
from palrcon.impl import PalRcon


class Player(TypedDict):
    name: str
    playeruid: int
    steamid: int


def parse_players(data: str) -> Dict[int, Player]:
    """
    name,playeruid,steamid
    namename,0123456789,01234567890123456
    """
    lines = data.splitlines()
    players = {}
    keys = lines[0].split(",")
    if keys != ["name", "playeruid", "steamid"]:
        raise Exception("Unexpected keys")
    for line in lines:
        name, playeruid, steamid = line.split(",")
        if not playeruid.isdigit():
            continue
        if not steamid.isdigit():
            continue
        players[int(playeruid)] = {
            "name": name,
            "playeruid": int(playeruid),
            "steamid": int(steamid),
        }
    return players


"""
/Shutdown {Seconds} {MessageText}	Seconds で指定した秒数が経過後にサーバーをシャットダウンします。
MessageText に記入した内容がサーバー参加者に通知されます。
/DoExit	サーバーを強制終了します。
/Broadcast {MessageText}	サーバー参加者すべてに対してメッセージを送信します。
/KickPlayer {SteamID}	指定したSteamIDを持つプレイヤーをサーバーからキックします。
/BanPlayer {SteamID}	指定したSteamIDを持つプレイヤーをサーバーからBANします。
/TeleportToPlayer {SteamID}	指定したSteamIDを持つプレイヤーの現在地に対してテレポートします。
/TeleportToMe {SteamID}	指定したSteamIDを持つプレイヤーをコマンド実行者の座標へテレポートします。
/ShowPlayers	現在サーバーに参加しているすべてのプレイヤー情報を表示します。
/Info	サーバーの情報を表示します。
/Save	セーブを行います。
"""


class PalWorld:
    def __init__(self, executor: Executor):
        self._executor = executor

    async def _execute(self, *args):
        return await self._executor.execute(" ".join(args))

    async def shutdown(self, seconds: int, message: str) -> None:
        await self._execute("Shutdown", seconds, message)

    async def do_exit(self) -> None:
        await self._execute("DoExit")

    async def broadcast(self, message: str) -> None:
        await self._execute("Broadcast", message)

    async def kick_player(self, steamid: int) -> None:
        await self._execute("KickPlayer", steamid)

    async def ban_player(self, steamid: int) -> None:
        await self._execute("BanPlayer", steamid)

    async def teleport_to_player(self, steamid: int) -> None:
        await self._execute("TeleportToPlayer", steamid)

    async def teleport_to_me(self, steamid: int) -> None:
        await self._execute("TeleportToMe", steamid)

    async def fetch_players(self) -> Dict[int, Player]:
        return parse_players(await self._executor.execute("ShowPlayers"))

    async def fetch_info(self) -> str:
        return await self._executor.execute("Info")

    async def save(self) -> None:
        await self._executor.execute("Save")


async def main():
    rcon = await PalRcon.connect("127.0.0.1", password="pomepome")
    pal = PalWorld(rcon)
    print(await pal.fetch_info())
    print(await pal.fetch_players())
    await pal.broadcast("Hello, World!")


if __name__ == "__main__":
    asyncio.run(main())
