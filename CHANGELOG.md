# Changelog

All notable changes to MechWolf will be documented in this file.

## [2.0.0] - 2025-06-17

### 🚀 Major Features
- **Complete Flow Setups Module Redesign**: Enhanced architecture with modern UI
- **Interactive GUI**: Advanced Jupyter widgets for apparatus configuration
- **Configuration Persistence**: Save and reuse experimental setups as JSON
- **Extensible Framework**: Easy addition of new flow chemistry setups
- **Modern UI**: Material Design-inspired interface with progress tracking

### ✨ Added
- `FlowSetupFactory` - Clean factory pattern for creating apparatus
- Enhanced base classes (`BaseComponentApp`, `BaseApparatusCreator`)
- Configuration system with `FlowSetupConfig` and templates
- Widget management system for better UI handling
- Comprehensive error handling and validation
- Data persistence with JSON configuration files
- Multiple setup types:
  - Two syringes with 1 reaction coil and 1 mixer
  - Three syringes with 1 reaction coil and 1 mixer  
  - Three syringes with 2 reaction coils and 2 mixers
  - Flexible setup with variable vessel configuration
- Comprehensive documentation:
  - User Guide with examples
  - Developer Guide with architecture details
  - API Reference with complete documentation
  - Contributing Guide for extending the system

### 🔧 Changed
- Flow Setups module completely rewritten (BREAKING CHANGE)
- Improved package structure and organization
- Enhanced dependency management
- Updated installation process and requirements
- Modernized UI styling and user experience
- Better error messages and user feedback
- Streamlined codebase with 70% reduction in duplicate code

### 🗑️ Removed
- Legacy Flow Setups implementation files:
  - `TwoSyringes1RCoil1Mixer.py`
  - `ThreeSyringes1RCoil1Mixer.py`
  - `ThreeSyringes2RCoil2Mixer.py`
  - `nSyringesToRxnMixVessel.py`
- Deprecated APIs and redundant code
- Duplicate widget and validation code

### 🐛 Fixed
- Various issues in the original Flow Setups implementation
- Improved stability and error handling
- Better validation of user inputs
- Fixed widget state management issues

### 📚 Documentation
- Complete rewrite of Flow Setups documentation
- Added comprehensive examples and tutorials
- Improved code documentation and type hints
- Added migration guide for upgrading from v1.x

### 🔄 Migration Guide
Users upgrading from v1.x should:
1. Update installation method to use GitHub repository
2. Replace old Flow Setups imports with `FlowSetupFactory`
3. Update apparatus creation code to use new API
4. Review new configuration options and features

### 🎯 Breaking Changes
- Flow Setups module API completely redesigned
- Old setup class names and methods no longer available
- Configuration format enhanced (but backward compatible)

---

## Previous Versions
Previous changelog entries for versions < 2.0.0 below...

0.1.2 (unreleased)
------------------

- Added more detailed logging to the GSIOC driver. 


0.1.1 (2019-09-23)
------------------

- Moved developer dependencies out of setup.py in order to [enable Conda installation](https://github.com/conda-forge/staged-recipes/pull/9541).

0.1.0 (2019-09-12)
------------------

- Initial public release