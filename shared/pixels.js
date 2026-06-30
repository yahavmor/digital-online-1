async function loadFacebookPixel() {
    const p = getParams();
    if (!p.marketer) return;

    const res = await fetch('/shared/marketers.json');
    const marketers = await res.json();

    const m = marketers[p.marketer];
    if (!m || !m.fb_pixel) return;

    const s = document.createElement('script');
    s.innerHTML = `
      !function(f,b,e,v,n,t,s){
        if(f.fbq)return;
        n=f.fbq=function(){ n.callMethod ?
          n.callMethod.apply(n, arguments) : n.queue.push(arguments) };
        if(!f._fbq) f._fbq=n;
        n.push=n; n.loaded=!0; n.version='2.0'; n.queue=[];
        t=b.createElement(e); t.async=!0; t.src=v;
        s=b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t,s);
      }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

      fbq('init', '${m.fb_pixel}');
      fbq('track', 'PageView');
    `;
    document.head.appendChild(s);
}

loadFacebookPixel();
