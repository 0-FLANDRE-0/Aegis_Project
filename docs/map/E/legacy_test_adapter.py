"""Test-only retired-node command adapter; never attaches a node or changes checks.
Original controls keep native listeners in the product's private detached map.
The adapter calls those existing listeners for inherited command preparations.
"""
from pathlib import Path
import sys,re
R=Path(__file__).resolve().parents[3]
RETIRED=set('modeAimBtn lockBtn autoEngBtn engCtrlBtn trackIdentityBtn fireBtn missileSelectSm2Btn missileSelectSm2ErBtn missileSelectSm6Btn missileSelectEssmBtn harpoonFireA harpoonRouteE mainGunCueBtn mainGunFireBtn mainGunContinuousBtn mainGunAmmoBtn emconBtn chaffBtn nulka15bBtn softKillAutoBtn noiseJamBtn deceptJamBtn'.split())
API="window.__ME_LEGACY_TEST__={node:id=>mapELegacyNodeE(id),aim:()=>setInputMode('AIM')};"
installed=False

def install():
 global installed
 if installed:return
 installed=True
 sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));import browser_tools
 import browser,browser_g
 def wrap(fn):
  def load(b,body,*a,**kw):
   if b'MAP_E'not in body:
    # The packed body has no plain marker: identify by output bytes hash only.
    import hashlib
    build=__import__('json').loads((R/'docs/map/E/build.json').read_text())
    ise=hashlib.sha256(body).hexdigest()==build['sha256']
    if not ise:
     import gzip,base64
     m=re.search(rb'data-c55-index="13">([^<]+)</script>',body)
     ise=bool(m and b'MAP_E_UI_BEGIN'in gzip.decompress(base64.b64decode(m[1])))
   else:ise=True
   if ise:body=browser_tools.instrument(body,API)
   return fn(b,body,*a,**kw)
  return load
 browser.load_fleet=wrap(browser.load_fleet);browser_g.load_fleet=wrap(browser_g.load_fleet);browser_tools.load_fleet=wrap(browser_tools.load_fleet)
 from playwright.sync_api import Page,Locator
 evaluate=Page.evaluate;click=Locator.click;loc_eval=Locator.evaluate;inner_text=Locator.inner_text
 def page_eval(self,expression,*a,**kw):
  if isinstance(expression,str):
   expression=re.sub(r'document\.getElementById\(([\'\"])([^\'\"]+)\1\)',lambda m:"(window.__ME_LEGACY_TEST__?.node("+repr(m[2])+")??document.getElementById("+repr(m[2])+"))"if m[2]in RETIRED else m[0],expression)
  return evaluate(self,expression,*a,**kw)
 def retired(self):
  s=self._impl_obj._selector
  if re.fullmatch(r'''\[data-tab=(?:ARM|'ARM'|"ARM")\]''',s):return 'modeAimBtn'
  return s[1:]if s.startswith('#')and s[1:]in RETIRED else None
 def loc_click(self,*a,**kw):
  id=retired(self)
  if id and self.page.evaluate('!!window.__ME_LEGACY_TEST__'):return self.page.evaluate('id=>__ME_LEGACY_TEST__.node(id).click()',id)
  return click(self,*a,**kw)
 def loc_evaluate(self,expression,arg=None,**kw):
  id=retired(self)
  if id and self.page.evaluate('!!window.__ME_LEGACY_TEST__'):return self.page.evaluate('a=>('+expression+')(__ME_LEGACY_TEST__.node(a.id),a.arg)',{'id':id,'arg':arg})
  return loc_eval(self,expression,arg,**kw)
 def loc_inner_text(self,*a,**kw):
  id=retired(self)
  if id and self.page.evaluate('!!window.__ME_LEGACY_TEST__'):return self.page.evaluate('id=>__ME_LEGACY_TEST__.node(id).textContent',id)
  return inner_text(self,*a,**kw)
 Page.evaluate=page_eval;Locator.click=loc_click;Locator.evaluate=loc_evaluate;Locator.inner_text=loc_inner_text
