Ext.define('Bisque.Resource.User.Grid', {
    extend : 'Bisque.Resource.Grid',

    getFields : function(displayName) {
        var record = BQApp.userList[this.resource.owner];
        this.displayName = record ? record.find_tags('display_name').value : '';

        this.resource.display_name = this.displayName;
        var fields = this.callParent();
        fields[1] = this.displayName;
        fields[2] = (record && record['email']) || '';

        return fields;
    }
});
