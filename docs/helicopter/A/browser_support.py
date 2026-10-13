"""Native offline WebGL preview setup, independent of simulator tests."""
import os, shutil

def launch(pw, webgl=True):
    args = ['--no-sandbox', '--disable-dev-shm-usage']
    args += ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] if webgl else ['--disable-gpu']
    return pw.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE') or shutil.which('chromium'), headless=True, args=args)
