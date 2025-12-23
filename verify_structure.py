#!/usr/bin/env python
"""Verify code structure and syntax without external dependencies."""

import sys
import ast
from pathlib import Path

def check_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    project_root = Path(__file__).parent
    src_dir = project_root / 'src'
    
    print("="*60)
    print("Verifying Python Code Syntax")
    print("="*60)
    
    python_files = list(src_dir.glob('*.py'))
    
    all_valid = True
    for filepath in python_files:
        valid, error = check_syntax(filepath)
        status = "✓" if valid else "✗"
        print(f"{status} {filepath.name}")
        if not valid:
            print(f"  Error: {error}")
            all_valid = False
    
    print("\n" + "="*60)
    print("File Structure Check")
    print("="*60)
    
    expected_files = [
        'src/__init__.py',
        'src/main.py',
        'src/segmentation.py',
        'src/stabilization.py',
        'src/metrics.py',
        'src/utils.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        'README.md',
        'notebooks/analysis.ipynb',
        'spark_frontend/SPARK_PROMPT.md'
    ]
    
    for filepath in expected_files:
        full_path = project_root / filepath
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {filepath}")
        if not exists:
            all_valid = False
    
    print("\n" + "="*60)
    if all_valid:
        print("✓ All checks passed!")
        print("="*60)
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the server: uvicorn src.main:app --reload")
        print("3. Open notebooks/analysis.ipynb for interactive demo")
        return 0
    else:
        print("✗ Some checks failed!")
        print("="*60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
