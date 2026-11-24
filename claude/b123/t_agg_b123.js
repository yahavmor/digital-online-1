// ב123: הסיכום של משפך הלידים סופר את קרלין (karlen / karlin / קרלין) בנפרד, ולא כ-other. node t_agg_b123.js work/agg.js
const fs=require("fs");const code=fs.readFileSync(process.argv[2],"utf8");
const run=input=>new Function("input",code)(input);let n=0,f=0;const ok=(m,c,d)=>{n++;if(!c)f++;console.log((c?"ok  ":"FAIL")+" "+m+(c?"":"  <- "+JSON.stringify(d)))};
const r=run({leads:["1|2026-11-24|karlen|0501111111|","1|2026-11-24|karlin|0502222222|","7|2026-11-24||0502222222|","1|2026-11-24|rachel|0503333333|","1|2026-11-24|karlen|0504444444|t","1|2026-11-24|other1|0505555555|"].join("\n"),
 calls:"",spend:["תאריך|משווק|סכום ₪","24.11.2026|קרלין|80","24.11.2026|רחל|30"].join("\n"),sales:"תאריך|משווק|הערה\n24.11|קרלין|"});
const L=r.data.split("\n");console.log(r.data);
ok("karlen 24.11: 2 leads (karlen + karlin), 1 hot, spend 80, 1 sale",L.includes("2026-11-24\tkarlen\t2\t1\t80\t1"),L);
ok("rachel unchanged",L.includes("2026-11-24\trachel\t1\t0\t30\t0"),L);
ok("test lead (בדיקה) of karlen excluded; unknown marketer still other (1 lead)",L.includes("2026-11-24\tother\t1\t0\t\t0"),L);
ok("no karlen row under other",!L.some(l=>/\tother\t2/.test(l)),L);
ok("no phones in output",!/\d{7}/.test(r.data.replace(/\d{4}-\d{2}-\d{2}/g,"")),r.data);
console.log("TOTAL",n-f+"/"+n);process.exit(f?1:0)
