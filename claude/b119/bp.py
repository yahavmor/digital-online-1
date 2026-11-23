import json
code=open("agg.js").read()
C=8946556; PUB="1BH9ek3TUQYyeTqPfxuW6Sio1dkt-Jari688owyiSRtM"; PRIV="1VGSoVMTF6KCxsnW1FUBPBpDMWJFM1XqGmnS3VBMw0As"; SP="1TxtGeZjDHi0d2_OuQUBZDgUy74t-2CfsE5hHRuDpMgU"
def rows(i,sheet,tab,name):
    return {"id":i,"module":"google-sheets:filterRows","version":2,"parameters":{"__IMTCONN__":C},
     "mapper":{"from":"drive","limit":5000,"sheetId":tab,"sortOrder":"asc","spreadsheetId":sheet,"tableFirstRow":"A1:Z1","includesHeaders":False,"valueRenderOption":"UNFORMATTED_VALUE","dateTimeRenderOption":"SERIAL_NUMBER"},
     "metadata":{"designer":{"x":i*150,"y":0,"name":name}}}
def agg(i,feeder,val,name): return {"id":i,"module":"util:TextAggregator","version":1,"parameters":{"feeder":feeder,"rowSeparator":"\n"},"mapper":{"value":val},"metadata":{"designer":{"x":i*150,"y":0,"name":name}}}
flow=[
 {"id":1,"module":"datastore:SearchRecord","version":1,"parameters":{"limit":5000,"datastore":148094,"continueWhenNoRes":True},
  "mapper":{"filter":[[{"a":"stage","b":"1","o":"number:equal"}],[{"a":"stage","b":"7","o":"number:equal"}]]},"metadata":{"designer":{"x":0,"y":0,"name":"148094: שלב 1 (ליד) ושלב 7 (וואטסאפ)"}}},
 agg(2,1,"{{1.data.stage}}|{{substring(ifempty(1.data.first_seen; emptystring); 0; 10)}}|{{ifempty(1.data.marketer; emptystring)}}|{{1.data.phone}}|{{if(contains(ifempty(1.data.name; emptystring); \"בדיקה\"); \"t\"; emptystring)}}","שורות פנימיות (לא נשמרות)"),
 {"id":3,"module":"datastore:SearchRecord","version":1,"parameters":{"limit":5000,"datastore":153039,"continueWhenNoRes":True},
  "mapper":{"filter":[[{"a":"outcome","b":"callback_requested","o":"text:equal"}]]},"metadata":{"designer":{"x":450,"y":0,"name":"153039: ביקשו שיחה"}}},
 agg(4,3,"{{3.data.phone}}","טלפונים (פנימי)"),
 rows(5,SP,"הוצאה","הוצאה יומית (הממומן)"),
 agg(6,5,"{{5.`0`}}|{{5.`1`}}|{{5.`2`}}","הוצאה"),
 rows(7,PRIV,"מכירות","מכירות (גיליון פרטי, יהב)"),
 agg(8,7,"{{7.`0`}}|{{7.`1`}}","מכירות"),
 {"id":9,"module":"code:ExecuteCode","version":0,"parameters":{},
  "mapper":{"language":"javascript","inputFormat":"editor","codeEditorJavascript":code,
   "input":[{"name":"leads","value":"{{2.text}}"},{"name":"calls","value":"{{4.text}}"},{"name":"spend","value":"{{6.text}}"},{"name":"sales","value":"{{8.text}}"}]},
  "metadata":{"designer":{"x":1350,"y":0,"name":"סיכום לפי יום ומשווק (בלי פרטים אישיים)"}}},
 {"id":10,"module":"google-sheets:updateCell","version":2,"parameters":{"__IMTCONN__":C},
  "mapper":{"select":"map","spreadsheetId":PUB,"sheetId":"LeadFunnel","cell":"B2","value":"{{9.result.data}}","valueInputOption":"RAW"},"metadata":{"designer":{"x":1500,"y":0,"name":"LeadFunnel!B2 = סיכומים"}}},
 {"id":11,"module":"google-sheets:updateCell","version":2,"parameters":{"__IMTCONN__":C},
  "mapper":{"select":"map","spreadsheetId":PUB,"sheetId":"LeadFunnel","cell":"B1","value":"{{9.result.updated}}","valueInputOption":"RAW"},"metadata":{"designer":{"x":1650,"y":0,"name":"LeadFunnel!B1 = עודכן"}}},
]
bp={"name":"ב119 - סיכומי משפך הלידים לדשבורד של בן (כל 30 דק')","flow":flow,"metadata":{"version":1,"scenario":{"roundtrips":1,"maxErrors":3,"autoCommit":True,"autoCommitTriggerLast":True,"sequential":True,"confidential":False,"dataloss":False,"dlq":False,"freshVariables":False}}}
json.dump(bp,open("bp.json","w"),ensure_ascii=False)
print(json.dumps(bp,ensure_ascii=False))
