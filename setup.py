#!/usr/bin/env python3
"""
Setup script for Django project
Helps configure the project for both localhost and PythonAnywhere environments.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("Please use Python 3.8 or higher")
        return False

def setup_virtual_environment():
    """Setup virtual environment"""
    if os.path.exists('myenv'):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command('python -m venv myenv', 'Creating virtual environment')

def install_dependencies():
    """Install Python dependencies"""
    if os.name == 'nt':  # Windows
        activate_cmd = 'myenv\\Scripts\\activate && pip install -r requirements.txt'
    else:  # Unix/Linux/macOS
        activate_cmd = 'source myenv/bin/activate && pip install -r requirements.txt'
    
    return run_command(activate_cmd, 'Installing dependencies')

def setup_database():
    """Setup database"""
    if os.name == 'nt':  # Windows
        activate_cmd = 'myenv\\Scripts\\activate && python manage.py migrate'
    else:  # Unix/Linux/macOS
        activate_cmd = 'source myenv/bin/activate && python manage.py migrate'
    
    return run_command(activate_cmd, 'Setting up database')

def collect_static_files():
    """Collect static files"""
    if os.name == 'nt':  # Windows
        activate_cmd = 'myenv\\Scripts\\activate && python manage.py collectstatic --noinput'
    else:  # Unix/Linux/macOS
        activate_cmd = 'source myenv/bin/activate && python manage.py collectstatic --noinput'
    
    return run_command(activate_cmd, 'Collecting static files')

def check_environment_file():
    """Check if environment file exists"""
    env_file = Path('myenv/tokenemailandtelegram.txt')
    if env_file.exists():
        print("✅ Environment file exists")
        return True
    else:
        print("❌ Environment file not found")
        print("Please create myenv/tokenemailandtelegram.txt with your credentials")
        return False

def check_credentials_file():
    """Check if Google Sheets credentials file exists"""
    possible_paths = [
        Path('credentials.json'),
        Path('myenv/credentials.json'),
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"✅ Google Sheets credentials found at: {path}")
            return True
    
    print("❌ Google Sheets credentials not found")
    print("Please download credentials.json from Google Cloud Console")
    print("and place it in the project root")
    return False

def run_tests():
    """Run the comprehensive test suite"""
    if os.name == 'nt':  # Windows
        activate_cmd = 'myenv\\Scripts\\activate && python test_dual_environment.py'
    else:  # Unix/Linux/macOS
        activate_cmd = 'source myenv/bin/activate && python test_dual_environment.py'
    
    return run_command(activate_cmd, 'Running comprehensive tests')

def main():
    """Main setup function"""
    print("🚀 Django Project Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Virtual Environment", setup_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Database", setup_database),
        ("Static Files", collect_static_files),
        ("Environment File", check_environment_file),
        ("Google Sheets Credentials", check_credentials_file),
    ]
    
    # Run setup steps
    results = []
    for step_name, step_func in steps:
        result = step_func()
        results.append((step_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("SETUP SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {step_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} steps completed successfully")
    
    if passed == total:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Create a superuser: python manage.py createsuperuser")
        print("2. Run tests: python test_dual_environment.py")
        print("3. Start development server: python manage.py runserver")
        print("4. Visit http://localhost:8000")
    else:
        print(f"\n⚠️  {total - passed} step(s) failed. Please fix the issues above.")
        print("\nCommon issues:")
        print("- Make sure you have Python 3.8+ installed")
        print("- Check that you're in the correct directory")
        print("- Ensure you have internet connection for pip install")
        print("- Create the environment file with your credentials")
        print("- Download Google Sheets credentials from Google Cloud Console")
    
    # Offer to run tests
    if passed >= 4:  # At least basic setup is done
        print("\n" + "=" * 50)
        response = input("Would you like to run the comprehensive tests now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            run_tests()

if __name__ == "__main__":
    main() 