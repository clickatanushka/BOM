"""SMT wrong-polarity AI detection gate — Phase 1 (phone + laptop).

The package holds the reusable pieces. Everything runnable lives in scripts/.

    polarity.config     load / save config.yaml
    polarity.align      ArUco fixture detection and perspective flattening
    polarity.quality    blur and exposure gates on a crop
    polarity.pipeline   photo -> aligned -> cropped -> quality-checked
    polarity.model      build / load the classifier, PASS-CHECK-FAIL decision
    polarity.data       dataset walking and board-level grouping
"""
__version__ = "1.0.0"
