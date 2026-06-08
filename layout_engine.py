#  LAYOUT ENGINE
#  Calculates room dimensions and returns
#  placed equipment as a list of rectangles.
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

    #Track bounding box 
    max_x = 0
    max_y = 0

    def place(name, length, width, x, y, label=""):
        eq = Equipment(name, x, y, length, width, label)
        placed.append(eq)
        return eq

    #  NEW LAYOUT ORDER (bottom → top):
    #  ZONE A: TRANSFORMERS  (bottom, near entrance)
    #  ZONE B: HT / RMU PANEL
    #  ZONE C: LT PANELS
    #  ZONE D: DG SETS       (top)

    # ZONE A — TRANSFORMERS (bottom row, near entrance) 
    tx_start_x = ROOM_MARGIN
    tx_y       = ROOM_MARGIN
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

        if "transformer_ngr" in data:
            ngr = data["transformer_ngr"]
            last_tx_x2 = tx_start_x + n * tl + (n - 1) * tx_space
            place("transformer_ngr", ngr["length"], ngr["width"],
                  last_tx_x2 + TRANSFORMER_WALL_CLEARANCE, tx_y, "TX NGR")

        if "rtcc_panel" in data:
            rtcc = data["rtcc_panel"]
            place("rtcc_panel", rtcc["length"], rtcc["width"],
                  tx_start_x, tx_y, "RTCC Panel")

    zone_a_top = tx_max_y + HT_PANEL_CLEARANCE["front"]

    #ZONE B — HT / RMU PANEL ─
    cursor_x     = ROOM_MARGIN
    zone_b_y     = zone_a_top
    zone_b_height = 0

    if "ht_panel" in data:
        ht = data["ht_panel"]
        eq = place("ht_panel", ht["length"], ht["width"],
                   cursor_x, zone_b_y, f"HT Panel\n{ht['config']}")
        zone_b_height = max(zone_b_height, ht["width"])
        cursor_x = eq.x2 + PANEL_WALL_CLEARANCE

    if "rmu_panel" in data:
        rmu = data["rmu_panel"]
        eq = place("rmu_panel", rmu["length"], rmu["width"],
                   cursor_x, zone_b_y, f"RMU Panel\n{rmu['config']}")
        zone_b_height = max(zone_b_height, rmu["width"])
        cursor_x = eq.x2 + PANEL_WALL_CLEARANCE

    zone_b_top = zone_b_y + zone_b_height + HT_PANEL_CLEARANCE["back"]

    # ZONE C — LT PANELS 
    panel_y     = zone_b_top
    panel_x     = ROOM_MARGIN
    panel_max_y = panel_y

    for key, label in [
        ("main_lt_panel",    "Main LT Panel"),
        ("dg_sync_panel",    "DG Sync Panel"),
        ("apfc_panel",       "APFC Panel"),
        ("aux_panel",        "Aux Power Panel"),
        ("substation_panel", "Substation Panel"),
    ]:
        if key in data:
            d  = data[key]
            eq = place(key, d["length"], d["width"], panel_x, panel_y, label)
            panel_max_y = max(panel_max_y, eq.y2)
            panel_x = eq.x2 + APFC_SIDE_CLEARANCE

    zone_c_top = panel_max_y + LT_PANEL_CLEARANCE["front_to_front"]

    # ZONE D — DG SETS (top row) 
    dg_y     = zone_c_top
    dg_x     = ROOM_MARGIN
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

        if "dg_ngr" in data:
            ngr = data["dg_ngr"]
            last_dg_x2 = dg_x + n * dl + (n - 1) * DG_SPACING["side_by_side"]
            place("dg_ngr", ngr["length"], ngr["width"],
                  last_dg_x2 + 1000, dg_y, "DG NGR")

        if "dg_day_tank" in data:
            dt = data["dg_day_tank"]
            place("dg_day_tank", dt["length"], dt["width"],
                  dg_x, dg_max_y + DG_SPACING["rear"], "DG Day Tank")
            dg_max_y += DG_SPACING["rear"] + dt["width"]

    zone_d_top = dg_max_y + DG_SPACING["front"]

    #  CALCULATE ROOM SIZE
    # Zone bounding boxes
    def zone_x_max(names):
        eqs = [e for e in placed if e.name in names]
        return max((e.x2 for e in eqs), default=0)

    def zone_y_max(names):
        eqs = [e for e in placed if e.name in names]
        return max((e.y2 for e in eqs), default=0)

    all_x2 = [eq.x2 for eq in placed]
    all_y2 = [eq.y2 for eq in placed]

    content_max_x = max(all_x2)
    content_max_y = max(all_y2)

    # HT/RMU zone — typically narrower, creates L-shape step on right side
    ht_x_max = zone_x_max({"ht_panel", "rmu_panel"})
    ht_y_max = zone_y_max({"ht_panel", "rmu_panel"})

    room_w = content_max_x + ROOM_MARGIN
    room_h = content_max_y + ROOM_MARGIN

    # Round up to nearest 500 mm
    room_w = ((room_w + 499) // 500) * 500
    room_h = ((room_h + 499) // 500) * 500

    #Staircase shape: bottom-right AND top-right corner cuts 

    step_x, step_y   = None, None   # bottom-right cut
    step_x2, step_y2 = None, None   # top-right cut

    # Bottom-right cut (HT zone narrower than TX zone) 
    if ht_x_max > 0:
        cand_step_x = ((ht_x_max + ROOM_MARGIN + 499) // 500) * 500
        if cand_step_x < room_w - 1000:
            wide_eqs = [e for e in placed if e.x2 > cand_step_x]
            if wide_eqs:
                lowest_wide_y = min(e.y for e in wide_eqs)
                cand_step_y   = lowest_wide_y - ROOM_MARGIN
                cand_step_y   = max(cand_step_y, ht_y_max + ROOM_MARGIN)
                cand_step_y   = ((cand_step_y + 499) // 500) * 500
                if room_h * 0.1 < cand_step_y < room_h * 0.9:
                    step_x = cand_step_x
                    step_y = cand_step_y

    # Top-right cut 
    # For each horizontal band, find the max x2. If upper bands are narrower
    # than the full room width, cut the top-right corner.
    # Strategy: compare DG zone x_max vs TX zone x_max.
    dg_eqs  = [e for e in placed if e.name == "dg_set"]
    tx_eqs2 = [e for e in placed if e.name == "transformer"]

    #Top-right cut: tighten room_w to actual equipment extent 
    dg_eqs  = [e for e in placed if e.name == "dg_set"]
    tx_eqs2 = [e for e in placed if e.name == "transformer"]
    all_upper = dg_eqs + tx_eqs2

    if all_upper:
        # Widest equipment among TX and DG
        actual_x_max = max(e.x2 for e in all_upper)
        tight_room_w = actual_x_max + ROOM_MARGIN  # exact, no rounding

        # Always tighten room_w if equipment doesn't fill it
        if tight_room_w < room_w:
            room_w = int(tight_room_w)

        # Top-right step: if DG zone is narrower than TX zone
        if dg_eqs and tx_eqs2:
            dg_x_max = max(e.x2 for e in dg_eqs)
            tx_x_max = max(e.x2 for e in tx_eqs2)

            if dg_x_max < tx_x_max:
                # DG is narrower → cut top-right at DG level
                cand_step_x2 = int(dg_x_max + ROOM_MARGIN)
                dg_y_min     = min(e.y for e in dg_eqs)
                cand_step_y2 = dg_y_min - ROOM_MARGIN
                cand_step_y2 = ((cand_step_y2 + 499) // 500) * 500
                if room_h * 0.3 < cand_step_y2 < room_h * 0.95:
                    step_x2 = cand_step_x2
                    step_y2 = cand_step_y2

    # Place ancillary rooms in the right-side gap 
    from ancillary_rooms import place_ancillary_rooms
    ancillary_rooms, room_w = place_ancillary_rooms(placed, room_w, room_h)

    return placed, room_w, room_h, ancillary_rooms