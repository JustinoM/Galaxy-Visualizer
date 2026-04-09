"""Galaxy data management and SIMBAD queries."""
import sys
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, ClassVar
from astroquery.simbad import Simbad

from config import Config
from coordinate_formatter import CoordinateFormatter
from simbad_utils import extract_angular_size, angular_size_to_kpc, validate_morphology, convert_to_mpc, redshift_to_velocity, is_galaxy


class GalaxyData:
    """
    Galaxy positions based on actual RA/Dec and redshift data.
    
    Coordinate conventions (astronomically correct):
    - +X = East
    - +Y = North
    - +Z = Away from Earth
    """
    # Define the structure once
    GalaxyAttr = [
        'RA', 'DEC', 'VEL', 'DIS', 'RED', 'MORPH',
        'ANGULAR_SIZE_ARCMIN', 'SIZE_KPC'
    ]
    # Regular class attributes
    objects: ClassVar[List[str]] = []
    DEGREE_TO_KPC: ClassVar[Optional[float]] = None
    MEAN_DISTANCE: ClassVar[Optional[float]] = None
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Create dictionary attributes dynamically
        for attr_name in cls.GalaxyAttr:
            if not hasattr(cls, attr_name):
                setattr(cls, attr_name, {})
    

    
    @classmethod
    def load_from_simbad(cls, names: List[str]) -> None:
        """Query SIMBAD for all galaxies."""
        cls.objects = names
        simbad = Simbad()
        simbad.add_votable_fields('otype', 'morphtype', 'dim', 'mesrot',
                                  'mesdistance', 'rvz_redshift', 'velocity')
        simbad.TIMEOUT = 30
        
        print("=" * 80)
        print("QUERYING SIMBAD")
        print("=" * 80)
        
        to_be_deleted={}
        for gal in names:
            to_be_deleted[gal]=cls._query_one_galaxy(gal, simbad)
        
        # Keep only galaxies where to_be_deleted[name] is False
        
        # Remove from each dictionary
        for galaxy_name in cls.objects:
            if to_be_deleted[galaxy_name]==True:        	    
                for attr in cls.GalaxyAttr:
                    dict_obj = getattr(cls, attr)
                    if galaxy_name in dict_obj:                	
                        del dict_obj[galaxy_name]
                   
        # Remove from list of galaxies
        cls.objects = [name for name in cls.objects if not to_be_deleted.get(name, False)]
        	
        cls._process_none_size()
        
        if len(cls.objects) == 0:
        	    print("=" * 80)
        	    sys.exit(f"❌ Not enough galaxies to generate the visualization")
        	    	
        cls._calculate_derived_values()
    
    @classmethod
    def _process_none_size(cls):
        """Check sizes and assigns the mean for the galaxies without size."""
    	    
        # Extract all known sizes
        existing_sizes = [size for size in cls.SIZE_KPC.values() if size is not None]
        
        # Compute mean
        if len(existing_sizes) > 0:
            mean_size = sum(existing_sizes) / len(existing_sizes)
        else:
        	    mean_size = 10.0
        
        # Fill missing sizes with the mean
        for name, size in cls.SIZE_KPC.items():
            if size is None:
                cls.SIZE_KPC[name] = mean_size
                
    
    @classmethod
    def _query_one_galaxy(cls, name: str, simbad: Simbad) -> None:
        """Query a single galaxy from SIMBAD. Returns if it must be deleted from list"""
        result = simbad.query_object(name)
        
        if result is None or len(result) == 0:
            print(f"  ❌ {name} not recognised")            
            print(f"  ⚠ {name} will be deleted from galaxy list")
            return True
        
        if not is_galaxy(result['otype'][0]):           
            print(f"  ❌ {name} is not a galaxy")
            print(f"  ⚠ {name} will be deleted from galaxy list")
            return True
        
        print(f"✓ Data retrieved for {name}")
        
        # Extract RA/DEC data
        cls.RA[name] = np.nanmedian(np.array(result['ra'])) / 15.0  # hours
        cls.DEC[name] = np.nanmedian(np.array(result['dec']))
        
        if cls.RA[name] is None or cls.DEC[name] is None:
            print(f"  ❌ {name} has not assigned coordinates")
            print(f"  ⚠ {name} will be deleted from galaxy list")
            return True 
                        
        # Process distance
        dist_values = []
        for i in range(len(np.array(result['mesdistance.unit']))):
            dist = convert_to_mpc(
                np.array(result['mesdistance.dist'])[i],
                np.array(result['mesdistance.unit'])[i]
            )
            dist_values.append(dist)
        if all(np.isnan(dist_values) for dist_values in dist_values):
            cls.DIS[name] = None
        else:
            cls.DIS[name] = np.nanmedian(dist_values)
            
        if cls.DIS[name] is None:
            print(f"  ❌ {name} has not assigned distance")
            print(f"  ⚠ {name} will be deleted from galaxy list")
            return True
          
        # Redshift and velocity
        cls.RED[name] = np.nanmedian(np.array(result['rvz_redshift']))
        cls.VEL[name] = redshift_to_velocity(cls.RED[name])
        
        # Morphology - WITH VALIDATION
        raw_morph = result['morph_type'][0]
        cls.MORPH[name] = validate_morphology(raw_morph)
        
        # Extract size ---
        angular_size = extract_angular_size(result)
        cls.ANGULAR_SIZE_ARCMIN[name] = angular_size
        
        if angular_size is not None and cls.DIS[name] is not None and not np.isnan(cls.DIS[name]):
            cls.SIZE_KPC[name] = angular_size_to_kpc(angular_size, cls.DIS[name])
            print(f"  ✓ Size: {cls.SIZE_KPC[name]:.1f} kpc (from {angular_size:.2f} arcmin)")
        else:
            cls.SIZE_KPC[name] = None            
            print(f"  ❌ No size data available. Assuming the mean of the group")
        return False
        
       
    
    @classmethod
    def _calculate_derived_values(cls) -> None:
        """Calculate derived quantities."""
        distances = list(cls.DIS.values())
        
        mean_distance_mpc = np.nanmean(distances)
        cls.MEAN_DISTANCE = mean_distance_mpc
        
        # Convert to kpc for calculations
        mean_distance_kpc = mean_distance_mpc * Config.KPC_PER_MPC
        cls.DEGREE_TO_KPC = Config.DEG_TO_RAD * mean_distance_kpc
    
    @classmethod
    def get_positions(cls) -> Dict[str, np.ndarray]:
        """Get galaxy positions relative to group center."""
        rel_positions, rel_scopes = cls._get_positions_relative_to_first()
        center = cls._get_center(rel_positions)
        posit = {name: pos - center for name, pos in rel_positions.items()}
        scope = {name: sco for name, sco in rel_scopes.items()}
        return posit, scope
    
    
    @classmethod
    def _get_positions_relative_to_first(cls) -> Dict[str, np.ndarray]:
        """Calculate positions relative to first galaxy."""
        ra_deg = {name: hours * 15 for name, hours in cls.RA.items()}
       
        ref_name = cls.objects[0]
        ra_ref = ra_deg[ref_name]
        dec_ref = cls.DEC[ref_name]
        vel_ref = cls.VEL[ref_name]
        
        positions = {}
        halfsizes = {}
        for name in cls.objects:
            # RA offset: positive = East
            ra_offset_deg = ra_deg[name] - ra_ref
            ra_offset_kpc = (ra_offset_deg * cls.DEGREE_TO_KPC * 
                           np.cos(np.radians(dec_ref)))
            
            # Dec offset: positive = North
            dec_offset_deg = cls.DEC[name] - dec_ref
            dec_offset_kpc = dec_offset_deg * cls.DEGREE_TO_KPC
            
            # Z offset: positive = away from Earth
            z_offset_kpc = (cls.VEL[name] - vel_ref) * 0.1
            
            positions[name] = np.array([ra_offset_kpc, dec_offset_kpc, z_offset_kpc])
            halfsizes[name] = 0.5*cls.SIZE_KPC[name]
        
        return positions,halfsizes
    
    @staticmethod
    def _get_center(positions: Dict[str, np.ndarray]) -> np.ndarray:
        """Calculate centroid of positions."""
        return np.mean(list(positions.values()), axis=0)
    
    @classmethod
    def verify_conventions(cls) -> None:
        """Verify all astronomical conventions."""
        positions,scopes = cls.get_positions()
        
        print("\n" + "=" * 80)
        print("SIGN CONVENTION VERIFICATION")
        print("=" * 80)
        print("\nCOORDINATE SYSTEM:")
        print("  +X = EAST, +Y = NORTH, +Z = AWAY from Earth")
        print("\nGALAXY POSITIONS (relative to center):")
        print("-" * 80)
        
        for name, pos in positions.items():
            ew = "EAST" if pos[0] > 0 else "WEST"
            ns = "NORTH" if pos[1] > 0 else "SOUTH"
            visual_x = "LEFT" if pos[0] > 0 else "RIGHT"
            visual_y = "UP" if pos[1] > 0 else "DOWN"
            
            print(f"\n{name} ({cls.MORPH[name]}):")
            print(f"  True: X={pos[0]:6.1f} kpc ({ew}), Y={pos[1]:6.1f} kpc ({ns})")
            print(f"  Appears: {visual_y}, {visual_x}")
            print(f"  RA: {CoordinateFormatter.ra_to_hms(cls.RA[name])}")
            print(f"  Dec: {CoordinateFormatter.dec_to_dms(cls.DEC[name])}")
            print(f"  Vel: {cls.VEL[name]:6.1f} km/s")
            print(f"  Dist: {cls.DIS[name]:6.1f} Mpc")
            print(f"  z: {cls.RED[name]:6.5f}")

            if name in cls.ANGULAR_SIZE_ARCMIN and cls.ANGULAR_SIZE_ARCMIN[name] is not None:
            	    print(f"  Physical size: {cls.SIZE_KPC[name]:.1f} kpc")
            	    print(f"    (from {cls.ANGULAR_SIZE_ARCMIN[name]:.2f} arcmin)")
            else:
            	    print(f"  Physical size: Not available - Assumed {cls.SIZE_KPC[name]:.1f} kpc")
        