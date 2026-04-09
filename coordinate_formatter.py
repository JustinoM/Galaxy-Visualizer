"""Coordinate formatting utilities."""
import numpy as np

class CoordinateFormatter:
    """Format astronomical coordinates."""
    
    @staticmethod
    def ra_to_hms(ra_hours: float) -> str:
        """Convert RA from decimal hours to HMS format."""
        if ra_hours is None or np.isnan(ra_hours):
            return "Unknown"
        
        h = int(ra_hours)
        m = int((ra_hours - h) * 60)
        s = ((ra_hours - h) * 60 - m) * 60
        
        return f"{h:02d}h {m:02d}m {s:04.1f}s"
    
    @staticmethod
    def dec_to_dms(dec_deg: float) -> str:
        """Convert Dec from decimal degrees to DMS format."""
        if dec_deg is None or np.isnan(dec_deg):
            return "Unknown"
        
        sign = "+" if dec_deg >= 0 else "-"
        abs_dec = abs(dec_deg)
        
        d = int(abs_dec)
        m = int((abs_dec - d) * 60)
        s = ((abs_dec - d) * 60 - m) * 60
        
        return f"{sign}{d:02d}° {m:02d}' {s:04.1f}\""
