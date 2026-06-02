# Manually hardcoded the rules from excel given
# Transformer-to-Transformer spacing based on kV level
TRANSFORMER_SPACING = {
    11: 1500,
    22: 2000,
    33: 2500,
}

# Transformer to side wall
TRANSFORMER_WALL_CLEARANCE = 1500

# DG Set clearances
DG_SPACING = {
    "side_by_side": 2000,   # DG to DG side by side
    "rear":         2000,   # DG rear side
    "front":        3000,   # DG front side
}

# LT Panel clearances
LT_PANEL_CLEARANCE = {
    "front_to_front": 2000,
    "front_to_back":  1000,
    "wall_to_back":   1200,
}

# HT Panel clearances
HT_PANEL_CLEARANCE = {
    "front": 2000,
    "back":  1200,
}

# APFC panel side clearance
APFC_SIDE_CLEARANCE = 750

# General wall clearance for panels
PANEL_WALL_CLEARANCE = 1000

#  EQUIPMENT ARRANGEMENT RULES
# Describes how Equipment-1 faces Equipment-2

ARRANGEMENT_RULES = [
    # (equip1,           equip2,                  arrangement,       clearance_mm)
    ("transformer",      "main_lt_panel",          "opposite",        None),
    ("dg_set",           "dg_sync_panel",          "opposite",        None),
    ("main_lt_panel",    "dg_sync_panel",          "opposite",        2000),
    ("main_lt_panel",    "apfc_panel",             "opposite",        2000),
    ("apfc_panel",       "apfc_panel",             "side_by_side",    750),
    ("panel",            "panel",                  "side_by_side",    750),
    ("rtcc_panel",       "transformer",            "near",            None),   # wall/floor mounted
    ("ngr_panel",        "transformer",            "near",            None),   # near transformer & DG
]

# Default room margin around all equipment (outer boundary padding)
ROOM_MARGIN = 1500  # mm
