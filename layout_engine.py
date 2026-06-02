# ─────────────────────────────────────────────
#  LAYOUT ENGINE
#  Calculates room dimensions and returns
#  placed equipment as a list of rectangles.
# ─────────────────────────────────────────────

from rules import (
    TRANSFORMER_SPACING, TRANSFORMER_WALL_CLEARANCE,
    DG_SPACING, LT_PANEL_CLEARANCE, HT_PANEL_CLEARANCE,
    APFC_SIDE_CLEARANCE, PANEL_WALL_CLEARANCE, ROOM_MARGIN,
)


class Equipment:
    """Represents one placed piece of equipment in the layout."""
    def __init__(self, name, x, y, length, width, label=""):
        self.name   = name
        self.x      = x        # bottom-left X (mm)
        self.y      = y        # bottom-left Y (mm)
        self.length = length   # along X axis
        self.width  = width    # along Y axis
        self.label  = label or name

    @property
    def x2(self): return self.x + self.length
    @property
    def y2(self): return self.y + self.width

    def __repr__(self):
        return f"{self.name}  ({self.x},{self.y}) → ({self.x2},{self.y2})"


def calculate_layout(data: dict):
    """
    Main layout function.
    Returns:
        placed  : list[Equipment]
        room_w  : total room width  (X dimension) in mm
        room_h  : total room height (Y dimension) in mm
    """
    kv       = data.get("supply_kv", 11)
    tx_space = TRANSFORMER_SPACING.get(kv, 1500)

    placed = []
    cursor_x = ROOM_MARGIN   # current X pen
    cursor_y = ROOM_MARGIN   # current Y pen

    # ── Track bounding box ───────────────────────────────
    max_x = 0
    max_y = 0

    def place(name, length, width, x, y, label=""):
        eq = Equipment(name, x, y, length, width, label)
        placed.append(eq)
        return eq

    # ══════════════════════════════════════════════════════
    #  ZONE A  —  TOP ROW  (along top wall, back to wall)
    #  HT panel, RMU panel placed along top wall
    # ══════════════════════════════════════════════════════
    zone_a_y = ROOM_MARGIN                      # panels sit at bottom of their zone
    zone_a_height = 0                           # will be updated

    if "ht_panel" in data:
        ht = data["ht_panel"]
        eq = place("ht_panel", ht["length"], ht["width"],
                   cursor_x, zone_a_y, f"HT Panel\n{ht['config']}")
        zone_a_height = max(zone_a_height, ht["width"])
        cursor_x = eq.x2 + PANEL_WALL_CLEARANCE

    if "rmu_panel" in data:
        rmu = data["rmu_panel"]
        eq = place("rmu_panel", rmu["length"], rmu["width"],
                   cursor_x, zone_a_y, f"RMU Panel\n{rmu['config']}")
        zone_a_height = max(zone_a_height, rmu["width"])
        cursor_x = eq.x2 + PANEL_WALL_CLEARANCE

    # After top panels, add front clearance
    zone_a_top = zone_a_y + zone_a_height + HT_PANEL_CLEARANCE["front"]

    # ══════════════════════════════════════════════════════
    #  ZONE B  —  TRANSFORMER ROW
    #  Transformers placed side by side with spacing rules
    # ══════════════════════════════════════════════════════
    tx_start_x = ROOM_MARGIN
    tx_y       = zone_a_top          # transformers start below HT panel front clearance
    tx_max_y   = tx_y

    if "transformers" in data:
        tx = data["transformers"]
        n  = tx["count"]
        tl = tx["length"]
        tw = tx["width"]
        for i in range(n):
            x = tx_start_x + i * (tl + tx_space)
            eq = place("transformer", tl, tw, x, tx_y, f"TX-{i+1}\n{kv}kV")
            tx_max_y = max(tx_max_y, eq.y2)

        # Transformer NGR — placed right of last transformer, wall-mounted
        if "transformer_ngr" in data:
            ngr = data["transformer_ngr"]
            last_tx_x2 = tx_start_x + n * tl + (n - 1) * tx_space
            place("transformer_ngr", ngr["length"], ngr["width"],
                  last_tx_x2 + TRANSFORMER_WALL_CLEARANCE, tx_y, "TX NGR")

        # RTCC panel — near transformer, wall mounted (placed above tx row for now)
        if "rtcc_panel" in data:
            rtcc = data["rtcc_panel"]
            place("rtcc_panel", rtcc["length"], rtcc["width"],
                  tx_start_x, zone_a_y, "RTCC Panel")

    zone_b_top = tx_max_y + TRANSFORMER_WALL_CLEARANCE   # clearance below transformers

    # ══════════════════════════════════════════════════════
    #  ZONE C  —  LT PANEL ROW (opposite transformers)
    #  Main LT → DG Sync → APFC  side by side
    # ══════════════════════════════════════════════════════
    panel_y   = zone_b_top
    panel_x   = ROOM_MARGIN
    panel_max_y = panel_y

    for key, label in [
        ("main_lt_panel",  "Main LT Panel"),
        ("dg_sync_panel",  "DG Sync Panel"),
        ("apfc_panel",     "APFC Panel"),
        ("aux_panel",      "Aux Power Panel"),
        ("substation_panel", "Substation Panel"),
    ]:
        if key in data:
            d  = data[key]
            eq = place(key, d["length"], d["width"], panel_x, panel_y, label)
            panel_max_y = max(panel_max_y, eq.y2)
            # Clearance between LT panels
            panel_x = eq.x2 + APFC_SIDE_CLEARANCE

    zone_c_top = panel_max_y + LT_PANEL_CLEARANCE["front_to_front"]   # aisle in front of panels

    # ══════════════════════════════════════════════════════
    #  ZONE D  —  DG SET ROW
    # ══════════════════════════════════════════════════════
    dg_y   = zone_c_top
    dg_x   = ROOM_MARGIN
    dg_max_y = dg_y

    if "dg_sets" in data:
        dg = data["dg_sets"]
        n  = dg["count"]
        dl = dg["length"]
        dw = dg["width"]
        for i in range(n):
            x  = dg_x + i * (dl + DG_SPACING["side_by_side"])
            eq = place("dg_set", dl, dw, x, dg_y, f"DG-{i+1}")
            dg_max_y = max(dg_max_y, eq.y2)

        # DG NGR near DG sets
        if "dg_ngr" in data:
            ngr = data["dg_ngr"]
            last_dg_x2 = dg_x + n * dl + (n - 1) * DG_SPACING["side_by_side"]
            place("dg_ngr", ngr["length"], ngr["width"],
                  last_dg_x2 + 1000, dg_y, "DG NGR")

        # DG Day Tank near DG sets
        if "dg_day_tank" in data:
            dt = data["dg_day_tank"]
            place("dg_day_tank", dt["length"], dt["width"],
                  dg_x, dg_max_y + DG_SPACING["rear"], "DG Day Tank")
            dg_max_y += DG_SPACING["rear"] + dt["width"]

    zone_d_top = dg_max_y + DG_SPACING["front"]   # front clearance for DG

    # ══════════════════════════════════════════════════════
    #  CALCULATE ROOM SIZE
    # ══════════════════════════════════════════════════════
    all_x2 = [eq.x2 for eq in placed] + [ROOM_MARGIN]
    all_y2 = [eq.y2 for eq in placed] + [ROOM_MARGIN]

    content_max_x = max(all_x2)
    content_max_y = max(all_y2)

    room_w = content_max_x + ROOM_MARGIN
    room_h = content_max_y + ROOM_MARGIN

    # Round up to nearest 500 mm for clean room dimensions
    room_w = ((room_w + 499) // 500) * 500
    room_h = ((room_h + 499) // 500) * 500

    return placed, room_w, room_h
