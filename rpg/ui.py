"""How the player gives commands, so hints in the text can point the right way.

In the terminal the player types; the hint names the command ('trade'). The web page has no
command box, only the action menus, so there the hint names the menu entry instead.
rpg/web.py sets `web` to True; nothing else changes it.
"""

web = False

# where each hinted command lives in the web page's action menus (see actions.py)
MENU = {
    "trade": "People › See wares",
    "travel": "Rest & Time › Travel to…",
    "buy rations": "Rest & Time › Buy rations",
    "improve": "Info › Improve…",
    "hone": "Craft › Hone a technique…",
    "read": "Items › Read / study…",
    "save": "Game › Save…",
    "saves": "the Saves window",
}


def ref(cmd, key=None):
    """'trade' in the terminal; People › See wares on the web."""
    return MENU[key or cmd] if web else f"'{cmd}'"


def how(cmd, key=None):
    """The start of a 'do this to ...' hint: Type 'trade' / Use People › See wares."""
    return f"Use {MENU[key or cmd]}" if web else f"Type '{cmd}'"
