//  var start = new Date();
//  var end   = new Date();    
//  start.setISO8601('YYYY-MM-DDTHH:mm:SS');
//  end.setISO8601('YYYY-MM-DDTHH:mm:SS');      
//  var time_string = end.diff(start).toString();


      
// extension for Date class to parse ISO8901 variants      
// ex: "2010-10-13T16:52:35" "2010-10-13 16:52:35" 
// ex: "2010-10-13" "2010-10"    
Date.prototype.setISO8601 = function (string) {
    var regexp = "([0-9]{4})(-([0-9]{2})(-([0-9]{2})" +
        "([T|\\s]([0-9]{2}):([0-9]{2})(:([0-9]{2})(\.([0-9]+))?)?" +
        "(Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?";
    var d = string.match(new RegExp(regexp));

    var offset = 0;
    var date = new Date(d[1], 0, 1);

    if (d[3]) { date.setMonth(d[3] - 1); }
    if (d[5]) { date.setDate(d[5]); }
    if (d[7]) { date.setHours(d[7]); }
    if (d[8]) { date.setMinutes(d[8]); }
    if (d[10]) { date.setSeconds(d[10]); }
    if (d[12]) { date.setMilliseconds(Number("0." + d[12]) * 1000); }

    this.setTime(Number(date));
}

Date.prototype.setISO = function (string) {
    return this.setISO8601(string);
}

Date.prototype.toISOString = function () {
    function pad(n){return n<10 ? '0'+n : n};
    return this.getFullYear()+'-'+ 
           pad(this.getMonth()+1)+'-'+
           pad(this.getDate())+' '+
           pad(this.getHours())+':'+
           pad(this.getMinutes())+':'+
           pad(this.getSeconds());
}


Date.prototype.diff = function (another) {
    return new DateDiff(this - another);
}


//------------------------------------------------------------------------------
// Date time difference
//------------------------------------------------------------------------------

function DateDiff(ms) {
    this.weeks = 0; this.days = 0; 
    this.hours = 0; this.mins = 0; this.secs = 0; this.msecs = 0;  
    this.fromMS(ms);    
}

DateDiff.prototype.fromMS = function ( diff ) { 
    if (!diff) return;   
    this.weeks = 0; this.days = 0; 
    this.hours = 0; this.mins = 0; this.secs = 0; this.msecs = 0;  
    
    this.weeks = Math.floor(diff / (1000 * 60 * 60 * 24 * 7));
    diff -= this.weeks * (1000 * 60 * 60 * 24 * 7);

    this.days = Math.floor(diff / (1000 * 60 * 60 * 24)); 
    diff -= this.days * (1000 * 60 * 60 * 24);

    this.hours = Math.floor(diff / (1000 * 60 * 60)); 
    diff -= this.hours * (1000 * 60 * 60);
    
    this.mins = Math.floor(diff / (1000 * 60)); 
    diff -= this.mins * (1000 * 60);
    
    this.secs = Math.floor(diff / 1000); 
    diff -= this.secs * 1000;
    
    this.msecs = diff; 
}

DateDiff.prototype.toString = function () {
  var s = '';
  if (this.weeks>0) s += ''+ this.weeks +' weeks ';
  if (this.days>0)  s += ''+ this.days  +' days ';
  if (this.hours>0) s += ''+ this.hours +' hours ';
  if (this.mins>0)  s += ''+ this.mins  +' minutes ';    
  if (this.secs>0)  s += ''+ this.secs  +' seconds ';  
  if (s=='' && this.msecs>0)  s += ''+ this.msecs  +'ms';  
  return s;
}
