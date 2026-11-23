// שרת קבצים מקומי עם gzip, כמו GitHub Pages. שימוש: node srv.js <תיקייה> <פורט>
const http=require('http'),fs=require('fs'),path=require('path'),zlib=require('zlib');
const ROOT=path.resolve(process.argv[2]||'.'),PORT=+(process.argv[3]||8791);
const T={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.webp':'image/webp','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.mp4':'video/mp4','.woff2':'font/woff2','.json':'application/json'};
http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);if(p.endsWith('/'))p+='index.html';const f=path.join(ROOT,p);
 if(!f.startsWith(ROOT)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){r.writeHead(404);return r.end('nf')}
 const ext=path.extname(f),ty=T[ext]||'application/octet-stream',b=fs.readFileSync(f);
 if(/text|javascript|json|svg/.test(ty)&&/gzip/.test(q.headers['accept-encoding']||'')){r.writeHead(200,{'content-type':ty,'content-encoding':'gzip','cache-control':'max-age=600'});return r.end(zlib.gzipSync(b))}
 r.writeHead(200,{'content-type':ty,'content-length':b.length,'cache-control':'max-age=600'});r.end(b)}).listen(PORT,'127.0.0.1');
