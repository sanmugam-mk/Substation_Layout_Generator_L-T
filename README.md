# Automated Electrical Substation Layout Generator

## Overview

This project is a Python-based automation tool developed to generate electrical substation equipment layouts automatically in DXF format.

The system places major substation equipment such as transformers, HT panels, LT panels, DG sets, ancillary rooms, and access shutters while following predefined engineering spacing and clearance rules.

Instead of manually drafting layouts in AutoCAD, the user provides equipment configuration and dimensions, and the program generates a complete preliminary layout automatically.

---

## Sample Output

The generated layout includes:

- DG Sets
- HT Panel
- Transformers
- Perforated Rolling Shutters
- UPS & Battery Room
- SCADA Room
- Maintenance & Control Room
- Toilet
- RMU Panel Room
- Grid Layout
- Room Boundary
- AutoCAD-ready DXF Drawing

---

## Features

### Equipment Placement

Automatically places:

- Transformers
- HT Panels
- RMU Panels
- DG Sets
- LT Panels
- APFC Panels
- DG Synchronizing Panels
- RTCC Panels
- Auxiliary Equipment

while maintaining spacing and clearance requirements.

---

### Ancillary Room Generation

Automatically generates and positions:

- UPS & Battery Room
- SCADA Room
- Maintenance & Control Room
- Toilet
- RMU Panel Room

based on reference project dimensions.

---

### Transformer Bay Access Planning

Generates:

- Transformer Bays
- Perforated Rolling Shutters

to provide access for transformer installation and replacement.

---

### DXF Generation

Produces AutoCAD-compatible DXF drawings including:

- Equipment outlines
- Room boundaries
- Equipment labels
- Dimension annotations
- Grid system
- North arrow
- Title block

---

### Dynamic Layout Sizing

The layout adjusts automatically based on:

- Number of transformers
- Number of DG sets
- Panel dimensions
- Ancillary room dimensions
- Clearance requirements

---

## Layout Philosophy

The current layout follows:

```text
DG SETS

HT / LT PANELS

ANCILLARY ROOMS

TRANSFORMERS

PERFORATED ROLLING SHUTTERS

MAIN ENTRANCE
```

This arrangement ensures:

- Clear equipment segregation
- Accessible transformer replacement path
- Better utilization of floor space
- Consistent room positioning

---

## Project Structure

```text
substation_layout/
│
├── main.py
├── layout_engine.py
├── cad_generator.py
├── ancillary_rooms.py
├── rules.py
├── blocks.py
├── ht_panel.py
├── transformer_sizes.py
├── inputs.py
│
├── output/
│   └── generated_layout.dxf
│
└── README.md
```

---

## Core Modules

### layout_engine.py

Responsible for:

- Equipment placement
- Clearance calculations
- Layout arrangement
- Room dimension calculations

---

### ancillary_rooms.py

Responsible for:

- UPS & Battery Room placement
- SCADA Room placement
- Maintenance Room placement
- Toilet placement
- RMU Room placement
- Rolling Shutter placement

---

### cad_generator.py

Responsible for:

- DXF creation
- Drawing entities
- Room rendering
- Equipment rendering
- Text annotations

---

### rules.py

Contains engineering constraints such as:

- Equipment spacing
- Wall clearances
- Access clearances
- Layout margins

---

## Technologies Used

- Python 3
- EZDXF
- AutoCAD DXF Format

---

## Engineering Benefits

- Reduces manual drafting effort
- Produces consistent layouts
- Speeds up preliminary design work
- Enables rapid layout iterations
- Helps standardize substation design

---

## Current Status

### Completed

- Automatic equipment placement
- Transformer layout generation
- Ancillary room generation
- Rolling shutter placement
- DXF generation
- Room dimension annotations
- Dynamic room sizing

### In Progress

- Layout optimization
- Clearance validation checks
- Automatic design-rule verification
- Multiple substation configuration support

---

## Author

Sanmugasundaram M.K.

Internship Project – Electrical Substation Layout Automation