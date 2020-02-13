//-------------------------------------------------------------------------
// TagExplore
//-------------------------------------------------------------------------
function TagExplore(tag_str, component) {
    this.container = component;
    this.queryTag( tag_str );
}

TagExplore.prototype.queryTag = function( tag_str ) {
  var v = tag_str.split(':');
  this.title = v[0];
  this.tag = v[1];  
  this.query = new BQQuery("/data_service/image?tag_values="+this.tag, this, callback(this, this.createValues) );
}

function encodeURLquery(s) {
    return escape(s).replace(/\s/g, '+');
}

TagExplore.prototype.createValues = function(q) {
  if (q.tags.length <= 0) return;

  this.html = '<h3>'+this.title+':</h3>';
  this.html += '<ul>';

  for (var i=0; i<q.tags.length; i++) {
    this.html += '<li><a href=\'/client_service/browser?tag_query='+encodeURLquery(this.tag)+':"'+encodeURLquery(q.tags[i])+'"\'>';  
    this.html += q.tags[i]+'</a></li>';        
  }  

  this.html += '</ul>';
  
  this.container.add( { title: this.title, html: this.html, autoScroll: true, } );
}

//-------------------------------------------------------------------------
// DataExplore
//-------------------------------------------------------------------------

function DataExplore(str, component) {
    var tags = str.split(';');
    var items = new Array();
    for (var i=0; i<tags.length; i++) {
        items.push( new TagExplore(tags[i], component) );
    }
    return items;
}


