"""Galaxy rendering in 3D."""
import numpy as np
from typing import Tuple, Optional
import matplotlib.pyplot as plt

from morphology_parser import MorphologyParser
from galaxy_generator import generate_sphere, generate_spiral_galaxy, generate_elliptic_galaxy, generate_3d_irregular_galaxy

class GalaxyRenderer:
    """Render different galaxy types in 3D."""
    
    @staticmethod
    def render(ax, pos: np.ndarray, name: str, morph_code: str, size: float, color: str, 
               config, box_limits: Tuple[float, float, float]) -> None:
        """Render appropriate galaxy type based on morphology."""
        galaxy_type, barred, param = MorphologyParser.parse(morph_code)
        
        # Default: plot center
        plot_center = True
        
        if galaxy_type == 'S':
            GalaxyRenderer._render_spiral(ax, pos, size, barred, param, color, config, box_limits)
            plot_center = not barred
        
        elif galaxy_type in ('E', 'L'):
            GalaxyRenderer._render_elliptical(ax, pos, size, galaxy_type, param, color, config)
            plot_center = (galaxy_type == 'E')
        
        elif galaxy_type == 'I':
            GalaxyRenderer._render_irregular(ax, pos, size, color, config, box_limits)
            plot_center = False
            
        elif galaxy_type == 'U':
        	    size=size/0.1
        	    
        # Plot center if needed (0.1-> 10% of the total size for S and E)
        if plot_center:
            GalaxyRenderer._plot_center(ax, pos, size*0.1, color, config, box_limits)
        
        # Picker to whow info
        #sc = ax.scatter(*pos, picker=True, s=300)
        # Add label
        ax.text(*pos, f"       {name}", color=color, fontsize=11, weight='bold')
    
    @staticmethod
    def _render_spiral(ax, pos, size: float, barred: bool, param: Optional[int], color: str,
                       config, box_limits) -> None:
        """Render spiral galaxy."""         
        tightness = 0.8 * (param if param is not None and param > 0 else 1)
        cycles = 0.5 if barred else 2
        
        generate_spiral_galaxy(
            ax, tuple(pos), size=size, arms=2, tightness=tightness,
            cycles=cycles, barred=barred, color=color
        )
    
    @staticmethod
    def _render_elliptical(ax, pos, size: float, galaxy_type: str, param: Optional[int],
                           color: str, config) -> None:
        """Render elliptical or lenticular galaxy."""
        alpha = 0.3 if galaxy_type == 'L' else 0.7
        ellipticity = param if param is not None else 0
        
        r = 0.5*size
        
        radii = [r, r * (1 - ellipticity * 0.1), r * 0.0]
        
        generate_elliptic_galaxy(
            ax, tuple(pos), radii, rotation_matrix=None,
            color=color, alpha=alpha, resolution=200
        )
    
    @staticmethod
    def _render_irregular(ax, pos, size: float, color: str, config, box_limits) -> None:
        """Render irregular galaxy."""
        # Use the 3D irregular galaxy generator
        generate_3d_irregular_galaxy(
            ax, center=tuple(pos), 
            size=size,  # Size in kpc
            color=color, 
            alpha=0.7, 
            n_points=500,
            irregularity=0.5  # More irregular
        )
        
        
    @staticmethod
    def _plot_center(ax, pos, size: float, color: str, config, box_limits) -> None:
        """Plot galaxy center sphere."""
        generate_sphere(
            ax, center=tuple(pos), box=box_limits, radius=0.5*size,
            color=color, alpha=0.5, n_meridians=50, n_circles=50
        )
