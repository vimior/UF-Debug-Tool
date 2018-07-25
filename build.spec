# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['e:\\venv\\py35_x2\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'E:\\Vinman\\UFACTORY\\demo\\UF-Debug-Tool'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

import os
current_dir = os.getcwd()
connect_icon_path = os.path.join(current_dir, 'icon', 'connect.png')
disconnect_icon_path = os.path.join(current_dir, 'icon', 'disconnect.png')
main_icon_path = os.path.join(current_dir, 'icon', 'main.png')
a.datas.append(('/icon/connect.png', connect_icon_path, 'DATA'))
a.datas.append(('/icon/disconnect.png', disconnect_icon_path, 'DATA'))
a.datas.append(('/icon/main.png', main_icon_path, 'DATA'))

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='UF-Debug-Tool',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False)
