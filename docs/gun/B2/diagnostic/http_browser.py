"""Serve identical instrumented bytes over loopback, avoiding 22MB CDP fulfil IPC.
Every case still boots a fresh page and browser context. Native UI events and
startup sequence are the original browser_tools.load_fleet sequence.
"""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
def serve(body):
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
   self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start()
 return server,f'http://127.0.0.1:{server.server_port}/helo-f1?view3d=0'
def load_http(browser,url,own='CG_52_LATE_TICONDEROGA',width=1000,height=760,errors=None):
 p=browser.new_page(viewport={'width':width,'height':height});p.on('pageerror',lambda e:errors.append(str(e))if errors is not None else None)
 p.add_init_script('window.__NAVAL_SIM_SEED__=1831565813;');p.goto(url,timeout=90000)
 p.wait_for_selector('#aegisShipConfirmBtn',timeout=90000);c=p.locator('[data-deployment-a]:visible');c.locator('[data-ally-choice]').select_option('NONE');c.locator('[data-enemy-choice]').select_option('NONE');c.locator('[data-target-choice]').select_option('NONE');c.locator('[data-enemy-aircraft-choice]').select_option('OFF');p.locator('#aegisShipSelect').select_option(own);p.locator('#aegisShipConfirmBtn').click()
 p.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__',timeout=120000)
 p.evaluate("()=>{document.getElementById('wip125DepartBtn').click();__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);}")
 return p
