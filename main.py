#!/usr/bin/env python3
import os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from inputs        import collect_inputs
from layout_engine import calculate_layout
from cad_generator import generate_dxf


def main():
    data = collect_inputs()

    print("\n Calculating room layout and placing equipment...")
    placed, room_w, room_h, ancillary_rooms = calculate_layout(data)

    print(f"\n Layout result:")
    print(f"   Room size : {room_w} mm x {room_h} mm")
    for eq in placed:
        print(f"   {eq.label.replace(chr(10),' | '):30s}  pos=({eq.x},{eq.y})  size={eq.length}x{eq.width} mm")

    # Timestamped filename — each run creates a new file, no permission conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(os.getcwd(), "output", f"substation_layout_{timestamp}.dxf")
    generate_dxf(
    placed,
    room_w,
    room_h,
    data,
    ancillary_rooms=ancillary_rooms,
    output_path=out
    )


if __name__ == "__main__":
    main()


