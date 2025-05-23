# lol_viz2025.spec

# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Collect all plotly.graph_objs submodules (including _scattergl, _figure, etc)
plotly_submodules = collect_submodules('plotly.graph_objs')

# Collect plotly data files (json, templates, etc)
plotly_data = collect_data_files('plotly')

# Collect dash_ag_grid data files (like package-info.json)
dag_data = collect_data_files('dash_ag_grid')

# Path to your source folder (adjust if needed)
src_path = os.path.abspath('src')

# Paths to resource folders relative to spec file (one level above src)
ressources_path = os.path.abspath('ressources')
data_path = os.path.abspath('data')

a = Analysis(
    ['src/app.py'],
    pathex=[src_path],
    binaries=[],
    datas=plotly_data + dag_data + [
        (ressources_path, 'ressources'),
        (data_path, 'data'),
    ],
    hiddenimports=plotly_submodules,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='lol_viz2025one',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
    onefile=True,
)