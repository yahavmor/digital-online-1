// קריאת כל הפרמטרים מה־URL
const P = new URLSearchParams(location.search);

// אובייקט מסודר עם כל הפרמטרים החשובים
const params = {
    marketer: P.get('marketer') || '',
    supplier: P.get('lm_supplier') || '',
    src: P.get('utm_source') || '',
    medium: P.get('utm_medium') || '',
    campaign: P.get('utm_campaign') || '',
    ref: P.get('ref') || P.get('variant') || '',
    page: P.get('page') || ''
};

// פונקציה שמחזירה את כל הפרמטרים לכל דף בפלואו
function getParams() {
    return params;
}
