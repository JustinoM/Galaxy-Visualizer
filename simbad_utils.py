"""Utility functions for SIMBAD queries and data processing."""
import numpy as np
import pandas as pd
import sys
import re
from typing import List, Any, Optional, Dict
from astroquery.simbad import Simbad




# Import galaxy groups
try:
    from galaxy_groups import galaxy_groups
except ImportError:
    galaxy_groups = {}
    print("Warning: galaxy_groups module not found")

# Import config for constants
try:
    from config import Config
except ImportError:
    # Fallback constants if config not available
    class Config:
        C_LIGHT = 299792.458
        DEG_TO_RAD = 0.017453293
        KPC_PER_MPC = 1000


def get_input(galaxy_groups_dict: dict = None) -> List[str]:
    """Get galaxy names from command line arguments."""
    if galaxy_groups_dict is None:
        galaxy_groups_dict = galaxy_groups
    
    if len(sys.argv) < 2:
        print("Error: Provide at least one galaxy name or group name")
        print(f"Usage: {sys.argv[0]} galaxy1 galaxy2 ...")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Check if it's a predefined group
        matched_key = next(
            (key for key in galaxy_groups_dict.keys() 
             if key.lower() == sys.argv[1].lower()),
            None
        )
        if matched_key:
            Config.GROUP_NAME = matched_key
            members = galaxy_groups_dict[matched_key]["galaxies"]
            print("=" * 80)
            print(f"PREDEFINED GROUP: {Config.GROUP_NAME}")
            print("=" * 80)
            return members
    
    # Individual galaxy names
    members = sys.argv[1:]
    print("=" * 80)
    print(f"GROUP OF {len(members)} GALAXIES")
    print("=" * 80)
    for i, name in enumerate(members, 1):
        print(f"  {i}. {name}")
    
    return members


def convert_to_mpc(dist_value: Any, unit_str: str) -> float:
    """Convert distance to Mpc."""
    if dist_value is None or pd.isna(dist_value):
        return np.nan
    
    try:
        value = float(dist_value)
    except (ValueError, TypeError):
        return np.nan
    
    if not unit_str:
        return np.nan
    
    unit = unit_str.strip().lower()
    
    conversion = {
        'pc': 1e-6,
        'kpc': 1e-3,
        'mpc': 1.0,
        'gpc': 1e3,
        'ly': 3.06601394e-7,
        'km': 3.24077929e-23,
    }
    
    if unit in conversion:
        return value * conversion[unit]
    
    print(f"Warning: unknown unit '{unit_str}'")
    return np.nan


def redshift_to_velocity(z: float, relativistic: bool = True) -> float:
    """Convert redshift to velocity in km/s."""
    if relativistic:
        return Config.C_LIGHT * ((1 + z)**2 - 1) / ((1 + z)**2 + 1)
    return z * Config.C_LIGHT


def extract_from_colormap(cmap_name: str, n_colors: int) -> List[str]:
    """Extract n colors from a matplotlib colormap."""
    from matplotlib.colors import to_hex
    import matplotlib.pyplot as plt
    
    cmap = plt.get_cmap(cmap_name)
    positions = np.linspace(0, 1, n_colors)
    return [to_hex(cmap(pos)) for pos in positions]


def is_galaxy(otype_value: Any) -> bool:
    """Check if SIMBAD object type is a galaxy."""
    if otype_value is None:
        return False
    
    otype = str(otype_value).strip()
    if not otype:
        return False
    
    galaxy_types = {
        'G', 'LSB', 'bCG', 'SBG', 'H2G', 'EmG',  # Direct galaxies
        'AGN', 'SyG', 'Sy1', 'Sy2', 'rG', 'LIN', 'QSO', 'Bla', 'BLL',  # Active
        'GiP', 'GiG', 'GiC', 'BiC', 'IG',  # Environment
        'PaG', 'GrG', 'CGG', 'ClG', 'SCG',  # Groups/clusters
        'AGN', 'AG?'   # Active galaxy
    }
    
    if otype in galaxy_types:
        return True
    
    if otype.startswith('G') and len(otype) <= 3:
        return True
    
    return False


def validate_morphology(morph_value: Any) -> str:
    """
    Validate and clean SIMBAD morphology value.
    
    SIMBAD sometimes returns invalid values like "-1.2" for galaxies.
    """
    if morph_value is None or pd.isna(morph_value):
        return "Unknown"
    
    morph_str = str(morph_value).strip()
    
    if not morph_str:
        return "Unknown"
    
    # Check for numeric values (like "-1.2")
    try:
        float(morph_str)
        # If we get here, it's numeric -> invalid
        print(f"  ⚠ Numeric morphology '{morph_str}' → 'Unknown'")
        return "Unknown"
    except ValueError:
        # Not a number, keep as is
        return morph_str

"""Galaxy size extraction and conversion utilities."""

def extract_angular_size(result):
    """
    Extract angular size from SIMBAD result.
    
    Parameters:
    -----------
    result : astropy.table.Table
        SIMBAD query result
    
    Returns:
    --------
    float : Major axis angular size in arcminutes, or None if not available
    """
    if 'galdim_majaxis' not in result.colnames:
        return None
    
    dim_data = result['galdim_majaxis'][0]
    
    if dim_data is None or pd.isna(dim_data):
        return None
    
    # Parse the dimension string
    try:
        dim_str = str(dim_data).strip()
        # Format is typically "MAJORxMINOR" or "MAJOR MINOR ANGLE"
        numbers = re.findall(r"[\d.]+", dim_str)
        
        if numbers:
            # First number is major axis in arcminutes
            return float(numbers[0])
    except Exception as e:
        print(f"  ⚠ Could not parse angular size: {e}")
    
    return None


def angular_size_to_kpc(angular_size_arcmin: float, distance_mpc: float) -> Optional[float]:
    """
    Convert angular size (arcminutes) to physical size (kpc).
    
    Formula: physical size (kpc) = distance (kpc) * angular size (radians)
    
    Parameters:
    -----------
    angular_size_arcmin : float
        Angular size in arcminutes
    distance_mpc : float
        Distance in Megaparsecs
    
    Returns:
    --------
    float : Physical size in kiloparsecs, or None if conversion fails
    """
    if angular_size_arcmin is None or distance_mpc is None:
        return None
    
    # Convert arcminutes to radians
    angular_size_rad = angular_size_arcmin * (np.pi / 180.0) / 60.0
    
    # Convert distance from Mpc to kpc
    distance_kpc = distance_mpc * 1000.0
    
    # Calculate physical size
    physical_size_kpc = angular_size_rad * distance_kpc
    
    return physical_size_kpc



        
def setup_simbad() -> Simbad:
    """Configure and return a Simbad instance."""
    simbad = Simbad()
    simbad.add_votable_fields('otype', 'morphtype', 'dim', 'mesrot',
                              'mesdistance', 'rvz_redshift', 'velocity')
    simbad.TIMEOUT = 30
    return simbad
