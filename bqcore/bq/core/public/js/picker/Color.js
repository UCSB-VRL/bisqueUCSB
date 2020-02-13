/*******************************************************************************

  BQ.picker.Color - Color picker provides a simple color palette for choosing
    colors. The picker can be rendered to any container. The
    available default to a standard 40-color palette; this can be customized with the {@link #colors} config.

    Typically you will need to implement a handler function to be notified when the user chooses a color from the picker;
    you can register the handler using the {@link #event-select} event, or by implementing the {@link #handler} method.

  Modification from original Ext.picker.Color

  Author: Dima Fedorov <dimin@dimin.net> <http://www.dimin.net/>
  Copyright (C) Center for BioImage Informatics <www.bioimage.ucsb.edu>
  FreeBSD License

  Version: 1

  History:
    2012-11-07 16:18:49 - first version

@example
Ext.create('BQ.picker.Color', {
    value: '993300',  // initial selected color
    renderTo: Ext.getBody(),
    listeners: {
        select: function(picker, selColor) {
            alert(selColor);
        }
    }
});

*******************************************************************************/

Ext.define('BQ.picker.Color', {
    extend: 'Ext.Component',
    requires: 'Ext.XTemplate',
    alias: 'widget.bqcolorpicker',
    alternateClassName: 'BQ.ColorPalette',

    /**
     * @cfg {String} [componentCls='x-color-picker']
     * The CSS class to apply to the containing element.
     */
    componentCls : 'bq-color-picker',

    /**
     * @cfg {String} [selectedCls='x-color-picker-selected']
     * The CSS class to apply to the selected element
     */
    selectedCls: 'bq-color-picker-selected',

    /**
     * @cfg {String} value
     * The initial color to highlight (should be a valid 6-digit color hex code without the # symbol). Note that the hex
     * codes are case-sensitive.
     */
    value : null,

    /**
     * @cfg {String} clickEvent
     * The DOM event that will cause a color to be selected. This can be any valid event name (dblclick, contextmenu).
     */
    clickEvent :'click',

    /**
     * @cfg {Boolean} allowReselect
     * If set to true then reselecting a color that is already selected fires the {@link #event-select} event
     */
    allowReselect : false,

    /**
     * @property {String[]} colors
     * An array of 6-digit color hex code strings (without the # symbol). This array can contain any number of colors,
     * and each hex code should be unique. The width of the picker is controlled via CSS by adjusting the width property
     * of the 'x-color-picker' class (or assigning a custom class), so you can balance the number of colors with the
     * width setting until the box is symmetrical.
     *
     * You can override individual colors if needed:
     *
     *     var cp = new Ext.picker.Color();
     *     cp.colors[0] = 'FF0000';  // change the first box to red
     *
     * Or you can provide a custom array of your own for complete control:
     *
     *     var cp = new Ext.picker.Color();
     *     cp.colors = ['000000', '993300', '333300'];
     */
    colors : [
        '000000', '993300', '333300', '003300', '003366', '000080', '333399', '333333',
        '800000', 'FF6600', '808000', '008000', '008080', '0000FF', '666699', '808080',
        'FF0000', 'FF9900', '99CC00', '339966', '33CCCC', '3366FF', '800080', '969696',
        'FF00FF', 'FFCC00', 'FFFF00', '00FF00', '00FFFF', '00CCFF', '993366', 'C0C0C0',
        'FF99CC', 'FFCC99', 'FFFF99', 'CCFFCC', 'CCFFFF', '99CCFF', 'CC99FF', 'FFFFFF'
    ],

    /**
     * @cfg {Function} handler
     * A function that will handle the select event of this picker. The handler is passed the following parameters:
     *
     * - `picker` : ColorPicker
     *
     *   The {@link Ext.picker.Color picker}.
     *
     * - `color` : String
     *
     *   The 6-digit color hex code (without the # symbol).
     */

    /**
     * @cfg {Object} scope
     * The scope (`this` reference) in which the `{@link #handler}` function will be called.
     *
     * Defaults to this Color picker instance.
     */

    colorRe: /(?:^|\s)color-(.{6})(?:\s|$)/,

    /*
    renderTpl: [
        '<tpl for="colors">',
            '<a href="#" class="color-{.}" hidefocus="on">',
                '<em><span style="background:#{.}" unselectable="on">&#160;</span></em>',
            '</a>',
        '</tpl>'
    ],
    */

    renderTpl: [
        '<tpl for="objects">',
            '<a href="#" class="color-{color}" hidefocus="on">',
                '<em><span style="background:#{color};" unselectable="on"></span></em>',
                '{title}',
            '</a>',
        '</tpl>'
    ],

    // private
    initComponent : function(){
        var me = this;

        me.callParent(arguments);
        me.addEvents(
            /**
             * @event select
             * Fires when a color is selected
             * @param {Ext.picker.Color} this
             * @param {String} color The 6-digit color hex code (without the # symbol)
             */
            'select'
        );

        if (me.handler) {
            me.on('select', me.handler, me.scope, true);
        }
    },


    // private
    initRenderData : function(){
        var me = this;

        objects = [];
        for (var i=0; i<me.colors.length; i++)
            objects[i] = { color: me.colors[i], title: me.titles[i] };

        return Ext.apply(me.callParent(), {
            itemCls: me.itemCls,
            colors: me.colors,
            objects: objects,
        });
    },

    onRender : function(){
        var me = this,
            clickEvent = me.clickEvent;

        me.callParent(arguments);

        me.mon(me.el, clickEvent, me.handleClick, me, {delegate: 'a'});
        // always stop following the anchors
        if(clickEvent != 'click'){
            me.mon(me.el, 'click', Ext.emptyFn, me, {delegate: 'a', stopEvent: true});
        }
    },

    // private
    afterRender : function(){
        var me = this,
            value;

        me.callParent(arguments);
        if (me.value) {
            value = me.value;
            me.value = null;
            me.select(value, null, true);
        }
    },

    // private
    handleClick : function(event, target){
        var me = this,
            color;

        event.stopEvent();
        if (!me.disabled) {
            color = target.className.match(me.colorRe)[1];
            me.select(color.toUpperCase(), target);
        }
    },

    /**
     * Selects the specified color in the picker (fires the {@link #event-select} event)
     * @param {String} color A valid 6-digit color hex code (# will be stripped if included)
     * @param {Boolean} [suppressEvent=false] True to stop the select event from firing.
     */
    select : function(color, target, suppressEvent){

        var me = this,
            selectedCls = me.selectedCls,
            value = me.value,
            el;

        var color_name = target ? target.innerText || target.text || target.textContent : '';
        if (color_name.toLowerCase() === 'custom') {
            Ext.create('Ext.tip.ToolTip', {
                target: target,
                anchor: 'top',
                //cls: 'bq-viewer-tip',
                //width :  w,
                //minWidth: w,
                //maxWidth: w,
                //height:  h,
                //minHeight: h,

                layout: 'fit',
                autoHide: false,
                shadow: false,
                items: [{
                    xtype: 'colorpicker',
                    //width :  500,
                    //height:  100,
                    listeners: {
                        select: function(picker, selColor) {
                            if (picker) picker.ownerCt.destroy();
                            me.fireEvent('select', me, selColor);
                        },
                        scope: this,
                    },
                }],
            }).show();
            return;
        }

        color = color.replace('#', '');
        if (!me.rendered) {
            me.value = color;
            return;
        }


        if (color != value || me.allowReselect) {
            el = me.el;

            if (me.value) {
                el.down('a.color-' + value).removeCls(selectedCls);
            }
            el.down('a.color-' + color).addCls(selectedCls);
            me.value = color;
            if (suppressEvent !== true) {
                me.fireEvent('select', me, color);
            }
        }
    },

    /**
     * Get the currently selected color value.
     * @return {String} value The selected value. Null if nothing is selected.
     */
    getValue: function(){
        return this.value || null;
    }
});
