# risnaberti/nanumber/core.py
import re
from datetime import datetime
from .exceptions import TemplateError, TemplateNotFoundError

PLACEHOLDER_RE = re.compile(r"\{([^}]+)\}")


class NumberGenerator:
    """
    Universal auto-number generator with customizable templates.
    
    Supports placeholders:
    - {Y}: 4-digit year (2025)
    - {y}: 2-digit year (25)
    - {m}: 2-digit month (01-12)
    - {d}: 2-digit day (01-31)
    - {H}: 2-digit hour (00-23)
    - {M}: 2-digit minute (00-59)
    - {S}: 2-digit second (00-59)
    - {number}: Auto-incrementing number with padding
    
    Example:
        >>> from risnaberti.nanumber import NumberGenerator, SQLAlchemyStorage
        >>> storage = SQLAlchemyStorage("sqlite:///nanumber.db")
        >>> gen = NumberGenerator(storage)
        >>> gen.generate("invoice", "INV-{Y}-{number}", pad=5)
        'INV-2025-00001'
    """
    
    def __init__(
        self, 
        storage, 
        default_pad: int = 4, 
        default_pad_char: str = "0", 
        default_pad_side: str = "left", 
        templates: dict = None
    ):
        """
        Initialize NumberGenerator.
        
        Args:
            storage: Storage backend (MemoryStorage or SQLAlchemyStorage)
            default_pad: Default padding length for numbers (default: 4)
            default_pad_char: Character for padding (default: "0")
            default_pad_side: Padding side "left" or "right" (default: "left")
            templates: Dict of predefined templates per entity
        
        Example with templates:
            >>> templates = {
            ...     "invoice": {
            ...         "template": "INV-{Y}-{number}",
            ...         "pad": 5,
            ...         "pad_char": "0",
            ...         "pad_side": "left"
            ...     }
            ... }
            >>> gen = NumberGenerator(storage, templates=templates)
            >>> gen.generate("invoice")  # Uses predefined template
        """
        self.storage = storage
        self.default_pad = default_pad
        self.default_pad_char = default_pad_char
        self.default_pad_side = default_pad_side
        self.templates = templates or {}

    def _pad(self, value: int, pad: int, pad_char: str, pad_side: str) -> str:
        """Apply padding to number value."""
        s = str(value)
        if pad_side == "right":
            return s.ljust(pad, pad_char)[:pad]
        return s.rjust(pad, pad_char)[-pad:]

    def _render(
        self, 
        template: str, 
        number_val: int, 
        date: datetime, 
        pad: int, 
        pad_char: str, 
        pad_side: str
    ) -> str:
        """Render template with placeholder replacements."""
        replacements = {
            "Y": f"{date.year:04d}",
            "y": f"{date.year % 100:02d}",
            "m": f"{date.month:02d}",
            "d": f"{date.day:02d}",
            "H": f"{date.hour:02d}",
            "M": f"{date.minute:02d}",
            "S": f"{date.second:02d}",
            "number": self._pad(number_val, pad, pad_char, pad_side),
        }
        
        def repl(m):
            token = m.group(1)
            if token not in replacements:
                valid_placeholders = ", ".join(f"{{{k}}}" for k in replacements.keys())
                raise TemplateError(
                    f"Unknown placeholder: {{{token}}}. "
                    f"Valid placeholders: {valid_placeholders}"
                )
            return replacements[token]
        
        return PLACEHOLDER_RE.sub(repl, template)

    def generate(
        self, 
        key: str, 
        template: str = None, 
        pad: int = None, 
        pad_char: str = None, 
        pad_side: str = None, 
        date: datetime = None
    ) -> str:
        """
        Generate auto-number for given key.
        
        Args:
            key: Unique identifier for number sequence
            template: Format template (uses predefined if None)
            pad: Number padding length
            pad_char: Character for padding
            pad_side: "left" or "right"
            date: Date for placeholders (default: now)
        
        Returns:
            Generated number string
        
        Raises:
            TemplateNotFoundError: If key not in templates and template not provided
            TemplateError: If template contains invalid placeholders
        
        Example:
            >>> gen.generate("invoice", "INV-{Y}-{number}", pad=5)
            'INV-2025-00001'
        """
        date = date or datetime.now()
        
        # Load from predefined templates if available
        if template is None:
            if key not in self.templates:
                raise TemplateNotFoundError(
                    f"Template '{key}' not found and no template provided. "
                    f"Available templates: {list(self.templates.keys()) or 'None'}"
                )
            
            cfg = self.templates[key]
            template = cfg.get("template")
            pad = pad if pad is not None else cfg.get("pad", self.default_pad)
            pad_char = pad_char if pad_char is not None else cfg.get("pad_char", self.default_pad_char)
            pad_side = pad_side if pad_side is not None else cfg.get("pad_side", self.default_pad_side)
        
        # Use defaults if not specified
        pad = pad if pad is not None else self.default_pad
        pad_char = pad_char or self.default_pad_char
        pad_side = pad_side or self.default_pad_side

        # Get next number from storage
        next_val = self.storage.increment(key)
        
        return self._render(template, next_val, date, pad, pad_char, pad_side)

    def reset(self, key: str, value: int = 0):
        """
        Reset number sequence for given key.
        
        Args:
            key: Unique identifier for number sequence
            value: Reset to this value (default: 0)
        
        Example:
            >>> gen.reset("invoice", 0)  # Next generate will be 1
        """
        self.storage.reset(key, value)