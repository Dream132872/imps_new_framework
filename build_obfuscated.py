#!/usr/bin/env python
"""
Build script to obfuscate Python code and copy static assets to dist directory.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

# File extensions to copy (non-Python files)
STATIC_EXTENSIONS = {
    '.html', '.css', '.js', '.json', '.po', '.mo', '.pot',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
    '.woff', '.woff2', '.ttf', '.eot',
    '.txt', '.md', '.yml', '.yaml',
    '.xml', '.csv',
}

# Directories to exclude from obfuscation but include in copy
EXCLUDE_FROM_OBFUSCATION = [
    '*/migrations/*',
    '*/tests/*',
    '*/__pycache__/*',
    '*/locale/*',
    '*/templates/*',
    '*/static/*',
]

# Directories to copy entirely
DIRS_TO_COPY = [
    'templates',
    'static',
    'locale',
    'migrations_history',
]

# Files to copy from root
ROOT_FILES_TO_COPY = [
    'requirements.txt',
    'pyproject.toml',
]


def remove_bom_from_file(file_path: Path) -> bool:
    """Remove BOM from a file if present."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]
            with open(file_path, 'wb') as f:
                f.write(content)
            print(f"  Removed BOM from: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False


def remove_bom_from_directory(directory: Path):
    """Remove BOM from all Python files in directory."""
    print("Removing BOM characters from Python files...")
    count = 0
    for root, dirs, files in os.walk(directory):
        # Skip cache directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env', '.venv', 'dist']]

        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if remove_bom_from_file(file_path):
                    count += 1

    if count > 0:
        print(f"Removed BOM from {count} files")
    else:
        print("No BOM characters found")


def copy_static_files(src_dir: Path, dst_dir: Path):
    """Copy all non-Python static files to destination."""
    print(f"\nCopying static files from {src_dir} to {dst_dir}...")

    copied_count = 0
    skipped_dirs = {'__pycache__', '.git', 'venv', 'env', '.venv', 'dist', '.pytest_cache'}
    skipped_paths = {'templates', 'static', 'locale'}  # These are handled separately

    for root, dirs, files in os.walk(src_dir):
        # Filter out skipped directories
        dirs[:] = [d for d in dirs if d not in skipped_dirs]

        # Skip if this path is handled separately
        rel_path = Path(root).relative_to(src_dir)
        if any(skipped in str(rel_path) for skipped in skipped_paths):
            continue

        dst_path = dst_dir / rel_path

        # Create destination directory
        dst_path.mkdir(parents=True, exist_ok=True)

        for file in files:
            src_file = Path(root) / file
            dst_file = dst_path / file

            # Skip Python files (already obfuscated)
            if file.endswith('.py'):
                continue

            # Copy file if it matches static extensions
            file_ext = src_file.suffix.lower()
            if file_ext in STATIC_EXTENSIONS:
                try:
                    shutil.copy2(src_file, dst_file)
                    copied_count += 1
                except Exception as e:
                    print(f"  Error copying {src_file}: {e}")

    print(f"Copied {copied_count} static files")


def copy_special_directories(src_dir: Path, dst_dir: Path):
    """Copy special directories entirely (templates, static, locale, migrations)."""
    print("\nCopying special directories...")

    for dir_name in DIRS_TO_COPY:
        src_path = src_dir / dir_name
        if src_path.exists() and src_path.is_dir():
            dst_path = dst_dir / dir_name
            if dst_path.exists():
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
            print(f"  Copied {dir_name}/")

    # Copy migrations_history from project root
    migrations_src = Path('src') / 'migrations_history'
    if migrations_src.exists():
        migrations_dst = dst_dir / 'migrations_history'
        if migrations_dst.exists():
            shutil.rmtree(migrations_dst)
        shutil.copytree(migrations_src, migrations_dst, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
        print(f"  Copied migrations_history/")


def copy_infrastructure_templates_and_static(src_dir: Path, dst_dir: Path):
    """Copy templates and static directories from infrastructure layers."""
    print("\nCopying infrastructure templates and static files...")

    copied_templates = set()
    copied_static = set()

    # Find all infrastructure directories
    for root, dirs, files in os.walk(src_dir):
        # Skip cache directories
        if '__pycache__' in root or '.git' in root:
            continue

        # Look for infrastructure directories
        if 'infrastructure' in root:
            infra_path = Path(root)

            # Check for templates directory
            templates_src = infra_path / 'templates'
            if templates_src.exists() and templates_src.is_dir():
                # Calculate relative path from src
                rel_path = templates_src.relative_to(src_dir)
                templates_dst = dst_dir / rel_path

                # Avoid duplicate copies
                if str(rel_path) not in copied_templates:
                    if templates_dst.exists():
                        shutil.rmtree(templates_dst)
                    shutil.copytree(templates_src, templates_dst, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
                    copied_templates.add(str(rel_path))
                    print(f"  Copied templates: {rel_path}")

            # Check for static directory
            static_src = infra_path / 'static'
            if static_src.exists() and static_src.is_dir():
                rel_path = static_src.relative_to(src_dir)
                static_dst = dst_dir / rel_path

                # Avoid duplicate copies
                if str(rel_path) not in copied_static:
                    if static_dst.exists():
                        shutil.rmtree(static_dst)
                    shutil.copytree(static_src, static_dst, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
                    copied_static.add(str(rel_path))
                    print(f"  Copied static: {rel_path}")


def copy_locale_files(src_dir: Path, dst_dir: Path):
    """Copy locale files (.po, .mo) from all apps."""
    print("\nCopying locale files...")

    for root, dirs, files in os.walk(src_dir):
        if 'locale' in root:
            locale_path = Path(root)
            rel_path = locale_path.relative_to(src_dir)
            locale_dst = dst_dir / rel_path

            locale_dst.mkdir(parents=True, exist_ok=True)

            for file in files:
                if file.endswith(('.po', '.mo', '.pot')):
                    src_file = locale_path / file
                    dst_file = locale_dst / file
                    shutil.copy2(src_file, dst_file)
                    print(f"  Copied locale: {rel_path}/{file}")


def ensure_runtime_in_src(dist_dir: Path):
    """Ensure PyArmor runtime is accessible from obfuscated code."""
    runtime_src = dist_dir / 'pyarmor_runtime_000000'
    runtime_dst = dist_dir / 'src' / 'pyarmor_runtime_000000'

    if runtime_src.exists():
        if runtime_dst.exists():
            # Remove existing destination if it exists
            shutil.rmtree(runtime_dst)
        print("\nMoving PyArmor runtime to src directory...")
        shutil.move(str(runtime_src), str(runtime_dst))
        print("  Runtime moved successfully")


def main():
    """Main build function."""
    project_root = Path(__file__).parent
    src_dir = project_root / 'src'
    dist_dir = project_root / 'dist'

    print("=" * 60)
    print("Building Obfuscated Django Application")
    print("=" * 60)

    # Step 1: Remove BOM from source files
    print("\n[Step 1] Cleaning source files...")
    remove_bom_from_directory(src_dir)

    # Step 2: Remove old dist directory
    if dist_dir.exists():
        print(f"\n[Step 2] Removing old dist directory...")
        shutil.rmtree(dist_dir)
        print("  Old dist removed")

    # Step 3: Obfuscate Python files
    print(f"\n[Step 3] Obfuscating Python files with PyArmor...")
    exclude_args = []
    for pattern in EXCLUDE_FROM_OBFUSCATION:
        exclude_args.extend(['--exclude', pattern])

    cmd = [
        'pyarmor', 'gen', '--recursive',
        '--output', str(dist_dir),
    ] + exclude_args + [
        str(src_dir)
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("  Obfuscation completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"  Error during obfuscation: {e}")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("  ERROR: PyArmor not found. Please install it with: pip install pyarmor")
        sys.exit(1)

    # Step 4: Copy static files
    dist_src = dist_dir / 'src'
    if not dist_src.exists():
        print(f"\nERROR: Obfuscated src directory not found at {dist_src}")
        sys.exit(1)

    print(f"\n[Step 4] Copying static assets...")
    copy_static_files(src_dir, dist_src)

    # Step 5: Copy infrastructure templates and static
    print(f"\n[Step 5] Copying infrastructure templates and static...")
    copy_infrastructure_templates_and_static(src_dir, dist_src)

    # Step 6: Copy locale files
    print(f"\n[Step 6] Copying locale files...")
    copy_locale_files(src_dir, dist_src)

    # Step 7: Copy special directories
    print(f"\n[Step 7] Copying special directories...")
    copy_special_directories(src_dir, dist_src)

    # Step 8: Ensure runtime is accessible
    print(f"\n[Step 8] Setting up PyArmor runtime...")
    ensure_runtime_in_src(dist_dir)

    # Step 9: Copy root files
    print(f"\n[Step 9] Copying root configuration files...")
    for file_name in ROOT_FILES_TO_COPY:
        src_file = project_root / file_name
        if src_file.exists():
            dst_file = dist_dir / file_name
            shutil.copy2(src_file, dst_file)
            print(f"  Copied {file_name}")

    print("\n" + "=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    print(f"\nObfuscated code is in: {dist_dir}")
    print(f"To run Django, use:")
    print(f"  cd {dist_dir}")
    print(f"  python src/manage.py runserver")
    print("\nOr from project root:")
    print(f"  python -m dist.src.manage runserver")
    print("=" * 60)


if __name__ == '__main__':
    main()

