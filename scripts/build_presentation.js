/** Rebuild Area71 MPS presentation from the verified NEW-source data audit JSON. */
const pptxgen=require('pptxgenjs');
const fs=require('fs');const path=require('path');
const {warnIfSlideElementsOutOfBounds}=require('/home/oai/skills/slides/pptxgenjs_helpers');
const root=path.resolve(__dirname,'..');
const audit=JSON.parse(fs.readFileSync(path.join(root,'docs','data_audit.json'),'utf8'));
const stats=audit.summary;
const pptx=new pptxgen();pptx.layout='LAYOUT_WIDE';pptx.author='Area71 / Operations Intelligence';pptx.subject='Area71 MPS new-source data intelligence';pptx.title='Area71 MPS Client Intelligence — Verified Source Presentation';pptx.company='Area71';pptx.lang='en-US';pptx.theme={headFontFace:'Aptos Display',bodyFontFace:'Aptos',lang:'en-US'};
const C={dark:'063C35',deep:'082F29',green:'08725D',mint:'11AB87',pale:'EAF6EF',white:'FFFFFF',bg:'F7FAF8',ink:'173D35',secondary:'55756D',subtle:'8BA29A',line:'DCEBE4',gold:'E9AF60',goldPale:'FFF1DD',red:'C95151',redPale:'FCEAE7',blue:'3D79AF',bluePale:'EAF3FB'};
const W=13.333,H=7.5;const SH=pptx.ShapeType;const FONT='Aptos';let index=0;
const t=(s,txt,x,y,w,h,o={})=>s.addText(txt,{x,y,w,h,fontFace:FONT,fontSize:14,color:C.ink,margin:0,breakLine:false,fit:'shrink',...o});
const box=(s,x,y,w,h,fill=C.white,rad=.16,border=C.line)=>{s.addShape(SH.roundRect,{x,y,w,h,rectRadius:rad,fill:{color:fill},line:border?{color:border,width:.75}:{color:fill,width:0}})};
const line=(s,x1,y1,x2,y2,color=C.line,width=1)=>s.addShape(SH.line,{x:x1,y:y1,w:x2-x1,h:y2-y1,line:{color,width}});
const dot=(s,x,y,col=C.mint,diam=.14)=>s.addShape(SH.ellipse,{x,y,w:diam,h:diam,fill:{color:col},line:{color:col}});
function base(title,kicker,subtitle='',notes=''){
 const s=pptx.addSlide();index++;
 s.background={color:C.bg};
 s.addShape(SH.rect,{x:0,y:0,w:W,h:.08,fill:{color:C.green},line:{color:C.green}});
 t(s,kicker.toUpperCase(),.6,.32,11,.3,{fontSize:10.5,color:C.green,bold:true,charSpacing:1.4});
 t(s,title,.6,.78,12.15,.65,{fontSize:30,bold:true,color:C.ink,breakLine:false});
 if(subtitle)t(s,subtitle,.6,1.54,12.05,.52,{fontSize:13,color:C.secondary});
 line(s,.6,7.10,12.72,7.10,C.line,.6);
 t(s,'AREA71  /  MPS CLIENT INTELLIGENCE',.6,7.18,9,.19,{fontSize:9,bold:true,charSpacing:.55,color:C.subtle});
 t(s,String(index).padStart(2,'0'),12.2,7.15,.48,.22,{fontSize:10,bold:true,color:C.subtle,align:'right'});
 s.addNotes(`${notes}\n[Sources]\nInternal source: MPS Client Updates (NEW).xlsx, “MPS Client Info” master worksheet; verified audit in docs/data_audit.json.\n[/Sources]`);
 return s;
}
function addCard(s,x,y,w,h,title,desc,accent=C.green){box(s,x,y,w,h);s.addShape(SH.rect,{x,y,w:.055,h,fill:{color:accent},line:{color:accent}});t(s,title,x+.26,y+.28,w-.44,.38,{fontSize:16,bold:true});t(s,desc,x+.26,y+.80,w-.51,h-1.0,{fontSize:12.5,color:C.secondary,breakLine:false})}
function metric(s,x,y,w,label,value,foot='',accent=C.green){box(s,x,y,w,1.35);t(s,label.toUpperCase(),x+.23,y+.17,w-.5,.21,{fontSize:9.5,bold:true,color:C.secondary,charSpacing:.7});t(s,String(value),x+.22,y+.46,w-.45,.5,{fontSize:27,bold:true,color:accent});t(s,foot,x+.23,y+1.08,w-.4,.18,{fontSize:10,color:C.subtle})}
function labelPill(s,txt,x,y,w,kind='green'){
 const colors={green:[C.pale,C.green],red:[C.redPale,C.red],gold:[C.goldPale,'9B611B'],blue:[C.bluePale,C.blue]};
 const [bg,fg]=colors[kind];box(s,x,y,w,.35,bg,.10,bg);t(s,txt,x+.10,y+.065,w-.2,.20,{fontSize:10,bold:true,color:fg,align:'center'});
}
function listline(s,text,x,y,w,accent=C.mint,fs=15){dot(s,x,y+.105,accent,.11);t(s,text,x+.23,y,w-.25,.54,{fontSize:fs,color:C.ink})}

// 01 cover
{
 const s=pptx.addSlide();index++;s.background={color:C.dark};
 s.addShape(SH.rect,{x:9.78,y:0,w:3.553,h:7.5,fill:{color:'0B584C'},line:{color:'0B584C'}});
 for(let i=0;i<5;i++)for(let j=0;j<4;j++)s.addShape(SH.roundRect,{x:10.12+j*.69,y:.66+i*.74,w:.42,h:.42,rectRadius:.05,line:{color:'257767',width:.4},fill:{color:(i+j)%3===0?'21A587':'115D51',transparency:(i+j)%3===0?20:38}});
 t(s,'area71',.72,.58,4,.54,{fontSize:31,bold:true,color:C.white});
 t(s,'OPERATIONS  ×  SALES',.75,1.55,7,.4,{fontSize:13,color:'8DE4C7',bold:true,charSpacing:2});
 t(s,'FROM SPREADSHEET\nTO CLIENT INTELLIGENCE',.72,2.18,9,2.12,{fontSize:37,bold:true,color:C.white,breakLine:false});
 t(s,'A practical database and three decision-support tools, built from the verified MPS Client Updates (NEW) workbook.',.75,4.77,7.8,1.08,{fontSize:17,color:'C5EADD',breakLine:false});
 line(s,.75,6.47,8.9,6.47,'317A6C');t(s,'NOVEMBER 2026  •  AREA71',.75,6.66,8,.36,{fontSize:12,color:'A2D7C6',bold:true,charSpacing:1});
 s.addNotes('Opening: We are not simply reformatting Excel. We are reducing avoidable decisions made with hidden or inconsistent data. No external revenue-loss statistic is claimed here.\n[Sources]\nInternal: MPS Client Updates (NEW).xlsx and presentation_context_script.md for intended audience/workflow (not for numerical results).\n[/Sources]');
}
// 02 reality
{
 const s=base('The problem is not the spreadsheet. It is the friction.','01 / The operating reality','Critical context is present, but distributed across long rows, status labels, and team-specific views.');
 addCard(s,.65,2.3,3.88,3.22,'Operations: hidden blockers','Shipment stops, compliance requirements, and production updates can remain buried until the next status check.',C.red);
 addCard(s,4.73,2.3,3.88,3.22,'Sales: slow preparation','A rep must inspect product history, ad performance, and notes before making a relevant follow-up.',C.gold);
 addCard(s,8.81,2.3,3.88,3.22,'Leadership: competing views','Duplicated sheets can lead to mismatched counts, unclear ownership, and inconsistent reporting.',C.green);
 box(s,.65,5.8,12.04,.73,C.pale,.1,C.pale);t(s,'DESIGN PRINCIPLE     The system should reveal where human attention is needed — not make decisions silently.',.98,6.03,11.5,.28,{fontSize:15,bold:true,color:C.dark});
}
// 03 verified audit
{
 const s=base('A verified baseline from the NEW workbook','02 / Source audit','We counted the canonical MPS Client Info register once, while preserving all six worksheets.');
 metric(s,.64,2.35,2.88,'Client profiles',stats.clients,'Explicit client IDs');
 metric(s,3.74,2.35,2.88,'Product records',stats.products,'Main-register products');
 metric(s,6.85,2.35,2.88,'Original fields',35,'Source columns A–AI');
 metric(s,9.96,2.35,2.72,'Markets',stats.markets,'Recorded geographies');
 box(s,.64,4.02,12.04,2.14,C.white,.12,C.line);
 t(s,'Source integrity summary',.94,4.29,6,.35,{fontSize:18,bold:true});
 listline(s,'142 current review findings generated from the source values',.94,4.9,6.7,C.gold,14);
 listline(s,'9 inferred client links require confirmation',.94,5.43,6.7,C.red,14);
 t(s,'Original workbook preserved\nOther five tabs archived, not double-counted',8.6,4.76,3.5,1.07,{fontSize:13,bold:true,color:C.green});
}
// 04 architecture
{
 const s=base('One governed source → three useful tools','03 / System architecture','An untouched archive plus an editable operational database, with source-row traceability.');
 box(s,.66,2.32,3.1,1.45,C.white);t(s,'ORIGINAL XLSX',.9,2.60,2.62,.3,{fontSize:15,bold:true,color:C.green});t(s,'Six archived sheets\nMain register selected',.9,3.00,2.64,.58,{fontSize:13,color:C.secondary});
 t(s,'→',3.89,2.62,.65,.6,{fontSize:38,color:C.green,align:'center'});
 box(s,4.68,2.25,3.75,1.58,C.pale,.12,C.pale);t(s,'EDITABLE DATABASE',4.96,2.56,3.2,.3,{fontSize:15,bold:true,color:C.dark});t(s,'183 clients · 592 products\nAudit log · source confidence',4.96,2.98,3.0,.59,{fontSize:13,color:C.ink});
 t(s,'→',8.55,2.62,.6,.6,{fontSize:38,color:C.green,align:'center'});
 box(s,9.33,2.32,3.35,1.45,C.white);t(s,'TEAM DASHBOARD',9.58,2.60,2.8,.3,{fontSize:15,bold:true,color:C.green});t(s,'Search · edit · export\nClient and product profiles',9.58,3.02,2.83,.57,{fontSize:13,color:C.secondary});
 line(s,6.56,3.92,6.56,4.49,C.green,2);
 box(s,.66,4.64,3.82,1.34,C.white);t(s,'01   ANOMALY GUARD',.93,4.95,3.2,.3,{fontSize:15,bold:true});t(s,'Operational holds + data checks',.93,5.36,3.2,.36,{fontSize:12,color:C.secondary});
 box(s,4.74,4.64,3.82,1.34,C.white);t(s,'02   ASK THE DATA',5.01,4.95,3.25,.3,{fontSize:15,bold:true});t(s,'Question → grounded reports',5.01,5.36,3.25,.36,{fontSize:12,color:C.secondary});
 box(s,8.82,4.64,3.86,1.34,C.white);t(s,'03   CLIENT BRIEF',9.1,4.95,3.27,.3,{fontSize:15,bold:true});t(s,'Meeting notes + account history',9.1,5.36,3.29,.36,{fontSize:12,color:C.secondary});
 t(s,'No automatic PPC pauses, client messaging or live currency conversion.',.72,6.45,12,.25,{fontSize:11,color:C.secondary});
}
// 05 before after
{
 const s=base('What changes in the daily workflow?','04 / The shift','One person can update a record; both functions can consume a consistent, traceable view.');
 box(s,.64,2.26,5.82,3.82,C.white);box(s,6.83,2.26,5.82,3.82,C.pale,.14,C.pale);
 labelPill(s,'BEFORE · MANUAL',.96,2.57,2.1,'red');labelPill(s,'AFTER · SYSTEM',7.15,2.57,2.13,'green');
 const left=['Search long sheets for one product','Compare several status and note fields','Calculate ratios manually','Ask another team to verify next steps'];
 const right=['Search one linked product/client record','See calculated ratios and review flags','Get a report in seconds','Assign an owner and record a decision'];
 left.forEach((x,i)=>listline(s,x,.99,3.16+i*.6,5.18,C.red,14));
 right.forEach((x,i)=>listline(s,x,7.18,3.16+i*.6,5.18,C.mint,14));
 t(s,'The objective: less manual checking, more verifiable decisions.',.78,6.44,11.8,.4,{fontSize:17,bold:true,color:C.green,align:'center'});
}
// 06 alerts
{
 const s=base('Tool 01  /  Anomaly Guard','05 / Operations intelligence','A clear review queue instead of hidden red flags scattered across Excel cells.');
 const cats=[['Shipment stopped',29,C.red],['Compliance status',17,'E69C63'],['ACOS ≥ 100%',29,C.gold],['Client link review',9,C.blue],['TACOS formula errors',39,C.blue],['Other data checks',19,C.green]];
 box(s,.64,2.3,7.27,3.82,C.white);t(s,'Import-time alert categories',.94,2.60,6,.35,{fontSize:17,bold:true});
 cats.forEach(([title,n,color],i)=>{let y=3.03+i*.46;t(s,title,.96,y,2.37,.25,{fontSize:13});s.addShape(SH.roundRect,{x:3.46,y:y+.055,w:n/39*3.33,h:.20,rectRadius:.05,line:{color},fill:{color}});t(s,String(n),6.97,y,0.5,.25,{fontSize:13,bold:true,align:'right'})});
 box(s,8.18,2.3,4.51,3.82,C.dark,.16,C.dark);t(s,'142',8.55,2.76,3.7,.83,{fontSize:55,bold:true,color:C.white,align:'center'});t(s,'ACTIVE REVIEW ALERTS',8.51,3.76,3.8,.3,{fontSize:12,bold:true,color:'B5E8D2',charSpacing:1,align:'center'});
 t(s,'46 critical  ·  39 high  ·  57 medium',8.50,4.55,3.82,.5,{fontSize:14,color:C.white,align:'center'});t(s,'Status label ≠ confirmed business impact',8.53,5.34,3.75,.45,{fontSize:12,color:'B7DCD2',align:'center'});
 t(s,'Findings can be acknowledged, assigned, investigated, and resolved with an evidence note.',.75,6.49,12,.35,{fontSize:12,color:C.secondary});
}
// 07 integrity exceptions
{
 const s=base('An anomaly is a question, not a conclusion','06 / Data integrity','The system highlights discrepancies without silently changing client data.');
 addCard(s,.66,2.31,3.85,3.36,'Row 530 · Organic sales','Recorded $0.00; calculated $253.15 from $299.71 total minus $46.56 ad sales. Verify source formula/reporting period.',C.red);
 addCard(s,4.75,2.31,3.85,3.36,'Row 194 · TACOS','Source reads 239.05%; calculated ≈2.39%. Likely a percentage scaling issue; original value remains intact.',C.gold);
 addCard(s,8.84,2.31,3.85,3.36,'9 inferred client links','Neighboring rows suggest an association, but it must be reviewed before the client relationship is confirmed.',C.blue);
 box(s,.68,6.0,11.99,.55,C.pale,.09,C.pale);t(s,'Never label a reconciliation difference as missing revenue without checking the underlying reports.',.93,6.17,11.5,.23,{fontSize:13,bold:true,color:C.dark});
}
// 08 actual case
{
 const s=base('A real operational example: MPS-28724-02','07 / Live account walkthrough','Five products for Hozaifa Bin Sadeque, with mixed operational statuses and PPC results.');
 metric(s,.66,2.36,2.72,'Portfolio products',5,'One linked client');metric(s,3.60,2.36,2.72,'Recorded holds',2,'Shipping STOP',C.red);metric(s,6.55,2.36,2.72,'UAE trash-bag ACOS','125.7%','107.24 ÷ 85.29',C.red);metric(s,9.49,2.36,3.16,'Best UK example','21.7%','Hydrogen bottle ACOS');
 box(s,.66,4.08,12.0,2.0,C.white);t(s,'What should happen next?',.95,4.37,6.3,.36,{fontSize:18,bold:true});
 listline(s,'Ops confirms the underlying shipping reason and next milestone.',.98,4.95,10.9,C.red,15);
 listline(s,'PPC reviews campaign economics before changing bids or targeting.',.98,5.49,10.9,C.gold,15);
 t(s,'No automated keyword pause is executed.',.72,6.46,10,.3,{fontSize:12,color:C.secondary});
}
// 09 reporting
{
 const s=base('Tool 02  /  Ask the Data','08 / Reporting intelligence','Turn common questions into calculations against the edited database—without copying into pivot tables.');
 box(s,.65,2.25,5.65,3.9,C.dark,.16,C.dark);t(s,'ASK IN PLAIN ENGLISH',1.01,2.58,4.95,.3,{fontSize:13,bold:true,color:'A3E5CF',charSpacing:.8});
 const qs=['“Sales versus ad spend by marketplace”','“Show blocked products in UAE”','“Highest ACOS products”','“PPC performance by specialist”'];
 qs.forEach((x,i)=>{box(s,.98,3.07+i*.64,4.98,.46,'175E51',.08,'175E51');t(s,x,1.15,3.18+i*.64,4.6,.25,{fontSize:13,color:C.white})});
 box(s,6.61,2.25,6.07,3.9,C.white);t(s,'GET A GROUNDED OUTPUT',6.91,2.58,5.5,.32,{fontSize:13,color:C.green,bold:true,charSpacing:.8});
 const data=stats.marketplace.filter(a=>a.marketplace!=='Not set').slice(0,4);
 t(s,'MARKET     TOTAL SALES     AD SPEND',6.91,3.11,5.5,.3,{fontSize:11,bold:true,color:C.subtle});
 data.forEach((a,i)=>{let y=3.52+i*.55;line(s,6.94,y+.40,12.28,y+.40,C.line,.6);t(s,a.marketplace,6.92,y,1.2,.31,{fontSize:13,bold:true});t(s,'$'+Math.round(a.total_sales).toLocaleString(),8.39,y,1.75,.31,{fontSize:13});t(s,'$'+Math.round(a.ad_spend).toLocaleString(),10.40,y,1.73,.31,{fontSize:13})});
 t(s,'Supported question patterns are explicit: this offline version does not interpret arbitrary queries.',.74,6.48,11.9,.35,{fontSize:11.8,color:C.secondary});
}
// 10 chart
{
 const s=base('Marketplace view: actual recorded totals','09 / Verified data','Total sales versus ad spend are distinct metrics, each summed from the main register.');
 box(s,.65,2.21,12.05,4.43,C.white);
 const markets=stats.marketplace.filter(x=>x.marketplace!=='Not set');const mx=Math.max(...markets.map(a=>a.total_sales));
 t(s,'TOTAL SALES',.98,2.55,1.55,.25,{fontSize:10,bold:true,color:C.green});t(s,'AD SPEND',2.73,2.55,1.5,.25,{fontSize:10,bold:true,color:'B97A37'});
 let y=3.06;for(const a of markets){t(s,a.marketplace,.96,y+.08,1.03,.24,{fontSize:13,bold:true});let width=a.total_sales/mx*7.8;s.addShape(SH.roundRect,{x:2.05,y:y+.03,w:width,h:.22,rectRadius:.06,fill:{color:C.green},line:{color:C.green}});let swidth=Math.max(.03,a.ad_spend/mx*7.8);s.addShape(SH.roundRect,{x:2.05,y:y+.30,w:swidth,h:.17,rectRadius:.04,fill:{color:C.gold},line:{color:C.gold}});t(s,'$'+Math.round(a.total_sales).toLocaleString(),10.3,y+.09,1.78,.24,{fontSize:13,bold:true,align:'right'});y+=.52}
 t(s,`TOTAL RECORDED SALES  $${Math.round(stats.total_sales).toLocaleString()}       AD SPEND  $${Math.round(stats.ad_spend).toLocaleString()}`,1.03,6.27,10.9,.22,{fontSize:12,bold:true,color:C.dark});
}
// 11 definitions
{
 const s=base('Use the right denominator before taking action','10 / Metric literacy','The application recalculates key ratios from the raw financial inputs.');
 addCard(s,.65,2.38,3.83,3.24,'ACOS','Ad spend ÷ ad-attributed sales. Above 100% means ad spend exceeds ad sales for the recorded period.',C.red);
 t(s,'$107.24  ÷  $85.29',.97,4.83,3.24,.38,{fontSize:18,bold:true,color:C.red,align:'center'});
 addCard(s,4.75,2.38,3.83,3.24,'TACOS','Ad spend ÷ total sales. It measures ad cost relative to all recorded sales, not just attributed sales.',C.gold);
 t(s,'$107.24  ÷  $309.22',5.07,4.83,3.24,.38,{fontSize:18,bold:true,color:'B57622',align:'center'});
 addCard(s,8.85,2.38,3.83,3.24,'Ad ROAS','Ad-attributed sales ÷ ad spend. Do not substitute total sales for ad-attributed sales.',C.green);
 t(s,'$85.29  ÷  $107.24',9.15,4.83,3.26,.38,{fontSize:18,bold:true,color:C.green,align:'center'});
 t(s,'All three examples reference the same recorded product row in the NEW workbook.',.81,6.37,11.8,.43,{fontSize:13,color:C.secondary,align:'center'});
}
// 12 client brief
{
 const s=base('Tool 03  /  Client Brief','11 / Sales intelligence','Bring product history, status, recorded client requirements and campaign data into one concise preparation sheet.');
 box(s,.68,2.23,7.33,3.94,C.white);t(s,'CLIENT: HOZAIFA BIN SADEQUE',1.00,2.57,6.6,.3,{fontSize:14,bold:true,color:C.green});t(s,'MPS-28724-02  •  5 PRODUCTS',1.00,2.98,6.7,.25,{fontSize:11,color:C.subtle});
 const bullets=['Hydrogen Water Bottle 2025 (UK) · ACOS 21.7%','Trash bag 60pcs (UAE) · ACOS 125.7%','Two products marked “Shipping STOP”','Client requirements include a two-product allocation request'];
 bullets.forEach((x,i)=>listline(s,x,1.02,3.61+i*.55,6.55,i===1?C.red:C.mint,13));
 box(s,8.28,2.23,4.38,3.94,C.pale,.15,C.pale);t(s,'60-SECOND TALKING POINTS',8.60,2.60,3.76,.42,{fontSize:15,bold:true,color:C.dark});
 const talking=['Confirm the status of the two held products.','Ask PPC to review high-ACOS campaigns.','Validate inventory before suggesting a restock.'];talking.forEach((x,i)=>listline(s,x,8.60,3.31+i*.83,3.63,C.green,13));
 t(s,'Never claim that a logistics or PPC fix is already complete unless the responsible team confirms it.',.83,6.46,11.8,.36,{fontSize:12,color:C.secondary});
}
// 13 ops flow
{
 const s=base('An Operations workflow that closes the loop','12 / Daily operations','Turn a flagged problem into a documented, trackable action.');
 const steps=[['01','Scan alerts','Filter critical/high findings by product or status.'],['02','Verify the source','Open the original row and check the actual blocker.'],['03','Assign ownership','Name the responsible Ops or PPC specialist.'],['04','Record outcome','Add evidence, next milestone and review status.']];
 steps.forEach((st,i)=>{const x=.65+i*3.06;box(s,x,2.72,2.79,2.62,i%2===0?C.white:C.pale,.14,i%2===0?C.line:C.pale);t(s,st[0],x+.22,3.0,2.4,.60,{fontSize:34,bold:true,color:C.green});t(s,st[1],x+.22,3.72,2.33,.36,{fontSize:16,bold:true});t(s,st[2],x+.22,4.17,2.3,.86,{fontSize:12.5,color:C.secondary});if(i<3)t(s,'→',x+2.78,3.62,.27,.42,{fontSize:20,color:C.green,align:'center'})});
 box(s,.66,5.79,12.0,.72,C.dark,.10,C.dark);t(s,'A reviewed alert is not necessarily a resolved business issue. Keep the underlying status accurate.',.99,6.0,11.43,.26,{fontSize:14,bold:true,color:C.white});
}
// 14 sales workflow
{
 const s=base('A Sales workflow with better account context','13 / Daily sales','Personalize follow-ups using evidence — and ask Operations before promising timelines.');
 box(s,.66,2.34,3.73,3.52,C.white);labelPill(s,'1 · FIND',.98,2.69,1.13,'blue');t(s,'Search a client',.98,3.28,3.08,.5,{fontSize:19,bold:true});t(s,'One ID connects multiple markets, products, notes, and statuses.',.98,4.05,3.05,1.13,{fontSize:14,color:C.secondary});
 box(s,4.80,2.34,3.73,3.52,C.white);labelPill(s,'2 · REVIEW',5.11,2.69,1.42,'gold');t(s,'Generate a brief',5.11,3.28,3.08,.5,{fontSize:19,bold:true});t(s,'Spot recorded holds, PPC outliers, inventory signals, and past requests.',5.11,4.05,3.08,1.13,{fontSize:14,color:C.secondary});
 box(s,8.94,2.34,3.73,3.52,C.white);labelPill(s,'3 · FOLLOW UP',9.25,2.69,1.72,'green');t(s,'Confirm and act',9.25,3.28,3.08,.5,{fontSize:19,bold:true});t(s,'Agree a next action, capture notes, and preserve the handoff context.',9.25,4.05,3.08,1.13,{fontSize:14,color:C.secondary});
 t(s,'The outcome is fewer generic pitches and better coordination, not automatically generated promises.',.75,6.29,12,.55,{fontSize:14,bold:true,color:C.green,align:'center'});
}
// 15 edit experience
{
 const s=base('A database designed for daily edits','14 / Usability','No need to navigate 35 columns for every small update.');
 const cards=[['Product records','Search by client ID, SKU, ASIN, marketplace or status; edit a focused record.'],['Client directory','Keep stable client information, relationships and communication context.'],['Review queue','Assign owners and store evidence against generated alerts.'],['Exports & backups','Download CSV snapshots, preserve original Excel and back up the SQLite file.']];
 cards.forEach((q,i)=>{let x=.67+(i%2)*6.14,y=2.31+Math.floor(i/2)*1.96;addCard(s,x,y,5.82,1.65,q[0],q[1],i%2?C.gold:C.green)});
 t(s,'All product records carry an original worksheet row reference and a client-link confidence label.',.82,6.55,11.9,.29,{fontSize:12,color:C.secondary});
}
// 16 governance
{
 const s=base('Respect client data. Keep the scope honest.','15 / Governance','The local build is appropriate for a controlled one-person pilot, not a public multi-user deployment.');
 addCard(s,.67,2.28,5.83,3.62,'What works locally','Private SQLite database; editable record screens; immutable original source archive; human alert review; activity log; manual backups.',C.green);
 addCard(s,6.85,2.28,5.83,3.62,'What production still requires','Authenticated accounts, role-based access, encrypted storage, tested backup/restore, secure hosting, and a migration plan.',C.red);
 box(s,.67,6.12,12.01,.49,C.pale,.08,C.pale);t(s,'No Amazon, email, WhatsApp, Google Sheets or currency-rate integration is enabled.',.95,6.27,11.4,.25,{fontSize:12.5,bold:true,color:C.dark});
}
// 17 rollout
{
 const s=base('Make adoption controlled, not disruptive','16 / Recommended rollout','Start with source validation, assign ownership, then move into repeatable team reviews.');
 const steps=[['PILOT 01','Validate client links','Confirm the nine inferred relationships and known source discrepancies.'],['PILOT 02','Nominate data owners','Agree who updates shipping, listing, inventory and PPC fields.'],['PILOT 03','Run real workflows','Test daily alert review, a report query, and a Sales client brief.'],['LATER','Scope secure hosting','Add access controls and production integrations only after sign-off.']];
 steps.forEach((p,i)=>{let x=.68+i*3.05;box(s,x,2.38,2.79,3.58,i%2===0?C.white:C.pale,.13,i%2===0?C.line:C.pale);t(s,p[0],x+.24,2.73,2.31,.23,{fontSize:11,bold:true,color:C.green,charSpacing:.7});t(s,p[1],x+.24,3.29,2.32,.62,{fontSize:18,bold:true});t(s,p[2],x+.24,4.22,2.28,1.24,{fontSize:13,color:C.secondary})});
 t(s,'A strong pilot ends with cleaner source data, a review habit, and measured time saved — not just a dashboard.',.76,6.39,11.9,.43,{fontSize:13,color:C.secondary,align:'center'});
}
// 18 close
{
 const s=pptx.addSlide();index++;s.background={color:C.dark};
 s.addShape(SH.rect,{x:0,y:0,w:.18,h:H,fill:{color:C.mint},line:{color:C.mint}});
 t(s,'WHAT WE BUILT',.75,.72,9,.37,{fontSize:13,bold:true,color:'8CE1C5',charSpacing:1.4});
 t(s,'ONE DATABASE.\nTHREE PRACTICAL TOOLS.\nONE SOURCE OF TRUTH.',.75,1.55,11.4,2.55,{fontSize:34,bold:true,color:C.white});
 const next=['Demo: edit a product and trace its source row','Run a marketplace report and review one alert','Generate a client briefing and record a note'];
 next.forEach((x,i)=>{dot(s,.85,4.67+i*.56,C.mint,.11);t(s,x,1.07,4.61+i*.56,10.3,.34,{fontSize:16,color:'D3EEE3'})});
 line(s,.8,6.65,12.42,6.65,'377769');t(s,'AREA71  •  MPS OPERATIONS & SALES',.85,6.92,10,.29,{fontSize:12,color:'8CE1C5',bold:true,charSpacing:1});
 s.addNotes('Close: The pilot is ready to explore locally, but live business decisions require source verification and named owners. Next decision: approve client-link review, one-person trial, and future secure deployment requirements.\n[Sources]\nInternal verified source: MPS Client Updates (NEW).xlsx and delivered local application.\n[/Sources]');
}

// Slide canvas diagnostics; intentional background/card + text overlays are excluded from overlap checker.
for(const slide of pptx._slides){warnIfSlideElementsOutOfBounds(slide,pptx)}
const out=path.join(root,'docs','Area71_MPS_Client_Intelligence_Presentation.pptx');
pptx.writeFile({fileName:out}).then(()=>console.log('Created',out,'slides',index)).catch(e=>{console.error(e);process.exit(1)});
