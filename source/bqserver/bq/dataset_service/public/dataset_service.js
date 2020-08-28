/*******************************************************************************

  BQ.dataset.Service  -

  Author: Dima Fedorov

  Version: 1

  History:
    2011-09-29 13:57:30 - first creation

*******************************************************************************/

Ext.define('BQ.dataset.Service', {
    alias: 'bq.datasetservice',
    mixins: {
        observable: 'Ext.util.Observable'
    },

    service_url: '/dataset_service/',

    constructor: function (config) {
        this.mixins.observable.constructor.call(this, config);
        this.addEvents(
            'running',
            'success',
            'error'
        );
    },

    getOperation: function() {
        return this.operation;
    },

    onSuccess: function() {
        this.fireEvent( 'success', this );
    },

    onError: function() {
        this.fireEvent( 'error', this );
    },

    run: function(dataset_url, operation, arguments) {
        this.operation = operation;
        arguments = arguments || {};
        arguments.duri = dataset_url;
        var l = [];
        for (var i in arguments)
            l.push( i+'='+arguments[i] );
        var uri = this.service_url + operation + '?' + l.join('&');

        this.fireEvent( 'running', this );
        BQFactory.request ({
            uri : uri,
            cb : callback(this, this.onSuccess),
            errorcb: callback(this, this.onError),
            cache : false,
        });
    },

    // available operations

    // this will change permissions for all of dataset members
    run_permission: function(dataset_url, permission) {
        this.run(dataset_url, 'permission', {permission: permission});
    },

    // this will remove all dataset members and the dataset itself
    run_delete: function(dataset_url) {
        this.run(dataset_url, 'delete');
    },

    // this will add dataset shares to all of its members
    run_share: function(dataset_url) {
        this.run(dataset_url, 'share');
    },

});

