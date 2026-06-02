#  USER INPUT COLLECTION

from ht_panel import get_ht_panel_size, get_rmu_panel_size

def parse_dims(s):
    """Parse '2000x1500' → (2000, 1500). Returns None if skipped."""
    s = s.strip()
    if not s or s.lower() in ("skip", "none", "-", ""):
        return None
    parts = s.lower().replace("x", "x").split("x")
    if len(parts) != 2:
        raise ValueError(f"Enter dimensions as LENGTHxWIDTH (e.g. 2000x1500), got: '{s}'")
    return int(parts[0].strip()), int(parts[1].strip())


def ask(prompt, default=None):
    val = input(prompt).strip()
    if not val and default is not None:
        return default
    return val


def collect_inputs():
    """
    Interactively collect all equipment inputs from user.
    Returns a dict describing the substation.
    """
    print("\n" + "="*55)
    print("  SUBSTATION LAYOUT GENERATOR — INPUT COLLECTION")
    print("="*55)
    print("  Press ENTER to skip equipment not present.")
    print("  Dimensions format: LENGTHxWIDTH  (in mm)")
    print("="*55 + "\n")

    data = {}

    # ── Power supply voltage ─────────────────────────────
    print("[ 1 ] POWER SUPPLY")
    kv_raw = ask("  Supply voltage (11 / 22 / 33 kV) [default 11]: ", "11")
    data["supply_kv"] = int(kv_raw.replace("kv", "").replace("KV", "").strip())

    # ── RMU Panel ────────────────────────────────────────
    print("\n[ 2 ] RMU PANEL")
    rmu_present = ask("  Is RMU panel present? (y/n) [n]: ", "n").lower()
    if rmu_present == "y":
        print("  Config options: 2incomer+1outgoing | 2incomer+2outgoing | 1incomer+1outgoing | 1incomer+2outgoing")
        rmu_cfg = ask("  RMU configuration: ", "1incomer+2outgoing")
        rmu_l, rmu_w = get_rmu_panel_size(rmu_cfg)
        data["rmu_panel"] = {"length": rmu_l, "width": rmu_w, "config": rmu_cfg}
        print(f"  → RMU size auto-set: {rmu_l} x {rmu_w} mm")

    # ── HT Panel ─────────────────────────────────────────
    print("\n[ 3 ] HT PANEL")
    ht_present = ask("  Is HT panel present? (y/n) [y]: ", "y").lower()
    if ht_present == "y":
        print("  Config options: 1incomer+2outgoings | 1incomer+3outgoings | ... | 1incomer+6outgoings")
        ht_cfg = ask("  HT panel configuration: ", "1incomer+2outgoings")
        ht_l, ht_w = get_ht_panel_size(ht_cfg)
        data["ht_panel"] = {"length": ht_l, "width": ht_w, "config": ht_cfg}
        print(f"  → HT panel size auto-set: {ht_l} x {ht_w} mm")

    # ── Transformers ─────────────────────────────────────
    print("\n[ 4 ] TRANSFORMERS")
    n_tx = int(ask("  Number of transformers (0 to skip): ", "0"))
    if n_tx > 0:
        from transformer_sizes import get_transformer_size, TRANSFORMER_SIZES
        kv = data["supply_kv"]

        # Show available standard ratings for selected kV
        std_ratings = sorted(TRANSFORMER_SIZES.get(kv, {}).keys())
        print(f"  Standard ratings for {kv}kV: {std_ratings}")
        print(f"  (Enter one of the above, or any custom kVA value)")

        kva_raw = ask(f"  Transformer rating (kVA): ", "1000")
        kva = int(kva_raw.strip())

        tx_l, tx_w, tx_h = get_transformer_size(kv, kva)

        if kva in std_ratings:
            print(f"  → Standard size auto-set: {tx_l} x {tx_w} mm  (H={tx_h} mm)")
        else:
            print(f"  → Custom kVA={kva} — calculated size: {tx_l} x {tx_w} mm  (H={tx_h} mm)")

        data["transformers"] = {
            "count":  n_tx,
            "length": tx_l,
            "width":  tx_w,
            "height": tx_h,
            "kva":    kva,
        }

    # ── DG Sets ──────────────────────────────────────────
    print("\n[ 5 ] DG SETS")
    n_dg = int(ask("  Number of DG sets (0 to skip): ", "0"))
    if n_dg > 0:
        dg_dims = parse_dims(ask("  DG set dimensions LxW mm: "))
        if dg_dims is None:
            dg_dims = (3500, 1500)
        dg_indoor = ask("  Indoor or Outdoor? (indoor/outdoor) [indoor]: ", "indoor").lower()
        data["dg_sets"] = {
            "count": n_dg,
            "length": dg_dims[0],
            "width": dg_dims[1],
            "location": dg_indoor,
        }

    # ── DG Day Tank (only relevant if DG sets present) ───
    if n_dg > 0:
        print("\n[ 6 ] DG DAY TANK")
        dgtank = ask("  DG day tank present? (y/n) [n]: ", "n").lower()
        if dgtank == "y":
            dt_dims = parse_dims(ask("  Day tank dimensions LxW mm: "))
            if dt_dims:
                data["dg_day_tank"] = {"length": dt_dims[0], "width": dt_dims[1]}

    # ── Main LT Panel ────────────────────────────────────
    print("\n[ 7 ] MAIN LT PANEL")
    lt_dims = parse_dims(ask("  Main LT panel dimensions LxW mm (Enter to skip): "))
    if lt_dims:
        data["main_lt_panel"] = {"length": lt_dims[0], "width": lt_dims[1]}

    # ── DG Synchronizing Panel (only if DG sets present) ─
    if n_dg > 0:
        print("\n[ 8 ] DG SYNCHRONIZING PANEL")
        dgs_dims = parse_dims(ask("  DG sync panel dimensions LxW mm (Enter to skip): "))
        if dgs_dims:
            data["dg_sync_panel"] = {"length": dgs_dims[0], "width": dgs_dims[1]}

    # ── APFC Panel ───────────────────────────────────────
    print("\n[ 9 ] APFC PANEL")
    apfc_dims = parse_dims(ask("  APFC panel dimensions LxW mm (Enter to skip): "))
    if apfc_dims:
        data["apfc_panel"] = {"length": apfc_dims[0], "width": apfc_dims[1]}

    # ── Transformer NGR ──────────────────────────────────
    print("\n[ 10 ] TRANSFORMER NGR")
    ngr_tx = parse_dims(ask("  Transformer NGR dimensions LxW mm (Enter to skip): "))
    if ngr_tx:
        data["transformer_ngr"] = {"length": ngr_tx[0], "width": ngr_tx[1]}

    # ── DG Set NGR (only if DG sets present) ────────────
    if n_dg > 0:
        print("\n[ 11 ] DG SET NGR")
        ngr_dg = parse_dims(ask("  DG set NGR dimensions LxW mm (Enter to skip): "))
        if ngr_dg:
            data["dg_ngr"] = {"length": ngr_dg[0], "width": ngr_dg[1]}

    # ── RTCC Panel ───────────────────────────────────────
    print("\n[ 12 ] RTCC PANEL")
    rtcc = parse_dims(ask("  RTCC panel dimensions LxW mm (Enter to skip): "))
    if rtcc:
        data["rtcc_panel"] = {"length": rtcc[0], "width": rtcc[1]}

    # ── Auxiliary Power Panel ────────────────────────────
    print("\n[ 13 ] AUXILIARY POWER PANEL")
    aux = parse_dims(ask("  Auxiliary power panel dimensions LxW mm (Enter to skip): "))
    if aux:
        data["aux_panel"] = {"length": aux[0], "width": aux[1]}

    # ── Substation Panel ─────────────────────────────────
    print("\n[ 14 ] SUBSTATION PANEL")
    sub = parse_dims(ask("  Substation panel dimensions LxW mm (Enter to skip): "))
    if sub:
        data["substation_panel"] = {"length": sub[0], "width": sub[1]}

    print("\n" + "="*55)
    print("  Input collection complete.")
    print("="*55 + "\n")
    return data
