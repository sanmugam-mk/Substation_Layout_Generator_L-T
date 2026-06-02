#  CAD GENERATOR  —  Full DXF output

import ezdxf
from ezdxf import colors
from blocks import (
    define_transformer_block, define_ht_panel_block, define_rmu_panel_block,
    define_lt_panel_block, define_dg_set_block, define_apfc_block,
    define_generic_panel_block, define_ngr_block,
    define_dg_day_tank_block, define_rtcc_block,
)
LAYERS = {
    "ROOM_BOUNDARY":   (colors.WHITE,   35),
    "TRANSFORMER":     (colors.YELLOW,  25),
    "HT_PANEL":        (2,              25),   # red
    "LT_PANEL":        (colors.CYAN,    20),
    "DG_SET":          (colors.GREEN,   20),
    "ANCILLARY":       (6,              18),   # magenta
    "DIMENSIONS":      (colors.BLUE,    9),
    "LABELS":          (colors.WHITE,   9),
    "CLEARANCE_LINES": (8,              9),
    "GRID":            (9,              9),
}

def setup_doc():
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"]   = 4   # mm
    doc.header["$MEASUREMENT"] = 1   # metric
    doc.header["$DIMSCALE"]   = 100
    doc.header["$LUNITS"]     = 4   # mm

    # Load standard linetypes
    doc.linetypes.add("DASHED",  pattern="A,.5,-.25")
    doc.linetypes.add("CENTER",  pattern="A,1.0,-.25,.25,-.25")
    doc.linetypes.add("DASHDOT", pattern="A,.5,-.25,.0,-.25")

    for name,(col,lw) in LAYERS.items():
        layer = doc.layers.add(name, color=col)
        layer.dxf.lineweight = lw
    return doc

def _insert_block(msp, block_name, x, y, xscale=1, yscale=1):
    msp.add_blockref(
        block_name, (x, y),
        dxfattribs={"xscale": xscale, "yscale": yscale, "layer": "0"}
    )

def _rect(msp, x1, y1, x2, y2, layer, lw=18, linetype=None):
    att = {"layer": layer, "lineweight": lw}
    if linetype:
        att["linetype"] = linetype
    msp.add_lwpolyline(
        [(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)],
        dxfattribs={**att, "closed": True}
    )

def _label(msp, x, y, text, layer="LABELS", height=150, angle=0):
    msp.add_text(
        text,
        dxfattribs={"layer":layer,"height":height,"insert":(x,y),"rotation":angle}
    )

def _dim_horiz(msp, x1, x2, y, text, tick_h=200):
    """Simple horizontal dimension annotation."""
    msp.add_line((x1,y),(x2,y),dxfattribs={"layer":"DIMENSIONS","lineweight":9})
    msp.add_line((x1,y-tick_h),(x1,y+tick_h),dxfattribs={"layer":"DIMENSIONS","lineweight":9})
    msp.add_line((x2,y-tick_h),(x2,y+tick_h),dxfattribs={"layer":"DIMENSIONS","lineweight":9})
    _label(msp,(x1+x2)/2,y+tick_h*0.5,text,"DIMENSIONS",height=150)

def _dim_vert(msp, x, y1, y2, text, tick_h=200):
    """Simple vertical dimension annotation."""
    msp.add_line((x,y1),(x,y2),dxfattribs={"layer":"DIMENSIONS","lineweight":9})
    msp.add_line((x-tick_h,y1),(x+tick_h,y1),dxfattribs={"layer":"DIMENSIONS","lineweight":9})
    msp.add_line((x-tick_h,y2),(x+tick_h,y2),dxfattribs={"layer":"DIMENSIONS","lineweight":9})
    _label(msp,x+tick_h*0.6,(y1+y2)/2,text,"DIMENSIONS",height=150,angle=90)

def _clearance_box(msp, eq, pad):
    _rect(msp, eq.x-pad, eq.y-pad, eq.x2+pad, eq.y2+pad,
          "CLEARANCE_LINES", lw=9, linetype="DASHED")

def _grid(msp, room_w, room_h, grid_size=1000):
    """Light reference grid."""
    x = grid_size
    while x < room_w:
        msp.add_line((x,0),(x,room_h),dxfattribs={"layer":"GRID","lineweight":1,"linetype":"DASHDOT"})
        _label(msp,x,room_h+100,f"{int(x)}",layer="GRID",height=80)
        x += grid_size
    y = grid_size
    while y < room_h:
        msp.add_line((0,y),(room_w,y),dxfattribs={"layer":"GRID","lineweight":1,"linetype":"DASHDOT"})
        _label(msp,-200,y,f"{int(y)}",layer="GRID",height=80)
        y += grid_size
 
def generate_dxf(placed, room_w, room_h, data, output_path="substation_layout.dxf"):
    kv = data.get("supply_kv", 11)
    doc = setup_doc()
    msp = doc.modelspace()

    # ── Pre-define all blocks ─────────────────────────
    block_map = {}

    for eq in placed:
        L, W = eq.length, eq.width
        key  = eq.name

        if key == "transformer":
            bn = define_transformer_block(doc, L, W, kv)
        elif key == "ht_panel":
            cfg = data.get("ht_panel",{}).get("config","")
            bn = define_ht_panel_block(doc, L, W, cfg)
        elif key == "rmu_panel":
            cfg = data.get("rmu_panel",{}).get("config","")
            bn = define_rmu_panel_block(doc, L, W, cfg)
        elif key == "main_lt_panel":
            bn = define_lt_panel_block(doc, L, W, "MAIN LT PANEL")
        elif key == "dg_sync_panel":
            bn = define_lt_panel_block(doc, L, W, "DG SYNC PANEL")
        elif key == "apfc_panel":
            bn = define_apfc_block(doc, L, W)
        elif key == "dg_set":
            bn = define_dg_set_block(doc, L, W)
        elif key == "transformer_ngr":
            bn = define_ngr_block(doc, L, W, "TX NGR")
        elif key == "dg_ngr":
            bn = define_ngr_block(doc, L, W, "DG NGR")
        elif key == "dg_day_tank":
            bn = define_dg_day_tank_block(doc, L, W)
        elif key == "rtcc_panel":
            bn = define_rtcc_block(doc, L, W)
        elif key == "aux_panel":
            bn = define_generic_panel_block(doc, L, W, "AUX PANEL")
        elif key == "substation_panel":
            bn = define_generic_panel_block(doc, L, W, "SUBSTATION PANEL")
        else:
            bn = define_generic_panel_block(doc, L, W, eq.label)

        block_map[id(eq)] = bn

    # ── Room boundary ─────────────────────────────────
    # Double-line walls (structural)
    wall_t = 230   # 230mm brick wall
    _rect(msp, -wall_t, -wall_t, room_w+wall_t, room_h+wall_t,
          "ROOM_BOUNDARY", lw=50)
    _rect(msp, 0, 0, room_w, room_h, "ROOM_BOUNDARY", lw=35)

    # Hatch wall fill
    hatch = msp.add_hatch(color=8, dxfattribs={"layer":"ROOM_BOUNDARY"})
    hatch.set_pattern_fill("ANSI31", scale=80, angle=45)
    hatch.paths.add_polyline_path(
        [(-wall_t,-wall_t),(room_w+wall_t,-wall_t),
         (room_w+wall_t,room_h+wall_t),(-wall_t,room_h+wall_t)], is_closed=True
    )
    # Cutout inner area from hatch
    hatch.paths.add_polyline_path(
        [(0,0),(room_w,0),(room_w,room_h),(0,room_h)], is_closed=True
    )

    # Door opening (bottom wall centre, 1800mm)
    door_w  = 1800
    door_cx = room_w / 2
    # Erase wall segment for door
    msp.add_line((door_cx-door_w/2,-wall_t),(door_cx-door_w/2,0),
                 dxfattribs={"layer":"ROOM_BOUNDARY","lineweight":50})
    msp.add_line((door_cx+door_w/2,-wall_t),(door_cx+door_w/2,0),
                 dxfattribs={"layer":"ROOM_BOUNDARY","lineweight":50})
    # Door swing arc
    msp.add_arc(
        center=(door_cx-door_w/2, 0), radius=door_w*0.95,
        start_angle=-15, end_angle=90,
        dxfattribs={"layer":"ROOM_BOUNDARY","lineweight":9,"linetype":"DASHED"}
    )
    _label(msp, door_cx, -wall_t-200, "MAIN ENTRANCE (1800mm)", layer="LABELS", height=180)

    # ── Grid ──────────────────────────────────────────
    _grid(msp, room_w, room_h)

    # ── Place equipment blocks ────────────────────────
    CLEAR_PADS = {
        "transformer":   500,
        "dg_set":        400,
        "ht_panel":      300,
        "main_lt_panel": 300,
        "dg_sync_panel": 300,
        "apfc_panel":    200,
    }
    tx_index = 1
    dg_index = 1

    for eq in placed:
        bn = block_map[id(eq)]
        _insert_block(msp, bn, eq.x, eq.y)

        # Clearance dashed box
        pad = CLEAR_PADS.get(eq.name, 150)
        _clearance_box(msp, eq, pad)

        # Equipment number tag (for transformers and DGs)
        if eq.name == "transformer":
            _label(msp, eq.x+eq.length/2, eq.y2+300, f"TX-{tx_index}", height=200)
            tx_index += 1
        elif eq.name == "dg_set":
            _label(msp, eq.x+eq.length/2, eq.y2+300, f"DG-{dg_index}", height=200)
            dg_index += 1

    # ── Room dimensions ───────────────────────────────
    _dim_horiz(msp, 0, room_w, -wall_t-500, f"ROOM WIDTH = {room_w} mm")
    _dim_vert(msp, room_w+wall_t+500, 0, room_h, f"ROOM DEPTH = {room_h} mm")

    # ── Title block (bottom right) ───────────────────
    tb_x = room_w - 3000
    tb_y = -wall_t - 1800
    _rect(msp, tb_x, tb_y, room_w+wall_t, tb_y+1600, "ROOM_BOUNDARY", lw=18)
    _label(msp, tb_x+200, tb_y+1200, "SUBSTATION EQUIPMENT LAYOUT", layer="LABELS", height=220)
    _label(msp, tb_x+200, tb_y+900,  f"SUPPLY: {kv} kV", layer="LABELS", height=160)
    _label(msp, tb_x+200, tb_y+650,  f"ROOM: {room_w} x {room_h} mm", layer="LABELS", height=160)
    _label(msp, tb_x+200, tb_y+400,  f"SCALE: 1:100 (ALL DIMS IN mm)", layer="LABELS", height=140)
    _label(msp, tb_x+200, tb_y+150,  "AUTO-GENERATED — VERIFY BEFORE USE", layer="LABELS", height=120)

    # ── North arrow ───────────────────────────────────
    na_x = 500
    na_y = room_h + wall_t + 500
    msp.add_circle((na_x,na_y),250,dxfattribs={"layer":"LABELS","lineweight":18})
    msp.add_line((na_x,na_y),(na_x,na_y+400),dxfattribs={"layer":"LABELS","lineweight":25})
    _label(msp,na_x,na_y+420,"N",layer="LABELS",height=200)

    doc.saveas(output_path)

    print(f"\n{'='*55}")
    print(f"  ✅  DXF generated successfully")
    print(f"{'='*55}")
    print(f"  File      : {output_path}")
    print(f"  Room size : {room_w} mm × {room_h} mm")
    print(f"  Equipment : {len(placed)} items placed")
    print(f"  Layers    : {len(LAYERS)} (colour-coded)")
    print(f"{'='*55}\n")
    return output_path
