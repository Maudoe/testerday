global.window = {};
require('E:/testerday/alpega_i18n.js');
const cyb = window.ALPEGA.cyb;
const out = process.argv[2];
require('fs').writeFileSync(out, JSON.stringify(cyb, null, 1));
console.log('dumped', cyb.length, 'cards ->', out);
