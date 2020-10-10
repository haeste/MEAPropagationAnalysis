# -*- mode: python -*-
a = Analysis(['~mygui.py'],
             pathex=['/home/chris/Workspace/PropagationCalculator'],
             hiddenimports=['scipy.special._ufuncs.cxx'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='~mygui',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='~mygui')
