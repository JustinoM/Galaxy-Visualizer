# Galaxy Visualizer

A Python-based 3D visualization tool for galaxy groups using actual astronomical data from the SIMBAD database.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation using PIP](#installation-using-pip)
- [Installation with Conda](#installation-using-conda-recommended)
- [Step-by-step Conda Installation](#installation-with-conda-step-by-step)
- [Requirements File](#requirements-file)
- [Usage](#usage)
- [Using Individual Galaxies](#using-individual-galaxies)
- [Common Galaxy Designation Formats](#common-galaxy-designation-formats)
- [Using Predefined Groups](#using-predefined-groups)
- [Examples](#examples)
- [Interactive Controls](#interactive-controls)
- [Predefined Galaxy Groups](#predefined-galaxy-groups)
- [Data Sources](#data-sources)
- [Output](#output)
- [Coordinate Conventions](#coordinate-conventions)
- [File Structure](#file-structure)
- [How It Works](#how-it-works)
- [Limitations](#limitations)
- [License](#license)
- [Author](#author)
- [Acknowledgments](#acknowledgments)
- [Version](#version)
- [See Also](#see-also)
- [Troubleshooting](#troubleshooting)
  
## Overview

Galaxy Visualizer creates interactive 3D visualizations of any galaxy group with astronomically correct positions. It queries real astronomical data from the SIMBAD database (RA, Dec, redshift, distance, morphology, angular size) and renders each galaxy with an appropriate 3D representation based on its morphological classification.

### Features

- **Real Astronomical Data**: Queries SIMBAD for actual galaxy positions, distances, and physical properties
- **Astronomically Correct Coordinates**: +X = East, +Y = North, +Z = Away from Earth
- **Morphology-based Rendering**: Different visual representations for spiral, elliptical, lenticular, and irregular galaxies
- **Interactive 3D View**:
  - Mouse rotation and zoom
  - Click on galaxies to display detailed information
  - Keyboard controls for view adjustment
- **Predefined Groups**: Built-in catalog of galaxy groups (Local Group, M81 Group, Stephan's Quintet, etc.)
- **Custom Groups**: Create your own groups by providing galaxy names

## Requirements

- Python 3.9+
- Required packages:
  - numpy
  - matplotlib
  - scipy
  - pandas
  - astroquery
  - astropy

## Installation using PIP

```bash
git clone https://github.com/JustinoM/Galaxy-Visualizer.git
cd Galaxy-Visualizer
pip install -r requirements.txt
```
## Installation using Conda (recommended)

```bash
git clone https://github.com/JustinoM/Galaxy-Visualizer.git
cd Galaxy-Visualizer
conda env create -f environment.yml
```
### Installation using Conda (step-by-step)
1. Download Galaxy Visualizer
   ```bash
   git clone https://github.com/JustinoM/Galaxy-Visualizer.git
   cd Galaxy-Visualizer
   ```
2. Create a new conda environment (Python 3.9 or later):
   ```bash
   conda create -n galaxy_viz python=3.9
   conda activate galaxy_viz
   ```
3. Install required packages using conda (most are available in conda-forge):
   ```bash
   conda install -c conda-forge numpy matplotlib scipy pandas astropy
   ```
4. Install astroquery (not always in default conda channels, but available via conda-forge):
   ```bash
   conda install -c conda-forge astroquery
   ```
6. Verify installation:
   ```bash
   python -c "import astroquery; print('OK')"
   ```
8. Test the visualizer:
   ```bash
   python Galaxy_Visualizer.py "Markarian Chain"
   ```
   or
   ```bash
   ./Galaxy_Visualizer.py "Markarian Chain"
   ```
   
### Requirements File
```
numpy>=1.21.0
matplotlib>=3.5.0
scipy>=1.7.0
pandas>=1.3.0
astroquery>=0.4.6
astropy>=5.0
```

## Usage

If you are using a conda environment, you must activate it before executing Galaxy Visualizer
```bash
conda activate galaxy_viz
```

### Basic Usage

Galaxy Visualizer accepts names of individual galaxies (separated by spaces) or predefined groups (contained in galaxy_groups.py file)

### Using Individual Galaxies

```
python Galaxy_Visualizer.py galaxy1 galaxy2 galaxy3...
```

If you include spaces in a galaxy's name, use quotes around the name. For example, these 4 examples are equivalent:
```
python Galaxy_Visualizer.py "M 101" NGC5474
python Galaxy_Visualizer.py "M 101" "NGC 5474"
python Galaxy_Visualizer.py M101 NGC5474
python Galaxy_Visualizer.py "M101" ngc5474
```
However, it's a safe practice to include a space between the catalogue name and the identifier, e.g., "NGC 5194"

####  Common Galaxy Designation Formats

| Catalog Type        | Format Example                 | Notes                                    |
|-----|--------|----|
| Messier (M)         | M 31 or M31                    | Standard format for Messier objects.     |
| NGC                 | NGC 224                        | Most common identifier for galaxies.     |
| IC                  | IC 342                         | Supplement to the NGC.                   |
| PGC                 | PGC 2557                       | Principal Galaxies Catalogue.            |
| UGC                 | UGC 12158                      | For galaxies north of -02°30' decl.      |
| ESO                 | ESO 350-40                     | For southern sky galaxies.               |


  
### Using Predefined Groups

Some predefined Galaxy Groups are stored in galaxy_groups.py file as a Python dictionary. You can add your own.
Some examples
```
python Galaxy_Visualizer.py "M81 Group"
python Galaxy_Visualizer.py "Local Group"
python Galaxy_Visualizer.py "Stephan's Quintet"
```

### Examples

#### Leo Triplet
python Galaxy_Visualizer.py M65 M66 NGC3628

#### M81 Group
python Galaxy_Visualizer.py "M81 Group"

#### Custom group
python Galaxy_Visualizer.py NGC253 NGC247 NGC7793

## Interactive Controls

### Mouse Controls
- Drag: Rotate the 3D view
- Scroll: Zoom in/out
- Click on galaxy: Display detailed information

### Keyboard Controls

| Key | Action |
|-----|--------|
| t | Toggle help text overlay |
| r | Reset to default view |
| h | Earth view (looking from Earth direction) |
| z | Side view |
| a | Toggle aspect ratio (auto/equal) |
| Up/Down | Change elevation angle |
| Left/Right | Change azimuth angle |
| Ctrl+Left/Right | Change roll angle |

## Predefined Galaxy Groups

The tool includes the following predefined groups in galaxy_groups.py file:

### Nearby Groups
- Local Group (excluding Milky Way)
- IC 342 Maffei Group
- M81 Group
- Sculptor Group
- M83 Group

### Compact Groups
- Stephan's Quintet
- Roberts Quartet
- Hickson 44, 56
- Shakhbazian 1, 12
- Copeland Septet
- Seyfert's Sextet

### Other Groups
- Leo Triplet
- M96 Group
- Coma I Group
- M101, M51, M74, M77 Groups
- NGC 1023, NGC 2997, NGC 5866 Groups
- Abell 400, 1367, 1656
- Markarian Chain
- The Devil's Mask

## Data Sources

All astronomical data is queried in real-time from the SIMBAD Astronomical Database operated by CDS, Strasbourg. The tool retrieves:
- Coordinates (RA, Dec)
- Redshift and radial velocity
- Distance measurements
- Morphological classification
- Angular size (for physical size calculation)

## Output

The visualization displays:
- 3D positions of galaxies relative to the group center
- Morphology-based rendering (spiral arms, elliptical shapes, irregular structures)
- Connection lines with distance labels between galaxies
- Earth position with distance to the group
- Clickable galaxies showing: coordinates, distance, velocity, redshift, physical size

An example of output by console:
```
================================================================================
GROUP OF 3 GALAXIES
================================================================================
  1. NGC253
  2. NGC247
  3. NGC7793
================================================================================
QUERYING SIMBAD
================================================================================
✓ Data retrieved for NGC253
  ✓ Size: 31.0 kpc (from 28.84 arcmin)
✓ Data retrieved for NGC247
  ✓ Size: 17.4 kpc (from 17.02 arcmin)
✓ Data retrieved for NGC7793
  ✓ Size: 10.7 kpc (from 10.00 arcmin)

================================================================================
SIGN CONVENTION VERIFICATION
================================================================================

COORDINATE SYSTEM:
  +X = EAST, +Y = NORTH, +Z = AWAY from Earth

GALAXY POSITIONS (relative to center):
--------------------------------------------------------------------------------

NGC253 (SAB(s)c):
  True: X=-6630.7 kpc (WEST), Y=  58.5 kpc (NORTH)
  Appears: UP, RIGHT
  RA: 00h 47m 33.1s
  Dec: -25° 17' 19.7"
  Vel:  258.8 km/s
  Dist:    3.7 Mpc
  z: 0.00086
  Physical size: 31.0 kpc
    (from 28.84 arcmin)

NGC247 (SAB(s)d):
  True: X=-6636.5 kpc (WEST), Y= 345.3 kpc (NORTH)
  Appears: UP, RIGHT
  RA: 00h 47m 08.6s
  Dec: -20° 45' 37.4"
  Vel:  162.0 km/s
  Dist:    3.5 Mpc
  z: 0.00054
  Physical size: 17.4 kpc
    (from 17.02 arcmin)

NGC7793 (SA(s)d):
  True: X=13267.2 kpc (EAST), Y=-403.8 kpc (SOUTH)
  Appears: DOWN, LEFT
  RA: 23h 57m 49.8s
  Dec: -32° 35' 27.7"
  Vel:  226.8 km/s
  Dist:    3.7 Mpc
  z: 0.00076
  Physical size: 10.7 kpc
    (from 10.00 arcmin)
```

### Coordinate Conventions
```
+X = EAST (appears on LEFT in the view)
+Y = NORTH (appears UP in the view)
+Z = AWAY from Earth
```

## File Structure
```
Galaxy-Visualizer/
├── Galaxy_Visualizer.py       # Main entry point
├── Galaxy_Visualizer_logo.png # Logo of the mrogram
├── config.py                  # Configuration settings
├── galaxy_data.py             # SIMBAD data management
├── galaxy_generator.py        # 3D shape generation
├── galaxy_renderer.py         # Galaxy rendering logic
├── group_plotter.py           # Main plotting class
├── morphology_parser.py       # Morphology code parsing
├── coordinate_formatter.py    # RA/Dec formatting utilities
├── simbad_utils.py            # SIMBAD query utilities
├── galaxy_groups.py           # Predefined galaxy groups
└── galaxy_images/             # Galaxy example images
    ├── spiral.png
    ├── barred_spiral.png
    ├── elliptical.png
    ├── lenticular.png
    └── irregular.png
```

## How It Works

1. Query SIMBAD: For each galaxy name, queries the SIMBAD database
2. Data Validation: Filters non-galaxies, missing coordinates, or missing distances
3. Coordinate Conversion: Converts RA/Dec to Cartesian coordinates (X,Y,Z)
4. Physical Size Calculation: Converts angular size to kpc using distance
5. Morphology Parsing: Interprets SIMBAD morphology codes
6. 3D Rendering: Creates appropriate 3D shapes for each galaxy type
7. Interaction Setup: Enables mouse and keyboard controls

## Limitations

- Galaxy sizes and spiral orientations are indicative, not exact
- Requires active internet connection for SIMBAD queries
- Some galaxies may be filtered out if missing essential data
- Image credits for example galaxy images belong to NASA/ESA as noted in the interface

## License

This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0).

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made
- NonCommercial — You may not use the material for commercial purposes
- ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license

Full license text: https://creativecommons.org/licenses/by-nc-sa/4.0/

## Author

Justino Martinez
- GitHub: @JustinoM
- Website: justino.info

## Acknowledgments

- DeepSeek (https://www.deepseek.com) - AI assistance for documentation formatting, code review, and technical explanations
- SIMBAD Astronomical Database (CDS, Strasbourg) for providing astronomical data
- NASA/ESA Hubble Space Telescope for example galaxy images
- Open source community for the scientific Python stack


## Version

Current version: 1.1.0 (2026-03-06)

## See Also

- Leo Triplet 3D (https://github.com/JustinoM/leo-triplet-3d) - A specialized visualization of the Leo Triplet galaxies that was the origin of Galaxy Visualizer

## Troubleshooting

### No galaxies found error
SIMBAD may not recognize some galaxies or may lack distance data. Try using the predefined groups or verify galaxy names using the SIMBAD website (http://simbad.u-strasbg.fr/simbad/).

### Matplotlib backend issues
If you encounter Qt platform errors, try:
export QT_QPA_PLATFORM=xcb

### Slow performance
Reduce the number of galaxies in your group or decrease the resolution parameters in galaxy_generator.py

---

Created for astronomical education and visualization purposes.
