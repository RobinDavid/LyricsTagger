from distutils.core import setup
import py2exe
import sys
from glob import glob

sys.path.append("C:\Program Files\Common Files\Microsoft Shared\VSTO\10.0")
#data_files= [("Microsoft.VC100.CRT",glob(r'C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\redist\ia64\Microsoft.VC100.CRT\*.*'))]
#setup(data_files=data_files, zipfile=None, windows=["taggergui.py"])
setup(zipfile=None, windows=["lyricsTaggerGui.py"],options={"py2exe": {"includes": ["sip", "PyQt4.QtGui"]}})
#setup(windows=["testt"])

'''
options = {
    'py2exe': {
        'dll_excludes': [
            'MSVCP90.dll'
         ]
     }
}
'''