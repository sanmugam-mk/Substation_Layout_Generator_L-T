#  HT PANEL SIZE LOGIC  (hardcoded from sheet)
#  All lengths in millimetres (mm)
# Each entry: (no_of_verticals, one_vertical_length_mm, total_length_mm, has_bus_coupler, has_bus_pt, has_line_pt)

HT_PANEL_CONFIGS = {
    # configuration_string : dict
    "1incomer+2outgoings": {
        "verticals": 3, "bus_coupler": True,  "bus_pt": False, "line_pt": True,
        "vertical_length": 1200, "total_length": 6000,
    },
    "1incomer+3outgoings": {
        "verticals": 4, "bus_coupler": False, "bus_pt": False, "line_pt": False,
        "vertical_length": 1200, "total_length": 4800,
    },
    "1incomer+4outgoings": {
        "verticals": 5, "bus_coupler": False, "bus_pt": False, "line_pt": False,
        "vertical_length": 1200, "total_length": 6000,
    },
    "1incomer+5outgoings": {
        "verticals": 6, "bus_coupler": False, "bus_pt": False, "line_pt": False,
        "vertical_length": 1200, "total_length": 7200,
    },
    "1incomer+6outgoings": {
        "verticals": 7, "bus_coupler": False, "bus_pt": False, "line_pt": False,
        "vertical_length": 1200, "total_length": 8400,
    },
}

RMU_PANEL_CONFIGS = {
    "2incomer+1outgoing": {
        "verticals": 3, "bus_coupler": True,  "bus_pt": True,  "line_pt": False,
        "vertical_length": 1200, "total_length": 6000,
    },
    "2incomer+2outgoing": {
        "verticals": 4, "bus_coupler": False, "bus_pt": False, "line_pt": False,
        "vertical_length": 1200, "total_length": 4800,
    },
    "1incomer+1outgoing": {
        "verticals": 2, "bus_coupler": True,  "bus_pt": False, "line_pt": False,
        "vertical_length": 1200, "total_length": 3600,
    },
    "1incomer+2outgoing": {
        "verticals": 3, "bus_coupler": False, "bus_pt": False, "line_pt": False,
        "vertical_length": 1200, "total_length": 3600,
    },
}

# Standard panel depth (width in floor plan) — typical value
HT_PANEL_DEPTH  = 1200  
RMU_PANEL_DEPTH = 1000   
def get_ht_panel_size(configuration: str):
    """
    Returns (total_length_mm, depth_mm) for given HT panel config string.
    e.g. '1incomer+3outgoings'
    """
    key = configuration.replace(" ", "").lower()
    if key in HT_PANEL_CONFIGS:
        cfg = HT_PANEL_CONFIGS[key]
        return cfg["total_length"], HT_PANEL_DEPTH
    raise ValueError(f"Unknown HT panel configuration: '{configuration}'. "
                     f"Valid options: {list(HT_PANEL_CONFIGS.keys())}")

def get_rmu_panel_size(configuration: str):
    """
    Returns (total_length_mm, depth_mm) for given RMU panel config string.
    """
    key = configuration.replace(" ", "").lower()
    if key in RMU_PANEL_CONFIGS:
        cfg = RMU_PANEL_CONFIGS[key]
        return cfg["total_length"], RMU_PANEL_DEPTH
    raise ValueError(f"Unknown RMU panel configuration: '{configuration}'. "
                     f"Valid options: {list(RMU_PANEL_CONFIGS.keys())}")
