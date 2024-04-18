import sys
import os
myDir = os.getcwd()
sys.path.append(myDir)

from pathlib import Path
path = Path(myDir)

metax_path=str(path.parent.absolute())
print(metax_path)

sys.path.append(metax_path)

from MetaX.utils.GUI import runGUI

if __name__ == "__main__":
    runGUI()

