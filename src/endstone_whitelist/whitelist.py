from endstone import ColorFormat, Player
from endstone.command import CommandSender, Command
from endstone.event import PlayerLoginEvent, event_handler
from endstone.plugin import Plugin
import json
import os

class Whitelist(Plugin):
    api_version = "0.11"
    commands = {
        "wl": {
            "description": "Whitelist command",
            "usages": ["/wl add <player: target>",
                       "/wl remove <player: target>",
                       "/wl list [filter: string]",
                       "/wl help",
                       "/wl on",
                       "/wl off"
                       ],
            "permissions": ["endstone_whitelist.command.wl"],
        }
    }
    permissions = {
        "endstone_whitelist.command.wl": {
            "description": "Allow users to use the /wl command.",
            "default": "op",
        }
    }
    def on_enable(self)->None:
        self.save_default_config()
        self.file_path = os.path.join(self.data_folder, "players.json")
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({"players": []}, f)
        self.load_players()
        self.whitelist_enabled = False
        self.allowed_players = set()
        self.register_events(self)
        self.logger.info(f"{ColorFormat.GREEN}Enabled successfully!")
    def on_disable(self)->None:
        self.logger.info(f"{ColorFormat.RED}Disabled successfully!")
    def set_status(self, status: bool):
        self.whitelist_enabled = status
    def get_status(self) -> bool:
        return self.whitelist_enabled
    def get_allowed_players(self):
        return self.allowed_players
    def load_players(self):
        with open(self.file_path, "r") as f:
            data = json.load(f)
        self.allowed_players = set(data.get("players", []))
    def save_players(self):
        with open(self.file_path, "w") as f:
            json.dump({
                "players": list(self.allowed_players)
            }, f, indent=4)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if command.name != "wl":
            return False
        if len(args) < 1 or len(args) == 0:
            sender.send_message(f"{ColorFormat.YELLOW}Use /wl help")
            return True
        sub_cmd = args[0].lower()
        match sub_cmd:
            case "help":
                sender.send_message(f"{ColorFormat.YELLOW}--- Whitelist Commands ---")
                sender.send_message(f"{ColorFormat.GREEN}/wl on {ColorFormat.WHITE}- Enable whitelist")
                sender.send_message(f"{ColorFormat.GREEN}/wl off {ColorFormat.WHITE}- Disable whitelist")
                sender.send_message(f"{ColorFormat.GREEN}/wl add <player> {ColorFormat.WHITE}- Add player to whitelist")
                sender.send_message(f"{ColorFormat.GREEN}/wl remove <player> {ColorFormat.WHITE}- Remove player from whitelist")
                sender.send_message(f"{ColorFormat.GREEN}/wl list {ColorFormat.WHITE}- Show all whitelisted players")
                sender.send_message(f"{ColorFormat.GREEN}/wl list online {ColorFormat.WHITE}- Show online players")
                sender.send_message(f"{ColorFormat.GREEN}/wl list offline {ColorFormat.WHITE}- Show offline players")
                sender.send_message(f"{ColorFormat.GREEN}/wl help {ColorFormat.WHITE}- Show this help")
                return True
            case "list":
                all_players = sorted(p for p in self.allowed_players)
                if not all_players:
                    sender.send_message(f"{ColorFormat.YELLOW}Whitelist is empty.")
                    return True
                online_names = {p.name for p in self.server.online_players}
                if len(args) >= 2:
                    sub = args[1]
                    if sub == "online":
                        players = [p for p in all_players if p in online_names]
                        title = "Online whitelisted players"
                    elif sub == "offline":
                        players = [p for p in all_players if p not in online_names]
                        title = "Offline whitelisted players"
                    else:
                        sender.send_message(f"{ColorFormat.RED}Invalid filter. Use: online/offline")
                        return True
                else:
                    players = all_players
                    title = "Whitelisted players"
                if not players:
                    sender.send_message(f"{ColorFormat.YELLOW}No players found.")
                    return True
                formatted = [
                    f"{ColorFormat.GREEN}{p}" if p in online_names else f"{ColorFormat.GRAY}{p}"
                    for p in players
                ]
                player_list = ", ".join(formatted)
                sender.send_message(f"{ColorFormat.GREEN}{title} ({len(players)}):")
                sender.send_message(player_list)
                return True
            case "on":
                if self.get_status():
                    if isinstance(sender, Player):
                        sender.send_message(f"{ColorFormat.YELLOW}Whitelist is already enabled!")
                    self.logger.info(f"{ColorFormat.YELLOW}Whitelist is already enabled!")
                    return True
                self.set_status(True)
                self.load_players()
                kicked = 0
                for player in self.server.online_players:
                    if player.name not in self.allowed_players:
                        player.kick(f"{ColorFormat.MATERIAL_REDSTONE}You are not in whitelist!")
                        kicked += 1
                self.logger.info(f"{ColorFormat.GREEN}Enabled whitelist! Kicked {kicked} player(s)")
                if isinstance(sender, Player):
                    sender.send_message(f"{ColorFormat.GREEN}Enabled whitelist! Kicked {kicked} player(s)")
                return True
            case "off":
                if not self.get_status():
                    if isinstance(sender, Player):
                        sender.send_message(f"{ColorFormat.YELLOW}Whitelist is already disabled!")
                    self.logger.info(f"{ColorFormat.YELLOW}Whitelist is already disabled!")
                    return True
                self.set_status(False)
                self.logger.info(f"{ColorFormat.RED}Disabled whitelist!")
                if isinstance(sender, Player):
                    sender.send_message(f"{ColorFormat.RED}Disabled whitelist!")
                return True
            case "add":
                if len(args) < 2:
                    sender.send_message("Missing player")
                    return True
                player = args[1]
                self.allowed_players.add(player)
                self.save_players()
                message = self.config.get("messages", {}).get("player_added")
                message = message.replace("{player}", player)
                sender.send_message(message)
                return True
            case "remove":
                if len(args) < 2:
                    sender.send_message("Missing player")
                    return True
                target = args[1]
                if target in self.allowed_players:
                    self.allowed_players.remove(target)
                    self.save_players()
                    for p in self.server.online_players:
                        if p.name == target:
                            p.kick(f"{ColorFormat.MATERIAL_REDSTONE}You have been removed from whitelist!")
                            break
                    message = self.config.get("messages", {}).get("player_removed") or "Removed {player} from whitelist"
                    message = message.replace("{player}", target)
                    sender.send_message(message)
                else:
                    message = self.config.get("messages", {}).get(
                        "player_not_in_whitelist") or "{player} isn't in whitelist!"
                    message = message.replace("{player}", target)
                    sender.send_message(message)
                return True
        return True

    @event_handler
    def on_player_login(self, event: PlayerLoginEvent):
        if not self.get_status():
            return
        if event.player.name not in self.allowed_players:
            event.kick_message = f"{ColorFormat.YELLOW}You are not in whitelist!"
            event.is_cancelled = True