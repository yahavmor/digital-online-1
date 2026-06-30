function sendLead(data) {
    const p = getParams();

    const lm = new URLSearchParams();
    lm.append('lm_form', data.form);
    lm.append('lm_key', data.key);
    lm.append('subscribers_name', data.name);
    lm.append('subscribers_phone', data.phone);
    lm.append('subscribers_email', data.email);

    lm.append('lm_supplier', p.supplier);
    lm.append('utm_medium', p.medium);
    lm.append('utm_campaign', p.campaign);
    lm.append('fields[REF]', p.ref);

    fetch('https://api.leadmanager.co.il/handlers/lm/submit.cms?' + lm.toString(), {
        method: 'GET',
        mode: 'no-cors'
    });
}
