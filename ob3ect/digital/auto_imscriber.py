#!/usr/bin/env python3
import hashlib, os, pathlib, re, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frob import frobenius_phase


class AutoImscriber:
    def __init__(self, description: str):
        self.description = description.strip()
        self.name        = self._make_name()
        self.keywords    = self._extract_keywords()

    def _make_name(self) -> str:
        base  = self.description.split("—")[0].strip()
        clean = re.sub(r"[^a-zA-Z0-9]", "", base)
        return clean + "Ob3ect"

    def _extract_keywords(self):
        lower    = self.description.lower()
        keywords = []
        if any(w in lower for w in ["hopf", "antipode", "invert"]):      keywords.append("inversion")
        if any(w in lower for w in ["monad", "bind", "unit"]):           keywords.append("monadic")
        if any(w in lower for w in ["frobenius", "split", "fuse"]):      keywords.append("frobenius")
        if any(w in lower for w in ["topos", "classifier", "logic"]):    keywords.append("logical")
        if any(w in lower for w in ["quantum", "superposition", "meas"]):keywords.append("quantum")
        if any(w in lower for w in ["linear", "resource", "clone"]):     keywords.append("resource")
        if any(w in lower for w in ["hott", "path", "univalence"]):      keywords.append("higher")
        return keywords or ["general"]

    def generate(self) -> str:
        return f'''#!/usr/bin/env python3
"""
{self.description}

Auto-imscribed on {datetime.now().strftime("%Y-%m-%d")}
"""
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import frobenius_phase

class {self.name}:
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def verify(self) -> bool:
        print(f"=== {{self.__class__.__name__}} ===")
        frob_ok = frobenius_phase(self.source)
        print(f"Closure: {{frob_ok}}")
        return frob_ok

if __name__ == "__main__":
    sys.exit(0 if {self.name}().verify() else 1)
'''

    def save(self):
        folder     = self.name.lower().replace("ob3ect", "")
        target_dir = pathlib.Path(__file__).parent / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / f"{folder}_ob3ect.py"
        target_file.write_text(self.generate())
        print(f"New ob3ect imscribed → {target_file}")


class MetaAutoImscriberOb3ect:
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def verify(self) -> bool:
        print("=== Meta Auto-Imscriber Ob3ect ===")
        # Self-imscription: the imscriber can imscribe its own source
        frob_ok = frobenius_phase(self.source)
        # Generation check: produce a stub and verify it parses cleanly
        stub = AutoImscriber("TestStub — auto-generated self-imscription").generate()
        import ast
        parse_ok = True
        try:
            ast.parse(stub)
        except SyntaxError:
            parse_ok = False
        print(f"  Generated stub parses : {parse_ok}")
        closure = frob_ok and parse_ok
        print(f"Closure: {closure}")
        return closure


if __name__ == "__main__":
    if len(sys.argv) > 1:
        AutoImscriber(" ".join(sys.argv[1:])).save()
    else:
        sys.exit(0 if MetaAutoImscriberOb3ect().verify() else 1)
