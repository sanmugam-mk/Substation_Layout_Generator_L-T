# ─────────────────────────────────────────────────────────────
#  ANCILLARY ROOMS — hardcoded from reference project drawing
#  Original sizes (mm) — NO scaling, expand room_w if needed
# ─────────────────────────────────────────────────────────────
ANCILLARY_GAP = 1500   # gap between DG right edge and rooms
ROOM_DEFS = [
    {
        "name": "UPS &\nBATTERY\nROOM",
        "length": 3500,
        "width": 4000,
        "col": "A",
    },

    {
        "name": "SCADA\nROOM",
        "length": 3500,
        "width": 4000,
        "col": "A",
    },

    {
        "name": "TOILET",
        "length": 3500,
        "width": 1600,
        "col": "A",
    },

    {
        "name": "MAINTENANCE &\nCONTROL\nROOM",
        "length": 3500,
        "width": 4400,
        "col": "A",
    },

    {
        "name": "RMU PANEL\nROOM",
        "length": 4100,
        "width": 4150,
        "col": "B",
    },
]

def place_ancillary_rooms(placed_equipment, room_w, room_h):
    from rules import ROOM_MARGIN

    dg_eqs = [e for e in placed_equipment if e.name == "dg_set"]
    tx_eqs = [e for e in placed_equipment if e.name == "transformer"]

    if not dg_eqs or not tx_eqs:
        return [], room_w

    dg_x_max = max(e.x2 for e in dg_eqs)
    dg_y_max = max(e.y2 for e in dg_eqs)
    tx_y_max = max(e.y2 for e in tx_eqs)
    tx_y_min = min(e.y  for e in tx_eqs)

    # ── Gap: right of DG, between TX top and DG top ───────────
    gap_x     = dg_x_max + ANCILLARY_GAP
    gap_y_bot = tx_y_max + ANCILLARY_GAP   # above TX
    gap_y_top = dg_y_max - ANCILLARY_GAP   # below DG
    avail_h   = gap_y_top - gap_y_bot

    rooms = []

    # UPS + SCADA column
    ups = next(r for r in ROOM_DEFS if "UPS" in r["name"])
    scada = next(r for r in ROOM_DEFS if "SCADA" in r["name"])

    rooms.append({
        "name": ups["name"],
        "x": gap_x,
        "y": gap_y_bot,
        "length": ups["length"],
        "width": ups["width"]
    })

    rooms.append({
        "name": scada["name"],
        "x": gap_x,
        "y": gap_y_bot + ups["width"],
        "length": scada["length"],
        "width": scada["width"]
    })

    # TOILET + MAINTENANCE column
    toilet = next(r for r in ROOM_DEFS if r["name"] == "TOILET")
    maint = next(r for r in ROOM_DEFS if "MAINTENANCE" in r["name"])

    col2_x = gap_x + 3500

    # Toilet touches top wall
    toilet_y = room_h - toilet["width"]

    rooms.append({
        "name": toilet["name"],
        "x": col2_x,
        "y": toilet_y,
        "length": toilet["length"],
        "width": toilet["width"]
    })

    # Maintenance directly below toilet
    maint_y = toilet_y - maint["width"]

    rooms.append({
        "name": maint["name"],
        "x": col2_x,
        "y": maint_y,
        "length": maint["length"],
        "width": maint["width"]
    })

    # RMU ROOM
    # Touch top wall and right wall
    rmu = next(r for r in ROOM_DEFS if "RMU" in r["name"])

    rmu_x = room_w - rmu["length"] - 50
    rmu_y = room_h - rmu["width"]

    rooms.append({
        "name": rmu["name"],
        "x": rmu_x,
        "y": rmu_y,
        "length": rmu["length"],
        "width": rmu["width"]
    })

# PERFORATED ROLLING SHUTTER
# BELOW TRANSFORMER ROW
    SHUTTER_GAP = 1000

    shutter_y = tx_y_min - SHUTTER_GAP

    print("TX bottom =", tx_y_min)
    print("Shutter =", shutter_y)

    # create one shutter for each transformer
    tx_sorted = sorted(tx_eqs, key=lambda e: e.x)

    for tx in tx_sorted:
        rooms.append({
            "name": "PERFORATED\nROLLING SHUTTER",
            "x": tx.x,
            "y": shutter_y,
            "length": tx.length,
            "width": 500,
            "shutter": True,
        })
    max_x = max(
        r["x"] + r["length"]
        for r in rooms
        if not r.get("shutter")
        and "RMU" not in r["name"]
    )
    new_room_w = max_x + ROOM_MARGIN
    new_room_w = ((new_room_w + 499) // 500) * 500
    room_w = max(room_w, new_room_w)

    # Also ensure room_h covers rooms
    '''max_y = max(r["y"] + r["width"] for r in rooms if not r.get("shutter"))
    if max_y + ROOM_MARGIN > room_h:
        room_h_new = ((max_y + ROOM_MARGIN + 499) // 500) * 500
        room_h = max(room_h, room_h_new)'''
    return rooms, room_w

