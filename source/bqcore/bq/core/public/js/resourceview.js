Ext.define('BQ.ResourceViewer', {
    statics : {
        dispatch : function(resource) {
            if (resource instanceof BQObject)
                this.initViewer(resource);
            else
                this.loadResource(resource);
        },

        loadResource : function(resourceURL) {
            BQApp.setLoading('Fetching resource...');
            BQFactory.request({
                uri         :   resourceURL,
                uri_params  :   {view : 'deep'}, // TODO: only request deep if really needed; and only with paging!
                cb          :   this.initViewer,
                errorcb     :   this.onError
            });
        },

        initViewer : function(resource) {
            BQApp.setLoading(false);
            BQApp.resource = resource;
            BQ.Preferences.load(resource.resource_uniq); //loading in resource level preferences
            BQApp.setAnalysisQuery(encodeURIComponent('(accepted_type:"{1}" or "{1}":::)'.replace(/\{1\}/g, resource.resource_type)));

            var resourceCt = Bisque.ResourceFactoryWrapper.getResource({
                resource    :   resource,
                layoutKey   :   Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Page
            });
            BQApp.setCenterComponent(resourceCt);
        },

        onError: function(error) {
            BQApp.setLoading(false);
            BQ.ui.error('Error fetching resource: <br>' + error.message);
            this.initViewer();
        },
    }
});
