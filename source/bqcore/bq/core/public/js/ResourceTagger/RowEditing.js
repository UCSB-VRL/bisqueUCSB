/*
@class BQ.grid.plugin.RowEditing
@extends Ext.grid.plugin.RowEditing

This is just an error fix for original Ext.grid.plugin.RowEditing
ExtJS 4.1, 4.2.1

Author: Dima Fedorov
*/

if (Ext.getVersion().version !== '4.2.1.883')
    console.warn('BQ.grid.plugin.RowEditing: Patches ExtJS 4.2.1 and may not work in other versions and should be checked!');

Ext.define('BQ.grid.plugin.RowEditing', {
    extend : 'Ext.grid.plugin.RowEditing',
    alias : 'bq.rowediting',

    cancelEdit : function() {
        var me = this;
        me.callParent();

        var form = me.getEditor().getForm();
        if (!form.isValid())
            me.fireEvent('canceledit', me.grid, {});
        this.finishEdit();
    },

    completeEdit : function() {
        this.callParent(arguments);
        this.finishEdit();
    },

    finishEdit : function() {
        if (this.context)
            this.context.grid.getSelectionModel().deselect(this.context.record);
    },

    // dima: fix for extjs 4.2.1
    setColumnField: function(column, field) {
        var me = this,
            editor = me.getEditor();
         
        editor.removeColumnEditor(column);

        field = Ext.apply({
            name: column.dataIndex,
            column: column,
            flex: 1,
            _marginWidth: 1,
        }, field);
        
        var fieldContainer = column.isLocked() ? editor.lockedColumnContainer : editor.normalColumnContainer;
        field = fieldContainer.insert(column.getVisibleIndex(), field);
        column.field = field;
        field.on('change', editor.onFieldChange, editor); 
    },
});
