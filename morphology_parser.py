"""Parse and classify SIMBAD morphology codes."""
import re
import pandas as pd
from typing import Tuple, Optional

class MorphologyParser:
    """Parse and classify SIMBAD morphology codes."""
    
    # Arm tightness mapping
    ARM_MAP = {
        'a': 0, 'ab': 5, 'b': 1, 'bc': 6,
        'c': 2, 'cd': 7, 'd': 3, 'dm': 8, 'm': 4
    }
    
    @classmethod
    def parse(cls, morph_code: Optional[str]) -> Tuple[str, Optional[bool], Optional[int]]:
        """
        Parse SIMBAD morphology code into components.
        
        Returns:
            (type_code, barred_status, tightness_or_ellipticity)
            type_code: 'E' (elliptical), 'S' (spiral), 'L' (lenticular), 
                      'I' (irregular), 'U' (unknown)
        """
        if morph_code is None or pd.isna(morph_code) or str(morph_code).strip() == '':
            return ('U', None, None)
        
        # Clean code
        code = cls._clean_code(str(morph_code))
        
        if code.startswith('d'): # dwarf: take the second char
        		code=code[1:]
        # Check types in order
        if code.startswith(('S0', 'SB0', 'SAB0')):
            return ('L', None, None)
        
        if code.startswith('E'):            
            return cls._parse_elliptical(code)
        
        if code.startswith(('I', 'Irr')):
            return ('I', None, None)
        
        
        if 'S' in code:
            return cls._parse_spiral(code)
        
        return ('U', None, None)
    
    @classmethod
    def _clean_code(cls, code: str) -> str:
        """Remove quality flags and modifiers."""
        code = code.split(':')[0]
        return code.replace('pec', '').replace('?', '').replace('p', '').strip()
    
    @classmethod
    def _parse_elliptical(cls, code: str) -> Tuple[str, None, Optional[int]]:
        """Parse elliptical galaxy code."""
        match = re.search(r'E([0-7]?)', code)
        
        if match and match.group(1):
            return ('E', None, int(match.group(1)))
        return ('E', None, None)
    
    @classmethod
    def _parse_spiral(cls, code: str) -> Tuple[str, bool, int]:
        """Parse spiral galaxy code."""
        barred = code.startswith(('SB', 'SAB'))
        
        # Extract spiral part
        if code.startswith('SB'):
            spiral_part = code[2:]
        elif code.startswith('SAB'):
            spiral_part = code[3:]
        elif code.startswith('SA'):
            spiral_part = code[2:]
        else:
            spiral_part = code[1:]
        
        # Remove ring modifiers
        spiral_part = re.sub(r'\([rs]+\)', '', spiral_part)
        spiral_part = spiral_part.replace('r', '').replace('s', '').replace('rs', '')
        
        # Find arm type
        for arm_code, num_value in cls.ARM_MAP.items():
            if arm_code in spiral_part:
                return ('S', barred, num_value)
        
        # Default to type b
        return ('S', barred, 1)
