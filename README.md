# Whitelist
- **A whitelist plugin for [Endstone](https://github.com/EndstoneMC/endstone)**
---

# Configuration (config.toml)
```aiignore
[messages]
player_added = "§aAdded {player} to whitelist"
player_removed = "§cRemoved {player} from whitelist"
player_not_in_whitelist = "§e{player} isn't in whitelist"

whitelist_enabled = "§aWhitelist enabled! Kicked {kicked} player(s)"
whitelist_disabled = "§cWhitelist disabled!"

already_enabled = "§eWhitelist is already enabled!"
already_disabled = "§eWhitelist is already disabled!"

missing_player = "§cMissing player name"

not_whitelisted = "§cYou are not in whitelist!"
removed_kick = "§cYou have been removed from whitelist!"
```


## Commands
| Command | Description                             |
|---------|-----------------------------------------|
| `/wl on` | Enable whitelist                        |
| `/wl off` | Disable whitelist                       |
| `/wl add <player>` | Add player to whitelist                 |
| `/wl remove <player>` | Remove player from whitelist            |
| `/wl list` | Show all whitelisted players            |
| `/wl list online` | Show online whitelisted players         |
| `/wl list offline` | Show whitelisted offline players        |
| `/wl help` | Show a list of Whitelist plugin command |                  |
## Permission
- `endstone_whitelist.command.wl` — Permission for all Whitelist plugin commands