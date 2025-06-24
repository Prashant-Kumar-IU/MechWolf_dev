# Legacy Files Archive

This directory contains the original Phase2_ApparatusBuilder files that have been replaced by the new modular architecture.

## Archived Files

These files have been **superseded** by the modular v2 system:

- **`apparatus_gui.py`** (678 lines) - Legacy integrated GUI
- **`pump_configurator.py`** (740 lines) - Legacy pump configuration
- **`component_configurator.py`** (657 lines) - Legacy component configuration  
- **`connection_builder.py`** (594 lines) - Legacy connection builder
- **`apparatus_validator.py`** (516 lines) - Legacy validation system
- **`apparatus_visualizer.py`** (494 lines) - Legacy visualization

**Total**: 3,679 lines of legacy code safely preserved.

## Why Archived?

1. **Replaced by modular system**: The new `models/`, `registry/`, `ui/`, `core/` structure provides the same functionality with better organization
2. **Dependency issues**: These files rely on missing `shared_components` module
3. **Maintenance burden**: Keeping both systems would create confusion and maintenance overhead
4. **GitHub compatibility**: These files contained hardcoded paths that would break on other machines

## Migration Path

- **Old**: `from .apparatus_gui import ApparatusBuilderGUI`
- **New**: `from . import create_tabbed_apparatus_designer` (or `create_tabbed_apparatus_designer_v2`)

## If You Need Legacy Functionality

If you specifically need these legacy files:

1. They are preserved here for reference
2. Update the hardcoded paths before use
3. Install missing `shared_components` dependencies
4. Consider migrating to the v2 modular system instead

---

**Note**: The main `tabbed_apparatus_designer.py` (1,346 lines) is still active as a fallback for the modular system.