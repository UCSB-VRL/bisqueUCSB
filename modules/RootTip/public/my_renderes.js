/*******************************************************************************

  BQ.renderers.roottip.Mex

  Author: Dima Fedorov

  Version: 1

  History:
    2011-09-29 13:57:30 - first creation

*******************************************************************************/

// overwrite standard renderer with our own
Ext.onReady( function() {
    BQ.renderers.resources.mex = 'BQ.renderers.roottip.Mex';
});


// provide our renderer
Ext.define('BQ.renderers.roottip.Mex', {
    extend: 'BQ.renderers.Mex',

    initComponent : function() {
        this.callParent();
        this.res_uri_for_tools = this.res_uri_for_tools.replace('module_service', 'data_service');
        this.root = this.res_uri_for_tools.replace(/\/\w+_service\/.*$/i, '');
        // little hack to get already parsed MEX
        this.mex = (this.resource && this.resource.doc)? this.resource.doc : undefined;
        if (!this.mex || !this.mex.children || this.mex.children.length<1) {
            this.mex = null;
            BQFactory.request({
                uri: this.res_uri_for_tools,
                cb: callback(this, 'initMex'),
                errorcb: callback(this, 'onerror'),
                uri_params: { view: 'full' },
            });
        }
    },

    initMex : function(mex) {
        this.mex = mex;
    },

    onerror: function(message) {
        BQ.ui.error('Error fethnig resource:<br>' + message);
    },

    createPlot : function(menu, name, template) {
        if (!this.res_uri_for_tools) return;
        menu.add({
            text: template[name+'/label']?template[name+'/label']:'Plot',
            scope: this,
            handler: this.doPlot,
        });
    },

    doPlot : function() {
        if (!this.res_uri_for_tools || !this.mex) {
            BQ.ui.notification('The data is being initialized, please try again a bit later...');
            return;
        }
        var template = this.template_for_tools || {};
        var xmap    = "tag-value-number";
        var xreduce = "vector";
        var xpath   = [];
        var titles  = [];
        if (!this.mex.children || this.mex.children.length<1) {
            xpath.push('//gobject[@type="tipangle"]/tag[@name="angle"]');
            titles.push('angles');
        } else {
            for (var i=0; (p=this.mex.children[i]); i++) {
                if (!(p instanceof BQMex)) continue;
                var s = '//mex[@uri="'+p.uri+'"]'+'//gobject[@type="tipangle"]/tag[@name="angle"]';
                xpath.push(s);
                titles.push('angles '+i);
                //s = '//mex[@uri="'+p.uri+'"]'+'//gobject[@type="tipangle"]/tag[@name="growth"]';
                //xpath.push(s);
                //titles.push('growth '+i);
            }
        }

        var title = template[name+'/title'];
        if (title instanceof Array) title = title.join(', ');
        var opts = { args: {numbins: template[name+'/args/numbins']}, titles: titles, };
        this.plotter = Ext.create('BQ.stats.Dialog', {
            url     : this.res_uri_for_tools,
            xpath   : xpath,
            xmap    : xmap,
            xreduce : xreduce,
            title   : title,
            opts    : opts,
            root    : this.root,
        });

    },

});


