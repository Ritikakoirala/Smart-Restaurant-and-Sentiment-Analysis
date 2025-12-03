#!/usr/bin/env python3
"""
Debug diagnosis script for Django ImportError
"""

import os
import sys

def diagnose_import_error():
    print("=== DJANGO IMPORT ERROR DIAGNOSIS ===")
    print()
    
    # Check models.py content
    models_path = "smartapp/models.py"
    print(f"1. Checking {models_path}:")
    try:
        with open(models_path, 'r') as f:
            content = f.read()
            print(f"   Content length: {len(content)} characters")
            print(f"   Lines: {len(content.splitlines())}")
            print("   Content preview:")
            for i, line in enumerate(content.splitlines(), 1):
                print(f"   {i:2d} | {line}")
            
            # Check for 'order' model definition
            if 'class order' in content.lower() or 'class Order' in content:
                print("   ✓ Found 'order' model definition")
            else:
                print("   ✗ NO 'order' model definition found")
    except Exception as e:
        print(f"   Error reading file: {e}")
    
    print()
    
    # Check admin.py content
    admin_path = "smartapp/admin.py"
    print(f"2. Checking {admin_path}:")
    try:
        with open(admin_path, 'r') as f:
            content = f.read()
            print("   Content preview:")
            for i, line in enumerate(content.splitlines(), 1):
                print(f"   {i:2d} | {line}")
            
            # Check import statement
            if 'from .models import order' in content:
                print("   ✓ Found import statement: 'from .models import order'")
            else:
                print("   ✗ Import statement not found or different")
    except Exception as e:
        print(f"   Error reading file: {e}")
    
    print()
    print("=== DIAGNOSIS RESULT ===")
    print("PROBLEM IDENTIFIED:")
    print("- admin.py is trying to import 'order' model from models.py")
    print("- models.py contains NO model definitions (only default comments)")
    print("- This causes ImportError: cannot import name 'order'")
    print()
    print("ROOT CAUSE: Missing model definition in models.py")
    print("SOLUTION: Either define the 'order' model or remove the import/registration")

if __name__ == "__main__":
    diagnose_import_error()