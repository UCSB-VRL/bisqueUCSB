/*
 @class BQ.form.ComboBox
 @extends Ext.form.field.ComboBox

 This is just a modification to function as a value box allowing initial values not present in the store

 Author: Dima Fedorov
 */

Ext.define('BQ.form.ComboBox', {
    extend : 'Ext.form.field.ComboBox',
    alias : ['widget.bqcombobox', 'widget.bqcombo'],

    setValue : function(value, doSelect) {
        this.valueNotFoundText = value;
        if (!this.rawValue)
            this.rawValue = value;
        return this.callParent(arguments);
    },
});

