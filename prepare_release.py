#!/usr/bin/env python3
"""
MechWolf Release Preparation Script
Prepares files for GitHub release
"""

import os
import json
import subprocess
from datetime import datetime

def update_version_info():
    """Update version information in key files"""
    version = "2.0.0"
    date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📝 Updating version to {version}")
    
    # Update mechwolf/__init__.py (already done)
    print("✅ mechwolf/__init__.py already updated")
    
    # Update setup.py (already done) 
    print("✅ setup.py already updated")
    
    return version, date

def run_tests():
    """Run quick tests to ensure everything works"""
    print("🧪 Running tests...")
    
    try:
        # Test import
        result = subprocess.run([
            "python", "-c", 
            "import mechwolf; from mechwolf.DataEntry.FlowSetups import FlowSetupFactory; print('✅ All imports successful')"
        ], capture_output=True, text=True, check=True)
        print("✅ Import test passed")
        
        # Test Flow Setups
        result = subprocess.run([
            "python", "-c",
            "from mechwolf.DataEntry.FlowSetups import FlowSetupFactory; FlowSetupFactory.print_available_setups()"
        ], capture_output=True, text=True, check=True)
        print("✅ Flow Setups test passed")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False

def create_release_notes():
    """Create release notes template"""
    release_notes = """
# MechWolf v2.0.0 - Enhanced Flow Setups Module

## 🚀 Major Features
- **Complete Flow Setups redesign** with modern UI and extensible architecture
- **Interactive GUI** for apparatus configuration using Jupyter widgets
- **Configuration persistence** - save and reuse experimental setups
- **Extensible framework** for adding new flow chemistry setups

## 🔧 Improvements
- Enhanced data entry tools with better validation
- Improved error handling and user feedback
- Comprehensive documentation and guides
- Better code organization and maintainability

## 📚 Documentation
- [User Guide](mechwolf/DataEntry/FlowSetups/docs/USER_GUIDE.md)
- [Developer Guide](mechwolf/DataEntry/FlowSetups/docs/DEVELOPER_GUIDE.md) 
- [API Reference](mechwolf/DataEntry/FlowSetups/docs/API_REFERENCE.md)
- [Contributing Guide](mechwolf/DataEntry/FlowSetups/docs/CONTRIBUTING.md)

## 💻 Installation

### Quick Install
```bash
pip install git+https://github.com/Prashant-Kumar-IU/MechWolf_dev.git
```

### Development Install
```bash
git clone https://github.com/Prashant-Kumar-IU/MechWolf_dev.git
cd MechWolf_dev
pip install -e .
# Or run: python install.py
```

## 🚨 Breaking Changes
- Flow Setups module API has been redesigned
- See [CHANGELOG.md](CHANGELOG.md) for detailed migration information

## 🧪 Quick Start
```python
from mechwolf.DataEntry.FlowSetups import FlowSetupFactory
FlowSetupFactory.print_available_setups()
```

## 👥 Contributors
- **Prashant Kumar** - Flow Setups module redesign and enhancements
- **Dr. Nicola Pohl** - Project supervision and guidance
- **Benjamin Lee & Alex Mijalis** - Original MechWolf framework
"""
    
    with open("RELEASE_NOTES.md", "w") as f:
        f.write(release_notes.strip())
    
    print("✅ Release notes created: RELEASE_NOTES.md")

def main():
    print("=" * 60)
    print("🚀 MechWolf v2.0.0 Release Preparation")
    print("=" * 60)
    
    # Update version info
    version, date = update_version_info()
    
    # Run tests
    if not run_tests():
        print("\n❌ Tests failed. Please fix issues before releasing.")
        return False
    
    # Create release notes
    create_release_notes()
    
    print("\n" + "=" * 60)
    print("✅ Release preparation complete!")
    print("=" * 60)
    
    print(f"\n📋 Next steps:")
    print(f"1. Review RELEASE_NOTES.md")
    print(f"2. Commit all changes:")
    print(f"   git add .")
    print(f"   git commit -m 'Prepare v{version} release'")
    print(f"3. Push to GitHub:")
    print(f"   git push origin main")
    print(f"4. Create GitHub release:")
    print(f"   - Go to: https://github.com/Prashant-Kumar-IU/MechWolf_dev/releases")
    print(f"   - Click 'Create a new release'")
    print(f"   - Tag: v{version}")
    print(f"   - Title: MechWolf v{version} - Enhanced Flow Setups")
    print(f"   - Copy content from RELEASE_NOTES.md")
    print(f"   - Publish release")
    
    print(f"\n🎉 Users can then install with:")
    print(f"   pip install git+https://github.com/Prashant-Kumar-IU/MechWolf_dev.git")
    
    return True

if __name__ == "__main__":
    main()
