# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path


myDir = os.getcwd()
sys.path.append(myDir)
path = Path(myDir)

metax_path=str(path.parent.absolute())
print(metax_path)

sys.path.append(metax_path)
from MetaX.utils.GUI import runGUI

runGUI()
