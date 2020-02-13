Ext.define('Bisque.ResourceBrowser.LayoutFactory', {

    statics : {

        baseClass : 'Bisque.ResourceBrowser.Layout',

        getClass : function(layout) {
            var layoutKey = Ext.Object.getKey(Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS, layout);
            var className = Bisque.ResourceBrowser.LayoutFactory.baseClass + '.' + layoutKey;

            return className;
        },

        getLayout : function(config) {
            var className = this.getClass(config.browser.layoutKey);

            if (Ext.ClassManager.get(className))
                return Ext.create(className, config);
            else {
                Ext.log({
                    msg : Ext.String.format('Unknown layout: {0}', className),
                    level : 'warn',
                    stack : true
                });
                return Ext.create(Bisque.ResourceBrowser.Layout + '.Base', config);
            }
        }
    }
});

// Available layout enumerations
Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS = {
    "Compact" : 1,
    "Card" : 2,
    "PStrip" : 3,
    "PStripBig" : 3.1,
    "Full" : 4,
    "List" : 5,
    "IconList" : 6,
    'Page' : 7,
    'Grid' : 8,
    'Annotator' : 9,

    // for backwards compatibility
    "COMPACT" : 1,
    "CARD" : 2,
};

Bisque.ResourceBrowser.LayoutFactory.DEFAULT_LAYOUT = Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Compact;

/**
 * BaseLayout: Abstract base layout from which all other layouts derive
 *
 * @param {}
 *            configOpts : Layout related options such as type, size etc.
 */
Ext.define('Bisque.ResourceBrowser.Layout.Base', {
    extend : 'Ext.panel.Panel',

    inheritableStatics : {
        layoutCSS : null,
        readCSS : function() {
            var me = {};

            me.layoutCSS = this.layoutCSS;
            me.layoutEl = {
                width : null,
                height : null,
                stdImageHeight : 280,
                stdImageWidth : 280,
            };

            if (me.layoutCSS) {
                me.css = Ext.util.CSS.getRule('.' + me.layoutCSS).style;

                me.layoutEl.padding = parseInt(me.css['padding']);
                me.layoutEl.margin = parseInt(me.css['margin']);
                me.layoutEl.border = parseInt(me.css['borderWidth']);

                me.layoutEl.width = (me.css['width'].indexOf('%') == -1) ? parseInt(me.css['width']) : me.css['width'];
                me.layoutEl.height = (me.css['height'].indexOf('%') == -1) ? parseInt(me.css['height']) : me.css['height'];

                me.layoutEl.outerWidth = me.layoutEl.width + (me.layoutEl.padding + me.layoutEl.border + 2 * me.layoutEl.margin);
                me.layoutEl.outerHeight = me.layoutEl.height + (me.layoutEl.padding + me.layoutEl.border + 2 * me.layoutEl.margin);
            }

            return me;
        }
    },

    constructor : function(configOpts) {
        Ext.apply(this, {
            browser : configOpts.browser,
            direction : configOpts.direction,

            key : configOpts.browser.layoutKey,
            parentCt : configOpts.browser.centerPanel,
            msgBus : configOpts.browser.msgBus,
            showGroups : configOpts.browser.showGroups,

            resQ : [],
            layoutEl : {},
            border : false,
            autoScroll : true,
            toggleAll : false,
        });

        this.callParent(arguments);

        Ext.apply(this, Ext.ClassManager.getClass(this).readCSS());
        this.manageEvents();
    },

    manageEvents : function() {
        //this.on('afterrender', function(){this.animateIn(this.direction)}, this);

        if (this.browser.selType == 'SINGLE')
            this.on({
                'select' : function(resCt) {
                    if (Ext.Object.getSize(this.browser.resourceQueue.selectedRes) != 0)
                        this.browser.resourceQueue.selectedRes.toggleSelect(false);
                    this.browser.resourceQueue.selectedRes = resCt;

                    this.msgBus.fireEvent('ResSelectionChange', [resCt.resource.uri]);
                },
                'unselect' : function(resCt) {
                    this.browser.resourceQueue.selectedRes = {};
                    this.msgBus.fireEvent('ResSelectionChange', []);
                },
                scope : this
            });
        else
            this.on({
                'select' : function(resCt) {
                    this.browser.resourceQueue.selectedRes[resCt.resource.uri] = resCt;
                    var selRes = this.browser.resourceQueue.selectedRes;
                    var selection = Ext.Object.getKeys(selRes);
                    this.msgBus.fireEvent('ResSelectionChange', selection);
                },

                'unselect' : function(resCt) {
                    delete this.browser.resourceQueue.selectedRes[resCt.resource.uri];
                    var selRes = this.browser.resourceQueue.selectedRes;
                    var selection = Ext.Object.getKeys(selRes);
                    this.msgBus.fireEvent('ResSelectionChange', selection);
                },

                scope : this
            });
    },

    toggleSelectAll : function() {
        this.toggleAll = !this.toggleAll;

        if (this.browser.selType != 'SINGLE') {
            for (var i = 0; i < this.resQ.length; i++) {
                this.resQ[i].toggleSelect(this.toggleAll);
                this.resQ[i].fireEvent('select', this.resQ[i]);
            }
        }
    },

    Init : function(resourceQueue, thisCt) {
        this.resQ = resourceQueue;
        if (!thisCt)
            thisCt = this;

        var resCt = [], resCtSub = [], i = 0, currentGrp;

        // if no results were obtained for a given query, show a default no-results message
        if (this.resQ.length == 0) {
            this.noResults();
            return;
        }

        // Avoid 'if' in for loop for speed
        if (this.showGroups) {
            while (i < this.resQ.length) {
                currentGrp = this.getGroup(this.resQ[i]);

                while (i < this.resQ.length && (this.getGroup(this.resQ[i]) == currentGrp)) {
                    this.resQ[i].setSize({
                        width : this.layoutEl.width,
                        height : this.layoutEl.height
                    });
                    this.resQ[i].addCls(this.layoutCSS);
                    resCtSub.push(this.resQ[i]);
                    this.relayEvents(this.resQ[i], ['select', 'unselect']);

                    i++;
                }

                try {
                    var str = Ext.String.ellipsis(decodeURIComponent(currentGrp), 80);
                } catch (e) {
                    var str = Ext.String.ellipsis(currentGrp, 80);
                }

                resCt.push(new Ext.form.FieldSet({
                    items : resCtSub,
                    cls : 'fieldSet',
                    margin : '8 0 0 8',
                    width : (this.getParentSize().width - 30),
                    //autoScroll:true,
                    padding : 0,
                    title : '<b>Group </b><i>' + str + '</i>',
                    collapsible : true,
                    collapsed : false
                }));
                resCtSub = [];
            }
        } else {
            // Code for laying out resource containers in this layout container
            for (var i = 0; i < this.resQ.length; i++) {
                this.resQ[i].setSize({
                    width : this.layoutEl.width,
                    height : this.layoutEl.height
                });
                this.resQ[i].addCls(this.layoutCSS);

                if (this.browser.resourceQueue.selectedRes[this.resQ[i].resource.uri])
                    this.resQ[i].cls = 'resource-view-selected';

                resCt.push(this.resQ[i]);
                this.relayEvents(this.resQ[i], ['select', 'unselect']);
            }
        }
        thisCt.add(resCt);
    },

    noResults : function() {
        this.imgNoResults = Ext.create('Ext.Img', {
            width : 300,
            margin : 0,
            padding : 0,
            src : BQ.Server.url('/core/js/ResourceBrowser/Images/no-results.png'),
        });

        var ct = Ext.create('Ext.panel.Panel', {
            border : false,
            layout : {
                type : 'vbox',
                pack : 'center',
                align : 'center'
            },
        });

        ct.addListener('afterlayout', function(me) {
            me.add(this.imgNoResults)
        }, this, {
            single : true
        });

        this.layout = 'fit';
        this.add(ct);
        // "add" calls doLayout internally so 'fit' will be applied
    },

    getParentSize : function() {
        return this.browser.centerPanel.getSize();
    },

    getVisibleElements : function(direction) {
        var ctSize = this.getParentSize();

        var nRow = Math.floor(ctSize.height / this.layoutEl.outerHeight);
        var nCol = Math.floor(ctSize.width / this.layoutEl.outerWidth);

        if (this.showGroups)
            return this.getNoGroupedElements(this.browser.resourceQueue.getTempQ(nRow * nCol, direction));
        else
            return nRow * nCol;
    },

    getNoGroupedElements : function(resData) {
        var currentGrp, i = 0, noGrp = 1, grpObj = {};
        grpObj[noGrp] = 0;

        while (i < resData.length && !this.containerFull(grpObj)) {
            currentGrp = this.getGroup(resData[i]);

            while (i < resData.length && !this.containerFull(grpObj) && (this.getGroup(resData[i]) == currentGrp)) {
                grpObj[noGrp] = grpObj[noGrp] + 1;
                i++;
            }

            if (this.containerFull(grpObj)) {
                i--;
                break;
            }

            noGrp++;
            grpObj[noGrp] = 0;
        }

        return i;
    },

    getGroup : function(res) {
        var grp = '', tagHash = {}, value;
        var tagRef = res.resource.tags;
        var name, value;

        for (var i = 0; i < tagRef.length; i++)
            tagHash[tagRef[i].name] = tagRef[i].value;

        for (var k = 0; k < this.showGroups.tags.length; k++) {
            name = this.showGroups.tags[k];
            try {
                name = decodeURIComponent(this.showGroups.tags[k]);
            } catch (e) {
                name = this.showGroups.tags[k];
            }

            try {
                value = tagHash[decodeURIComponent(this.showGroups.tags[k])];
            } catch (e) {
                value = tagHash[this.showGroups.tags[k]];
            }
            grp += name + ( value ? ':' + value : '') + ', ';
        }

        return grp.substring(0, grp.length - 2);
    },

    containerFull : function(grpObj) {
        var barHeight = 42;
        var ctSize = this.getParentSize();

        var bodyHeight = ctSize.height - (Ext.Object.getSize(grpObj) * barHeight);

        var nRow = Math.floor(bodyHeight / this.layoutEl.outerHeight);
        var nCol = Math.floor(ctSize.width / this.layoutEl.outerWidth);

        var grpRow = 0;
        for (var i in grpObj)
        grpRow += Math.ceil(grpObj[i] / nCol);

        return (grpRow > nRow);
    },
});

// Compact Layout: Shows resources as thumbnails
Ext.define('Bisque.ResourceBrowser.Layout.Compact', {
    extend : 'Bisque.ResourceBrowser.Layout.Base',

    inheritableStatics : {
        layoutCSS : 'ImageCompact'
    },

    constructor : function() {
        this.callParent(arguments);
        this.layoutEl.imageWidth = 150;
        this.layoutEl.imageHeight = 150;
    }
});

// Card Layout: Shows resources as cards (thumbnail + tag/value pairs)
Ext.define('Bisque.ResourceBrowser.Layout.Card', {
    extend : 'Bisque.ResourceBrowser.Layout.Base',

    inheritableStatics : {
        layoutCSS : 'ImageCard'
    },

    constructor : function() {
        this.callParent(arguments);
        this.layoutEl.imageWidth = 120;
        this.layoutEl.imageHeight = 120;
    }
});

// Full Layout: Shows all the tags assosiated with a resource
Ext.define('Bisque.ResourceBrowser.Layout.Full', {
    extend : 'Bisque.ResourceBrowser.Layout.Base',

    inheritableStatics : {
        layoutCSS : 'ImageFull'
    },

    constructor : function() {
        this.callParent(arguments);

        this.layoutEl.imageHeight = 270;
        this.layoutEl.imageWidth = 270;
    },

    getVisibleElements : function() {
        return 10;
    }
});

// List Layout: Lists the basic information about each resource
Ext.define('Bisque.ResourceBrowser.Layout.List', {
    extend : 'Bisque.ResourceBrowser.Layout.Full',

    inheritableStatics : {
        layoutCSS : 'ResourceList'
    },

    getVisibleElements : function() {
        return 35;
    }
});

// IconList Layout: Lists the basic information about each resource along with an icon
Ext.define('Bisque.ResourceBrowser.Layout.IconList', {
    extend : 'Bisque.ResourceBrowser.Layout.List',

    inheritableStatics : {
        layoutCSS : 'ResourceIconList'
    },

    constructor : function() {
        this.callParent(arguments);

        this.layoutEl.iconHeight = 65;
        this.layoutEl.iconWidth = 65;
    },

    getVisibleElements : function() {
        return 3500;
    }
});

Ext.define('Bisque.ResourceBrowser.Layout.Page', {
    extend : 'Bisque.ResourceBrowser.Layout.Base',

    inheritableStatics : {
        layoutCSS : null
    },
});

// Grid layout: Shows resources in a grid
Ext.define('Bisque.ResourceBrowser.Layout.Grid', {
    extend : 'Bisque.ResourceBrowser.Layout.Base',

    inheritableStatics : {
        layoutCSS : null
    },

    constructor : function() {
        Ext.apply(this, {
            layout : 'fit'
        });
        this.callParent(arguments);
    },

    Init : function(resourceQueue) {
        // if no results were obtained for a given query, show a default no-results message
        if (resourceQueue.length == 0) {
            this.noResults();
            return;
        }

        this.layoutConfig = this.browser.layoutConfig || {};
        this.add(this.getResourceGrid());

        var resource, list = [];
        for (var i = 0; i < resourceQueue.length; i++) {
            resourceQueue[i].layoutMgr = this;
            list.push(resourceQueue[i].getFields());
        }
        this.resourceStore.loadData(list);

        var selModel = this.resourceGrid.getSelectionModel();
        this.resQ = resourceQueue;

        this.resourceGrid.on('afterrender', function(me) {
            var resourceQueue = this.resQ, selModel = this.resourceGrid.getSelectionModel();
            for (var i = 0; i < resourceQueue.length; i++)
                if (this.browser.resourceQueue.selectedRes[resourceQueue[i].resource.uri])
                    selModel.select(i, true);
        }, this, {
            single : true
        });
    },

    getVisibleElements : function(direction) {
        var ctHeight = this.getParentSize().height - 22;
        // height of grid header = 22px
        var noEl = Math.floor(ctHeight / 21) + 1;
        var tempQ = this.browser.resourceQueue.getTempQ(noEl, direction);
        var elHeight, currentHeight = 0;

        for (var i = 0; i < tempQ.length; i++) {
            tempQ[i].layoutMgr = this;
            elHeight = tempQ[i].getFields()[6].height;
            if (currentHeight + elHeight > ctHeight)
                break;
            else
                currentHeight += elHeight;
        }

        return i;
    },

    getResourceGrid : function() {
        this.resourceGrid = Ext.create('Ext.grid.Panel', {
            store : this.getResourceStore(),
            cls: 'bq_browser_grid',
            border : 0,
            multiSelect : true,
            simpleSelect : true,
            listeners : {
                scope : this,
                'itemclick' : function(view, record, item, index) {
                    var resource = record.get('raw');
                    this.browser.msgBus.fireEvent('ResourceSingleClick', resource.resource);
                    this.fireEvent('select', resource);
                },
                'itemdblclick' : function(view, record, item, index) {
                    var resource = record.get('raw');
                    this.browser.msgBus.fireEvent('ResourceDblClick', resource.resource);
                }
            },
            plugins : new Ext.ux.DataTip({
                tpl : '<div>{name}:{value}</div>'
            }),

            columns : {
                items : [{
                    dataIndex : 'icon',
                    menuDisabled : true,
                    sortable : false,
                    align : 'center',
                    maxWidth : this.layoutConfig.colIconWidth || 70,
                    minWidth : 1,
                }, {
                    text : this.layoutConfig.colNameText || 'Name',
                    dataIndex : 'name',
                    sortable : false,
                    align : 'left',
                    flex : 0.4,
                    attribute : 'name',
                    listeners: {
                        scope: this,
                        headerclick: this.onHeaderClick,
                    },
                }, {
                    text : this.layoutConfig.colValueText || 'Owner',
                    dataIndex : 'value',
                    attribute : 'owner',
                    sortable : false,
                    flex : 0.6,
                    listeners: {
                        scope: this,
                        headerclick: this.onHeaderClick,
                    },
                }, {
                    text : 'Type',
                    dataIndex : 'type',
                    attribute : 'type',
                    sortable : false,
                    hidden : true,
                    listeners: {
                        scope: this,
                        headerclick: this.onHeaderClick,
                    },
                }, {
                    text : this.layoutConfig.colDateText || 'Time modified',
                    sortable : false,
                    dataIndex : 'ts',
                    attribute : 'ts',
                    flex : 0.4,
                    listeners: {
                        scope: this,
                        headerclick: this.onHeaderClick,
                    },
                }],
                defaults : {
                    tdCls : 'align',
                    align : 'center',
                    sortable : true,
                    flex : 0.4
                }
            }
        });

        return this.resourceGrid;
    },

    onHeaderClick : function(header, column) {
        var attr = column.attribute,
            command_bar = this.browser.commandBar,
            btn = command_bar.getComponent('btnTS'),
            mnu = btn.menu.getComponent('btn_sort_'+attr);
        if (mnu.checked === false) {
            mnu.setChecked(true);
        } else {
            command_bar.onSortOrder(btn);
        }

        /*var my_grid = this.resourceGrid;;
        setTimeout(function() {
            var c = my_grid.columns[1];
            c.addCls('bq_sorted');
        }, 100);*/
    },

    getResourceStore : function() {
        this.resourceStore = Ext.create('Ext.data.ArrayStore', {
            fields : ['icon', 'name', 'value', 'type', {
                name : 'ts',
                convert : function(value) {
                    var date = Ext.Date.parse(value, BQ.Date.patterns.BisqueTimestamp);
                    return Ext.Date.format(date, BQ.Date.patterns.ISO8601Long);
                }
            }, 'raw']
        });

        return this.resourceStore;
    },
});


// Annotator layout: shows full resource view and a strip with Next and Prev buttons at the bottom
Ext.define('Bisque.ResourceBrowser.Layout.Annotator', {
    extend : 'Bisque.ResourceBrowser.Layout.Base',

    inheritableStatics : {
        layoutCSS : null
    },

    layout: {
        type: 'fit',
        //align: 'stretch',
    },
    cls: 'bq-annotator',


    Init : function(resourceQueue) {
        // if no results were obtained for a given query, show a default no-results message
        if (resourceQueue.length == 0) {
            this.noResults();
            return;
        }

        this.layoutConfig = this.browser.layoutConfig || {};

        /*this.add([{
            xtype: 'container',
            itemId: 'center_viewer',
            flex: 1,
        }, {
            xtype: 'container',
            height: 40,
            layout: {
                type: 'hbox',
                align: 'stretch',
            },
            defaults: {
                scale: 'large',
            },
            items: [{
                xtype: 'button',
                text: 'Previous',
                width: 100,
            }, {
                xtype: 'tbspacer',
                flex: 1,
            }, {
                xtype: 'button',
                text: 'Next',
                width: 100,
            }],
        }]);*/

        //var rq = resourceQueue[0].layoutMgr = this;
        this.loadResource(resourceQueue[0].resource);
    },

    getVisibleElements : function(direction) {
        return 1;
    },

    loadResource : function(resource) {
        this.setLoading('Fetching resource...');
        BQFactory.request({
            uri: resource.uri,
            uri_params: {view : 'deep'},
            cb: callback(this, this.onLoadResource),
            errorcb: callback(this, this.onError)
        });
    },

    onLoadResource : function(resource) {
        this.setLoading(false);
        if (this.editor) {
            this.remove(this.editor, true);
        }

        this.editor = Bisque.ResourceFactoryWrapper.getResource({
            resource: resource,
            layoutKey: Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Page,
        });

        this.add(this.editor);
    },

    onError: function(error) {
        BQApp.setLoading(false);
        BQ.ui.error('Error fetching resource: <br>' + error.message);
    },

});

