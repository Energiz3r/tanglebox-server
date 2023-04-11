from py2exe import freeze

freeze(
    console=['main.py'],
    windows=[],
    data_files=[],
    zipfile=None,
    options={'bundle_files': 0},
    version_info={}
)