"""Area71 MPS client intelligence: offline, source-auditable analysis and editing engine."""
from __future__ import annotations
import csv, datetime as dt, io, json, math, os, re, sqlite3, threading
from collections import Counter, defaultdict
from pathlib import Path

COLS=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH','AI']
FIELD_NAMES=[
 'EXW Price per unit','Shipping Cost per Unit','Landing Price (USD)','Last Communication Date','Product Status Email Date',
 'Joining Date','Number of Winning Products','Account / Brand / Account Opening Status','Client ID','Client Name',
 'Client Requirements','Product Name','Payment Status','Production Status','Shipment Status','Restock','Marketplace',
 'Product Status','SKU','ASIN','Shipment Status 02','PPC Specialist','Product Live Date','Total Orders','Total Sales (USD)',
 'Ad Sales (USD)','Source Organic Sales (USD)','Ad Spend (USD)','Source ACOS','Source TACOS','PPC Units','Source Organic Units',
 'Refunded Units','Available Units','Notes'
]
FIELD_MAP=dict(zip(COLS,FIELD_NAMES))
CLIENT_FIELDS=['D','E','F','G','H','J','K']
PRODUCT_GROUPS={
 'Product & sourcing':['L','Q','S','T','A','B','C'],
 'Operations':['M','N','O','P','R','U','V','W'],
 'Sales & PPC':['X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH'],
 'Notes':['AI']
}
NUMERIC_COLS={'C','G','X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH'}
PERCENT_COLS={'AC','AD'}


def serial(v):
 if isinstance(v,(dt.datetime,dt.date,dt.time)):return v.isoformat()
 if isinstance(v,(int,float,str,bool)) or v is None:return v
 return str(v)


def numeric(value):
 if value is None or isinstance(value,bool):return None
 if isinstance(value,(float,int)):
  if math.isfinite(value):return float(value)
  return None
 text=str(value).strip().replace(',','').replace('$','').replace('USD','').strip()
 if not text:return None
 if text in ('-','—','N/A','NA','#DIV/0!','#VALUE!'):return None
 if not re.fullmatch(r'-?\d+(?:\.\d+)?%?',text):return None
 try:
  return float(text[:-1])/100 if text.endswith('%') else float(text)
 except ValueError:return None


def st(value):return '' if value is None else str(value).strip()
def data_value(d,k):return d.get(k) if d else None
def num(d,k):return numeric(data_value(d,k))

def money(v):return f'${v:,.2f}' if v is not None else '—'

def clean_market(v):
 t=st(v).upper().replace(' ', '')
 a={'UNITEDARABEMIRATES':'UAE','DE':'GER','GERMANY':'GER','US':'USA','UNITEDSTATES':'USA','GB':'UK','UNITEDKINGDOM':'UK','ITALY':'IT','CANADA':'CA','U.A.E':'UAE'}
 return a.get(t,t) if t else 'Not set'


def derived(d):
 sales,ad_sales,spend=num(d,'Y'),num(d,'Z'),num(d,'AB')
 orders,ppc_units=num(d,'X'),num(d,'AE')
 return {
 'total_sales':sales,'ad_sales':ad_sales,'ad_spend':spend,
 'organic_sales':round(sales-ad_sales,2) if sales is not None and ad_sales is not None else None,
 'acos':spend/ad_sales if spend is not None and ad_sales is not None and ad_sales>0 else None,
 'tacos':spend/sales if spend is not None and sales is not None and sales>0 else None,
 'roas':ad_sales/spend if ad_sales is not None and spend is not None and spend>0 else None,
 'organic_units':orders-ppc_units if orders is not None and ppc_units is not None else None,
 'marketplace':clean_market(d.get('Q')),
 }


def connect(path):
 c=sqlite3.connect(str(path),timeout=15,check_same_thread=False)
 c.row_factory=sqlite3.Row
 c.execute('PRAGMA foreign_keys=ON')
 c.execute('PRAGMA busy_timeout=10000')
 return c

SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT);
CREATE TABLE IF NOT EXISTS clients (
 client_id TEXT PRIMARY KEY, name TEXT NOT NULL DEFAULT '', data_json TEXT NOT NULL DEFAULT '{}',
 archived INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS products (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 source_sheet TEXT,source_row INTEGER,client_id TEXT REFERENCES clients(client_id) ON UPDATE CASCADE,
 link_quality TEXT NOT NULL DEFAULT 'explicit',data_json TEXT NOT NULL,
 archived INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_prod_client ON products(client_id);
CREATE INDEX IF NOT EXISTS idx_prod_source ON products(source_row);
CREATE TABLE IF NOT EXISTS source_rows (
 id INTEGER PRIMARY KEY AUTOINCREMENT,sheet_name TEXT NOT NULL,source_row INTEGER NOT NULL,
 data_json TEXT NOT NULL,formulas_json TEXT NOT NULL DEFAULT '{}',UNIQUE(sheet_name,source_row));
CREATE TABLE IF NOT EXISTS client_notes (
 id INTEGER PRIMARY KEY AUTOINCREMENT, client_id TEXT NOT NULL, note_type TEXT,source_sheet TEXT,source_row INTEGER,
 text TEXT NOT NULL, UNIQUE(client_id,note_type,source_sheet,source_row,text));
CREATE TABLE IF NOT EXISTS alerts (
 alert_key TEXT PRIMARY KEY,product_id INTEGER REFERENCES products(id), client_id TEXT,
 rule TEXT NOT NULL, severity TEXT NOT NULL, title TEXT NOT NULL, detail TEXT NOT NULL,
 suggestion TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'open',owner TEXT NOT NULL DEFAULT '',
 review_note TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1,
 updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_alert_active ON alerts(active,state);
CREATE TABLE IF NOT EXISTS audit (
 id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 entity TEXT NOT NULL,entity_key TEXT NOT NULL,action TEXT NOT NULL,
 changes TEXT NOT NULL DEFAULT '{}');
'''

def init_db(c):c.executescript(SCHEMA);c.commit()

def json_load(v):
 try:return json.loads(v)
 except Exception:return {}

def list_products(c,include_archived=False):
 q='SELECT * FROM products'+('' if include_archived else ' WHERE archived=0')+' ORDER BY id'
 out=[]
 for row in c.execute(q).fetchall():
  d=json_load(row['data_json']);m=derived(d)
  out.append({**m,'id':row['id'],'source_sheet':row['source_sheet'],'source_row':row['source_row'],'client_id':row['client_id'],
   'link_quality':row['link_quality'],'data':d,'product_name':st(d.get('L')),'status':st(d.get('R')),
   'ppc_specialist':st(d.get('V')),'sku':st(d.get('S')),'asin':st(d.get('T')),
   'archived':bool(row['archived']),'updated_at':row['updated_at']})
 return out

def list_clients(c,include_archived=False):
 pcounts=Counter(r['client_id'] for r in c.execute('SELECT client_id FROM products WHERE archived=0'))
 data=[]
 q='SELECT * FROM clients'+('' if include_archived else ' WHERE archived=0')+' ORDER BY name COLLATE NOCASE'
 for r in c.execute(q):
  vals=json_load(r['data_json'])
  data.append({'client_id':r['client_id'],'name':r['name'],'data':vals,'product_count':pcounts[r['client_id']],
   'archived':bool(r['archived']),'updated_at':r['updated_at']})
 return data

def summary(c):
 prods=list_products(c); clients=list_clients(c)
 markets={};status=Counter(); matched=0; linked=Counter()
 for p in prods:
  mk=p['marketplace'];a=markets.setdefault(mk,dict(marketplace=mk,product_count=0,total_sales=0,ad_sales=0,ad_spend=0,live_count=0,blocked_count=0,sales_rows=0))
  a['product_count']+=1;status[p['status'] or 'Not set']+=1;linked[p['link_quality']]+=1
  if 'live' in p['status'].lower():a['live_count']+=1
  if is_blocked(p['data']):a['blocked_count']+=1
  for k in ('total_sales','ad_sales','ad_spend'):
   if p[k] is not None:a[k]+=p[k]
  if p['total_sales'] is not None:a['sales_rows']+=1
  if p['client_id']:matched+=1
 market_rows=[]
 for a in markets.values():
  a['roas']=round(a['ad_sales']/a['ad_spend'],2) if a['ad_spend']>0 else None
  for k in ('total_sales','ad_sales','ad_spend'):a[k]=round(a[k],2)
  market_rows.append(a)
 market_rows.sort(key=lambda d:d['total_sales'],reverse=True)
 alerts=c.execute("SELECT severity,COUNT(*) AS n FROM alerts WHERE active=1 AND state!='resolved' GROUP BY severity").fetchall()
 open_alerts={r['severity']:r['n'] for r in alerts}
 return {'clients':len(clients),'products':len(prods),'linked_products':matched,
   'linked_by_method':dict(linked),'markets':len([x for x in markets if x!='Not set']),
   'total_sales':round(sum(p['total_sales'] or 0 for p in prods),2),
   'ad_sales':round(sum(p['ad_sales'] or 0 for p in prods),2),
   'ad_spend':round(sum(p['ad_spend'] or 0 for p in prods),2),
   'status_distribution':dict(status),'marketplace':market_rows,'alerts':open_alerts,
   'source_sheets':[dict(sheet=r['sheet_name'],rows=r['n']) for r in c.execute('SELECT sheet_name,COUNT(*) n FROM source_rows GROUP BY sheet_name')]}

def is_blocked(d):
 txt=' '.join(st(d.get(k)).lower() for k in ('R','O','U','N'))
 return any(t in txt for t in ('shipping stop','compliance issue','complaince issue','vat','weee','battery reg','shipment stop','shipping hold','customs hold'))

def generate_alerts_for(p):
 d=p['data'];derived_vals=derived(d);out=[]
 def add(rule,severity,title,detail,suggestion):
  out.append({'alert_key':f'{rule}:{p["id"]}','product_id':p['id'],'client_id':p['client_id'],
   'rule':rule,'severity':severity,'title':title,'detail':detail,'suggestion':suggestion})
 status=st(d.get('R')).lower();ship=st(d.get('O')).lower();ship2=st(d.get('U')).lower();prod=st(d.get('N')).lower()
 if 'compliance' in status or 'complaince' in status or any(t in status for t in ('vat','weee','battery reg')):
  add('compliance_hold','critical','Compliance requirement / hold',f'Product status reads “{d.get("R")}”. This is a recorded status, not confirmation of the cause.','Verify the exact compliance issue with Operations and document resolution.')
 elif 'shipping stop' in status or 'stop' in ship or ship2.strip()=='stop':
  add('shipping_hold','critical','Shipment stopped',f'Product status: {d.get("R") or "not set"}; shipment: {d.get("O") or "not set"}; secondary shipment: {d.get("U") or "not set"}.','Confirm supplier/shipment blocker and update the owner and next action.')
 if p['link_quality'] in ('neighbor_inferred','unlinked'):
  add('client_link_review','high','Client link needs confirmation',f'Client relationship was {p["link_quality"].replace("_"," ")}. Source row {p["source_row"]}.','Check source register and confirm the correct client in the product editor.')
 if derived_vals['acos'] is not None and derived_vals['acos']>=1:
  add('high_acos','high','ACOS at or above 100%',f'Ad spend {money(derived_vals["ad_spend"])} ÷ ad sales {money(derived_vals["ad_sales"])} = {derived_vals["acos"]*100:.1f}% ACOS.','PPC specialist should review campaign profitability and attribution before changing bids.')
 if derived_vals['organic_sales'] is not None and num(d,'AA') is not None:
  gap=derived_vals['organic_sales']-num(d,'AA')
  if abs(gap)>0.10:
   add('organic_mismatch','high','Organic sales do not reconcile',f'Source organic sales {money(num(d,"AA"))}; expected total {money(derived_vals["total_sales"])} - ad sales {money(derived_vals["ad_sales"])} = {money(derived_vals["organic_sales"])}; gap {gap:+,.2f} USD.','Check source organic cell / formula before correcting. Do not infer missing revenue.')
 for src_col,label in (('AA','Organic sales'),('AC','ACOS'),('AD','TACOS'),('AF','Organic units')):
  src_value=st(d.get(src_col))
  if src_value in ('#DIV/0!','#VALUE!','#REF!','#NUM!','#N/A','#NAME?'):
   add('source_formula_error_'+src_col.lower(),'medium',f'Source {label} formula error',
    f'Source column {src_col} contains {src_value} (original row {p["source_row"]}).',
    'Review the original formula. Reports use independently calculated metrics when sufficient inputs exist.')
 if derived_vals['tacos'] is not None and num(d,'AD') is not None:
  diff=derived_vals['tacos']-num(d,'AD')
  if abs(diff)>0.005:
   add('tacos_mismatch','medium','TACOS source formula/value differs',f'Source TACOS {num(d,"AD")*100:.2f}% vs recomputed {derived_vals["tacos"]*100:.2f}%.','Check percentage formatting and source formula. Use recomputed TACOS for reports.')
 if 'live' in status and not st(d.get('T')):
  add('missing_asin','medium','Live listing without ASIN',f'Product is marked Live but ASIN is empty (source row {p["source_row"]}).','Confirm whether the ASIN is missing or the Live status needs updating.')
 if p['marketplace']=='Not set':
  add('missing_marketplace','medium','Marketplace missing','Product row has no marketplace recorded.','Confirm the marketplace; reports currently group it under Not set.')
 if derived_vals['ad_sales'] is not None and derived_vals['total_sales'] is not None and derived_vals['ad_sales']>derived_vals['total_sales']+0.1:
  add('ad_sales_gt_total','medium','Ad-attributed sales exceed total sales',f'Ad-attributed sales {money(derived_vals["ad_sales"])} exceed total sales {money(derived_vals["total_sales"])}.','Check reporting time periods and attribution sources for consistency.')
 if derived_vals['ad_spend'] is not None and derived_vals['ad_spend']<0:
  add('negative_ad_spend','medium','Negative ad spend',f'Ad spend is {money(derived_vals["ad_spend"])}.','Verify refunds/credits or data entry before changing the value.')
 return out

def sync_alerts(c):
 prods=list_products(c);new={}
 for p in prods:
  for a in generate_alerts_for(p):new[a['alert_key']]=a
 existing={r['alert_key']:r for r in c.execute('SELECT * FROM alerts')}
 with c:
  for k,al in new.items():
   r=existing.get(k)
   if r:
    c.execute('UPDATE alerts SET client_id=?,severity=?,title=?,detail=?,suggestion=?,active=1,updated_at=CURRENT_TIMESTAMP WHERE alert_key=?',
      (al['client_id'],al['severity'],al['title'],al['detail'],al['suggestion'],k))
   else:
    c.execute('INSERT INTO alerts (alert_key,product_id,client_id,rule,severity,title,detail,suggestion) VALUES (?,?,?,?,?,?,?,?)',
      tuple(al[x] for x in ('alert_key','product_id','client_id','rule','severity','title','detail','suggestion')))
  for k,r in existing.items():
   if k not in new and r['active']:
    c.execute('UPDATE alerts SET active=0,updated_at=CURRENT_TIMESTAMP WHERE alert_key=?',(k,))
 return len(new)

def get_alerts(c,active=True):
 q="SELECT a.*,p.source_row,p.data_json,c.name AS client_name FROM alerts a LEFT JOIN products p ON p.id=a.product_id LEFT JOIN clients c ON c.client_id=a.client_id"
 if active:q+=' WHERE a.active=1'
 q+=' ORDER BY CASE a.severity WHEN "critical" THEN 0 WHEN "high" THEN 1 ELSE 2 END,a.alert_key'
 out=[]
 for r in c.execute(q):
  d=json_load(r['data_json'])
  out.append({k:r[k] for k in r.keys() if k!='data_json'}|{'product_name':st(d.get('L')),'marketplace':clean_market(d.get('Q'))})
 return out

def update_alert(c,key,new):
 row=c.execute('SELECT * FROM alerts WHERE alert_key=?',(key,)).fetchone()
 if not row:raise ValueError('Alert not found')
 state=st(new.get('state',row['state']));owner=st(new.get('owner',row['owner']));note=st(new.get('review_note',row['review_note']))
 if state not in ('open','acknowledged','investigating','resolved'):raise ValueError('Invalid alert state')
 if state=='resolved' and not note:raise ValueError('Add a review note before resolving an alert')
 with c:
  c.execute('UPDATE alerts SET state=?,owner=?,review_note=?,updated_at=CURRENT_TIMESTAMP WHERE alert_key=?',(state,owner,note,key))
  audit(c,'alert',key,'review',{'state':state,'owner':owner,'review_note':note})
 return {'ok':True}

def audit(c,entity,key,action,changes):
 c.execute('INSERT INTO audit(entity,entity_key,action,changes) VALUES (?,?,?,?)',(entity,str(key),action,json.dumps(changes,ensure_ascii=False,default=serial)))

def valid_client_id(value):
 return bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_\-]{1,63}',value))

def save_product(c,record_id,values):
 fields=values.get('data')
 if not isinstance(fields,dict):raise ValueError('Expected product field object')
 if not st(fields.get('L')):raise ValueError('Product name is required')
 if len(json.dumps(fields,ensure_ascii=False,default=serial))>120000:raise ValueError('Product entry too large')
 # Reject silent substitution of fields outside defined source schema.
 if set(fields)-set(COLS):raise ValueError('Unknown Excel columns: '+', '.join(sorted(set(fields)-set(COLS))))
 cleaned={k:(v if v is None or isinstance(v,(int,float,bool)) else str(v)) for k,v in fields.items()}
 client_id=st(values.get('client_id')) or None
 if client_id and not c.execute('SELECT 1 FROM clients WHERE client_id=? AND archived=0',(client_id,)).fetchone():
  raise ValueError('Selected client does not exist; create the client first')
 original_data={}
 if record_id:
  previous=c.execute('SELECT data_json FROM products WHERE id=?',(record_id,)).fetchone()
  if previous:original_data=json_load(previous['data_json'])
 for k in ('X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH'):
  val=cleaned.get(k)
  if st(val) and numeric(val) is None:
   if record_id and val==original_data.get(k):continue  # leave imported formula error untouched
   raise ValueError(f'{FIELD_MAP[k]} needs a valid number; unchanged imported errors may remain until reviewed')
 with c:
  if record_id:
   row=c.execute('SELECT * FROM products WHERE id=?',(record_id,)).fetchone()
   if not row:raise ValueError('Product not found')
   original=json_load(row['data_json'])
   c.execute('UPDATE products SET client_id=?,link_quality=?,data_json=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',
     (client_id, 'confirmed' if client_id else 'unlinked',json.dumps(cleaned,ensure_ascii=False,default=serial),record_id))
   delta={k:{'before':original.get(k),'after':cleaned.get(k)} for k in COLS if original.get(k)!=cleaned.get(k)}
   if row['client_id']!=client_id:delta['linked_client_id']={'before':row['client_id'],'after':client_id}
   audit(c,'product',record_id,'update',delta)
  else:
   cur=c.execute('INSERT INTO products(source_sheet,source_row,client_id,link_quality,data_json) VALUES (?,?,?,?,?)',
    ('User entry',None,client_id,'confirmed' if client_id else 'unlinked',json.dumps(cleaned,ensure_ascii=False,default=serial)))
   record_id=cur.lastrowid
   audit(c,'product',record_id,'create',cleaned)
 sync_alerts(c)
 return {'id':record_id}

def save_client(c,client_id,values):
 data=values.get('data')
 if not isinstance(data,dict):raise ValueError('Expected client data')
 if any(k not in CLIENT_FIELDS for k in data):raise ValueError('Unknown client field')
 name=st(data.get('J'))
 if not name:raise ValueError('Client name required')
 if not valid_client_id(client_id):raise ValueError('Client ID should contain letters, digits, underscores or hyphens')
 old=c.execute('SELECT * FROM clients WHERE client_id=?',(client_id,)).fetchone()
 if old and old['archived']:raise ValueError('This Client ID was archived; restore instead of recreating')
 with c:
  if old:
   earlier=json_load(old['data_json'])
   c.execute('UPDATE clients SET name=?,data_json=?,updated_at=CURRENT_TIMESTAMP WHERE client_id=?',
    (name,json.dumps(data,ensure_ascii=False,default=serial),client_id))
   audit(c,'client',client_id,'update',{'before':earlier,'after':data})
  else:
   c.execute('INSERT INTO clients(client_id,name,data_json) VALUES (?,?,?)',
    (client_id,name,json.dumps(data,ensure_ascii=False,default=serial)))
   audit(c,'client',client_id,'create',data)
 return {'client_id':client_id}

def archive_entity(c,entity,identifier,archived):
 table='products' if entity=='product' else 'clients' if entity=='client' else ''
 if not table:raise ValueError('Invalid entity')
 key='id' if entity=='product' else 'client_id'
 if entity=='client' and archived:
  n=c.execute('SELECT COUNT(*) FROM products WHERE client_id=? AND archived=0',(identifier,)).fetchone()[0]
  if n:raise ValueError('Move or archive linked products before archiving this client')
 with c:
  cur=c.execute(f'UPDATE {table} SET archived=?,updated_at=CURRENT_TIMESTAMP WHERE {key}=?',(1 if archived else 0,identifier))
  if not cur.rowcount:raise ValueError('Record not found')
  audit(c,entity,identifier,'archive' if archived else 'restore',{})
 sync_alerts(c)
 return {'ok':True}

def notes_for_client(c,client_id):
 return [{k:r[k] for k in r.keys()} for r in c.execute('SELECT id,note_type,source_sheet,source_row,text FROM client_notes WHERE client_id=? ORDER BY source_row',(client_id,))]

def client_brief(c,client_id):
 cli=c.execute('SELECT * FROM clients WHERE client_id=? AND archived=0',(client_id,)).fetchone()
 if not cli:raise ValueError('Client not found')
 data=json_load(cli['data_json'])
 prs=[p for p in list_products(c) if p['client_id']==client_id]
 total=sum(p['total_sales'] or 0 for p in prs);adspend=sum(p['ad_spend'] or 0 for p in prs)
 blocked=[p for p in prs if is_blocked(p['data'])]
 high=[p for p in prs if p['acos'] is not None and p['acos']>=1]
 live=[p for p in prs if 'live' in p['status'].lower()]
 risknotes=[p for p in prs if p['link_quality'] in ('neighbor_inferred','unlinked')]
 interesting=sorted(prs,key=lambda p:(p['total_sales'] or 0),reverse=True)[:5]
 talking=[]
 if blocked:talking.append(f'Ask Operations to confirm blocker and next update for {blocked[0]["product_name"]} ({blocked[0]["marketplace"]}); do not promise a resolution date.')
 if high:talking.append(f'Review {high[0]["product_name"]} campaigns with PPC specialist: calculated ACOS {high[0]["acos"]*100:.1f}%; validate report period and margin before changing spend.')
 candidates=[p for p in live if (num(p['data'],'AH') is not None and num(p['data'],'AH')<=5 and (p['total_sales'] or 0)>0)]
 if candidates:talking.append(f'Check actual inventory and reorder lead time for {candidates[0]["product_name"]} (recorded available units {int(num(candidates[0]["data"],"AH"))}).')
 if not talking:talking.append('Verify product status, inventory, client priorities and next milestone before proposing a new launch or restock.')
 return {'client_id':client_id,'name':cli['name'],'client_data':data,'product_count':len(prs),
  'marketplaces':sorted(set(p['marketplace'] for p in prs)), 'live_count':len(live),'blocked_count':len(blocked),
  'high_acos_count':len(high),'total_sales':round(total,2),'ad_spend':round(adspend,2),
  'notes':notes_for_client(c,client_id),'products':prs,'top_products':interesting,'talking_points':talking,
  'review_links':len(risknotes),'disclaimer':'All observations reflect the uploaded source snapshot and later local edits. Validate current Amazon data before making client promises.'}

def execute_query(c,prompt):
 """Deliberately constrained natural language query: transparent local parsing, no LLM or freeform SQL."""
 text=st(prompt).lower();prods=list_products(c);summ=summary(c);clients=list_clients(c)
 if not text:raise ValueError('Enter a reporting question')
 match_market=re.search(r'\b(uae|uk|ca|italy|it|ger|germany|usa|us)\b',text)
 market=clean_market(match_market.group(1)) if match_market else None
 def select_market(ps):return [p for p in ps if not market or p['marketplace']==market]
 def table(title,columns,rows,chart=None,footnote=''):
  return dict(title=title,columns=columns,rows=rows[:150],row_count=len(rows),chart=chart or None,footnote=footnote)
 if 'help' in text or text in ('?','examples'):
  return table('Supported question examples',['Example'],[[s] for s in ['Sales versus ad spend by marketplace','Show blocked products in UAE','Highest ACOS products','Top 10 products by sales','Live products by marketplace','PPC performance by specialist','Which products need restock?','Client MPS-28724-02']])
 m=re.search(r'\b(mps-[\w-]+)\b',text,re.I)
 if m:
  client=m.group(1).upper();items=[p for p in prods if st(p['client_id']).upper()==client]
  rows=[[p['product_name'],p['marketplace'],p['status'],round(p['total_sales'] or 0,2),round((p['acos'] or 0)*100,1) if p['acos'] is not None else None,p['source_row']] for p in items]
  return table('Products for '+client,['Product','Market','Status','Total sales ($)','ACOS (%)','Source row'],rows)
 if any(s in text for s in ('by marketplace','per marketplace','each marketplace','marketplace summary','marketplace performance','sales vs','sales versus','revenue by marketplace','performance by market','sales by marketplace')):
  rows=[]
  for a in summ['marketplace']:
   if market and a['marketplace']!=market:continue
   rows.append([a['marketplace'],a['product_count'],a['total_sales'],a['ad_sales'],a['ad_spend'],a['roas'],a['blocked_count']])
  ch=[{'name':r[0],'sales':r[2],'spend':r[4]} for r in rows]
  return table('Marketplace performance',['Marketplace','Products','Total sales ($)','Ad sales ($)','Ad spend ($)','Ad ROAS (x)','Blocked'],rows,ch,'ROAS = ad-attributed sales ÷ ad spend. Total sales are not ad-attributed sales.')
 if 'ppc' in text and any(k in text for k in ('performance','specialist','guy','owner','by')):
  groups=defaultdict(lambda:{'products':0,'sales':0,'ad_sales':0,'spend':0})
  for p in select_market(prods):
   key=p['ppc_specialist'] or 'Unassigned';b=groups[key];b['products']+=1
   for field,out in [('total_sales','sales'),('ad_sales','ad_sales'),('ad_spend','spend')]:b[out]+=p[field] or 0
  rows=[[k,v['products'],round(v['sales'],2),round(v['ad_sales'],2),round(v['spend'],2),round(v['spend']/v['ad_sales']*100,1) if v['ad_sales']>0 else None] for k,v in groups.items()]
  rows.sort(key=lambda r:r[4],reverse=True)
  return table('PPC portfolio by recorded specialist',['Specialist','Products','Total sales ($)','Ad sales ($)','Ad spend ($)','Portfolio ACOS (%)'],rows,footnote='Portfolio-level ratio computed from ad spend and ad-attributed sales. Attribution periods may differ.')
 if any(w in text for w in ('blocked','shipping stop','compliance','hold','stopped','bottleneck')):
  chosen=[p for p in select_market(prods) if is_blocked(p['data'])]
  rows=[[p['client_id'] or 'Review link',p['product_name'],p['marketplace'],p['status'],st(p['data'].get('O')),p['source_row']] for p in chosen]
  return table('Recorded blocked/held products',['Client ID','Product','Marketplace','Product status','Shipment status','Source row'],rows,footnote='Based on recorded workflow statuses only; not independently verified.')
 if 'acos' in text or ('advertising' in text and any(x in text for x in ('high','worst'))):
  chosen=[p for p in select_market(prods) if p['acos'] is not None]
  chosen.sort(key=lambda p:p['acos'],reverse=True)
  limit=10
  m=re.search(r'\b(top|highest|worst)\s+(\d+)\b',text)
  if m:limit=min(100,int(m.group(2)))
  if any(k in text for k in ('over 100','above 100','100%','at least 100')):chosen=[p for p in chosen if p['acos']>=1]
  rows=[[p['client_id'],p['product_name'],p['marketplace'],round(p['acos']*100,1),p['ad_sales'],p['ad_spend'],p['ppc_specialist']] for p in chosen[:limit]]
  return table('ACOS review list',['Client ID','Product','Marketplace','ACOS (%)','Ad sales ($)','Ad spend ($)','PPC specialist'],rows)
 if 'restock' in text or 'inventory' in text or 'low stock' in text:
  chosen=[p for p in select_market(prods) if st(p['data'].get('P')) or (num(p['data'],'AH') is not None and num(p['data'],'AH')<=5 and 'live' in p['status'].lower())]
  rows=[[p['client_id'],p['product_name'],p['marketplace'],p['data'].get('P'),num(p['data'],'AH'),p['status']] for p in chosen]
  rows.sort(key=lambda r:(r[4] if r[4] is not None else 99999))
  return table('Restock and low-available-unit review',['Client ID','Product','Marketplace','Restock status','Available units','Product status'],rows,footnote='Low stock is a screening threshold (5 units), not a restock recommendation without lead time and sell-through data.')
 if 'live' in text and any(k in text for k in ('product','market','count')):
  chosen=[p for p in select_market(prods) if 'live' in p['status'].lower()]
  return table('Recorded live products',['Client ID','Product','Marketplace','ASIN','Live date'],[[p['client_id'],p['product_name'],p['marketplace'],p['asin'],serial(p['data'].get('W'))] for p in chosen])
 if any(x in text for x in ('top product','top 10','top 5','best seller','highest sales','sales leaders')):
  chosen=sorted(select_market(prods),key=lambda p:p['total_sales'] or 0,reverse=True)
  m=re.search(r'\btop\s*(\d+)\b',text);limit=min(100,int(m.group(1))) if m else 10
  rows=[[p['client_id'],p['product_name'],p['marketplace'],round(p['total_sales'] or 0,2),round(p['ad_spend'] or 0,2)] for p in chosen[:limit]]
  return table('Top products by recorded total sales',['Client ID','Product','Marketplace','Total sales ($)','Ad spend ($)'],rows)
 if 'client' in text and ('count' in text or 'how many' in text):
  return table('Client count',['Metric','Value'],[['Distinct explicit client IDs',len(clients)],['Product rows',len(prods)]])
 raise ValueError('I can answer supported operational questions, but not arbitrary natural-language requests offline. Try “Sales versus ad spend by marketplace”, “Blocked products in UAE”, “Top 10 products by sales”, “Highest ACOS products”, or “Client MPS-28724-02”.')

def csv_export(c,what):
 out=io.StringIO();w=csv.writer(out)
 if what=='products':
  w.writerow(['App ID','Linked client ID','Link quality','Source sheet','Source row']+[FIELD_MAP[x] for x in COLS]+['Calculated ACOS','Calculated TACOS','Calculated Organic Sales'])
  for p in list_products(c):
   w.writerow([p['id'],p['client_id'],p['link_quality'],p['source_sheet'],p['source_row']]+[serial(p['data'].get(x)) for x in COLS]+[p['acos'],p['tacos'],p['organic_sales']])
 elif what=='clients':
  w.writerow(['Client ID','Client Name']+[FIELD_MAP[x] for x in CLIENT_FIELDS if x!='J']+['Product count'])
  for c1 in list_clients(c):
   w.writerow([c1['client_id'],c1['name']]+[serial(c1['data'].get(x)) for x in CLIENT_FIELDS if x!='J']+[c1['product_count']])
 elif what=='alerts':
  w.writerow(['Key','Severity','Rule','Client','Product','Detail','State','Owner','Review Note'])
  for a in get_alerts(c):w.writerow([a[x] for x in ['alert_key','severity','rule','client_id','product_name','detail','state','owner','review_note']])
 elif what=='source_archive':
  w.writerow(['Source Sheet','Row','Cached Values (JSON)','Original Formulas (JSON)'])
  for r in c.execute('SELECT * FROM source_rows ORDER BY sheet_name,source_row'):
   w.writerow([r['sheet_name'],r['source_row'],r['data_json'],r['formulas_json']])
 else:raise ValueError('Unsupported export')
 return out.getvalue().encode('utf-8-sig')
