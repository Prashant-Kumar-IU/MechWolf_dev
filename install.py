#!/usr/bin/env python3
"""
MechWolf v2.0.0 Installation Script
Automated installation with dependency checking for Windows/Linux/Mac
"""

import subprocess
import sys
import os
import platform

def run_command(cmd, description=""):
    """Run command and return success status"""
    print(f"🔄 {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ Success: {description or cmd}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {description or cmd}")
        print(f"   Error: {e.stderr}")
        return False, e.stderr

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version < (3, 7):
        print(f"❌ Python 3.7+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def main():
    print("=" * 60)
    print("🔬 MechWolf v2.0.0 Installation Script")
    print("   Enhanced Flow Chemistry Automation Platform")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists("setup.py"):
        print("❌ setup.py not found. Please run this script from the MechWolf_dev directory.")
        sys.exit(1)
    
    print(f"✅ Platform: {platform.system()} {platform.release()}")
    
    # Upgrade pip first
    success, _ = run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )
    
    # Install in development mode
    success, _ = run_command(
        f"{sys.executable} -m pip install -e .",
        "Installing MechWolf in development mode"
    )
    
    if not success:
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
    
    # Ask about development dependencies
    print("\n" + "─" * 50)
    install_dev = input("📦 Install development dependencies (black, pytest, etc.)? [y/N]: ").lower()
    if install_dev in ['y', 'yes']:
        run_command(
            f"{sys.executable} -m pip install -e .[dev]",
            "Installing development dependencies"
        )
    
    # Ask about chemistry dependencies
    print("\n" + "─" * 50)
    install_chem = input("🧪 Install chemistry dependencies (RDKit, etc.)? [y/N]: ").lower()
    if install_chem in ['y', 'yes']:
        run_command(
            f"{sys.executable} -m pip install -e .[chemistry]",
            "Installing chemistry dependencies"
        )
    
    print("\n" + "=" * 60)
    print("🎉 MechWolf v2.0.0 installed successfully!")
    print("=" * 60)
    
    print("\n📚 Documentation:")
    print("   • User Guide: mechwolf/DataEntry/FlowSetups/docs/USER_GUIDE.md")
    print("   • Developer Guide: mechwolf/DataEntry/FlowSetups/docs/DEVELOPER_GUIDE.md")
    print("   • API Reference: mechwolf/DataEntry/FlowSetups/docs/API_REFERENCE.md")
    
    print("\n🚀 Quick Test:")
    print("   Run the following command to test the installation:")
    print(f'   {sys.executable} -c "import mechwolf; print(f\\"MechWolf v{{mechwolf.__version__}} imported successfully!\\")"')
    
    print("\n🔬 Flow Setups Quick Start:")
    print("   from mechwolf.DataEntry.FlowSetups import FlowSetupFactory")
    print("   FlowSetupFactory.print_available_setups()")
    
    print("\n📖 Examples:")
    print("   • Check the 'examples/' directory for Jupyter notebooks")
    print("   • Try 'jupyter notebook templates/' for template notebooks")
    
    # Test import
    print("\n🧪 Testing import...")
    test_success, output = run_command(
        f'{sys.executable} -c "import mechwolf; print(f\\"MechWolf v{{mechwolf.__version__}} imported successfully!\\")"',
        "Testing MechWolf import"
    )
    
    if test_success:
        print(f"   {output.strip()}")
    
    print("\n" + "=" * 60)
    print("Installation complete! Happy flow chemistry! 🧪⚗️")
    print("=" * 60)

if __name__ == "__main__":
    main()
