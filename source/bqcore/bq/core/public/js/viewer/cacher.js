var buffer = [];

function doCacheTile (buf, pos, url) {
    try {
        var xhr = buf[pos];
        xhr.open('GET', url);
        xhr.responseType = 'blob';
        xhr.send();
    } catch (e) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url);
        xhr.responseType = 'blob';
        xhr.send();
        buf[pos] = xhr;
    }
};

self.onmessage = function(e) {
    var data = e.data;
    if (data.url && data.pos) {
        doCacheTile (buffer, data.pos, data.url);
    };
};