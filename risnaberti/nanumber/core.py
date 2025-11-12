# nanumber/core.py
import re
from datetime import datetime
from .exceptions import TemplateError

PLACEHOLDER_RE = re.compile(r"\{([^}]+)\}")

class NumberGenerator:
    def __init__(self, storage, default_pad=4, default_pad_char="0", default_pad_side="left", templates=None):
        self.storage = storage
        self.default_pad = default_pad
        self.default_pad_char = default_pad_char
        self.default_pad_side = default_pad_side
        self.templates = templates or {}

    def _pad(self, value: int, pad:int, pad_char:str, pad_side:str) -> str:
        s = str(value)
        if pad_side == "right":
            return s.ljust(pad, pad_char)[:pad]
        return s.rjust(pad, pad_char)[-pad:]

    def _render(self, template: str, number_val: int, date: datetime, pad, pad_char, pad_side):
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
                raise TemplateError(f"Unknown placeholder: {{{token}}}")
            return replacements[token]
        return PLACEHOLDER_RE.sub(repl, template)

    def generate(self, key: str, template: str = None, pad: int = None, pad_char: str = None, pad_side: str = None, date: datetime = None) -> str:
        date = date or datetime.now()
        # load default template if provided via templates dict
        if template is None and key in self.templates:
            cfg = self.templates[key]
            template = cfg.get("template")
            pad = pad if pad is not None else cfg.get("pad", self.default_pad)
            pad_char = pad_char if pad_char is not None else cfg.get("pad_char", self.default_pad_char)
            pad_side = pad_side if pad_side is not None else cfg.get("pad_side", self.default_pad_side)
        pad = pad if pad is not None else self.default_pad
        pad_char = pad_char or self.default_pad_char
        pad_side = pad_side or self.default_pad_side

        next_val = self.storage.increment(key)
        return self._render(template, next_val, date, pad, pad_char, pad_side)

    def reset(self, key: str, value: int = 0):
        self.storage.reset(key, value)
