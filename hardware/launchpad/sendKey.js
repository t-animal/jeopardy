var ks = require('node-key-sender')

function sendKey(key) {
    if (process.env.NODE_ENV === 'test') {
        console.log(key);
        return;
    }

    ks.sendKey(key)
}

module.exports = sendKey