"""Configuration settings for the galaxy visualizer."""

class Config:
    """Plot configuration settings."""
    
    # Figure
    FIG_SIZE = (12, 9)
    
    # Size of the center mark    
    CENTER_SIZE = 150
    
    GROUP_NAME = "Galaxy Group"
    
    # Colors
    COLORS = {
        "center": "#FF8C00",     # Dark orange
        "earth": "#FF8C00",      # Dark orange
        "connection": "#9370DB"   # Medium purple
    }
    
    # Zoom
    ZOOM_SCALE = 1.2
    
    # Physical constants
    C_LIGHT = 299792.458  # km/s
    DEG_TO_RAD = 0.017453293
    KPC_PER_MPC = 1000
