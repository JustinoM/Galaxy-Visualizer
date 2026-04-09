#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Galaxy Group Sky-Oriented 3D View
=================================

A 3D visualization of any galaxy group with astronomically correct positions.
"""

__author__ = "Justino Martinez"
__version__ = "1.1.0"
__date__ = "2026-03-06"
__bluesky__ = "@justino.info"
__github__ = "https://github.com/JustinoM"
__repository__ = "https://github.com/JustinoM/Galaxy-Visualizer"

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

from config import Config
from galaxy_data import GalaxyData
from group_plotter import GroupPlotter
from simbad_utils import extract_from_colormap, get_input
from galaxy_groups import galaxy_groups

# Set Qt platform
os.environ['QT_QPA_PLATFORM'] = 'xcb'


def main() -> None:
    """Main execution."""
    try:    	
        # Get input
        galaxies = get_input(galaxy_groups)
        
        # Initialize the GalaxyData class 
        GalaxyData.__init_subclass__()

        # Load data from SIMBAD
        GalaxyData.load_from_simbad(galaxies)
        
        # Refresh list because some of them could be discarded
        galaxies = GalaxyData.objects
        
        # Assign colors
        colors = extract_from_colormap('brg', len(GalaxyData.objects))
        colors_galaxy = {galaxy: colors[i] for i, galaxy in enumerate(galaxies)}
        Config.COLORS = {**Config.COLORS, **colors_galaxy}
        
        # Verify conventions
        GalaxyData.verify_conventions()
        
        # Create and show plot
        plotter = GroupPlotter(Config, GalaxyData)
        plotter.plot()
        
        print("\n" + "=" * 80)
        print("VISUALIZATION COMPLETE")
        print("=" * 80)
        print("✓ +X = EAST (astronomically correct)")
        print("✓ +Y = NORTH (astronomically correct)")
        print("✓ EAST appears on LEFT (matches sky)")

        plotter.show()

        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
