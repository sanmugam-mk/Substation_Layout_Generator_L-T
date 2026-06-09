# ─────────────────────────────────────────────────────────────
#  ANCILLARY ROOMS — hardcoded from reference project drawing
#  Original sizes (mm) — NO scaling, expand room_w if needed
# ─────────────────────────────────────────────────────────────
ANCILLARY_GAP = 1500   # gap between DG right edge and rooms

ROOM_DEFS = [
    {"name": "UPS &\nBATTERY\nROOM",        "length": 3500, "width": 4000, "col": "A"},
    {"name": "SCADA\nROOM",                  "length": 3500, "width": 4000, "col": "A"},
    {"name": "TOILET",                       "length": 3500, "width": 1600, "col": "A"},
    {"name": "MAINTENANCE &\nCONTROL\nROOM", "length": 3500, "width": 4400, "col": "A"},
    {"name": "RMU PANEL\nROOM",              "length": 4100, "width": 4150, "col": "B"},
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

    gap_x = dg_x_max + ANCILLARY_GAP

    rooms = []

    # ── Col A: all 4 rooms stacked, pushed to TOP wall ────────
    col_a_x = gap_x

    ups    = next(r for r in ROOM_DEFS if "UPS"         in r["name"])
    scada  = next(r for r in ROOM_DEFS if "SCADA"       in r["name"])
    toilet = next(r for r in ROOM_DEFS if "TOILET"      in r["name"])
    maint  = next(r for r in ROOM_DEFS if "MAINTENANCE" in r["name"])
    rmu    = next(r for r in ROOM_DEFS if "RMU"         in r["name"])

    # Stack order top → bottom: TOILET, MAINTENANCE, SCADA, UPS
    col_a_order = [toilet, maint, scada, ups]
    cy = room_h  # start from top wall, stack downward

    for rd in col_a_order:
        cy -= rd["width"]
        rooms.append({
            "name":   rd["name"],
            "x":      col_a_x,
            "y":      cy,
            "length": rd["length"],
            "width":  rd["width"],
        })

# ── RMU Panel — flush to RIGHT wall, top wall ─────────────
    rmu_y        = room_h - rmu["width"]          # flush to top wall
    rmu_actual_x = room_w - rmu["length"]         # flush to right wall

    rooms.append({
        "name":   rmu["name"],
        "x":      rmu_actual_x,
        "y":      rmu_y,
        "length": rmu["length"],
        "width":  rmu["width"],
    })

    # ── UPS & Battery — directly below RMU, same X ────────────
    ups_y = rmu_y - ups["width"]
    for r in rooms:
        if "UPS" in r["name"]:
            r["x"]      = rmu_actual_x
            r["y"]      = ups_y
            r["length"] = rmu["length"]
            break

# ── Shift Col A to sit LEFT of RMU column ─────────────────
    # RMU is at room_w - 4100, Col A (3500 wide) sits left of it
    col_a_new_x = rmu_actual_x - 3500

    for r in rooms:
        if "UPS" not in r["name"] and "RMU" not in r["name"] and not r.get("shutter"):
            r["x"]      = col_a_new_x
            r["length"] = 3500   # enforce consistent width

    # ── Expand room_w so both columns flush to right wall ──────
    # room_w must equal rmu_actual_x + rmu length (already set)
    # but rmu_actual_x was set from OLD room_w — recalculate
    new_rmu_x = room_w - rmu["length"]
    for r in rooms:
        if "RMU" in r["name"]:
            r["x"] = new_rmu_x
        if "UPS" in r["name"]:
            r["x"] = new_rmu_x
            r["length"] = rmu["length"]

    col_a_new_x = new_rmu_x - 3500
    for r in rooms:
        if "UPS" not in r["name"] and "RMU" not in r["name"] and not r.get("shutter"):
            r["x"] = col_a_new_x
    # ── Perforated Rolling Shutter — below each TX ────────────
    SHUTTER_GAP = 200
    shutter_y   = tx_y_min - SHUTTER_GAP - 500   # below TX bottom

    tx_sorted = sorted(tx_eqs, key=lambda e: e.x)
    for tx in tx_sorted:
        rooms.append({
            "name":    "PERFORATED\nROLLING SHUTTER",
            "x":       tx.x,
            "y":       shutter_y,
            "length":  tx.length,
            "width":   500,
            "shutter": True,
        })

    # ── Expand room_w if needed ───────────────────────────────
    max_x = max(r["x"] + r["length"] for r in rooms if not r.get("shutter"))
    new_room_w = max_x + ROOM_MARGIN
    new_room_w = ((new_room_w + 499) // 500) * 500
    room_w = new_room_w

    # Final pass — re-anchor everything flush to right wall
    final_rmu_x = room_w - rmu["length"]
    final_col_a_x = final_rmu_x - 3500
    for r in rooms:
        if r.get("shutter"):
            continue
        if "RMU" in r["name"]:
            r["x"] = final_rmu_x
        elif "UPS" in r["name"]:
            r["x"] = final_rmu_x
            r["length"] = rmu["length"]
        else:
            r["x"] = final_col_a_x
            r["length"] = 3500

    return rooms, room_w