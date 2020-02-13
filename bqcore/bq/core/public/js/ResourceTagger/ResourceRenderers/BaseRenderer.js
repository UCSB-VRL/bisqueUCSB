// Renderers are defined here for now
Bisque.ResourceTagger.LinkRenderer = function(value, metaData, record) {
    return Ext.String.format('<a href={0} target="_blank">{1}</a>', value, value);
};

/*Bisque.ResourceTagger.ResourceRenderer = function(value, metaData, record) {
    return Ext.String.format('<a href={0} target="_blank">{1}</a>', BQ.Server.url("/client_service/view?resource=" + value), value);
};*/

Bisque.ResourceTagger.ResourceRenderer = function(value, metaData, record) {
    var url = BQ.Server.url('/client_service/view?resource=' + value),
        unique = 'bqresource_' + new Date().valueOf();

    BQFactory.request({
        uri: value,
        uri_params: { view:'short' },
        cb: function(r) {
            var el = Ext.get(unique),
                text = r.resource_type;
            if (r.name) {
                text += ':' + r.name;
            }
            if (r.value) {
                text += ' - ' + r.value;
            }
            el.dom.textContent = text;
        },
    });

    return Ext.String.format('<a href="{0}" target="_blank" id="{1}">{2}</a>', url, unique, value);
};

Bisque.ResourceTagger.EmailRenderer = function(value, metaData, record) {
    return Ext.String.format('<a href={0} target="_blank">{1}</a>', 'mailto:' + value, value);
};

/*Bisque.ResourceTagger.VertexRenderer = function(value, metaData, record) {
    var comboHtml = '<select>';
    var vertices = record.raw.vertices, vertex;

    for (var i = 0; i < vertices.length; i++) {
        vertex = vertices[i];
        comboHtml += '<option>';

        for (var j = 0; j < vertex.xmlfields.length; j++)
            if (vertex[vertex.xmlfields[j]] != null || vertex[vertex.xmlfields[j]] != undefined)
                comboHtml += vertex.xmlfields[j] + ':' + vertex[vertex.xmlfields[j]] + ', ';
        comboHtml += '</option>';
    }
    comboHtml += '</select>';

    return comboHtml;
};*/

Bisque.ResourceTagger.VertexRenderer = function(value, metaData, record) {
    var s = '';
    var vertices = record.raw.vertices;
    var vertex=undefined;
    for (var i=0; (vertex=vertices[i]); i++) {
        var v =[vertex.x || 0, vertex.y || 0, vertex.z || 0, vertex.t || 0, vertex.c || 0];
        s += v.join(',') + '; ';
    }
    return s;
};

Bisque.ResourceTagger.RenderersAvailable = {
    'file' : Bisque.ResourceTagger.LinkRenderer,
    'link' : Bisque.ResourceTagger.LinkRenderer,
    'hyperlink' : Bisque.ResourceTagger.LinkRenderer,
    'statistics' : Bisque.ResourceTagger.LinkRenderer,
    'resource' : Bisque.ResourceTagger.ResourceRenderer,
    'bisqueresource' : Bisque.ResourceTagger.ResourceRenderer,
    'image' : Bisque.ResourceTagger.ResourceRenderer,
    'email' : Bisque.ResourceTagger.EmailRenderer,

    // Gobject renderers
    'point'     : Bisque.ResourceTagger.VertexRenderer,
    'polyline'  : Bisque.ResourceTagger.VertexRenderer,
    'polygon'   : Bisque.ResourceTagger.VertexRenderer,
    'rectangle' : Bisque.ResourceTagger.VertexRenderer,
    'square'    : Bisque.ResourceTagger.VertexRenderer,
    'circle'    : Bisque.ResourceTagger.VertexRenderer,
    'ellipse'   : Bisque.ResourceTagger.VertexRenderer,
    'label'     : Bisque.ResourceTagger.VertexRenderer,
    'line'      : Bisque.ResourceTagger.VertexRenderer,
    'square'    : Bisque.ResourceTagger.VertexRenderer,
};

Bisque.ResourceTagger.BaseRenderer = function(value, metaData, record) {
    var tagType = record.data.type.toLowerCase();
    if (tagType.indexOf('/data_service/') != -1 && record.raw.template && record.raw.template.Type)
        tagType = record.raw.template.Type.toLowerCase();

    var renderer = Bisque.ResourceTagger.RenderersAvailable[tagType];

    if (renderer)
        return renderer.apply(this, arguments);
    else
        return Ext.String.htmlEncode(value);
};
