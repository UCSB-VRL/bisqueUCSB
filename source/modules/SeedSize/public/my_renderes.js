/*******************************************************************************

  BQ.renderers.seedsize.Mex

  Author: Dima Fedorov

  Version: 1
  
  History: 
    2011-09-29 13:57:30 - first creation
    
*******************************************************************************/


// overwrite standard renderer with our own
BQ.renderers.resources.mex = 'BQ.renderers.seedsize.Mex';

// provide our renderer
Ext.define('BQ.renderers.seedsize.Mex', {
    extend: 'BQ.renderers.Mex',

    createMenuExportPackage : function(menu) {
        if (!this.res_uri_for_tools) return;
        if (!this.template_for_tools) return;
        var template = this.template_for_tools || {};
        if (!('export_package' in template) || template['export_package']==false) return; 
        menu.add({
            text: template['export_package/label'] || 'Area, Major and Minor axis as CSV files per image in a GZip package',
            scope: this,
            handler: this.fetchImageFileNames,
        }); 
    }, 

    fetchImageFileNames : function() {
        this.setLoading('Fetching image file names');
        var mex = this.mex;
        
        this.image_names = {};
        var myiterable = mex.dict['execute_options/iterable'];
        this.images = Ext.clone(mex.iterables[myiterable]);
        
        // fetch dataset name
        this.num_requests = 1;        
        BQFactory.request({ uri: this.images['dataset'], 
                            cb: callback(this, 'onResource'), 
                            errorcb: callback(this, 'onerror'), 
                            //uri_params: {view:'short'}, 
                         });          
        
        if ('dataset' in this.images) delete this.images['dataset'];
        if ('undefined' in this.images) delete this.images['undefined'];        
        // fetch image names 
        for (var u in this.images) {
            var sub_mex = this.images[u];
            this.images[u] = { mex: sub_mex.uri, name: null, };
            this.num_requests++;
        }        
        for (var u in this.images) {
            BQFactory.request({ uri: u, 
                                 cb: callback(this, 'onResource'), 
                                 errorcb: callback(this, 'onerror'), 
                                 //uri_params: {view:'short'}, // dima: by default it's short, if error happens we try to mark that in the list by fetched url
                             });            
        }
    },

    onerror: function (e) {
        BQ.ui.error(e.message);  
        this.num_requests--;
        if (e.request.request_url in this.images)
            delete this.images[e.request.request_url];
        if (this.num_requests<=0) this.onAllImages();
    }, 
    
    onResource: function(im) {
        this.num_requests--;   
        if (im instanceof BQImage)     
            this.images[im.uri].name = im.name;
        else if (im instanceof BQDataset)
            this.dataset_name = im.name;                 
        if (this.num_requests<=0) this.onAllImages();
    },    
    
    onAllImages: function() {
        this.setLoading(false);

        var staturls = [];
        for (var i in this.images) {
            var u = bq.url('/stats/csv?url='+this.images[i].mex);
            u += '&xmap=tag-value-number';
            u += '&xreduce=vector';
            u += "&xpath=//gobject[@type='seed']/tag[@name='area']";
            u += "&xpath1=//gobject[@type='seed']/tag[@name='major']";
            u += "&xpath2=//gobject[@type='seed']/tag[@name='minor']";
            u += "&title=area";
            u += "&title1=major";
            u += "&title2=minor";
            u += "&filename="+this.images[i].name+'.csv';            
            staturls.push(u);
        }
        //var r = new BQResource();
        //r.setValues(staturls);
        //var payload = r.toXML();
        
        //dima: ok, lot's of hackery here, what we'll do is create a hidden iframe withs html form inside activated automatically
        //      that will do a post to export service and later activate browser save as dialog
        
        //var url = '/export/initStream?compressionType=gzip';
        var url = bq.url('/export/initStream');
        var html = '<html><body>'+
                   '<form id="csvpost" name="csvpost" action="'+url+'" method="post">'+
                   '<input type="hidden" name="compressionType" value="gzip" />'+
                   '<input type="hidden" name="filename" value="'+(this.dataset_name||'full_dataset')+'" />'+
                   '<input type="hidden" name="urls" value="'+staturls.join(',')+'" />'+
                   '<input type="submit" value="Submit" /></form>'+
                   '<script type="text/javascript">document.getElementById("csvpost").submit();</script>'+
                   '</body></html>';
        //var w = window.open();
        //w.document.writeln(html);

        var ifr = Ext.DomHelper.append(document.body, {
            tag: 'iframe',
            frameBorder: 0,
            width: 0,
            height: 0,
            css: 'display:none; visibility:hidden; height:1px;',
        });
        ifr.contentDocument.writeln(html);

    },

});


