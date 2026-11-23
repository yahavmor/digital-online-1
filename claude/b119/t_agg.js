const fs=require("fs");const code=fs.readFileSync(__dirname+"/agg.js","utf8");
const run=input=>new Function("input",code)(input);let n=0,f=0;const ok=(m,c,d)=>{n++;if(!c)f++;console.log((c?"ok  ":"FAIL")+" "+m+(c?"":"  <- "+JSON.stringify(d)))};
const r=run({leads:["1|2026-11-22|rachel|0501111111|","7|2026-11-23||0501111111|","1|2026-11-23|amir|+972-52-2222222|","1|2026-11-23|galba|0533333333|t","1|2026-11-21|rachel|0504444444|","1|2026-11-23||0505555555|","1|2026-11-23|galba|0546666666|"].join("\n"),
 calls:"+972522222222\n0599999999",spend:["תאריך|משווק|סכום ₪","46348|רחל|100","46348|רחל|20.5","23.11.2026|גל|50","|אמיר|"].join("\n"),sales:"תאריך|משווק|הערה\n23.11|רחל|"});
const L=r.data.split("\n");console.log(r.data);
ok("no phones or names in output",!/\d{7}/.test(r.data.replace(/\d{4}-\d{2}-\d{2}/g,"")),r.data);
ok("rachel 22.11: 1 lead, hot via stage 7 (joined by phone)",L.includes("2026-11-22\trachel\t1\t1\t120.5\t0"),L);
ok("amir 23.11: 1 lead, hot via call request (+972 format)",L.includes("2026-11-23\tamir\t1\t1\t\t0"),L);
ok("test lead (בדיקה) excluded, gal 1 lead not hot, spend 50",L.includes("2026-11-23\tgal\t1\t0\t50\t0"),L);
ok("lead before 22.11 not counted; no-marketer -> other",!L.some(l=>l.includes("2026-11-21"))&&L.includes("2026-11-23\tother\t1\t0\t\t0"),L);
ok("sales 23.11 rachel counted, rows meta",L.includes("2026-11-23\trachel\t0\t0\t\t1")&&L.includes("spend_rows\t3")&&L.includes("sales_rows\t1"),L);
ok("updated is Israel time",/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(r.updated),r.updated);
console.log("TOTAL",n-f+"/"+n);process.exit(f?1:0)
