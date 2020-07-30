/*******************************************************************************

  BQ.selectors - selectors of inputs for module runs

  Author: Dima Fedorov

  Version: 1

  History:
    2011-09-29 13:57:30 - first creation

*******************************************************************************/

Ext.define('BQ.form.field.Number', {
    extend:'Ext.form.field.Number',
    alias: ['widget.bq_number'],

    defaultListConfig: {
        loadingHeight: 70,
        minWidth: 70,
        maxHeight: 300,
        shadow: 'sides'
    },

    triggerTpl: '<td style="{triggerStyle}" class="{triggerCls}">' +
                    '<div class="' + Ext.baseCSSPrefix + 'trigger-index-0 ' + Ext.baseCSSPrefix + 'form-trigger ' + Ext.baseCSSPrefix + 'form-spinner-up {spinnerUpCls} {childElCls}" role="button"></div>' +
                    '<div class="' + Ext.baseCSSPrefix + 'trigger-index-1 ' + Ext.baseCSSPrefix + 'form-trigger ' + Ext.baseCSSPrefix + 'form-spinner-down {spinnerDownCls} {childElCls}" role="button"></div>' +
                '</td>' +
                '<td style="{pickerStyle}" class="{triggerCls}">' +
                    '<div class="' + Ext.baseCSSPrefix + 'trigger-index-2 ' + Ext.baseCSSPrefix + 'form-trigger ' + Ext.baseCSSPrefix + 'form-picker {spinnerUpCls} {childElCls}" role="button"></div>' +
                '</td>' +
            '</tr>',

    initComponent: function() {
        var me = this;
        me.hidePicker = (!me.store);
        me.callParent();
    },

    getTriggerData: function(){
        var d = this.callParent();
        d.pickerStyle = this.hidePicker ? 'display:none' : '';
        return d;
    },

    getTriggerWidth: function() {
        var totalTriggerWidth = this.callParent();
        if (this.hidePicker)
            return totalTriggerWidth;
        return totalTriggerWidth*2;
    },

    onTrigger3Click: function() {
        this.onTriggerClick();
    },

    onTriggerClick: function() {
        var me = this;
        if (!me.readOnly && !me.disabled) {
            if (me.isExpanded) {
                me.collapse();
            } else {
                me.expand();
            }
            me.inputEl.focus();
        }
    },

    getPicker: function() {
        var me = this;
        return me.picker || (me.picker = me.createPicker());
    },

    // The picker (the dropdown) must have its zIndex managed by the same ZIndexManager which is
    // providing the zIndex of our Container.
    onAdded: function() {
        var me = this;
        me.callParent(arguments);
        if (me.picker) {
            me.picker.ownerCt = me.up('[floating]');
            me.picker.registerWithOwnerCt();
        }
    },

    createPicker: function() {
        var me = this,
            picker,
            pickerCfg = Ext.apply({
                xtype: 'boundlist',
                pickerField: me,
                selModel: {
                    mode: 'SINGLE'
                },
                floating: true,
                hidden: true,
                store: me.store,
                displayField: me.displayField,
                focusOnToFront: false,
                pageSize: me.pageSize,
                tpl: me.tpl
            }, me.listConfig, me.defaultListConfig);

        picker = me.picker = Ext.widget(pickerCfg);
        if (me.pageSize) {
            picker.pagingToolbar.on('beforechange', me.onPageChange, me);
        }

        me.mon(picker, {
            itemclick: me.onItemClick,
            refresh: me.onListRefresh,
            scope: me
        });

        me.mon(picker.getSelectionModel(), {
            beforeselect: me.onBeforeSelect,
            beforedeselect: me.onBeforeDeselect,
            selectionchange: me.onListSelectionChange,
            scope: me
        });

        return picker;
    },

    doAlign: function(){
        var me = this,
            picker = me.picker,
            aboveSfx = '-above',
            isAbove;

        // Align to the trigger wrap because the border isn't always on the input element, which
        // can cause the offset to be off
        me.picker.alignTo(me.triggerWrap, me.pickerAlign, me.pickerOffset);
        // add the {openCls}-above class if the picker was aligned above
        // the field due to hitting the bottom of the viewport
        isAbove = picker.el.getY() < me.inputEl.getY();
        me.bodyEl[isAbove ? 'addCls' : 'removeCls'](me.openCls + aboveSfx);
        picker[isAbove ? 'addCls' : 'removeCls'](picker.baseCls + aboveSfx);
    },

    alignPicker: function(){
        var me = this,
            picker = me.getPicker(),
            heightAbove = me.getPosition()[1] - Ext.getBody().getScroll().top,
            heightBelow = Ext.Element.getViewHeight() - heightAbove - me.getHeight(),
            space = Math.max(heightAbove, heightBelow);

        // Allow the picker to height itself naturally.
        if (picker.height) {
            delete picker.height;
            picker.updateLayout();
        }
        // Then ensure that vertically, the dropdown will fit into the space either above or below the inputEl.
        if (picker.getHeight() > space - 5) {
            picker.setHeight(space - 5); // have some leeway so we aren't flush against
        }

        if (me.isExpanded) {
            if (me.matchFieldWidth) {
                // Auto the height (it will be constrained by min and max width) unless there are no records to display.
                picker.setWidth(me.bodyEl.getWidth());
            }
            if (picker.isFloating()) {
                me.doAlign();
            }
        }
    },

    onListRefresh: function() {
        // Picker will be aligned during the expand call
        if (!this.expanding) {
            this.alignPicker();
        }
        //this.syncSelection();
    },

    getDisplayValue: function() {
        return this.displayTpl.apply(this.displayTplData);
    },

    onItemClick: function(picker, record){
        /*
         * If we're doing single selection, the selection change events won't fire when
         * clicking on the selected element. Detect it here.
         */
        var me = this,
            selection = me.picker.getSelectionModel().getSelection(),
            valueField = me.valueField;

        if (!me.multiSelect && selection.length) {
            if (record.get(valueField) === selection[0].get(valueField)) {
                // Make sure we also update the display value if it's only partial
                //me.displayTplData = [record.data];
                //me.setRawValue(me.getDisplayValue());
                me.setValue(selection[0].get(valueField));
                me.collapse();
            }
        }
    },

    expand: function() {
        var me = this,
            bodyEl, picker, collapseIf;

        if (me.rendered && !me.isExpanded && !me.isDestroyed) {
            me.expanding = true;
            bodyEl = me.bodyEl;
            picker = me.getPicker();
            collapseIf = me.collapseIf;

            // show the picker and set isExpanded flag
            picker.show();
            me.isExpanded = true;
            me.alignPicker();
            bodyEl.addCls(me.openCls);

            // monitor clicking and mousewheel
            me.mon(Ext.getDoc(), {
                mousewheel: collapseIf,
                mousedown: collapseIf,
                scope: me
            });
            Ext.EventManager.onWindowResize(me.alignPicker, me);
            me.fireEvent('expand', me);
            me.onExpand();
            delete me.expanding;
        }
    },

    onExpand: Ext.emptyFn,

    collapse: function() {
        if (this.isExpanded && !this.isDestroyed) {
            var me = this,
                openCls = me.openCls,
                picker = me.picker,
                doc = Ext.getDoc(),
                collapseIf = me.collapseIf,
                aboveSfx = '-above';

            // hide the picker and set isExpanded flag
            picker.hide();
            me.isExpanded = false;

            // remove the openCls
            me.bodyEl.removeCls([openCls, openCls + aboveSfx]);
            picker.el.removeCls(picker.baseCls + aboveSfx);

            // remove event listeners
            doc.un('mousewheel', collapseIf, me);
            doc.un('mousedown', collapseIf, me);
            Ext.EventManager.removeResizeListener(me.alignPicker, me);
            me.fireEvent('collapse', me);
            me.onCollapse();
        }
    },

    onCollapse: Ext.emptyFn,

    collapseIf: function(e) {
        var me = this;

        if (!me.isDestroyed && !e.within(me.bodyEl, false, true) && !e.within(me.picker.el, false, true) && !me.isEventWithinPickerLoadMask(e)) {
            me.collapse();
        }
    },

    isEventWithinPickerLoadMask: function(e) {
        var loadMask = this.picker.loadMask;

        return loadMask ? e.within(loadMask.maskEl, false, true) || e.within(loadMask.el, false, true) : false;
    },

    onBeforeSelect: function(list, record) {
        return this.fireEvent('beforeselect', this, record, record.index);
    },

    onBeforeDeselect: function(list, record) {
        return this.fireEvent('beforedeselect', this, record, record.index);
    },

    onListSelectionChange: function(list, selectedRecords) {
        var me = this,
            isMulti = me.multiSelect,
            hasRecords = selectedRecords.length > 0,
            valueField = me.valueField;
        // Only react to selection if it is not called from setValue, and if our list is
        // expanded (ignores changes to the selection model triggered elsewhere)
        if (!me.ignoreSelection && me.isExpanded) {
            if (!isMulti) {
                Ext.defer(me.collapse, 1, me);
            }
            /*
             * Only set the value here if we're in multi selection mode or we have
             * a selection. Otherwise setValue will be called with an empty value
             * which will cause the change event to fire twice.
             */
            if (isMulti || hasRecords) {
                me.setValue(selectedRecords[0].get(valueField));
            }
            if (hasRecords) {
                me.fireEvent('select', me, selectedRecords);
            }
            me.inputEl.focus();
        }
    },

});


/*******************************************************************************
Resource templated configs:

*******************************************************************************/

Ext.define('BQ.data.reader.Bisque', {
    extend: 'Ext.data.reader.Xml',
    alternateClassName: 'BQ.data.BisqueReader',
    alias : 'reader.bisque',

    //root :  'resource',
    //record: 'image',
    root :  '/',
    record: '/*:not(value or vertex or template)',

    constructor: function(config) {
        this.callParent(arguments);
        BQFactory.request({ uri: this.url+'?view=count',
                            cb: callback(this, 'onTotal'), });
        return this;
    },

    onTotal: function(r) {
        if (r.tags.length<1) return;
        if (r.tags[0].name != 'count') return;
        this.total_count = r.tags[0].value;
    },

    readRecords: function(doc) {
        var r = this.callParent([doc]);
        r.total = this.total_count || 10;
        return r;
    },

});

Ext.define('Resources', {
    extend : 'Ext.data.Model',
    fields : [ {name: 'Name', mapping: '@name' },
               {name: 'Value', mapping: '@value' },
               {name: 'Type', mapping: '@type' },
               //{name: 'Metadata', convert: getMetadata },
             ],
});


Ext.define('BQ.grid.Panel', {
    alias: 'bq.gridpanel',
    extend: 'Ext.panel.Panel',
    requires: ['Ext.button.Button', 'Ext.tree.*', 'Ext.data.*'],

    layout: 'fit',
    height: 300,

    pageSize: 100,          // number of records to fetch on every request
    trailingBufferZone: 20, // Keep records buffered in memory behind scroll
    leadingBufferZone: 20,  // Keep records buffered in memory ahead of scroll

    initComponent : function() {

        var url = this.url || '/data_service/image';
        this.reader = Ext.create('BQ.data.reader.Bisque', {
            url: url,
        });

        this.store = new Ext.data.Store( {
            model : 'Resources',
            autoLoad : true,
            //autoSync : false,
            remoteSort: true,
            buffered: true,
            pageSize: this.pageSize,

            proxy : {
                type: 'rest',
                url : this.reader.url+'?view=full',
                appendId: true,
                limitParam : 'limit',
                pageParam: undefined,
                startParam: 'offset',
                noCache: false,
                reader : this.reader,
            },

        });

        this.grid = Ext.create('Ext.grid.Panel', {
            store: this.store,
            loadMask: true,
            border: 0,
            //verticalScrollerType: 'paginggridscroller',
            //invalidateScrollerOnRefresh: false,
            disableSelection: false,
            //autoLoad: true,
            columns: [
                {text: "Name",  flex: 2, dataIndex: 'Name',  sortable: true},
                {text: "Value", flex: 2, dataIndex: 'Value', sortable: true},
                {text: "Type",  flex: 1, dataIndex: 'Type',  sortable: true},
                //{text: "Reading", width: 60, dataIndex: 'Reading', sortable: true},
                //{text: "Writing", width: 60, dataIndex: 'Writing', sortable: true},
                //{text: "Metadata", width: 100, dataIndex: 'Metadata', sortable: true},
                //{text: "Extensions", flex: 1, dataIndex: 'Extensions', sortable: true},
                //{text: "Source", width: 100, dataIndex: 'Source', sortable: true},
            ],
            viewConfig: {
                stripeRows: true,
                forceFit: true
            },
            verticalScroller: {
                trailingBufferZone: this.trailingBufferZone,  // Keep records buffered in memory behind scroll
                leadingBufferZone: this.leadingBufferZone,   // Keep records buffered in memory ahead of scroll
            },
        });
        this.items = [this.grid];
        this.callParent();
    },


});
