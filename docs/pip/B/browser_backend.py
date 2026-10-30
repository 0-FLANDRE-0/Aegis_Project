"""Headless-only: rasterize Canvas2D on CPU, retain actual SwiftShader WebGL.
The software GPU's accelerated Canvas2D took 8–9s per frame in the recorded
telemetry, causing Playwright's two-frame stability wait to expire. No page,
shader, clock, simulation, coordinate, or assertion code is replaced.
"""
def install():
 from playwright.sync_api import BrowserType
 native=BrowserType.launch
 def launch(self,*args,**kw):
  kw['args']=[*kw.get('args',[]),'--disable-accelerated-2d-canvas']
  return native(self,*args,**kw)
 BrowserType.launch=launch
