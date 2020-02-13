/*******************************************************************************

  BQ.renderers.javaappletex.Tag

  Author: Dima Fedorov

  Version: 1
  
  History: 
    2013-11-21 09:50:30 - first creation
    
*******************************************************************************/


// overwrite standard renderer with our own
BQ.renderers.resources.tag = 'BQ.javaappletex.Tag';
BQ.renderers.resources.mex = 'BQ.javaappletex.Mex';

var htmlWidget = function( html, title ) {
    var w = Ext.create('Ext.window.Window', {
        modal: true,
        width: BQApp?BQApp.getCenterComponent().getWidth()/1.6:document.width/1.6,
        height: BQApp?BQApp.getCenterComponent().getHeight()/1.2:document.height/1.2,
        buttonAlign: 'center',
        autoScroll: true,
        //html: html, // set html after the layout was done for proper sizing with 100% width and height 
        buttons: [ { text: 'Ok', handler: function () { w.close(); } }],
        title: (title && typeof title == 'string') ? title : undefined,
    });
    w.show(); 
    w.update(html); // set html after the layout was done for proper sizing with 100% width and height 
}; 

Ext.define('BQ.javaappletex.AppletRunner', {
    runApplet: function() {
        var mex = this.mex;
        var inputs = mex.inputs;
        var params = '';
        var par = new Ext.Template('<param name="{name}" value="{value}">');
        var ii = undefined;
        for (var i=0; ii=inputs[i]; ++i) {
            if (ii.type !== 'system-input')
                params += par.apply({name: ii.name, value: ii.value});
        }
        var html = new Ext.Template('<object type="application/x-java-applet" height="100%" width="100%" >\
            <param name="code" value="Sample" />\
            <param name="archive" value="Sample.jar" />\
            <param name="java_arguments" value="-Djnlp.packEnabled=true"/>\
            <param name="scriptable" value="true" />\
            <param name="mayscript" value="true" />\
            <param name="mex" value="{url}">\
            {params}\
            Applet failed to run.  No Java plug-in was found.\
        </object>');
        htmlWidget(html.apply({url: mex.uri, params: params}), 'My java applet');
    },
});

// provide our renderer
Ext.define('BQ.javaappletex.Tag', {
    extend: 'BQ.renderers.Tag',
    mixins: {
        canRun: 'BQ.javaappletex.AppletRunner',
    },
    
    initComponent : function() {
        this.callParent();
        this.insert(0, {
            xtype:   'button',
            text:    'Run my java applet', 
            iconCls: 'applet', 
            scale:   'large', 
            handler: Ext.Function.bind( this.runApplet, this ),
        });           
    },
});

Ext.define('BQ.javaappletex.Mex', {
    extend: 'BQ.renderers.Mex',
    mixins: {
        canRun: 'BQ.javaappletex.AppletRunner',
    },
    
    initComponent : function() {
        this.callParent();
        this.insert(0, {
            xtype:   'button',
            text:    'Run my java applet', 
            iconCls: 'applet', 
            scale:   'large', 
            handler: Ext.Function.bind( this.runApplet, this ),
        });           
    },
});


