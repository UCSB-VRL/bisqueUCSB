/*******************************************************************************

  BQ.upload.File - an extension and fix for file field with multiple
    file selection

  Author: Dima Fedorov

  Version: 2, based on ExtJS 4.2.1

  History:
    2012-02-10 12:08:48 - first creation

*******************************************************************************/

Ext.namespace('BQ.upload');

BQ.upload.isInputDirSupported = function() {
    var tmpInput = document.createElement('input');
    return ('webkitdirectory' in tmpInput
        || 'mozdirectory' in tmpInput
        || 'odirectory' in tmpInput
        || 'msdirectory' in tmpInput
        || 'directory' in tmpInput);
};

Ext.define('BQ.upload.File', {
    extend: 'Ext.form.field.File',
    alias: ['widget.filemultifield', 'widget.filemultiuploadfield'],
    cls: 'bq-upload-file',
    /**
     * @cfg {Boolean} multiple enables multiple file selection
     */
    multiple: false,
    directory: false,

    // private
    afterRender : function() {
        this.callParent();

        // make sure input is a multi file select
        var e = this.fileInputEl;
        if (e && e.dom) {
            e.dom.multiple = this.multiple;
            e.dom.webkitdirectory = this.directory; // allow selecting directories on webkit
            e.dom.nwdirectory = this.directory; // allow selecting directories on node-webkit
            e.dom.mozdirectory = this.directory;
            e.dom.odirectory = this.directory;
            e.dom.msdirectory = this.directory;
            e.dom.directory = this.directory;

            // fix for the error in proxying event into file input
            e.dom.style.width = this.getWidth()+'px';
            e.dom.style.height = this.getHeight()+'px';
        }
    },
});

if (Ext.getVersion().version !== '4.2.1.883')
    console.warn('Override for Ext.form.field.FileButton (File.js): Patches ExtJS 4.2.1 and may not work in other versions and should be checked!');

Ext.define('App.overrides.form.field.FileButton', {
    override: 'Ext.form.field.FileButton',
    //compatibility: '4.2.2',
    afterRender: function() {
        var me = this;
        me.callParent(arguments);
        me.fileInputEl.on('click', function(e) {
            if (this.ownerCt.directory === true && !BQ.upload.isInputDirSupported()) {
                BQ.ui.warning('Unfortunately, your browser does not allow directory upload, please use Google Chrome.');
                e.preventDefault();
                e.stopPropagation();
            }
        }, me);
    },
});


