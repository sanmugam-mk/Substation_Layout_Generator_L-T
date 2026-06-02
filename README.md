# CAD Automation Project

## Overview

This project automates electrical substation room layout generation using Python and AutoCAD DXF files.

The system generates room layouts based on user inputs such as:

* Supply Voltage
* Transformer Rating
* Number of Transformers
* HT Panel Configuration
* RMU Configuration

The application automatically:

* Determines transformer dimensions
* Applies engineering spacing rules
* Calculates room dimensions
* Places equipment within the layout
* Generates DXF output files

## Features

* Transformer sizing engine
* Rule-based layout generation
* Automatic room dimension calculation
* DXF generation using ezdxf
* Support for multiple voltage levels:

  * 11 kV
  * 22 kV
  * 33 kV
  * 66 kV

## Project Structure

main.py

inputs.py

rules.py

transformer_sizes.py

ht_panel.py

layout_engine.py

cad_generator.py

blocks.py

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Current Development

* Transformer sizing engine
* Room generation
* Transformer placement
* CAD output generation
