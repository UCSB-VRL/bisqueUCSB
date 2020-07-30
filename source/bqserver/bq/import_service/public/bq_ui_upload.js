/*******************************************************************************

  BQ.upload.Panel  - an integrated uploading tool allowing many file uploads
  BQ.upload.Dialog - uploader in the modal window

  Author: Dima Fedorov

------------------------------------------------------------------------------
  BQ.upload.Dialog:
------------------------------------------------------------------------------

  Sends multi-part form with a file and associated tags in XML format
  form parts should be something like this: file and file_tags

    The tag XML document is in the following form:
    <resource>
        <tag name='any tag' value='any value' />
        <tag name='another' value='new value' />
    </resource>


    The document can also contain special tag for processing and additional info:
    <resource name="XXX" permission="private|published" >
        <tag name='any tag' value='any value' />
        <tag name='ingest'>

            Permission setting for imported image as: 'private' or 'published'
            <tag name='permission' value='private' />
            or
            <tag name='permission' value='published' />

            Image is a multi-file compressed archive, should be uncompressed and images ingested individually:
            <tag name='type' value='zip-multi-file' />
            or
            Image is a compressed archive containing multiple files composing a time-series image:
            <tag name='type' value='zip-time-series' />
            or
            Image is a compressed archive containing multiple files composing a z-stack image:
            <tag name='type' value='zip-z-stack' />
            or
            Image is a compressed archive containing multiple files composing a 5-D image:
            <tag name='type' value='zip-5d-image' />
            This tag must have two additional tags with numbers of T and Z planes:
            <tag name='number_z' value='XXXX' />
            <tag name='number_t' value='XXXXX' />

        </tag>
    </resource>

    Example for a file "example.zip":

    <resource>
        <tag name='any tag' value='any value' />
        <tag name='ingest'>
            <tag name='permission' value='published' />
            <tag name='type' value='zip-5d-image' />
            <tag name='number_z' value='XXXX' />
            <tag name='number_t' value='XXXXX' />
        </tag>
    </resource>

------------------------------------------------------------------------------


  Version: 1

  History:
    2011-09-29 13:57:30 - first creation

*******************************************************************************/

Ext.namespace('BQ.upload');

BQ.upload.html5uploads = (window.File && window.FileList); // && window.FileReader); // - safari does not have FileReader...

BQ.upload.annotators = {
    'application/x-zip-compressed' : 'BQ.upload.ZipAnnotator',
    'application/x-compressed'     : 'BQ.upload.ZipAnnotator',
    'application/x-gzip'           : 'BQ.upload.ZipAnnotator',
    'application/zip'              : 'BQ.upload.ZipAnnotator',
    'application/gzip'             : 'BQ.upload.ZipAnnotator',
    'application/x-tar'            : 'BQ.upload.ZipAnnotator',
    'application/x-gtar'           : 'BQ.upload.ZipAnnotator',
};

BQ.upload.mime_packages = {
    'zip' : 'application/zip',
    'tar' : 'application/x-tar',
    'gz'  : 'application/x-gzip',
    'tgz' : 'application/x-gzip',
};

BQ.upload.mime_images = {
    'nii.gz' : 'image/gznii',
};

BQ.upload.view_resource = '/client_service/view?resource=';

//--------------------------------------------------------------------------------------
// BQ.upload.Annotator
// a base component for acquiring required annotations about a file being uploaded
// derived classes only need to provide the proper items list to create a form
// all elements of the form will be dynamically queried and added to the dictionary
// emmited in the "done" event
// Events:
//   done
//--------------------------------------------------------------------------------------

BQ.upload.ANNOTATOR_TYPES = {
    'zip-bisque':      "BisQue archive (upload and insert BisQue package)",
    'zip':             "just a compressed file (upload without unpacking)",
    'zip-multi-file':  "several unrelated images (unpack and insert each file individually)",
    'zip-time-series': "one time-series composed by a set of files (unpack and compose)",
    'zip-z-stack':     "one z-stack composed by a set of files (unpack and compose)",
    'zip-5d-image':    "one 5-D image composed by a set of files (unpack and compose)",
    //'zip-volocity':    "Volocity (*.mvd2) image (unpack and insert)",
    'zip-proprietary': "one proprietary series composed by a set of files (ex: Volocity, AndorIQ, Leica Lei, Olympus OIF, ...) (unpack and insert)",
    'zip-dicom':       "several DICOM files in a package (unpack and inspect)",
};

Ext.define('BQ.upload.Annotator', {
    extend: 'Ext.form.Panel',
    alias: 'widget.uploadannotator',

    frame: true,
    bodyPadding: 5,
    border: 0,
    cls: 'annotator',

    fieldDefaults: {
        labelAlign: 'right',
        labelWidth: 200,
        anchor: '100%',
    },

    onOk: function(e) {
        var form = this.getForm();
        if (!form.isValid()) return;

        var fields = form.getFields();
        var annotations = {};

        fields.each( function(){
            if (this.isVisible())
                annotations[ this.getName() ] = this.getValue();
        });

        this.fireEvent( 'done', annotations );
    },

});

//--------------------------------------------------------------------------------------
// BQ.upload.ZipAnnotator
// a specification for requesting additional annotations about the ZIP file
//--------------------------------------------------------------------------------------

Ext.define('BQ.upload.ZipAnnotator', {
    extend: 'BQ.upload.Annotator',
    alias: 'widget.uploadzipannotator',

    initComponent : function() {

        var types_data = [];
        for (var t in BQ.upload.ANNOTATOR_TYPES)
            types_data.push({ 'type': t, 'description': BQ.upload.ANNOTATOR_TYPES[t], });
        this.store_types = Ext.create('Ext.data.Store', {
            fields: ['type', 'description'],
            data : types_data,
        });

        var description = 'Please, tell us how to import compressed file "<b>'+this.file.name+'</b>". '+
                          'See "Help" for more information about types of acceptable archives.';
        this.items = [ {
                xtype: 'label',
                html: description,
                cls: 'question',
            },{
                xtype: 'combobox',
                name: 'type',
                fieldLabel: 'My compressed file is ',
                store: this.store_types,
                allowBlank: false,
                editable: false,
                queryMode: 'local',
                displayField: 'description',
                valueField: 'type',
                listeners:{
                     scope: this,
                     select: this.onTypeSelected,
                }
            }, {
                xtype: 'numberfield',
                name: 'number_z',
                fieldLabel: 'Number of Z slices',
                value: 1,
                minValue: 1,
                hidden: true,
                //maxValue: 50
            }, {
                xtype: 'numberfield',
                name: 'number_t',
                fieldLabel: 'Number of T points',
                value: 1,
                minValue: 1,
                hidden: true,
                //maxValue: 50
            }, {
                xtype: 'displayfield',
                name: 'channels_title',
                value: 'If your channels are stored as separate files, we need to know the number of channels (keep 0 otherwise):',
                cls: 'question',
                hidden: true,
            }, {
                xtype: 'numberfield',
                name: 'number_c',
                fieldLabel: 'Number of channels (samples)',
                value: 0,
                minValue: 0,
                hidden: true,
                //maxValue: 50
            }, {
                xtype: 'displayfield',
                name: 'resolution_title',
                value: 'It would be nice if you could also provide pixel resolution (keep 0 otherwise):',
                cls: 'question',
                hidden: true,
            }, {
                xtype: 'numberfield',
                name: 'resolution_x',
                fieldLabel: 'Pixel resolution X in microns',
                value: 0.0,
                minValue: 0,
                hidden: true,
                //maxValue: 50
            }, {
                xtype: 'numberfield',
                name: 'resolution_y',
                fieldLabel: 'Pixel resolution Y in microns',
                value: 0.0,
                minValue: 0,
                hidden: true,
                //maxValue: 50
            }, {
                xtype: 'numberfield',
                name: 'resolution_z',
                fieldLabel: 'Pixel resolution Z in microns',
                value: 0.0,
                minValue: 0,
                hidden: true,
                //maxValue: 50
            }, {
                xtype: 'numberfield',
                name: 'resolution_t',
                fieldLabel: 'Pixel resolution T in seconds',
                value: 0.0,
                minValue: 0,
                hidden: true,
                //maxValue: 50
            }];

        this.buttons = [{
            text: 'OK',
            formBind: true,
            handler: Ext.Function.bind( this.onOk, this ),
        }];

        this.callParent();
    },

    onTypeSelected: function(combo, records) {
        var togglable_fileds = { 'number_z':null, 'number_t':null, channels_title: null, number_c: null, 'resolution_title':null,
            'resolution_x':null, 'resolution_y':null, 'resolution_z':null, 'resolution_t':null };

        var my_types = {
            'zip-multi-file' : {},
            'zip-time-series': {channels_title: null, 'number_c':0, 'resolution_title':null, 'resolution_x':null, 'resolution_y':null, 'resolution_t':null},
            'zip-z-stack'    : {channels_title: null, 'number_c':0, 'resolution_title':null, 'resolution_x':null, 'resolution_y':null, 'resolution_z':null},
            'zip-5d-image'   : {'number_z':null, 'number_t':null, channels_title: null, 'number_c':0, 'resolution_title':null,
                                'resolution_x':null, 'resolution_y':null, 'resolution_z':null, 'resolution_t':null},
            'zip'            : {},
            //'zip-volocity'   : {},
            'zip-proprietary': {},
            'zip-dicom'      : {},
            'zip-bisque'     : {},
        };

        // the default state is false
        var numfileds = 0;
        var form = this.getForm();
        for (var i in togglable_fileds) {
            var e = my_types[records[0].data.type];
            var f = form.findField(i);
            if (!f) continue;

            if (i in e) {
                f.setVisible(true);
                ++numfileds;
            } else
                f.setVisible(false);
        }
        if (numfileds === 0) {
            var me = this;
            setTimeout(function(){ me.onOk(); }, 10);
        }
    },

});

//--------------------------------------------------------------------------------------
// BQ.ui.UploadItem
// item manages one file upload aspects, UI, progress and intentiates the actual uploader
// Events:
//   fileuploaded
//   filecanceled
//   fileerror
//--------------------------------------------------------------------------------------

BQ.upload.STATES = {
    'ANNOTATING': 0,
    'READY'     : 1,
    'UPLOADING' : 2,
    'INGESTING' : 3,
    'DONE'      : 4,
    'CANCELED'  : 5,
    'ERROR'     : 6,
};

BQ.upload.STATE_STRINGS = {
    0: 'Needs annotations',
    1: 'Ready',
    2: 'Uploading',
    3: 'Ingesting',
    4: 'Done',
    5: 'Canceled',
    6: 'Error',
};

BQ.upload.PERMISSIONS = {
    'PRIVATE': 0,
    'PUBLISHED': 1,
};

BQ.upload.PERMISSIONS_STRINGS = {
    0: 'private',
    1: 'published',
};

BQ.upload.formatFileSize = function (sz) {
    if (typeof sz !== 'number')
        return '';
    if (sz >= 1000000000)
        return '<b>'+((sz / 1000000000).toFixed(2)) + '</b>GB';
    if (sz >= 1000000)
        return '<b>'+((sz / 1000000).toFixed(2)) + '</b>MB';
    return '<b>'+((sz / 1000).toFixed(2)) + '</b>KB';
};

BQ.upload.get_file_mime = function (file) {
    var file_type = file.type,
        file_name = file.name;

    //var ext = file.name.split('.').reverse()[0];
    //if (ext in BQ.upload.mime_packages)
    //    file_type = BQ.upload.mime_packages[ext];

    for (var ext in BQ.upload.mime_images) {
        if (file_name.endsWith(ext)) {
            file_type = BQ.upload.mime_images[ext];
            break;
        }
    }

    if (file_type === file.type)
    for (var ext in BQ.upload.mime_packages) {
        if (file_name.endsWith(ext)) {
            file_type = BQ.upload.mime_packages[ext];
            break;
        }
    }
    return file_type;
}

BQ.upload.match_extension = function (filename, formats) {
    var exts = filename.split('.'),
        ext = exts.pop().toLowerCase(),
        exta = ext,
        i = 0;
    if (!formats) return ext;

    for (i=exts.length-1; i>=0; --i) {
        exta = exts[i].toLowerCase() + '.' + exta;
        if (exta in formats) {
            ext = exta;
        }
    }

    return ext;
}

Ext.define('BQ.upload.Item', {
    extend: 'Ext.container.Container', // container is much faster to be insterted
    alias: 'widget.uploaditem',
    requires: ['Ext.toolbar.Toolbar', 'Ext.tip.QuickTipManager', 'Ext.tip.QuickTip'],

    height: 70,
    closable: true,
    cls: 'uploaditem',
    layout: 'anchor',
    defaults: {
        border: 0,
        height_normal: 90,
        hysteresis: 100, // hysteresis in ms
    },

    initComponent : function() {
        this.state = BQ.upload.STATES.READY;

        this.progress = Ext.create('Ext.ProgressBar', {
            text:'Ready',
            //anchor: '-10',
            animate: true,
        });

        var fn = this.file.relativePath || this.file.webkitRelativePath || this.file.name || this.file.fileName;
        this.fileName = Ext.create('Ext.toolbar.TextItem', {
            text: '<b>'+fn+'</b>',
            cls: 'title',
            indent: true,
        });

        var s = 'Size: ' + BQ.upload.formatFileSize(this.file.size || this.file.fileSize);
        //var ext = fn.split('.').pop().toLowerCase();
        var ext = BQ.upload.match_extension(fn, this.formats_extensions);
        if (this.formats_extensions && ext in this.formats_extensions) {
            var cls = this.formats_extensions[ext].confidence > 0.5 ? 'good' : 'uncertain';
            s += ' (<span class="'+cls+'">'+this.formats_extensions[ext].fullname+'</span>)';
        } else {
            s += ' (file)';
        }

        this.fileSize = Ext.create('Ext.toolbar.TextItem', {
            itemId: 'label_size',
            cls: 'info',
            text: s,
            indent: true,
        });

        this.items = [{
            xtype: 'button',
            itemId: 'button_close',
            iconCls: 'close',
            cls: 'flatbutton button-close',
            scale: 'small',
            tooltip: 'Cancel uploading this file',
            scope: this,
            handler: this.destroy,
        }, {
            xtype: 'button',
            itemId: 'button_permission',
            cls: 'flatbutton button-permission',
            text: BQ.upload.PERMISSIONS_STRINGS[BQ.upload.PERMISSIONS.PRIVATE],
            scale: 'small',
            tooltip: 'Change file access permission',
            scope: this,
            handler: this.togglePermission,
        },
            this.fileName,
            this.fileSize,
            this.progress
        ];

        // try to update the mime type from what browser gives
        // all browsers on different systems give all kinds of things
        // try to safeguard this issue using the extension
        var file_type = BQ.upload.get_file_mime (this.file);

        this.annotator = undefined;
        if (file_type in BQ.upload.annotators) {
            this.state = BQ.upload.STATES.ANNOTATING;
            this.progress.setVisible(false);
            this.fileName.setVisible(false);
            this.fileSize.setVisible(false);
            this.annotator = Ext.create(BQ.upload.annotators[file_type], {
                file: this.file,
                listeners: {
                    done: this.onAnnotated,
                    scope: this,
                },
            });
            this.height = this.annotator.height;
            this.items.push(this.annotator);
        }

        this.callParent();
    },

    updateUi : function() {
        if (!this.progress) return;
        if (this.state === BQ.upload.STATES.ERROR && this.error)
            this.progress.updateText( BQ.upload.STATE_STRINGS[this.state] +': '+this.error);
        else
            this.progress.updateText( BQ.upload.STATE_STRINGS[this.state] );

        if (this.state<BQ.upload.STATES.DONE) {
            this.progress.removeCls( 'error' );
            this.progress.removeCls( 'done' );
        } else
        if (this.state===BQ.upload.STATES.DONE) {
            this.progress.removeCls( 'error' );
            this.progress.addCls( 'done' );
        } else
        if (this.state>BQ.upload.STATES.DONE) {
            this.progress.addCls( 'error' );
            this.progress.removeCls( 'done' );
        }
    },

    onDestroy : function() {
        this.cancel(true);
        this.callParent();
    },

    hasFile : function(f) {
        var fn1 = this.file.relativePath || this.file.webkitRelativePath || this.file.name || this.file.fileName;
        var fn2 = f.relativePath || f.webkitRelativePath || f.name || f.fileName;
        return fn1 === fn2;
    },

    getFile : function() {
        return this.file;
    },

    setFile : function(f) {
        this.file = f;
    },

    getState : function() {
        return this.state;
    },

    setState : function(state) {
        this.state = state;
        this.updateUi();
    },

    togglePermission : function() {
        if (this.permission)
            this.setPermission( BQ.upload.PERMISSIONS.PRIVATE );
        else
            this.setPermission( BQ.upload.PERMISSIONS.PUBLISHED );
    },

    setPermission : function(new_perm) {
        var btn = this.queryById('button_permission');
        if (this.state >= BQ.upload.STATES.UPLOADING) return;
        this.permission = new_perm;
        if (this.permission)
            btn.addCls('published');
        else
            btn.removeCls('published');
        btn.setText(BQ.upload.PERMISSIONS_STRINGS[this.permission]);
    },

    isReadyToUpload : function() {
        return (this.getState && this.getState()===BQ.upload.STATES.READY);
    },

    upload : function() {
        if (!this.isReadyToUpload()) return;
        var formconf = Ext.clone(this.formconf);
        // dima: force haproxy hashing to distribute transfer over to separate machines
        formconf.form_action += '_'+Math.random().toString(36).substring(2);

        //this.time_started = new Date();
        this.error = undefined;
        this.state = BQ.upload.STATES.UPLOADING;
        this.constructAnnotation();
        this.fup = new BQFileUpload(this.file, {
            uploadComplete: Ext.Function.bind( this.onComplete, this ),
            uploadFailed:   Ext.Function.bind( this.onFailed, this ),
            uploadCanceled: Ext.Function.bind( this.onCanceled, this ),
            uploadTransferProgress: Ext.Function.bind( this.onProgress, this ),
            uploadTransferStart:    Ext.Function.bind( this.onTransferStart, this ),
            uploadTransferEnd:      Ext.Function.bind( this.onTransferEnd, this ),
            formconf: formconf,
            resource: this.annotations ? this.annotations.toXML(): undefined,
        });
        this.fup.upload();
        this.updateUi();
    },

    cancel : function(noui) {
        if (this.state >= BQ.upload.STATES.DONE) return;
        this.state = BQ.upload.STATES.CANCELED;
        //BQ.ui.notification('Cancel');
        if (this.fup) {
            this.fup.cancel();
            this.fireEvent( 'filecanceled', this);
        }
        if (noui) return;
        this.updateUi();
    },

    onTransferStart : function(e) {
        //BQ.ui.notification('Started');
        this.time_started = new Date();
    },

    onTransferEnd : function(e) {
        //BQ.ui.notification('ended');
        this.time_finished_upload = new Date();
        this.state = BQ.upload.STATES.INGESTING;
        this.progress.updateProgress( 1.0 );
        this.updateUi();
    },

    doProgress : function() {
        this.progress_timeout = null; clearTimeout (this.progress_timeout);
        var e = this._progress_event;
        if (this.state != BQ.upload.STATES.UPLOADING) return;
        this.updateUi();
        var elapsed = (new Date() - this.time_started)/1000;
        this.progress.updateProgress( e.loaded/e.total, 'Uploading at ' + BQ.upload.formatFileSize(e.loaded/elapsed) +'/s' );
    },

    onProgress : function(e) {
        this._progress_event = e;
        if (this.progress_timeout) return;
        this.progress_timeout = setTimeout( Ext.Function.bind( this.doProgress, this ), this.hysteresis );
    },

    onComplete : function(e) {
        this.progress.updateProgress( 1.0 );
        this.state = BQ.upload.STATES.ERROR;
        this.time_finished = new Date();
        if (!this.time_finished_upload)
            this.time_finished_upload = this.time_finished;

        var elapsed = (this.time_finished_upload - this.time_started)/1000;
        var speed = BQ.upload.formatFileSize(this.file.size/elapsed)+'/s';
        var timing = ' in '+ this.time_finished.diff(this.time_started).toString() +
                     ' at '+ speed;

        // parse response
        if (e && e.target && e.target.responseXML && e.target.responseXML.firstChild && e.target.responseXML.firstChild.firstChild) {
            this.resource = BQFactory.createFromXml(e.target.responseXML.firstChild.firstChild);

            if (this.resource.uri) {
                // image inserted correctly
                this.state = BQ.upload.STATES.DONE;
                var s = 'Uploaded <a class="filename" href="'+BQ.upload.view_resource+this.resource.uri+'">'+this.file.name+'</a>'+' as <b>'+this.resource.resource_type+'</b> '+timing;
                this.fileName.setText(s);
            } else { // error returned in an XML doc
                var d = this.resource.toDict();
                this.error = Encoder.htmlEncode(d.error);
                this.fileName.setText('Error while uploading <b>'+this.file.name+'</b>'+' at '+timing);
            }
        } else if (e && e.target) { // some error happened with no XML output
            this.error = e.target.status+' - '+e.target.statusText;
            this.fileName.setText('Error while uploading <b>'+this.file.name+'</b>'+' at '+timing);
        }
        this.updateUi();
        this.fireEvent( 'fileuploaded', this);
    },

    onFailed : function(e) {
        if (e && e.target) {
            this.error = e.target.status+' - '+e.target.statusText;
            this.fileName.setText('Error while uploading <b>'+this.file.name+'</b>'+' at '+timing);
        }
        this.state = BQ.upload.STATES.ERROR;
        this.updateUi();
        this.fireEvent( 'fileerror', this);
    },

    onCanceled : function(e) {
        this.state = BQ.upload.STATES.CANCELED;
        this.updateUi();
        this.fireEvent( 'filecanceled', this);
    },

    constructAnnotation: function() {
        var resource = new BQResource();
        //resource.type = 'file';
        //resource.uri  = this.file.name;
        resource.name = this.file.name;
        var path = this.file.relativePath || this.file.webkitRelativePath || this.file.name || this.file.fileName;
        var prefix = this.path.getPath();
        if (this.path && prefix && prefix.length>0) {
            path = prefix + '/' + path;
            path = path.replace('//', '/');
        }
        if (path && path !== '') {
            resource.name = path;
            //resource.value = path;
        }

        // add access permission annotation
        if (this.permission) {
            resource.permission =  BQ.upload.PERMISSIONS_STRINGS[this.permission];
            //if (!this.annotation_dict)
            //    this.annotation_dict = {};
            //this.annotation_dict['permission'] = BQ.upload.PERMISSIONS_STRINGS[this.permission];
        }

        // add tagger annotations
        if (this.tagger) {
            var doc = this.tagger.resource.clone(true);
            resource.type = doc.type;
            resource.addtags( doc.tags, true );
            //resource.tags = doc.tags;
            resource.gobjects = doc.gobjects;
        }

        // create the ingest tag
        if (this.annotation_dict) {
            var d = this.annotation_dict;
            ingest = resource.addtag ({name: 'ingest'});
            for (var k in d)
                ingest.addtag({ name: k, value: d[k] });
        }
        this.annotations = resource;
    },

    onAnnotated : function(ann) {
        this.state = BQ.upload.STATES.READY;
        this.annotator.destroy();
        this.setHeight( this.height_normal );
        this.progress.setVisible(true);
        this.fileName.setVisible(true);
        this.fileSize.setVisible(true);
        this.annotation_dict = ann;
        var s = this.fileName.text+' - '+BQ.upload.ANNOTATOR_TYPES[ann.type];
        this.fileName.setText(s);
    },

});

//--------------------------------------------------------------------------------------
// BQ.upload.Panel
// upload manages items and all other UI aspects like drag and drop
// Events:
//    fileuploaded
//    filesuploaded
//    datasetcreated
//    filecanceled
//    filescanceled
//    fileadded
//    fileerror
//--------------------------------------------------------------------------------------

BQ.upload.UPLOAD_STRING = 'Uploading';

BQ.upload.DATASET_CONFIGS = {
    NORMAL   : 0,
    REQUIRE  : 1,
    PROHIBIT : 2,
};

BQ.upload.FS_FILES_IGNORE = {
    '.'         : '.',
    '..'        : '..',
    'Thumbs.db' : 'Thumbs.db',
    '.DS_Store' : '.DS_Store',
    '.Trashes'  : '.Trashes',
};

// Bioformats says it supports many non-image formats
BQ.upload.IGNORE_FMT_EXT = {
    'zip': true, 'xml': true, 'txt': true, 'amiramesh': true, 'cfg': true, 'csv': true, 'dat': true,
    'grey': true, 'htm': true, 'html': true, 'hx': true, 'inf': true, 'labels': true, 'log': true,
    'lut': true, 'mdb': true, 'pst': true, 'pty': true, 'rec': true, 'tim': true, 'xlog': true, 'zpo': true,
};

BQ.upload.DEFAULTS = {
    heading: 'File upload',
    maxFiles: 0, // use 1 for single file
    maxFileSize: 0, // maximum file size in bytes, 0 no limit
    //allowedFileTypes: undefined, // currently not supported, ex: { mime: ['image/tiff', 'image/jpeg'], exts: ['pptx', 'zip'] }
    //limitConcurrentUploads: undefined, // currently not supported, use 1 for sequential uploads
    dataset_configs: BQ.upload.DATASET_CONFIGS.NORMAL,
    hysteresis: 500,
};

Ext.define('BQ.upload.Panel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.bq_upload',
    componentCls: 'bq-upload-panel',

    requires: ['Ext.toolbar.Toolbar', 'Ext.tip.QuickTipManager', 'Ext.tip.QuickTip', 'BQ.picker.Path', 'Bisque.ResourceTaggerOffline'],

    border: 0,
    autoScroll: false,
    layout: 'fit',
    defaults: BQ.upload.DEFAULTS,

    formconf: { form_action: '/import/transfer', form_file: 'file', form_resource: 'file_resource' },

    processConfig: function() {
        if (this.maxFiles == 1)
            this.dataset_configs = BQ.upload.DATASET_CONFIGS.PROHIBIT;
    },

    initComponent : function() {

        this.processConfig();
        this.setLoading('Fetching supported formats...');
        BQ.is.fetchFormatsList( callback(this, this.onFormatsList), undefined );

        // footer's toolbar elements
        var dataset_btn_visible = true,
            dataset_btn_preseed = false;
        if (this.dataset_configs > BQ.upload.DATASET_CONFIGS.NORMAL) {
            dataset_btn_visible = false;
        }
        if (this.dataset_configs == BQ.upload.DATASET_CONFIGS.REQUIRE) {
            dataset_btn_preseed = true;
        }

        this.dockedItems = [{
            xtype: 'toolbar',
            itemId: 'toolbar_select',
            dock: 'top',
            defaults: {
                scale: 'large',
            },
            allowBlank: false,
            cls: 'tools',
            border: 0,
            layout: {
                overflowHandler: 'Menu'
            },
            items: [{
                xtype:'tbtext',
                html: '<h1>'+this.heading+':</h1>',
            }, {
                xtype: 'filemultifield',
                itemId: 'selector_files',
                buttonOnly: true,
                multiple: true,
                handler: this.chooseFiles,
                scope: this,
                buttonConfig: {
                    scale: 'large',
                    iconCls: 'icon browse',
                    text: 'Choose files',
                    tooltip: 'Select several local files to upload',
                    //cls: 'x-btn-default-large',
                },
                listeners: {
                    change: this.chooseFiles,
                    scope: this,
                },
            }, {
                xtype: 'filemultifield',
                itemId: 'selector_directory',
                buttonOnly: true,
                multiple: true,
                directory: true,
                scope: this,
                handler: this.chooseFiles,
                buttonConfig: {
                    scale: 'large',
                    iconCls: 'icon browse-folders',
                    text: 'Choose directory',
                    tooltip: 'Select a local directory to upload',
                    //cls: 'x-btn-default-large',
                },
                listeners: {
                    change: this.chooseFiles,
                    scope: this,
                },
            }, {
                xtype:'splitbutton',
                text: 'Toggle permissions',
                //cls: 'x-btn-default-large',
                tooltip: 'Toggle access right to all images, only works before the upload have started',
                //iconCls: 'add16',
                scope: this,
                handler: this.setPermissionsToggle,
                menu: [{
                    text: 'Set all published',
                    scope: this,
                    handler: function() { this.setPermissions(BQ.upload.PERMISSIONS.PUBLISHED); },
                }, {
                    text: 'Set all private',
                    scope: this,
                    handler: function() { this.setPermissions(BQ.upload.PERMISSIONS.PRIVATE); },
                }],
            }, {
                xtype: 'tbfill',
            }, {
                text: 'Formats',
                iconCls: 'icon formats',
                //cls: 'x-btn-default-large',
                tooltip: 'Show supported formats',
                handler: this.onFormats,
                scope: this,
            }, {
                text: 'Help',
                iconCls: 'icon help',
                //cls: 'x-btn-default-large',
                tooltip: 'Show help page about file uploading',
                handler: this.onHelp,
                scope: this,
            }],
        },{
            xtype: 'toolbar',
            dock: 'bottom',
            cls: 'footer',
            border: 0,
            defaults: {
                scale: 'large',
                //cls: 'x-btn-default-large',
            },
            items: [{
                xtype: 'button',
                itemId: 'btn_upload',
                text: 'Upload',
                disabled: true,
                iconCls: 'icon upload',
                scale: 'large',
                //cls: 'x-btn-default-large',
                tooltip: 'Start the upload of all queued files',
                scope: this,
                handler: this.upload,
            }, {
                xtype: 'button',
                itemId: 'btn_cancel',
                text: 'Cancel',
                disabled: true,
                iconCls: 'icon cancel',
                scale: 'large',
                //cls: 'x-btn-default-large',
                tooltip: 'Cancel all queued and uploading files',
                scope: this,
                handler: this.cancel,
            }, {
                xtype: 'button',
                itemId: 'btn_reupload',
                text: 'Re-upload failed',
                //disabled: true,
                hidden: true,
                iconCls: 'icon upload',
                scale: 'large',
                //cls: 'x-btn-default-large',
                tooltip: 'Re-upload all failed files',
                handler: Ext.Function.bind( this.reupload, this ),
            }, {
                xtype: 'tbspacer',
                cls: '',
                width: 50,
            }, {
                xtype: 'button',
                itemId: 'btn_dataset',
                text: 'Add to new dataset',
                //iconCls: 'icon cancel',
                scale: 'large',
                hidden: true,
                //cls: 'x-btn-default-large',
                tooltip: 'Add all uploaded files to a new dataset',
                scope: this,
                handler: function(me) {
                    Ext.Msg.prompt(
                        'Dataset name',
                        'Please enter a dataset name:',
                        function(btn, text) {
                            if (btn === 'ok') {
                                this.createNewDataset(text);
                            }
                        },
                        this,
                        false,
                        'Uploaded on '+(new Date()).toISOString()
                    );
                },
            }, {
                xtype: 'button',
                itemId: 'btn_dataset_add',
                text: 'Add to existing dataset',
                //iconCls: 'icon cancel',
                scale: 'large',
                hidden: true,
                //cls: 'x-btn-default-large',
                tooltip: 'Add all uploaded files to an existing dataset',
                scope: this,
                handler: function(me) {
                    Ext.create('Bisque.DatasetBrowser.Dialog', {
                        height: '85%',
                        width:  '85%',
                        listeners: {
                            scope: this,
                            DatasetSelect: function(me, resource) {
                                BQFactory.request ({
                                    uri : resource.uri,
                                    cb : callback(this, this.addToDataset),
                                    errorcb : function(error) {
                                        BQ.ui.error('Error fetching dataset', 4000);
                                    },
                                    uri_params: { view:'deep' },
                                });
                            },
                        },
                    });
                },
            }, {
                xtype: 'progressbar',
                itemId: 'progress',
                text: BQ.upload.UPLOAD_STRING,
                flex: 1,
                height: 30,
                style: 'margin-left: 30px; margin-right: 30px;',
                animate: false,
                value: 0,
                hidden: true,
            }],
        }];

        //--------------------------------------------------------------------------------------
        // items
        //--------------------------------------------------------------------------------------
        this.items = [{
            xtype: 'panel',
            border: 0,
            layout: 'border',
            defaults: { split: true, },
            items: [{
                xtype: 'container',
                border: 0,
                region:'center',
                layout: {
                    type: 'vbox',
                    align: 'stretch',
                    pack: 'start',
                },
                items: [{
                    xtype:'bq-picker-path',
                    itemId: 'upload_path',
                    height: 35,
                    prefix: 'Upload to: ',
                    path: this.getPreferredPath(),
                    listeners: {
                        scope: this,
                        browse: this.browsePath,
                        changed: this.onPathChanged,
                    },
                }, {
                    xtype: 'container',
                    itemId: 'uploadPanel',
                    border: 0,
                    //region:'center',
                    flex: 10,
                    autoScroll: true,
                    cls: 'upload',
                    html: '<div id="formats_background" class="background"></div><div class="background dropzone">Drop files here</div>',
                }],
            },{
                xtype: 'bq-tagger-offline',
                itemId: 'taggerPanel',
                title: 'Textual annotations',
                border: 0,
                region:'east',
                collapsible: true,
                width: 350,
                cls: 'tabs',
                deferredRender: true,
            }],
        }];

        this.callParent();
        if (BQ.Preferences)
        BQ.Preferences.get({
            key : 'Uploader',
            callback : Ext.bind(this.onPreferences, this),
        });
        this.btn_upload      = this.queryById('btn_upload');
        this.btn_cancel      = this.queryById('btn_cancel');
        this.btn_reupload    = this.queryById('btn_reupload');
        this.btn_dataset     = this.queryById('btn_dataset');
        this.btn_dataset_add = this.queryById('btn_dataset_add');
        this.progress        = this.queryById('progress');
        this.taggerPanel     = this.queryById('taggerPanel');
        this.uploadPanel     = this.queryById('uploadPanel');
    },

    afterRender : function() {
        this.callParent();

        // accept file drag and drop
        var el = this.getEl();
        if (el) {
            el.on( 'dragover', this.onDragOver, this );
            el.on( 'dragleave', this.onDragLeave, this );
            el.on( 'drop', this.onDrop, this );
        }

        // this is used for capturing window closing and promting the user if upload is in progress
        //Ext.EventManager.on(window, 'beforeunload', this.onClose, this);
        window.onbeforeunload = Ext.bind(this.onClose, this);
        // dima: also listen to closing the panel


        var el = this.queryById('upload_path').queryById('prefix').getEl(),
            s = '<p>Uploading to folder: <b>'+this.getPreferredPath()+'</b></p>';
        s += '<p>Press "Upload to" to change...</p>';
        this.doHighlight(el, s);
    },

    onDestroy : function() {
        this.cancel(true);
        this.callParent();
    },

    doHighlight: function(el, text) {
        setTimeout(function(){
            BQ.ui.highlight(el, text, {
                anchor:'top',
                timeout: 10000,
                mouseOffset : [0, 10],
                cls: 'bq-highlight',
            });
        }, 1000);
    },

    chooseFiles : function(field, value, opts) {
        var files = field.fileInputEl.dom.files;
        this.addFiles(files);
    },

    checkFile : function(f) {
        // first check if the file is already included
        var found = false;
        for (var i=0; i<this.uploadPanel.items.getCount(); i++) {
            var item = this.uploadPanel.items.getAt(i);
            if (item && item.hasFile)
                found = item.hasFile(f);
            if (found) break;
        }
        return found;
    },

    // private at this point, noui - should be true if you don't want file to be added to the list right here
    addFile : function(f, noui) {
        // first check if the file is already included
        if (this.checkFile(f)) {
            BQ.ui.notification('File already in the upload queue: '+f.name);
            return;
        }

        if (this.maxFileSize && this.maxFileSize>0 && this.maxFileSize > f.size) {
            BQ.ui.notification('File is too large: '+f.name);
            return;
        }

        if (this.maxFiles && this.maxFiles>0 && this.maxFiles <= this.uploadPanel.items.getCount()) {
            BQ.ui.notification('Maximum size of file queue reached...');
            return;
        }

        //allowedFileTypes: undefined, // currently not supported, ex: { mime: ['image/tiff', 'image/jpeg'], exts: ['pptx', 'zip'] }

        var fp = Ext.create('BQ.upload.Item', {
            file: f,
            formats_extensions: this.formats_extensions,
            formconf: this.formconf,
            tagger: this.taggerPanel,
            path: this.queryById('upload_path'),
            listeners: {
                    fileuploaded: this.onFileUploaded,
                    filecanceled: this.onFileCanceled,
                    fileerror: this.onFileError,
                    scope: this,
            },
        });

        if (!noui) {
            this.uploadPanel.add(fp);
            this.btn_upload.setDisabled(false);
            this.btn_upload.getEl().highlight('ffd232', {duration:250, iterations:6});
            //this.btn_reupload.setVisible(false);
            this.btn_cancel.setDisabled(false);
            this.taggerPanel.setDisabled(false);
            this.btn_dataset.setVisible(false);
            this.btn_dataset_add.setVisible(false);
        }
        this.fireEvent( 'fileadded', fp);
        return fp;
    },

    doProgress : function() {
        this.progress_timeout = null; clearTimeout (this.progress_timeout);
        var e = this._progress_event;
        this.progress.updateProgress( e.pos, e.message );
    },

    updateProgress : function(pos, message) {
        this._progress_event = {pos: pos, message: message};
        if (this.progress_timeout) return;
        this.progress_timeout = setTimeout( Ext.Function.bind( this.doProgress, this ), this.hysteresis );
    },

    // updating UI on very insert is expensive, create a list first and then update the UI
    // the problem dropping files is unknow number due to directory reading
    addDirectoryPrivate: function (item, path, dropped) {
        var me = this;
        path = path || '';
        if (item.isFile) {
            item.file(function(f) {
                f.relativePath = path + f.name;
                dropped.counts--;
                if (me.ignoreFile(f)) // skip ignored files
                    return;
                var fp = me.addFile(f, true);
                if (fp) dropped.files.push(fp);
                if (dropped.counts<1) {
                    me.uploadPanel.add(dropped.files);
                    me._dropped_dirs--;
                    if (me._dropped_dirs<1) {
                        me.progress.setVisible(false);
                        me.setLoading(false);
                        me.btn_upload.setDisabled(false);
                        me.btn_upload.getEl().highlight('ffd232', {duration:250, iterations:6});
                        me.btn_cancel.setDisabled(false);
                        me.btn_dataset.setVisible(false);
                        me.btn_dataset_add.setVisible(false);
                    }
                }
            });
        } else if (item.isDirectory) {
            dropped.counts--;
            var dr = item.createReader();
            dr.readEntries(function(entries) {
                var e = undefined;
                dropped.counts += entries.length;
                for (var i=0; (e=entries[i]); ++i) {
                    me.addDirectoryPrivate(e, path + item.name + '/', dropped);
                }
            });
        }
    },

    addDirectory: function (item, path) {
        this._dropped_dirs = this._dropped_dirs || 0;
        this._dropped_dirs++;
        var dropped = {
            counts: 1,
            files: [],
        };
        var me = this;
        setTimeout( function() { me.addDirectoryPrivate(item, path, dropped); }, 1);
    },

    // updating UI on very insert is expensive, create a list first and then update the UI
    addFilesPrivate : function(pos) {
        var total = this._files.length;
        if (pos>=total) {
            this.uploadPanel.add(this._fps);
            this.uploadPanel.removeCls('waiting');

            //var time_finished = new Date();
            //this.progress.updateProgress(100, 'Inserted in '+time_finished.diff(this._time_started).toString() );
            this.progress.setVisible(false);
            this.setLoading(false);
            this.btn_upload.setDisabled(false);
            this.btn_upload.getEl().highlight('ffd232', { duration: 250, iterations: 4, });
            this.btn_cancel.setDisabled(false);
            this.taggerPanel.setDisabled(false);
            this.btn_dataset.setVisible(false);
            this.btn_dataset_add.setVisible(false);
            this._files = undefined;
            this._fps = undefined;
            return;
        }

        var f = this._files[pos];
        var fp = this.addFile(f, true);
        if (fp) this._fps.push(fp);

        if (pos+1<total) {
            this.updateProgress( pos/total, 'Inserting files: '+(pos+1)+' of '+total );
        } else {
            clearTimeout (this.progress_timeout);
            this.progress_timeout = null;
            this.progress.updateProgress( 1, 'Rendering inserted files, wait a bit...' );
        }

        var me = this;
        setTimeout( function() { me.addFilesPrivate(pos+1); }, 1);
    },

    ignoreFile : function(f) {
        if (f.name in BQ.upload.FS_FILES_IGNORE) // skip ignored files
            return true;
        if (f.name.indexOf('._')===0) // MacOSX files starting at '._'
            return true;
        return false;
    },

    addFiles : function(files, items) {
        var notified = false;
        this.progress.setVisible(true);
        if (items)
            this.setLoading('Adding dropped files...');
        this._files = [];
        var f = undefined;
        for (var i=0; (f=files[i]); ++i) {
            if (this.ignoreFile(f)) // skip ignored files
                continue;
            if (items && items[i].webkitGetAsEntry) {
                var item = items[i].webkitGetAsEntry();
                if (item && item.isDirectory) {
                    this.addDirectory(item, '');
                    continue;
                }
            }
            if (f.size === 0 && f.type === '') {
                if (!notified) {
                    BQ.ui.warning('Unfortunately, your browser does not allow directory upload, please use Google Chrome.');
                    notified = true;
                }
                continue;
            }
            this._files.push(f);
        }

        if (this._files.length<1) {
            this.progress.setVisible(false);
            return;
        }
        this._fps = [];
        this.uploadPanel.addCls('waiting');
        this._time_started = new Date();
        this.addFilesPrivate(0);
    },

    upload : function() {
        this.all_done = false;
        this.files_uploaded = 0;

        var total = 0;
        this.uploadPanel.items.each( function(){
            if (this.isReadyToUpload && this.isReadyToUpload()) total++;
        });
        this.total = total;
        if (total===0) return;

        this._time_started = new Date();
        this.btn_upload.setDisabled(true);
        this.taggerPanel.setDisabled(true);
        this.btn_dataset.setVisible(false);
        this.btn_dataset_add.setVisible(false);
        this.progress.setVisible(true);
        this.progress.updateProgress(0, BQ.upload.UPLOAD_STRING);
        this.uploadPanel.items.each( function() { if (this.upload) this.upload(); } );
    },

    cancel : function(ondestroy) {
        if (!ondestroy) this.uploadPanel.setLoading('Canceling uploads...');
        this.uploadPanel.items.each( function() { if (this.cancel) this.cancel(); } );
        if (!ondestroy) {
            this.uploadPanel.setLoading(false);
            this.testDone(true);
            this.fireEvent( 'filescanceled', this);
        }
    },

    setPermissionsToggle : function() {
        this.uploadPanel.setLoading('Setting permissions...');
        this.uploadPanel.items.each( function() { if (this.togglePermission) this.togglePermission(); } );
        this.uploadPanel.setLoading(false);
    },

    setPermissions : function(new_perm) {
        this.uploadPanel.setLoading('Setting permissions...');
        this.uploadPanel.items.each( function() { if (this.setPermission) this.setPermission(new_perm); } );
        this.uploadPanel.setLoading(false);
    },

    blockPropagation: function (e) {
        if (e.stopPropagation) e.stopPropagation(); // DOM Level 2
        else e.cancelBubble = true;                 // IE
        if (e.preventDefault) e.preventDefault();   // prevent image dragging
        else e.returnValue=false;
    },

    onDragOver : function(e) {
        e = e ? e : window.event;
        this.blockPropagation(e);
        this.uploadPanel.addCls( 'dragging' );
    },

    onDragLeave : function(e) {
        e = e ? e : window.event;
        this.blockPropagation(e);
        this.uploadPanel.removeCls( 'dragging' );
    },

    onDrop : function(e) {
        e = e ? e : window.event;
        this.blockPropagation(e);
        this.uploadPanel.removeCls( 'dragging' );
        if (!e || !e.browserEvent || !e.browserEvent.dataTransfer || !e.browserEvent.dataTransfer.files) return;
        var files = e.browserEvent.dataTransfer.files;
        var items = e.browserEvent.dataTransfer.items;
        this.addFiles(files, items);
    },

    testDone : function(nomessage) {
        //var total = this.uploadPanel.items.getCount();
        var total = this.total;
        this.progress.updateProgress( this.files_uploaded/total, 'Uploaded '+this.files_uploaded+'/'+total );

        var e = this.uploadPanel.items.findBy( function(){ return (this.getState && this.getState()<BQ.upload.STATES.DONE); } );
        if (!e && this.files_uploaded>=total && !this.all_done) {
            this.all_done = true;

            // first find out if some files had upload error
            var failed = this.testFailed();
            if (!nomessage) {
                var time_finished = new Date();
                var s = ''+(total-failed)+' files uploaded successfully in '+time_finished.diff(this._time_started).toString();
                if (failed>0) s += '<br>Although '+failed+' files have failed to upload.';
                BQ.ui.notification(s);
            }

            this.progress.setVisible(false);
            this.btn_upload.setDisabled(true);
            this.btn_cancel.setDisabled(true);
            if (failed<1) {
                this.taggerPanel.setDisabled(true);
                this.btn_dataset.setVisible(true);
                this.btn_dataset_add.setVisible(true);
                BQ.ui.highlight(this.btn_dataset.getEl(), '<p>You can now add uploaded files to a dataset</p>', {
                    anchor:'bottom',
                    timeout: 10000,
                    //mouseOffset : [0, 10],
                    cls: 'bq-highlight',
                });
            }


            // fire all files uploaded event
            var res = [];
            this.uploadPanel.items.each( function() {
                if (this.resource && this.resource.uri)
                    res.push( this.resource );
            });
            this.fireEvent( 'filesuploaded', res, this);
        } else {
            this.btn_upload.setDisabled(false);
            this.btn_cancel.setDisabled(false);
            this.taggerPanel.setDisabled(false);
            this.btn_dataset.setVisible(false);
            this.btn_dataset_add.setVisible(false);
        }
    },

    onFileUploaded : function(fu) {
        this.files_uploaded++;
        this.fireEvent( 'fileuploaded', fu);
        this.testDone();
    },

    onFileCanceled : function(fu) {
        this.files_uploaded++;
        this.fireEvent( 'filecanceled', fu);
        this.testDone();
    },

    onFileError : function(fu) {
        this.files_uploaded++;
        this.fireEvent( 'fileerror', fu);
        this.testDone();
    },

    isDatasetMode : function() {
        return this.btn_dataset.pressed;
    },

    createNewDataset : function(name) {
        var members = [];
        this.uploadPanel.items.each( function() {
            if (this.resource && this.resource.uri) {
                members.push( new BQValue( "object", this.resource.uri ) );
            }
        });
        if (members.length<1) return;

        var dataset = new BQDataset();
        dataset.name = name;
        dataset.setMembers( members );
        dataset.save_(undefined, callback(this, 'onCreatedDataset'));
    },

    addToDataset : function(dataset) {
        var members = dataset.values;
        this.uploadPanel.items.each( function() {
            if (this.resource && this.resource.uri) {
                members.push( new BQValue( "object", this.resource.uri ) );
            }
        });
        dataset.save_(undefined, callback(this, this.onDatasetSaved));
    },

    onCreatedDataset : function(dataset) {
        BQ.ui.notification('Dataset created: "<a href="/client_service/view?resource='+dataset.uri+'">'+dataset.name+'</a>"', 10000);
        this.fireEvent( 'datasetcreated', dataset);
    },

    onDatasetSaved : function(dataset) {
        BQ.ui.notification('Dataset saved: "<a href="/client_service/view?resource='+dataset.uri+'">'+dataset.name+'</a>"', 10000);
        this.fireEvent( 'datasetsaved', dataset);
    },

    testFailed : function () {
        var failed=0;
        this.uploadPanel.items.each( function() {
            if (this.state != BQ.upload.STATES.DONE)
                failed++;
        });
        if (failed>0)
            this.btn_reupload.setVisible(true);
        else
            this.btn_reupload.setVisible(false);
        return failed;
    },

    reupload : function () {
        this.uploadPanel.setLoading('Removing succeeded uploads...');
        this.uploadPanel.items.each( function() {
            //if (this.state == BQ.upload.STATES.DONE) {
            //    this.destroy();
            //} else
            if (this.state > BQ.upload.STATES.DONE) {
                this.setState( BQ.upload.STATES.READY );
            }
        });
        this.btn_reupload.setVisible(false);
        this.uploadPanel.setLoading(false);
        this.upload();
    },

    // this is used for capturing window closing and promting the user if upload is in progress
    onClose : function() {
        var uploading=false,
            unuploaded=false;
        this.uploadPanel.items.each( function() {
            if (this.state>=BQ.upload.STATES.UPLOADING && this.state<BQ.upload.STATES.DONE) {
                uploading = true;
            }
            if (this.state>=BQ.upload.STATES.ANNOTATING && this.state<BQ.upload.STATES.UPLOADING) {
                unuploaded = true;
            }
            if (uploading || unuploaded) return false;
        });

        if (uploading) {
            return 'Upload in progress, by closing the page you will cancel all uploads!';
        }
        if (unuploaded) {
            this.btn_upload.getEl().highlight('ffd232', {duration:250, iterations:6});
            return 'There are unuploaded files, by closing the page you will cancel all uploads!';
        }
    },

    onHelp : function() {
        var w = Ext.create('Ext.window.Window', {
            title : 'Help',
            bodyStyle : 'padding: 10px',
            modal : true,
            autoScroll : true,
            width : BQApp ? BQApp.getCenterComponent().getWidth() / 1.8 : document.width / 1.8,
            height : BQApp ? BQApp.getCenterComponent().getHeight() / 1.1 : document.height / 1.1,
            maxWidth : 1000,
            buttonAlign : 'center',
            loader : {
                url : '/import/help.html',
                renderer : 'html',
                autoLoad : true,
                ajaxOptions : {
                    disableCaching : false,
                }
            },
            buttons : [{
                text : 'OK',
                handler : function(cmp, e) {
                    w.close();
                }
            }],
        }).show();
    },

    onFormats : function() {
        var w = Ext.create('Ext.window.Window', {
            title : 'Help',
            modal : true,
            layout : 'fit',
            width : BQApp ? BQApp.getCenterComponent().getWidth() / 1.8 : document.width / 1.8,
            height : BQApp ? BQApp.getCenterComponent().getHeight() / 1.1 : document.height / 1.1,
            maxWidth : 1000,
            border: 0,
            buttonAlign : 'center',
            buttons : [{
                text : 'OK',
                handler : function(cmp, e) {
                    w.close();
                }
            }],
            items: [{
                xtype: 'bq-formats',
            }],
        }).show();
    },

    onFormatsList : function(fmts) {
        this.formats = fmts;
        this.formats_extensions = {};
        this.formats_names = {};
        for (var n in fmts) {
            var f = fmts[n];
            if (!(f.fullname in this.formats_names) || this.formats_names[f.fullname]<f.confidence) {
                this.formats_names[f.fullname] = f.confidence;

            }

            var exts = f.extensions.split(',');
            var ext = undefined;
            for (var i=0; (ext=exts[i]); ++i) {
                if ( !(ext in BQ.upload.IGNORE_FMT_EXT) && (!(ext in this.formats_extensions) || this.formats_extensions[ext].confidence < f.confidence) )
                    this.formats_extensions[ext] = f;
            }
        }
        this.setLoading(false);
        var back = Ext.get('formats_background');
        if (back && back.dom) {
            var keys = Object.keys(this.formats_names).sort(function() {
                return Math.random() - 0.5;
            });
            var s='';
            var n = undefined;
            for (var i=0; (n=keys[i]); ++i) {
                var cls = this.formats_names[n] > 0.5 ? 'good' : 'uncertain';
                s += '<span class="'+cls+'" style="">'+n+'</span> ';
            }
            back.dom.innerHTML = s;
        }
    },

    getPreferredPath : function(template) {
        var t = template || '{date_iso}';
        var datenow = new Date();
        var vars = {
            user: BQApp.user && BQApp.user.user_name ? BQApp.user.user_name : '', // dima: not inited, requires later update
            date_iso: Ext.Date.format(datenow, 'Y-m-d'),
            datetime_iso: Ext.Date.format(datenow, 'Y-m-d H:i:s'),
            d: Ext.Date.format(datenow, 'd'),
            D: Ext.Date.format(datenow, 'D'),
            j: Ext.Date.format(datenow, 'j'),
            l: Ext.Date.format(datenow, 'l'),
            N: Ext.Date.format(datenow, 'N'),
            S: Ext.Date.format(datenow, 'S'),
            w: Ext.Date.format(datenow, 'w'),
            z: Ext.Date.format(datenow, 'z'),
            W: Ext.Date.format(datenow, 'W'),
            F: Ext.Date.format(datenow, 'F'),
            m: Ext.Date.format(datenow, 'm'),
            M: Ext.Date.format(datenow, 'M'),
            n: Ext.Date.format(datenow, 'n'),
            t: Ext.Date.format(datenow, 't'),
            L: Ext.Date.format(datenow, 'L'),
            o: Ext.Date.format(datenow, 'o'),
            Y: Ext.Date.format(datenow, 'Y'),
            y: Ext.Date.format(datenow, 'y'),
            a: Ext.Date.format(datenow, 'a'),
            A: Ext.Date.format(datenow, 'A'),
            g: Ext.Date.format(datenow, 'g'),
            G: Ext.Date.format(datenow, 'G'),
            h: Ext.Date.format(datenow, 'h'),
            H: Ext.Date.format(datenow, 'H'),
            i: Ext.Date.format(datenow, 'i'),
            s: Ext.Date.format(datenow, 's'),
            u: Ext.Date.format(datenow, 'u'),
            O: Ext.Date.format(datenow, 'O'),
            P: Ext.Date.format(datenow, 'P'),
            T: Ext.Date.format(datenow, 'T'),
            Z: Ext.Date.format(datenow, 'Z'),
            c: Ext.Date.format(datenow, 'c'),
            U: Ext.Date.format(datenow, 'U'),
            MS: Ext.Date.format(datenow, 'MS'),
            time: Ext.Date.format(datenow, 'time'),
            timestamp: Ext.Date.format(datenow, 'timestamp'),
        };
        for (var v in vars)
            t = t.replace( '{'+v+'}', vars[v] );

        //return Ext.Date.format(new Date(), 'Y-m-d');
        return t;
    },

    pathUserToBlob : function(path) {
        var p = path;
        if (p[0] !== '/')
            p = '/local/'+p;
        //var user = BQApp.user.user_name;
        //var p = '/blob_service/store/local/'+user+'/'+path;
        p = '/blob_service/store'+p;
        p = p.replace('//', '/');
        return p;
    },

    pathBlobToUser : function(path) {
        //var user = BQApp.user.user_name;
        path = path.replace('/blob_service/store', '');
        path = decodeURIComponent(path);
        return path;
    },

    browsePath : function() {
        var w = (BQApp?BQApp.getCenterComponent().getWidth():document.width)*0.3;
        var h = (BQApp?BQApp.getCenterComponent().getHeight():document.height)*0.8;
        var up = this.queryById('upload_path');
        var el = up.getPrefixButton().el;
        Ext.create('Ext.tip.ToolTip', {
            cls: 'bq-tooltip',
            target: el,
            anchor: 'top',
            floating: true,
            width :  w,
            maxWidth: w,
            minWidth: 300,
            height:  h,
            maxHeight: h,
            minHeight: 300,
            layout: 'fit',
            autoHide: false,
            shadow: true,
            border: false,
            defaults: {
                border : false,
            },
            items: [{
                xtype: 'bq-tree-files-panel',
                border: false,
                path: this.pathUserToBlob(up.getPath()),
                listeners: {
                    scope: this,
                    selected: function(url) {
                        this.onPathChanged(this, this.pathBlobToUser(url));
                        //this.queryById('upload_path').setPath(path);
                    },
                },
            }],
        }).show();
    },

    onPathChanged : function(cnt, path) {
        this.queryById('upload_path').setPath(path);
    },

    onPreferences: function(pref) {
        this.preferences = pref;
        this.queryById('upload_path').setPath(this.getPreferredPath(this.preferences.initial_path));
    },

});

//--------------------------------------------------------------------------------------
// BQ.upload.Dialog
// Instantiates upload panel in a modal window
// Events:
//   uploaded
//--------------------------------------------------------------------------------------

Ext.define('BQ.upload.Dialog', {
    extend: 'Ext.window.Window',
    alias: 'widget.bq_upload_dialog',
    requires: ['BQ.upload.Panel'],

    destory_on_upload: true,

    layout : 'fit',
    modal : true,
    border : false,
    width : '90%',
    height : '90%',

    monitorResize: true,
    closable : true,
    closeAction: 'destroy',

    constructor : function(config) {
        var uploader_config = {
            border: 0,
            flex:2,
            heading: config.title || 'Upload',
            formconf: { form_action: '/import/transfer', form_file: 'file', form_resource: 'file_resource' },
            listeners: {
                    filesuploaded: this.onFilesUploaded,
                    datasetcreated: this.onDatasetCreated,
                    scope: this,
            },
        };

        // move the config options that belong to the uploader
        for (var c in config)
            if (c in BQ.upload.DEFAULTS)
                 uploader_config[c] = config[c];

        this.upload_panel = Ext.create('BQ.upload.Panel', uploader_config);
        this.items = [this.upload_panel];
        config.title = undefined;

        this.callParent(arguments);
        this.on('beforeclose', this.onClose, this);
        this.show();
        return this;
    },

    onFilesUploaded : function(res, uploader) {
        if (this.upload_panel.isDatasetMode()) return;
        this.fireEvent( 'uploaded', res);
        if (this.destory_on_upload) {
            this.destroy();
        }
    },

    onDatasetCreated : function(dataset) {
        this.fireEvent( 'uploaded', [dataset]);
        if (this.destory_on_upload) {
            this.destroy();
        }
    },

    onClose: function(el) {
        if (this.should_be_closed) {
            return;
        }
        var s = this.upload_panel.onClose();
        if (!s) {
            return;
        }

        Ext.Msg.confirm(
             'Close upload?',
             s+'<br>Would you like to close upload?',
             function(btn) {
                 if (btn === 'yes') {
                     this.should_be_closed = true;
                     this.close();
                 }
             },
             this
        );

        return false; // disable closing
    },

});

Ext.define('BQ.panel.Web', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.bq-panel-web',

    autoScroll: true,

    initComponent : function() {
        if (this.url && !this.loader)
            this.loader = { url: this.url, renderer: 'html', autoLoad: false, ajaxOptions: { disableCaching: false, } };
        this.callParent();
    },

    afterRender : function() {
        this.callParent();
        var loader = this.getLoader();
        if (loader && !loader.autoLoad)
            loader.load();
    },
});
