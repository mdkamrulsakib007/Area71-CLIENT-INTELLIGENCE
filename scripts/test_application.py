"""Regression tests for the imported MPS source, data integrity, and three tools.
Every mutating test uses a disposable copy of the database.
Run: python3 scripts/test_application.py
"""
import sys,os,unittest,shutil,tempfile,sqlite3,json,csv,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from core import *
SOURCE=ROOT/'data'/'mps_intelligence.sqlite'

class TestMPS(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.db=Path(self.t.name)/'copy.sqlite';shutil.copy2(SOURCE,self.db);self.c=connect(self.db)
 def tearDown(self):self.c.close();self.t.cleanup()
 def test_integrity(self):
  self.assertEqual(self.c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
 def test_import_counts(self):
  s=summary(self.c);self.assertEqual(s['clients'],183);self.assertEqual(s['products'],592);self.assertEqual(s['markets'],6)
  self.assertEqual(s['linked_by_method']['neighbor_inferred'],9)
 def test_preserved_sheets(self):
  self.assertEqual(self.c.execute('SELECT COUNT(DISTINCT sheet_name) FROM source_rows').fetchone()[0],6)
  self.assertEqual(self.c.execute("SELECT COUNT(*) FROM source_rows WHERE sheet_name='MPS Client Info'").fetchone()[0],705)
  self.assertEqual(self.c.execute('SELECT COUNT(*) FROM source_rows').fetchone()[0],2557)
 def test_precise_financial_columns(self):
  p=next(p for p in list_products(self.c) if p['source_row']==4)
  self.assertAlmostEqual(p['total_sales'],309.22)
  self.assertAlmostEqual(p['ad_sales'],85.29)
  self.assertAlmostEqual(p['ad_spend'],107.24)
  self.assertAlmostEqual(p['acos'],107.24/85.29,places=9)
  self.assertAlmostEqual(p['organic_sales'],223.93)
 def test_flags_source_formula_errors(self):
  a=get_alerts(self.c);self.assertEqual(len(a),142)
  rule=Counter(x['rule'] for x in a)
  self.assertEqual(rule['source_formula_error_ad'],39)
  self.assertEqual(rule['organic_mismatch'],1)
  self.assertEqual(rule['tacos_mismatch'],1)
  self.assertEqual(rule['client_link_review'],9)
 def test_specific_reconciliation(self):
  err=next(a for a in get_alerts(self.c) if a['rule']=='organic_mismatch')
  self.assertEqual(err['source_row'],530)
  p=next(p for p in list_products(self.c) if p['source_row']==530)
  self.assertAlmostEqual(p['organic_sales'],253.15)
 def test_brief(self):
  b=client_brief(self.c,'MPS-28724-02');self.assertEqual(b['product_count'],5)
  self.assertEqual(b['blocked_count'],2);self.assertEqual(b['live_count'],3)
  self.assertGreater(len(b['talking_points']),0)
 def test_marketplace_query(self):
  report=execute_query(self.c,'sales versus ad spend by marketplace')
  self.assertEqual(report['title'],'Marketplace performance');self.assertGreaterEqual(report['row_count'],6)
  self.assertEqual(report['columns'][3],'Ad sales ($)')
 def test_operational_queries(self):
  self.assertGreater(execute_query(self.c,'blocked products in UAE')['row_count'],0)
  self.assertGreater(execute_query(self.c,'highest ACOS products')['row_count'],0)
  with self.assertRaises(ValueError):execute_query(self.c,'predict next year revenue by neural networks')
 def test_edit_retains_imported_error(self):
  p=next(p for p in list_products(self.c) if p['source_row']==37)
  self.assertEqual(p['data']['AD'],'#DIV/0!')
  d=dict(p['data']);d['AI']='Confirmed by test. No existing formula changed.'
  save_product(self.c,p['id'],{'client_id':p['client_id'],'data':d})
  newer=next(item for item in list_products(self.c) if item['id']==p['id'])
  self.assertEqual(newer['data']['AD'],'#DIV/0!');self.assertTrue('test' in newer['data']['AI'])
  self.assertGreater(self.c.execute('SELECT COUNT(*) FROM audit').fetchone()[0],0)
 def test_add_client_product_archive_restore(self):
  save_client(self.c,'MPS-TEST-999',{'data':{'J':'Example test client','K':'Source independent test'}})
  prod=save_product(self.c,None,{'client_id':'MPS-TEST-999','data':{'L':'Test Product','Q':'UAE','Y':100,'Z':40,'AB':10,'R':'Live'}})
  p=next(p for p in list_products(self.c) if p['id']==prod['id']);self.assertAlmostEqual(p['acos'],.25)
  archive_entity(self.c,'product',p['id'],True)
  self.assertFalse(any(a['id']==p['id'] for a in list_products(self.c)))
  archive_entity(self.c,'product',p['id'],False)
  self.assertTrue(any(a['id']==p['id'] for a in list_products(self.c)))
 def test_bad_new_financial_amount_rejected(self):
  with self.assertRaises(ValueError):save_product(self.c,None,{'client_id':None,'data':{'L':'Invalid number','Y':'abc'}})
 def test_review_resolution_requires_note(self):
  a=get_alerts(self.c)[0]
  with self.assertRaises(ValueError):update_alert(self.c,a['alert_key'],{'state':'resolved','review_note':''})
  self.assertTrue(update_alert(self.c,a['alert_key'],{'state':'resolved','review_note':'Reviewed source and evidence','owner':'Operations'})['ok'])
 def test_csv_export(self):
  text=csv_export(self.c,'products').decode('utf-8-sig')
  rows=list(csv.reader(io.StringIO(text)))
  self.assertEqual(len(rows)-1,592)
  self.assertIn('Calculated ACOS',rows[0])
 def test_zero_ad_sales_no_invalid_acos(self):
  p=next(p for p in list_products(self.c) if p['source_row']==7)
  self.assertIsNone(p['acos']);self.assertAlmostEqual(p['tacos'],32.38/89.97)

if __name__=='__main__':unittest.main(verbosity=2)
