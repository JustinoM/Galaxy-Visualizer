"""Main plotting class for galaxy group visualization."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox, TextArea, VPacker, HPacker
from typing import Optional, Tuple, List

from galaxy_renderer import GalaxyRenderer
from galaxy_generator import generate_sphere
from coordinate_formatter import CoordinateFormatter
from morphology_parser import MorphologyParser  
import time
import os
        

class GroupPlotter:
    """Create 3D visualization of a galaxy group."""
    
    def __init__(self, config, galaxy_data):
        """
        Initialize the plotter.
        
        Parameters:
        -----------
        config : Config
            Configuration object
        galaxy_data : GalaxyData
            Galaxy data object
        """
        self.config = config
        self.galaxy_data = galaxy_data
        self.fig = None
        self.ax = None
        self.positions,self.scopes = galaxy_data.get_positions()        
        self.box_limits = (1.0, 1.0, 1.0)
        self.help_text = None
        self._original_limits = None
        self.mouse = (0.0,0.0,0.0)
        
        # For click interaction
        self.pickable_points = None
        self.current_annotation = None
        self.current_galaxy = None
        self._just_picked = False
        self._last_pick_time = 0
        
        
    def plot(self) -> None:
        """Create the complete visualization."""
        self._setup_figure()
        self._setup_axes()        
        self._plot_galaxies()
        self._plot_center()        
        if len(self.galaxy_data.objects) > 1:
        		self._plot_polygon() 
        self._plot_earth()
        self._enable_interaction()
        
        plt.tight_layout()
    
    def _setup_figure(self) -> None:
        import matplotlib
        matplotlib.rcParams['toolbar'] = 'None'

        """Create figure and 3D axes."""
        self.fig = plt.figure(figsize=self.config.FIG_SIZE)
        self.ax = self.fig.add_subplot(111, projection="3d")
    
    def _setup_axes(self) -> None:
        """Configure axes labels and limits."""
        # Get all coordinates and scopes
        all_coords = np.array(list(self.positions.values()))
        all_scopes = np.array(list(self.scopes.values()))
        
        # Create sign array with same shape as all_coords
        signs = np.where(all_coords >= 0, 1, -1)  # Shape: (n, 3)

        # Reshape all_scopes for broadcasting: (n,) -> (n, 1)
        scopes_reshaped = all_scopes.reshape(-1, 1)  # Shape: (n, 1)

        # Apply operation
        sponge_coords = all_coords + signs * scopes_reshaped
        
        max_abs = np.max(np.abs(sponge_coords), axis=0)
        
        offset = 0.3 
        
        limitx = max_abs[0] * (1.0 + offset)
        limity = max_abs[1] * (1.0 + offset)
        limitz = max_abs[2] * (1.0 + offset)
        
        # Allow asymmetry for better visualization
        max_pos = np.max(sponge_coords, axis=0)
        limitzpos = max_pos[2] * (1.0 + offset)
        
        self.ax.set_xlim(-limitx, limitx)
        self.ax.set_ylim(-limity, limity)
        self.ax.set_zlim(-limitz, limitzpos)
        
        self.box_limits = (2*limitx, 2*limity, limitz + limitzpos)
        
        # Labels
        self.ax.set_xlabel('ΔX (+east) [kpc]', fontsize=11, labelpad=10)
        self.ax.set_ylabel('ΔY (+north) [kpc]', fontsize=11, labelpad=10)
        self.ax.set_zlabel('ΔZ (+away from Earth) [kpc]', fontsize=11, labelpad=10)
        
        # Title
        self.ax.set_title(self.config.GROUP_NAME, fontsize=14, weight='bold', pad=20)
        
        # Initial view
        self.ax.view_init(elev=-20, azim=145, roll=-60)
        self.ax.set_aspect('auto')
        self.ax.grid(True, alpha=0.3)
        
        # Help text
        self._add_help_text()
    
    def _add_help_text(self) -> None:
        """Add help text overlay."""
        help_note = (
            "Earth's position is not at scale, galactic structures\n"
            "are only indicative of the morphology, not orientation.\n"
            "Galactic size is orientative (only in XY plane)\n\n"
            "Use mouse to rotate, wheel to zoom, and click on\n"
            "galaxies to see their information\n\n"
            "Hot Keys\n"
            "   t: toggle this text\n"
            "   r: reset view\n"
            "   h: Earth view\n"
            "   z: Side view\n"
            "   a: toggle aspect ratio\n"
            "   ↑↓: change elevation\n"
            "   ←→: change azimuth\n"
            "   Ctrl+←→: change roll\n\n"
            "Justino @justino.info, 2026"
        )
        
        self.help_text = self.ax.text2D(
            0.5, 1.0, help_note,
            transform=self.ax.transAxes,
            fontsize=12, color='white', fontweight='bold',
            fontfamily='monospace',linespacing=1.5,
            bbox=dict(
            	    boxstyle='round,pad=0.5', 
            	    facecolor='black',             	    
            	    edgecolor='yellow',
                alpha=0.9,
                zorder=900000),
            zorder=900000,
            verticalalignment='top', horizontalalignment='left',
            visible=True
        )

    # ============================================================================
    # GALAXY PLOTTING METHODS
    # ============================================================================
    
    def _plot_galaxies(self) -> None:
        """Plot all galaxies and make them pickable."""
        # Lists for pickable points
        x_vals = []
        y_vals = []
        z_vals = []
        galaxy_list = []
        
        for name, pos in self.positions.items():
            x_vals.append(pos[0])
            y_vals.append(pos[1])
            z_vals.append(pos[2])
            galaxy_list.append(name)
            
            # Render the actual galaxy
            color = self.config.COLORS[name]
            morph_code = self.galaxy_data.MORPH[name]
            galaxy_size = self.galaxy_data.SIZE_KPC[name]
            GalaxyRenderer.render(
                self.ax, pos, name, morph_code, size=galaxy_size, color=color, 
                config=self.config, box_limits=self.box_limits
            )            
        # Create invisible pickable points (for click detection)
        self.pickable_points = self.ax.scatter(
            x_vals, y_vals, z_vals,
            alpha=0.0,                  # Completely invisible
            picker=True,                 # Enable picking
            pickradius=15                 # How close click needs to be (in pixels)
        )
        
        # Store galaxy names with the pickable points
        self.pickable_points.galaxy_names = galaxy_list
       
    
    

    
    def _plot_center(self) -> None:
        """Plot group center marker."""
        self.ax.scatter(0, 0, 0,
                       marker='+', color=self.config.COLORS['center'],
                       s=self.config.CENTER_SIZE, linewidth=2, depthshade=False)
        self.ax.text(0, 0, 5, '  Center', color=self.config.COLORS['center'],
                    fontsize=10)
    
    def _plot_polygon(self) -> None:
        """Draw polygon connecting galaxies."""
        names = list(self.positions.keys())
        coords = [self.positions[n] for n in names]
        N=len(names) 
        if N==2:
        	    M=1
        else:
        		M=N
        for i in range(M):
            j = (i + 1) % N
            p1, p2 = coords[i], coords[j]
            
            # Draw edge
            self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                        '--', color=self.config.COLORS['connection'],
                        linewidth=1.5, alpha=0.6)
                        
            # Distance label
            mid = (p1 + p2) / 2
            
            if N==2: # 2 galaxies, the "middle" is just over the center mark
                mid=(p1*1.9 + p2*2.1)/2 
                
            dist = np.linalg.norm(p2 - p1)
            unit = 'kpc'
            if dist > 1000:
                dist /= 1000
                unit = 'mpc'
            
            self.ax.text(*mid, f"{dist:.0f} {unit}",
                        color=self.config.COLORS['connection'],
                        fontsize=9, ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.2',
                                 facecolor='white', alpha=0.7))
            # Do not repeat with N=2
            if N==2:
            	    break
    
    def _plot_earth(self) -> None:
        """Plot Earth marker and view direction."""
        earth_pos = np.array([0, 0, -1.5 * self.box_limits[2]])
        
        # Earth marker
        self.ax.scatter(*earth_pos, marker='o', color=self.config.COLORS['earth'],
                       s=200, alpha=0.7, depthshade=False, zorder=1000)
        
        # Label
        labelpos = earth_pos + np.array([0, 0.1 * self.box_limits[1], 0])
        self.ax.text(*labelpos, 'EARTH', color=self.config.COLORS['earth'],
                    fontsize=12, weight='bold', ha='center', va='top', zorder=1000)
        
        # Line to center
        self.ax.plot([0, earth_pos[0]], [0, earth_pos[1]], [0, earth_pos[2]],
                    '--', color=self.config.COLORS['earth'],
                    linewidth=1.5, alpha=0.6)
        
        # Distance label
        mid = earth_pos / 2
        self.ax.text(*mid, f"{self.galaxy_data.MEAN_DISTANCE:.0f} mpc",
                    color=self.config.COLORS['earth'], fontsize=9,
                    ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
	
    # ============================================================================
    # INTERACTION METHODS
    # ============================================================================
    
    def _enable_interaction(self) -> None:
        """Enable keyboard and mouse interaction."""
        self._store_original_limits()
        
        self._connect_zoom()
        self._connect_keyboard()
        self._track_view_angles() 
        
        # Connect pick events for galaxy selection
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Connect background click to hide info
        self.fig.canvas.mpl_connect('button_press_event', self.on_background_click)
        
    def _store_original_limits(self) -> None:
        """Store original view limits for reset."""
        self._original_limits = (
            self.ax.get_xlim3d(),
            self.ax.get_ylim3d(),
            self.ax.get_zlim3d(),
            self.ax.elev, self.ax.azim, self.ax.roll
        )
    
    def _connect_zoom(self) -> None:
        """Connect mouse wheel zoom event."""
        def on_scroll(event):
            scale = 1/self.config.ZOOM_SCALE if event.button == 'up' else self.config.ZOOM_SCALE            
            for getter, setter in [
                (self.ax.get_xlim3d, self.ax.set_xlim3d),
                (self.ax.get_ylim3d, self.ax.set_ylim3d),
                (self.ax.get_zlim3d, self.ax.set_zlim3d)
            ]:
                limits = getter()
                mid = np.mean(limits)
                half = (limits[1] - limits[0]) * scale / 2
                setter([mid - half, mid + half])
            
            self.fig.canvas.draw_idle()
        
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)
    def _track_view_angles(self):
        """Print view angles when they change due to mouse interaction."""
        
        def on_motion(event):
            if event.inaxes != self.ax:
                return
            
            # Store current angles to compare with keyboard (this will print constantly during mouse move)
            self.mouse=(round(self.ax.elev,0),round(self.ax.azim,0),round(self.ax.roll,0))
            
        
        self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
    
    def _connect_keyboard(self) -> None:
        """Connect keyboard events with proper angle bounds."""
        def on_key_press(event):                        
            # Apply changes based on key
            if event.key in ('r', 'R'):
                self._reset_view()
                return
            elif event.key in ('h', 'H'):
                self._earth_view()
                return
            elif event.key in ('z', 'Z'):
                self._side_view()
                return
            elif event.key in ('a', 'A'):
                self._toggle_aspect()
                return
            elif event.key in ('t', 'T'):
                if self.help_text:
                    self.help_text.set_visible(not self.help_text.get_visible())
                    self.fig.canvas.draw_idle()
                return
                
            # Movement   
            # Set the step change in degrees
            step=1
            
            # Get current angles
            
            elev = round(self.ax.elev,0)
            azim = round(self.ax.azim,0)
            roll = round(self.ax.roll,0)
            
            # Compare with the stored to detect discrepancies with mouse and correct
            rest=tuple(map(sum, zip(self.mouse, (-elev,-azim,-roll))))
            if rest != (0.0,0.0,0.0):
                self.ax.view_init(elev=self.mouse[0], azim=self.mouse[1], roll=self.mouse[2])
                self.fig.canvas.draw_idle()
                elev = round(self.ax.elev,0)
                azim = round(self.ax.azim,0)
                roll = round(self.ax.roll,0)
                
            
            if event.key == 'ctrl+left':
                roll -= step
            elif event.key == 'ctrl+right':
                roll += step
            elif event.key == 'left':
                azim -= step
            elif event.key == 'right':
                azim += step
            elif event.key == 'up':
                elev -= step
            elif event.key == 'down':
                elev += step            
            else:
                return  # No change needed
            
            
            self.ax.view_init(elev=elev, azim=azim, roll=roll)
            # Sometimes needed for 3D: force a redraw of the axes
            self.ax.stale = True
            self.fig.canvas.draw_idle()
            # Store the new
            self.mouse=(elev,azim,roll)
            
            
        self.fig.canvas.mpl_connect('key_press_event', on_key_press)
    
    
    def _reset_view(self) -> None:
        """Reset to original view."""
        if self._original_limits:
            self.ax.set_xlim3d(self._original_limits[0])
            self.ax.set_ylim3d(self._original_limits[1])
            self.ax.set_zlim3d(self._original_limits[2])
            self.ax.view_init(elev=self._original_limits[3],
                             azim=self._original_limits[4],
                             roll=self._original_limits[5])
            self.fig.canvas.draw_idle()
            self.mouse=(round(self.ax.elev,0),round(self.ax.azim,0),round(self.ax.roll,0))
    
    def _earth_view(self) -> None:
        """Set view from Earth direction."""
        self.ax.view_init(elev=-90, azim=90, roll=0)        
        self.fig.canvas.draw_idle()
        self.mouse=(round(self.ax.elev,0),round(self.ax.azim,0),round(self.ax.roll,0))

    def _side_view(self) -> None:
        """Set a side view with Earth at right."""
        self.ax.view_init(elev=0, azim=0, roll=90)        
        self.fig.canvas.draw_idle()
        self.mouse=(round(self.ax.elev,0),round(self.ax.azim,0),round(self.ax.roll,0))
    
    def _toggle_aspect(self) -> None:
        """Toggle between auto and equal aspect."""
        if self.ax.get_aspect() == 'auto':
            self.ax.set_aspect('equal')
        else:
            self.ax.set_box_aspect(None)
            self.ax.set_aspect('auto')
        self.fig.canvas.draw_idle()
        
    # ============================================================================
    # GALAXY INFO DISPLAY METHODS
    # ============================================================================
    
    def on_pick(self, event):
        """Handle pick events - toggle galaxy info when a galaxy is clicked."""
        # Only process if it's our pickable points
        if event.artist != self.pickable_points:
            return
        
        if len(event.ind) == 0:
            return
        
        # Set flag to prevent background click from removing
        self._just_picked = True
        self._last_pick_time = time.time()
        
        # Get the clicked galaxy
        idx = event.ind[0]
        galaxy_name = self.pickable_points.galaxy_names[idx]
        galaxy_pos = self.positions[galaxy_name]
        
        # Toggle logic
        if self.current_galaxy == galaxy_name:
            # Same galaxy clicked - hide the info
            self.hide_galaxy_info()
        else:
            # Different galaxy clicked - show new info
            self.show_galaxy_info(galaxy_name, galaxy_pos)
    
    def on_background_click(self, event):
        """Handle background clicks - hide info."""
        # Don't hide if we just picked a galaxy (within 0.3 seconds)
        if time.time() - self._last_pick_time < 0.3:
            return
        
        # Only process clicks in the axes
        if event.inaxes != self.ax:
            return
        
        # Hide any visible annotation
        self.hide_galaxy_info()
        
    def _get_galaxy_png(self, galaxy_name):
        """Get PNG for galaxy, with fallback options."""
        import os
        import matplotlib.image as mpimg
        
        # Define possible PNG locations
        possible_paths = [
            f"galaxy_images/{galaxy_name}.png"        
        ]
        
        # Try specific galaxy PNG
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    return mpimg.imread(path)
                except:
                    continue
        
        # Fallback to morphology-based PNG
        morph_code = self.galaxy_data.MORPH[galaxy_name]
        galaxy_type, barred, param = MorphologyParser.parse(morph_code)
        
        type_to_png = {
            'S': 'spiral.png',
            'E': 'elliptical.png',
            'L': 'lenticular.png',
            'I': 'irregular.png'
        }
        
        if barred and galaxy_type == 'S':
            type_to_png['S'] = 'barred_spiral.png'
        
        for path in possible_paths:
            generic_path = f"galaxy_images/{type_to_png.get(galaxy_type, 'unknown.png')}"
            if os.path.exists(generic_path):
                try:
                    return mpimg.imread(generic_path)
                except:
                    continue
        
        return None
        
    def _get_morphology_image_info(self, galaxy_name):
        """Return path to appropriate morphology image."""
        from morphology_parser import MorphologyParser
        
        morph_code = self.galaxy_data.MORPH[galaxy_name]
        galaxy_type, barred, _ = MorphologyParser.parse(morph_code)
        
        credits=""
        title=""
        # Map morphology to filename
        if galaxy_type == 'S':
            filename = 'barred_spiral.png' if barred else 'spiral.png'
            title="Spiral Galaxy M83"
            credits=("NASA, ESA, and the Hubble Heritage Team (STScI/AURA)\n"
                     "ACK: W. Blair (STScI/Johns Hopkins University) and R. O'Connell (University of Virginia)"
            )
            if barred:
                title="Barred Spiral Galaxy NGC 1300"
                credits=("NASA, ESA, and The Hubble Heritage Team (STScI/AURA)\n"
                         "ACK: P. Knezek (WIYN)"
                ) 
        elif galaxy_type == 'E':
            filename = 'elliptical.png'
            title="Elliptical Galaxy NGC 3610"
            credits=("Creator:  NASA Goddard Space Flight Center (GSFC)")
        elif galaxy_type == 'L':
            filename = 'lenticular.png'
            title="Lenticular Galaxy Mrk 820"
            credits=("Creator: NASA Goddard Space Flight Center (GSFC)")
        elif galaxy_type == 'I':
            filename = 'irregular.png'
            title="Irregular Galaxy NGC 5477"
            credits=("Creator: NASA Goddard Space Flight Center (GSFC)")
        else:
            filename = 'unknown.png'
        
        return f"galaxy_images/{filename}", title, credits
        
    def show_galaxy_info(self, galaxy_name, position):
        """Display galaxy information near the galaxy."""
        # Hide any existing annotation first
        self.hide_galaxy_info()
        
        # Format info text
        info = self._format_galaxy_info(galaxy_name)
        
          
        # Get image for this galaxy
        img_path, img_title, img_credits= self._get_morphology_image_info(galaxy_name)
        
        # Create text area
        text_area = TextArea(info, textprops=dict(
            color='white',
            fontsize=12,
            fontweight='bold',
            fontfamily='monospace',
            linespacing=1.5
        ))
        
        # Create image area if available
        if img_path and os.path.exists(img_path):
            import matplotlib.image as mpimg
            img = mpimg.imread(img_path)
            
            image_box = OffsetImage(img, zoom=0.5)  # Adjust zoom as needed
            image_box.set_figure(self.fig)
            
            # Pack text and image side by side
            Hpacked = HPacker(children=[image_box, text_area],
                    align='center',
                    pad=10,
                    sep=20)
            if img_title != "" or img_credits != "":
                info=f"Example: {img_title}\n\n{img_credits}"
                credits_area = TextArea(info, textprops=dict(
                    color='white',
                    fontsize=8,
                    fontweight='bold',
                    fontfamily='monospace',
                    linespacing=1.5,
                    ha='left'
                ))                
                # Pack image and title+credits in vertical
                packed = VPacker(children=[Hpacked, credits_area],
                                align='center',                                
                                pad=0,
                                sep=5)
            else:
                packed = Hpacked
        else:
            packed = text_area
    
        # Create annotation box with custom styling
        self.current_annotation = AnnotationBbox(
            packed,
            (0.3, 0.70),
            xycoords='axes fraction',
            frameon=True,
            pad=0.5,
            bboxprops=dict(
                boxstyle='round,pad=0.5',
                facecolor='black',
                edgecolor='yellow',
                alpha=0.9,
                zorder=1000000
            ),
            zorder=1000000
        )
        
        self.ax.add_artist(self.current_annotation)
  
        # Store the current galaxy name
        self.current_galaxy = galaxy_name
        
        self.fig.canvas.draw_idle()
    
    def hide_galaxy_info(self):
        """Hide the current galaxy information."""
        if self.current_annotation:
            try:
                self.current_annotation.remove()
            except:
                pass
            self.current_annotation = None
            
        # Remove PNG if present
        if hasattr(self, 'image_ab') and self.image_ab:
            try:
                self.image_ab.remove()
            except:
                pass
            self.image_ab = None
		
        
        self.current_galaxy = None
        self.fig.canvas.draw_idle()
        
         

       
    def _format_galaxy_info(self, galaxy_name):
        """Format galaxy information text."""
        ra_form=CoordinateFormatter.ra_to_hms(self.galaxy_data.RA[galaxy_name])
        dec_form=CoordinateFormatter.dec_to_dms(self.galaxy_data.DEC[galaxy_name])
        info = (
            f"{galaxy_name} ({self.galaxy_data.MORPH[galaxy_name]})\n"
            f"RA  : {ra_form}\n"
            f"Dec : {dec_form}\n"
            f"Dist: {self.galaxy_data.DIS[galaxy_name]:.1f} Mpc\n"
            f"Vel : {self.galaxy_data.VEL[galaxy_name]:6.1f} km/s\n"
            f"z   : {self.galaxy_data.RED[galaxy_name]:6.5f}"
        )
        
        # Add size if available
        if (hasattr(self.galaxy_data, 'SIZE_KPC') and 
            galaxy_name in self.galaxy_data.SIZE_KPC and
            self.galaxy_data.SIZE_KPC[galaxy_name] is not None):
            
            size = self.galaxy_data.SIZE_KPC[galaxy_name]
            info += f"\nSize: {self._format_size(size)}"
        else:
            info += f"\nSize: Unknown"
        
        return info
    
    def _format_size(self, size_kpc):
        """Format size for display."""
        if size_kpc is None:
            return "Unknown"
        if size_kpc < 1:
            return f"{size_kpc*1000:.0f} pc"
        elif size_kpc > 1000:
            return f"{size_kpc/1000:.2f} Mpc"
        else:
            return f"{size_kpc:.1f} kpc"
        
    # ============================================================================
    # DISPLAY METHODS
    # ============================================================================
        
    def show(self) -> None:
        """Display the plot."""
        plt.show()
    
    def save(self, filename: str, dpi: int = 300) -> None:
        """Save the plot."""
        self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
