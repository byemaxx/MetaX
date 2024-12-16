import sys
import os
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
parentDir = os.path.abspath(os.path.join(script_dir, os.pardir))
grandParentDir = os.path.abspath(os.path.join(parentDir, os.pardir))
sys.path.append(grandParentDir)


from metax.gui.main_gui import runGUI

runGUI()