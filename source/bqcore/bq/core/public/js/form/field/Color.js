/*******************************************************************************

  BQ.form.field.Color - Color form field provides color selection for any form
        field, will work in all browsers and not limited to html5 color input.

  Author: Dima Fedorov <dimin@dimin.net> <http://www.dimin.net/>
  Copyright (C) Center for BioImage Informatics <www.bioimage.ucsb.edu>
  FreeBSD License

  Version: 1

  History:
    2012-11-07 16:18:49 - first version

@example
Ext.create('BQ.form.field.Color', {
    renderTo: ELEMENT,
    fieldLabel: 'MY LABEL',
    name: 'MY NAME',
    value: 'FF0000', // red
    listeners: {
        scope: this,
        change: function(field, value) {
            alert('got color: #'+value);
        },
    },
});

*******************************************************************************/


Ext.define('BQ.form.field.Color', {
    extend:'Ext.form.field.Base',
    alias: 'widget.colorfield',
    requires: ['Ext.picker.Color', 'Ext.draw.Color'],
    alternateClassName: ['BQ.form.ColorField', 'BQ.form.Color'],

    inputType: 'color',
    componentCls : Ext.baseCSSPrefix + 'form-color',
    matchFieldWidth: false,

    // got to use button instead of color due to limited browser support
    fieldSubTpl: [
        '<input id="{id}-checkbox" type="checkbox" value="" checked>',
        '<input id="{id}" type="button" {inputAttrTpl}',
        ' size="1"',
        '<tpl if="name"> name="{name}"</tpl>',
        '<tpl if="value"> value="{[Ext.util.Format.htmlEncode(values.value)]}"</tpl>',
        '<tpl if="placeholder"> placeholder="{placeholder}"</tpl>',
        '{%if (values.maxLength !== undefined){%} maxlength="{maxLength}"{%}%}',
        '<tpl if="readOnly"> readonly="readonly"</tpl>',
        '<tpl if="disabled"> disabled="disabled"</tpl>',
        '<tpl if="tabIdx"> tabIndex="{tabIdx}"</tpl>',
        //'<tpl if="fieldStyle"> style="{fieldStyle}"</tpl>',
        ' class="{fieldCls} {typeCls} {editableCls}" autocomplete="off"/>',
        {disableFormats: true}
    ],

    initComponent : function() {
        this.callParent();
    },

    afterRender : function() {
        this.onColorSelected(undefined, this.value);
    },

    applyRenderSelectors : function() {
        this.callParent();
        var id = this.inputEl.id+'-checkbox';
        this.checkbox = this.el.getById(id);
    },

    initEvents: function() {
        var me = this;
        me.callParent();
        me.mon(me.inputEl, 'click', me.onBoxClick, me);
        me.mon(me.checkbox, 'click', me.onCheckClick, me);
    },

    /**
    * @private Handle click on the checkbox button
    */
    onBoxClick: function(e) {
        var w = 540;
        var h = 85;
        Ext.create('Ext.tip.ToolTip', {
            target: this.inputEl,
            anchor: 'right',
            cls: 'bq-viewer-tip',
            width :  w,
            minWidth: w,
            //maxWidth: w,
            //height:  h,
            minHeight: h,

            layout: 'fit',
            autoHide: false,
            shadow: false,
            items: [{
                xtype: 'bqcolorpicker',
                //width :  500,
                //height:  100,
                listeners: {
                    scope: this,
                    select: this.onColorSelected,
                },
                colors : [ '000000', // trasparent
                           'FF0000', '00FF00', '0000FF', // RGB
                           'FFFFFF', // GRAY
                           '00FFFF', // CYAN
                           'FF00FF', // MAGENTA
                           'FFFF00', // YELLOW
                           'FF6600'  // custom orange
                ],
                titles : [ 'Hidden', // trasparent
                           'Red', 'Green', 'Blue', // RGB
                           'Gray', //GRAY
                           'Cyan', 'Magenta', 'Yellow', // YMC
                           'Custom' // custom orange
                ],
            }],
        }).show();
    },

    onColorSelected: function(picker, color) {
        var c = Ext.draw.Color.fromString('#'+color);
        this.c = c;
        this.setValue(color); //must be hex without #
        this.inputEl.setStyle( 'background-color', c.toString());
        this.inputEl.set({value: 'R:'+c.getRed()+', G:'+c.getGreen()+', B:'+c.getBlue() }); //resets the element label and value, must be run after setValue

        if (c.getHSL()[2] > 0.35)
            this.inputEl.setStyle( 'color', '#000000');
        else
            this.inputEl.setStyle( 'color', '#FFFFFF');

        if (color=='000000')
            this.checkbox.dom.checked = false;
        else
            this.checkbox.dom.checked = true;

        if (picker) picker.ownerCt.destroy();
    },

    onCheckClick: function(e) {
        if (this.checkbox.dom.checked) {
            this.onColorSelected(undefined, this.color_stored? this.color_stored:'000000');
        } else {
            this.color_stored = this.color? this.color:'000000'; //must be hex without #  (chris - use to assign from this.value)
            this.onColorSelected(undefined, '000000');
        }
    },
/*
    rawToValue: function(rawValue) {
        return rawValue;
    },

    valueToRaw: function(value) {
        return rawValue;
    },
    */

    setValue: function(value) {
        this.color = value;
        this.callParent(arguments);
    },

    getValue: function() {
        this.callParent(arguments);
        return this.color;
    },

    getColor: function() {
        return this.c;
    },

    createPicker: function() {
        var me = this;

        return new Ext.picker.Color({
            pickerField: me,
            ownerCt: me.ownerCt,
            renderTo: document.body,
            floating: true,
            hidden: true,
            focusOnShow: true,
            value: 'FF0000',
            listeners: {
                scope: me,
                select: me.onSelect
            },
            keyNavConfig: {
                esc: function() {
                    me.collapse();
                }
            }
        });
    },

    onSelect: function(m, d) {
        var me = this;

        me.setValue(d);
        me.fireEvent('select', me, d);
        me.collapse();
    },

    /**
     * @private
     * Sets the Date picker's value to match the current field value when expanding.
     */
    onExpand: function() {
        this.picker.setValue(this.getValue());
    },

    /**
     * @private
     * Focuses the field when collapsing the Date picker.
     */
    onCollapse: function() {
        this.focus(false, 60);
    },

    // private
    beforeBlur : function(){
        var me = this,
            v = me.getRawValue(),
            focusTask = me.focusTask;

        if (focusTask) {
            focusTask.cancel();
        }

        if (v) {
            me.setValue(v);
        }
    }

    /**
     * @cfg {Boolean} grow
     * @private
     */
    /**
     * @cfg {Number} growMin
     * @private
     */
    /**
     * @cfg {Number} growMax
     * @private
     */
    /**
     * @method autoSize
     * @private
     */
});
