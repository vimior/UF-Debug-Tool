# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=[
             'e:\\venv\\py35_x2\\Lib\\site-packages\\PyQt5\\Qt\\bin',
             'E:\\Vinman\\UFACTORY\\demo\\UF-Debug-Tool'],
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

def add_to_datas(p_path, prefix='/templates'):
    for plugin in os.listdir(p_path):
        path = os.path.join(p_path, plugin)
        if os.path.isdir(path):
            add_to_datas(path, prefix+'/'+plugin)
        elif os.path.isfile(path):
            a.datas.append((prefix+'/'+plugin, path, 'DATA'))

templates_path = os.path.join(current_dir, 'backend', 'templates')
static_path = os.path.join(current_dir, 'backend', 'static')
icon_path = os.path.join(current_dir, 'icon')

add_to_datas(icon_path, '/icon')
#add_to_datas(templates_path, '/backend/templates')
#add_to_datas(static_path, '/backend/static')

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
