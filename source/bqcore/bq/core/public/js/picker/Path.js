/*******************************************************************************

  BQ.picker.Path - File System path editor


  Author: Dima Fedorov <dimin@dimin.net> <http://www.dimin.net/>
  Copyright (C) Center for BioImage Informatics <www.bioimage.ucsb.edu>

  License: FreeBSD

  Events:
      browse
      changed

  Version: 1

  History:
    2014-04-03 16:18:49 - first version

*******************************************************************************/

Ext.define('BQ.picker.Path', {
    extend: 'Ext.container.Container',
    alias: 'widget.bq-picker-path',

    path: undefined, // initial path
    prefix: undefined, // Text displayed before the path

    cls: 'bq-picker-path',
    layout: {
        type: 'hbox',
        align: 'top',
        pack: 'start',
    },

    constructor : function(config) {
        /*this.addEvents({
            'browse' : true,
            'changed' : true,
        });*/
        this.callParent(arguments);
    },

    initComponent : function() {
        this.callParent(arguments);
        this.path = this.path || '/';
        this.parsePath(this.path);
        this.rerender();
    },

    setPath : function(path) {
        if (this.path === path) return;
        this.path = path;
        this.parsePath(this.path);
        this.rerender();
    },

    getPath : function() {
        return this.pathToString();
    },

    parsePath : function(path) {
        this._path = path === '/' ? [''] : path.split('/');
    },

    pathToString : function() {
        return this._path.join('/');
    },

    getPrefixButton : function() {
        return this.queryById('prefix');
    },

    rerender : function() {
        this.removeAll();
        var c = [];
        if (this.prefix)
            c.push({
                xtype: 'tbtext',
                itemId: 'prefix',
                cls: 'prefix',
                text: this.prefix,
                listeners: {
                    scope: this,
                    click: {
                        element: 'el',
                        fn: this.onBrowse,
                    },
                },
            });

        var stream = [];
        for (var i=0; i<this._path.length; ++i) {
            var p = this._path[i];
            stream.push({
                xtype: 'tbtext',
                itemId: 'path_'+i,
                cls: 'path',
                position: i,
                text: p,
                listeners: {
                    click: {
                        element: 'el',
                        fn: Ext.bind(this.onPath, this, [i]),
                    },
                },
            });
        }

        c.push({
            xtype: 'container',
            itemId: 'stream',
            cls: 'stream',
            flex: 10,
            layout: {
                type: 'hbox',
                align: 'top',
                pack: 'start',
            },
            items: stream,
        });

        this.add(c);
    },

    onBrowse : function(e, el, opts) {
        this.fireEvent('browse', this);
    },

    onPath : function(pos) {
        this._path.splice(pos+1,this._path.length-pos+1);
        var path = this.pathToString();
        this.rerender();
        this.fireEvent('changed', this, path);
    },

});
