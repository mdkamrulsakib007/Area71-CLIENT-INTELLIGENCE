"""Area71 MPS Intelligence — single-user, localhost-only web server. Python 3.9+; no packages required."""
import json,os,sys,webbrowser,threading,traceback,sqlite3,datetime,pathlib,shutil,urllib.parse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from core import (connect,init_db,list_products,list_clients,summary,get_alerts,client_brief,
 execute_query,save_product,save_client,update_alert,archive_entity,notes_for_client,
 csv_export,FIELD_MAP,PRODUCT_GROUPS,CLIENT_FIELDS,NUMERIC_COLS,PERCENT_COLS,serial,
 audit,sync_alerts,json_load)
ROOT=pathlib.Path(__file__).resolve().parent
DATABASE=ROOT/'data'/'mps_intelligence.sqlite'
PORT=int(os.environ.get('AREA71_PORT','8765'))
LOCK=threading.RLock()

class Handler(BaseHTTPRequestHandler):
 server_version='Area71Local/1.0'
 def log_message(self,fmt,*args):
  print('[%s] %s'%(self.log_date_time_string(),fmt%args))
 def _headers(self,code=200,ctype='application/json; charset=utf-8',bytes_len=None,filename=None):
  self.send_response(code)
  self.send_header('Content-Type',ctype)
  self.send_header('Cache-Control','no-store')
  self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('X-Frame-Options','DENY')
  self.send_header('Referrer-Policy','no-referrer')
  self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
  if filename:self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
  if bytes_len is not None:self.send_header('Content-Length',str(bytes_len))
  self.end_headers()
 def _respond(self,obj,code=200):
  b=json.dumps(obj,ensure_ascii=False,default=serial).encode('utf-8')
  self._headers(code,bytes_len=len(b));self.wfile.write(b)
 def _text(self,content,mime):
  b=content.encode('utf-8');self._headers(200,mime,len(b));self.wfile.write(b)
 def _error(self,e,code=400):self._respond({'error':str(e)},code)
 def _host_ok(self):
  host=self.headers.get('Host','').split(':')[0].lower()
  if host not in ('127.0.0.1','localhost'):
   self._error('Localhost only',403);return False
  return True
 def _conn(self):return connect(DATABASE)
 def do_GET(self):
  if not self._host_ok():return
  path=urllib.parse.urlsplit(self.path);route=path.path;params=urllib.parse.parse_qs(path.query)
  try:
   if route=='/' or route=='/index.html':
    return self._text((ROOT/'static'/'index.html').read_text(encoding='utf-8'),'text/html; charset=utf-8')
   if route in ('/style.css','/app.js'):
    return self._text((ROOT/'static'/route[1:]).read_text(encoding='utf-8'),'text/css; charset=utf-8' if route.endswith('.css') else 'text/javascript; charset=utf-8')
   if not route.startswith('/api/'):
    return self._error('Not found',404)
   with LOCK:
    c=self._conn()
    try:
     if route=='/api/health':return self._respond({'ok':c.execute('PRAGMA integrity_check').fetchone()[0]=='ok','app':'Area71 MPS Intelligence'})
     if route=='/api/config':
      return self._respond({'fields':FIELD_MAP,'groups':PRODUCT_GROUPS,'client_fields':CLIENT_FIELDS,
       'numeric_fields':sorted(NUMERIC_COLS),'percent_fields':sorted(PERCENT_COLS),'local_only':True})
     if route=='/api/summary':return self._respond(summary(c))
     if route=='/api/products':
      prods=list_products(c,include_archived=params.get('include_archived',['0'])[0]=='1')
      q=params.get('q',[''])[0].lower();market=params.get('market',[''])[0].upper();status=params.get('status',[''])[0].lower();client=params.get('client',[''])[0]
      def passes(p):
       if market and p['marketplace']!=market:return False
       if status and status not in p['status'].lower():return False
       if client and p['client_id']!=client:return False
       if q and q not in ' '.join(str(p.get(k) or '') for k in ('product_name','client_id','sku','asin','marketplace','status','ppc_specialist')).lower():return False
       return True
      prods=[p for p in prods if passes(p)];total=len(prods)
      page=max(1,int(params.get('page',['1'])[0]));limit=max(1,min(200,int(params.get('limit',['30'])[0])))
      return self._respond({'total':total,'page':page,'limit':limit,'items':prods[(page-1)*limit:page*limit]})
     if route.startswith('/api/product/'):
      pid=int(route.rsplit('/',1)[1]);p=next((p for p in list_products(c,True) if p['id']==pid),None)
      if not p:return self._error('Product not found',404)
      return self._respond(p)
     if route=='/api/clients':return self._respond(list_clients(c,params.get('include_archived',['0'])[0]=='1'))
     if route.startswith('/api/client/'):
      cid=urllib.parse.unquote(route.split('/api/client/',1)[1]);cl=next((v for v in list_clients(c,True) if v['client_id']==cid),None)
      if not cl:return self._error('Client not found',404)
      cl['notes']=notes_for_client(c,cid)
      return self._respond(cl)
     if route.startswith('/api/brief/'):
      cid=urllib.parse.unquote(route.split('/api/brief/',1)[1]);return self._respond(client_brief(c,cid))
     if route=='/api/alerts':return self._respond(get_alerts(c,params.get('active',['1'])[0]!='0'))
     if route=='/api/archive-tabs':return self._respond([dict(sheet=r['sheet_name'],rows=r['n']) for r in c.execute('SELECT sheet_name,COUNT(*) n FROM source_rows GROUP BY sheet_name ORDER BY sheet_name')])
     if route=='/api/source-rows':
      sheet=params.get('sheet',['MPS Client Info'])[0]
      q=params.get('q',[''])[0].lower();page=max(1,int(params.get('page',['1'])[0]));lim=20
      rows=c.execute('SELECT sheet_name,source_row,data_json,formulas_json FROM source_rows WHERE sheet_name=? ORDER BY source_row',(sheet,)).fetchall()
      filtered=[r for r in rows if not q or q in (r['data_json']+' '+str(r['source_row'])).lower()]
      return self._respond({'total':len(filtered),'page':page,'limit':lim,
       'items':[{k:r[k] for k in r.keys()} for r in filtered[(page-1)*lim:page*lim]]})
     if route=='/api/audit':
      rows=c.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 150').fetchall()
      return self._respond([{k:r[k] for k in r.keys()} for r in rows])
     if route=='/api/metadata':return self._respond({r['key']:json_load(r['value']) if r['value'][:1] in '[{' else json.loads(r['value']) for r in c.execute('SELECT * FROM meta')})
     if route=='/api/export':
      what=params.get('what',['products'])[0];b=csv_export(c,what)
      self._headers(200,'text/csv; charset=utf-8',len(b),f'Area71_{what}_{datetime.date.today().isoformat()}.csv');self.wfile.write(b);return
     return self._error('Route not found',404)
    finally:c.close()
  except Exception as e:
   traceback.print_exc();return self._error(e,400)
 def do_POST(self):
  if not self._host_ok():return
  route=urllib.parse.urlsplit(self.path).path
  if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':return self._error('Send JSON',415)
  size=int(self.headers.get('Content-Length','0'))
  if size>300000:return self._error('Request too large',413)
  try:body=json.loads(self.rfile.read(size).decode('utf-8')) if size else {}
  except Exception:return self._error('Invalid JSON')
  try:
   with LOCK:
    c=self._conn()
    try:
     if route=='/api/product':result=save_product(c,None,body)
     elif route.startswith('/api/product/'):
      result=save_product(c,int(route.rsplit('/',1)[1]),body)
     elif route=='/api/client':
      result=save_client(c,str(body.get('client_id','')).strip(),body)
     elif route.startswith('/api/client/'):
      cid=urllib.parse.unquote(route.split('/api/client/',1)[1]);result=save_client(c,cid,body)
     elif route.startswith('/api/alert/'):
      result=update_alert(c,urllib.parse.unquote(route.split('/api/alert/',1)[1]),body)
     elif route=='/api/analyze':result=execute_query(c,body.get('question',''))
     elif route=='/api/note':
      cid=str(body.get('client_id',''));txt=str(body.get('text','')).strip()
      if not cid or not c.execute('SELECT 1 FROM clients WHERE client_id=?',(cid,)).fetchone():raise ValueError('Select an existing client')
      if not txt or len(txt)>10000:raise ValueError('Note must contain 1–10,000 characters')
      with c:
       c.execute('INSERT INTO client_notes(client_id,note_type,source_sheet,source_row,text) VALUES (?,?,?,?,?)',(cid,'User note','Manual',None,txt))
       audit(c,'client',cid,'add_note',{'text':txt})
      result={'ok':True}
     elif route=='/api/archive':
      result=archive_entity(c,str(body.get('entity','')),body.get('id'),bool(body.get('archived',True)))
     elif route=='/api/backup':
      backup_dir=ROOT/'backups';backup_dir.mkdir(exist_ok=True)
      stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
      dest=backup_dir/f'mps-backup-{stamp}.sqlite'
      dst=sqlite3.connect(str(dest));c.backup(dst);dst.close()
      result={'ok':True,'filename':dest.name,'size_bytes':dest.stat().st_size}
     else:return self._error('Route not found',404)
     return self._respond(result)
    finally:c.close()
  except Exception as e:
   traceback.print_exc();return self._error(e)

def main():
 if not DATABASE.exists():sys.exit('Database missing: extract the whole ZIP, including data/mps_intelligence.sqlite')
 with connect(DATABASE) as conn:
  if conn.execute('PRAGMA integrity_check').fetchone()[0]!='ok':sys.exit('Database integrity check failed')
  sync_alerts(conn)
 server=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
 print('\nArea71 MPS Intelligence\n--------------------------------------------')
 print(f'Local dashboard: http://127.0.0.1:{PORT}')
 print('Your data stays on this computer. Press Ctrl+C to close.\n')
 if '--no-browser' not in sys.argv:threading.Timer(0.9,lambda:webbrowser.open(f'http://127.0.0.1:{PORT}')).start()
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
