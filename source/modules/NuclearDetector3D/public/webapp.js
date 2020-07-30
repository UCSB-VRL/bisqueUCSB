/*******************************************************************************

  BQ.renderers.multiroot.Image

  Author: Dima Fedorov

  Version: 1

  History:
    2015-11-25 13:57:30 - first creation

*******************************************************************************/


// overwrite standard renderer with our own
Ext.onReady( function() {
    BQ.renderers.resources.image = 'BQ.renderers.nd3d.Image';
});

// provide our renderer
Ext.define('BQ.renderers.nd3d.Image', {
    extend: 'BQ.renderers.Image',

    afterRender : function() {
        this.callParent();
        this.queryById('bar_bottom').add({
            xtype: 'tbspacer',
            width: 15,
        }, {
            xtype: 'colorfield',
            itemId: 'color1',
            cls: 'simplepicker',
            labelWidth: 0,
            name: 'color1',
            value: '0000ff',
            listeners: {
                scope: this,
                change: this.onNewGradient,
            },
        }, {
            xtype: 'colorfield',
            itemId: 'color2',
            cls: 'simplepicker',
            labelWidth: 0,
            name: 'color2',
            value: 'ffff00',
            listeners: {
                scope: this,
                change: this.onNewGradient,
            },
        }, {
            xtype: 'tbspacer',
            width: 15,
        }, {
            xtype: 'slider',
            width: 200,
            value: 0,
            animate: false,
            increment: 1,
            minValue: 0,
            maxValue: 100,
            listeners: {
                scope: this,
                change: this.onFilter,
            },
        }, {
            xtype: 'tbspacer',
            width: 20,
        }, {
            xtype:'button',
            text: 'Save',
            tooltip: 'Save filtered results into the module execution document',
            scope: this,
            handler: this.save,
        }, {
            xtype: 'tbspacer',
            flex: 1,
        });
    },

    onFilter : function(slider, newvalue) {
        BQGObject.confidence_cutoff = newvalue;
        var me = this;
        clearTimeout(this.updatetimer);
        this.updatetimer = setTimeout(function(){ me.reRenderGobs(); }, 50);
    },

    doFilter : function() {
        // request re-rendering of gobjects
        this.reRenderGobs();
    },

    save : function() {
        var me = this,
            points = this.gobjects[0];
        this.setLoading('Filtering...');
        // filter gobjects first
        points.gobjects = points.gobjects.filter(function(g){
            try {
                var confidence = g.gobjects[0].tags[0].value;
                if (confidence<BQGObject.confidence_cutoff) return false;
            } catch (e) {
                return true;
            }
            return true;
        });

        this.setLoading('Saving...');
        points.save_(
            undefined,
            function() {
                me.setLoading(false);
            },
            function() {
                me.setLoading(false);
                BQ.ui.error('Problem saving filtered points');
            }
        );
    },

    onNewGradient: function() {
        var c1 = this.queryById('color1').getColor(),
            c2 = this.queryById('color2').getColor();
        bq_create_gradient(c1.r,c1.g,c1.b,1.0, c2.r,c2.g,c2.b,1.0);
        this.reRenderGobs();
    }

});

