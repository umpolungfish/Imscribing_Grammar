"""Smoke test: produce ob3ects in all 8 domains."""
import sys
sys.path.insert(0, "..")
from core import Ob3ectFactory, DOMAIN_TEMPLATES

Ob3ectFactory.register_all()
print("Available domains:", Ob3ectFactory.available_domains())
errors = []
for dtype in Ob3ectFactory.available_domains():
    try:
        a = Ob3ectFactory.produce("test_%s" % dtype, dtype)
        print("  %-15s -> valid=%s, frobenius=%s" % (dtype, a.is_valid_ob3ect, a.split_fuse_report.frobenius_verdict))
        if not a.is_valid_ob3ect:
            bad = [k for k, vv in a.validate_all().items() if vv]
            errors.append("%s fails phases: %s" % (dtype, bad))
    except Exception as e:
        errors.append("%s: %s" % (dtype, e))
        print("  %-15s -> ERROR: %s" % (dtype, e))

if errors:
    print("FAILED: %d domains" % len(errors))
    for e in errors:
        print(" ", e)
    sys.exit(1)
else:
    print("ALL DOMAINS PRODUCED SUCCESSFULLY")
