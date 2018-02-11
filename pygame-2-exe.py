"""run with: python {file-name}.py build"""

import cx_Freeze

exe = [cx_Freeze.Executable("raycast3D.py")]

cx_Freeze.setup( name = "downloads", version = "1.0", options = {"build_exe": {"packages": [], "include_files": []}}, executables = exe )