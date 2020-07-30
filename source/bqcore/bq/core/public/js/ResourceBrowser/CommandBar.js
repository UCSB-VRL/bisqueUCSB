Ext.define('Bisque.ResourceBrowser.CommandBar', {
    extend : 'Ext.toolbar.Toolbar',

    constructor : function(configOpts) {
        this.viewMgr = configOpts.browser.viewMgr;
        this.slider = new Bisque.Misc.Slider({
            hidden : this.viewMgr.cBar.slider
        });

        Ext.apply(this, {
            browser : configOpts.browser,
            taqQuery : configOpts.browser.browserParams.tagQuery,

            msgBus : configOpts.browser.msgBus,
            westPanel : configOpts.browser.westPanel,
            organizerCt : configOpts.browser.organizerCt,
            datasetCt : configOpts.browser.datasetCt,
            hidden : configOpts.browser.viewMgr.cBar.cbar,

            layout : {
                type : 'hbox',
                align : 'middle'
            },
            items : [{
                xtype : 'tbspacer',
                width : 6
            }, {
                xtype : 'textfield',
                tooltip : 'Enter a tag query here',
                itemId : 'searchBar',
                flex : 7,
                scale : 'large',
                height : 25,
                boxMinWidth : 100,
                hidden : this.viewMgr.cBar.searchBar,
                value : configOpts.tagQuery,
                listeners : {
                    specialkey : {
                        fn : function(field, e) {
                            if (e.getKey() == e.ENTER)
                                this.btnSearch();
                        },

                        scope : this
                    },
                    scope : this,
                    focus : function(c) {
                        var tip = Ext.create('Ext.tip.ToolTip', {
                            target : c.el,
                            anchor : 'top',
                            minWidth : 500,
                            width : 500,
                            autoHide : true,
                            dismissDelay : 20000,
                            shadow : true,
                            autoScroll : true,
                            loader : {
                                url : '/core/html/querying.html',
                                renderer : 'html',
                                autoLoad : true
                            },
                        });
                        tip.show();
                    },
                }
            }, {
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/search.png'),
                hidden : this.viewMgr.cBar.searchBar,
                tooltip : 'Search',
                scale : 'large',
                handler : this.btnSearch,
                scope : this
            }, {
                xtype : 'tbseparator',
                hidden : this.viewMgr.cBar.searchBar
            }, {
                itemId : 'btnThumb',
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/thumb.png'),
                hidden : this.viewMgr.cBar.btnLayoutThumb,
                tooltip : 'Thumbnail view',
                toggleGroup : 'btnLayout',
                scale : 'large',
                handler : this.btnLayoutClick,
                padding : '3 0 3 0',
                scope : this
            }, {
                itemId : 'btnGrid',
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/grid.png'),
                hidden : this.viewMgr.cBar.btnLayoutGrid,
                tooltip : 'Grid view',
                scale : 'large',
                toggleGroup : 'btnLayout',
                handler : this.btnLayoutClick,
                padding : '3 0 3 0',
                scope : this
            }, {
                itemId : 'btnCard',
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/card.png'),
                hidden : this.viewMgr.cBar.btnLayoutCard,
                tooltip : 'Annotator view',
                scale : 'large',
                toggleGroup : 'btnLayout',
                handler : this.btnLayoutClick,
                padding : '3 0 3 0',
                scope : this
            }, {
                itemId : 'btnFull',
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/full.png'),
                hidden : this.viewMgr.cBar.btnLayoutFull,
                tooltip : 'Details view',
                scale : 'large',
                toggleGroup : 'btnLayout',
                handler : this.btnLayoutClick,
                padding : '3 0 3 0',
                scope : this
            }, '->', {
                itemId : 'btnRefresh',
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/refresh.png'),
                tooltip : 'Refresh browser',
                hidden : this.viewMgr.cBar.btnRefresh,
                scale : 'large',
                handler : this.btnRefresh,
                scope : this
            }, {
                itemId : 'btnActivate',
                //icon : BQ.Server.url('/core/js/ResourceBrowser/Images/activate.png'),
                text: 'Edit',
                tooltip : 'Switch to editing mode',
                state : 'ACTIVATE',
                hidden : this.viewMgr.cBar.btnActivate,
                scale : 'large',
                handler : this.btnActivate,
                scope : this,
                cls: 'bq-btn-edit',
            }, {
                xtype: 'splitbutton',
                itemId : 'btnTS',
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/desc.png'),
                tooltip : 'Sorting by time modified in descending order',
                hidden : this.viewMgr.cBar.btnTS,
                sortOrder : 'DESC',
                sortAttribute : '@ts',
                scale : 'large',
                handler : this.onSortOrder,
                scope : this,
                menu : {
                    cls: 'browser_toolbar_menu',
                    items : [{
                        text : 'Name',
                        itemId : 'btn_sort_name',
                        checked: false,
                        group: 'sorting',
                        sortAttribute : '@name',
                        scope: this,
                        checkHandler: this.onSortAttribute,
                    }, {
                        text : 'Time created',
                        itemId : 'btn_sort_created',
                        checked: false,
                        group: 'sorting',
                        sortAttribute : '@created',
                        scope: this,
                        checkHandler: this.onSortAttribute,
                    }, {
                        text : 'Time modified',
                        itemId : 'btn_sort_ts',
                        checked: true,
                        group: 'sorting',
                        sortAttribute : '@ts',
                        scope: this,
                        checkHandler: this.onSortAttribute,
                    }, {
                        text : 'Permission',
                        itemId : 'btn_sort_permission',
                        checked: false,
                        group: 'sorting',
                        sortAttribute : '@permission',
                        scope: this,
                        checkHandler: this.onSortAttribute,
                    }, {
                        text : 'Owner',
                        itemId : 'btn_sort_owner',
                        checked: false,
                        group: 'sorting',
                        sortAttribute : '@owner',
                        scope: this,
                        checkHandler: this.onSortAttribute,
                    }, {
                        text : 'Type',
                        itemId : 'btn_sort_type',
                        checked: false,
                        group: 'sorting',
                        sortAttribute : '@type',
                        scope: this,
                        checkHandler: this.onSortAttribute,
                    }],
                },
            }, {
                xtype : 'tbseparator',
                hidden : this.viewMgr.cBar.btnTS
            }, {
                tooltip : 'Previous page',
                itemId : 'btnLeft',
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/left.png'),
                hidden : this.viewMgr.cBar.btnLeft,
                scale : 'large',
                padding : '0 1 0 0',
                handler : function(me) {
                    //me.stopAnimation();
                    //me.el.frame("#B0CEF7");
                    this.browser.resourceQueue.loadPrev(this.browser.layoutMgr.getVisibleElements('left'/*direction:left*/));
                    this.browser.changeLayoutThrottled(this.browser.layoutKey, 'Left');
                },
                scope : this
            }, {
                tooltip : 'Next page (space-bar)',
                itemId : 'btnRight',
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/right.png'),
                hidden : this.viewMgr.cBar.btnRight,
                scale : 'large',
                padding : '0 0 0 1',
                handler : function(me) {
                    //me.stopAnimation();
                    //me.el.frame("#B0CEF7");
                    this.browser.resourceQueue.loadNext();
                    this.browser.changeLayoutThrottled(this.browser.layoutKey, 'Right');
                },

                scope : this
            }, this.slider, {
                xtype : 'tbseparator',
                hidden : this.viewMgr.cBar.btnGear
            }, {
                icon : BQ.Server.url('/core/js/ResourceBrowser/Images/gear.png'),
                hidden : this.viewMgr.cBar.btnGear,
                itemId : 'btnGear',
                scale : 'large',
                tooltip : 'Options',
                menu : {
                    cls: 'browser_toolbar_menu',
                    items : [{
                        xtype: 'menucheckitem',
                        text : 'Show my data',
                        itemId : 'btn_show_owner',
                        checked : true,
                        value: 'owner',
                        //group: 'show',
                        scope: this,
                        checkHandler: this.onWpublicCheck,
                    }, {
                        xtype: 'menucheckitem',
                        text : 'Show shared data',
                        itemId : 'btn_show_shared',
                        checked : false,
                        value: 'shared',
                        //group: 'show',
                        scope: this,
                        checkHandler: this.onWpublicCheck,
                    }, {
                        xtype: 'menucheckitem',
                        text : 'Show public data',
                        itemId : 'btn_show_public',
                        checked : false,
                        value: 'public',
                        //group: 'show',
                        scope: this,
                        checkHandler: this.onWpublicCheck,
                    }, /*{
                        text : 'Include published resources',
                        itemId : 'btnWpublic',
                        checked : false,
                        listeners : {
                            scope: this,
                            checkchange : {
                                fn : function(chkbox, value) {
                                    var uri = {
                                        offset : 0
                                    };
                                    configOpts.browser.browserParams.wpublic = value;
                                    configOpts.browser.msgBus.fireEvent('Browser_ReloadData', uri);
                                    if (this.organizerCt)
                                        this.organizerCt.reset();
                                },
                                scope : this
                            }
                        }
                    },*/ '-', {
                        text : 'Organize',
                        itemId : 'btnOrganize',
                        icon : BQ.Server.url('/core/js/ResourceBrowser/Images/organize.png'),
                        hidden : true,
                        handler : this.btnOrganizerClick,
                        scope : this
                    }, {
                        text : 'Datasets',
                        icon : BQ.Server.url('/core/js/ResourceBrowser/Images/datasets.png'),
                        hidden : true, //this.viewMgr.cBar.btnDataset,
                        handler : this.btnDatasetClick,
                        scope : this
                    }, {
                        text : 'Link',
                        icon : BQ.Server.url('/core/js/ResourceBrowser/Images/link.png'),
                        hidden : this.viewMgr.cBar.btnLink,
                        handler : function() {
                            var val = configOpts.browser.resourceQueue.uriStateToString(configOpts.browser.getURIFromState());

                            Ext.Msg.show({
                                title : 'Link to this view',
                                msg : 'Bisque URL:',
                                modal : true,
                                prompt : true,
                                width : 500,
                                buttons : Ext.MessageBox.OK,
                                icon : Ext.MessageBox.INFO,
                                value : val
                            });
                        }
                    }, '-', {
                        text: 'Full-screen',
                        //icon: BQ.Server.url('/core/js/ResourceBrowser/Images/link.png'),
                        hidden: this.viewMgr.cBar.btnFullscreen,
                        scope: this,
                        handler: this.onFullScreen,
                    }]
                }
            }, {
                xtype : 'tbspacer',
                flex : 0.2,
                maxWidth : 20
            }]
        });

        Bisque.ResourceBrowser.CommandBar.superclass.constructor.apply(this, arguments);

        this.manageEvents();
    },

    manageEvents : function() {
        this.msgBus.on('SearchBar_Query', function(query) {
            this.getComponent('searchBar').setValue(decodeURIComponent(query));
        }, this);

        this.mon(this, 'afterlayout', this.toggleLayoutBtn, this);

        this.slider.on('buttonClick', Ext.Function.createThrottled(function(newOffset) {
            var oldOffset = this.browser.resourceQueue.rqOffset + this.browser.resourceQueue.dbOffset.left;
            var diff = newOffset - oldOffset;

            if (diff > 0) {
                this.browser.resourceQueue.loadNext(diff);
                this.browser.changeLayoutThrottled(this.browser.layoutKey, 'Right');
            } else if (diff < 0) {
                this.browser.resourceQueue.loadPrev(-1 * diff);
                this.browser.changeLayoutThrottled(this.browser.layoutKey, 'Left');
            }
        }, 400, this), this);

    },

    btnRefresh : function() {
        if (this.organizerCt && this.organizerCt.isVisible()) {
            this.organizerCt.reset();
        }
        if (this.viewMgr.cBar.btnRefresh_only_update) {
            this.browser.msgBus.fireEvent('Browser_ReloadData', {});
        } else {
            this.browser.msgBus.fireEvent('Browser_ReloadData', {
                offset : 0,
                tag_query : '',
                tag_order : '',
            });
        }
        var t = this.westPanel.queryById('files');
        if (t && t.isVisible()) {
            t.reset();
        }
    },

    btnActivate : function(btn) {
        if (btn.state == 'ACTIVATE') {
            btn.setIcon(BQ.Server.url('/core/js/ResourceBrowser/Images/select.png'));
            btn.state = 'SELECT';
            btn.setTooltip('Switch to view mode');
            btn.addCls('active');
        } else {
            btn.setIcon(BQ.Server.url('/core/js/ResourceBrowser/Images/activate.png'));
            btn.state = 'ACTIVATE';
            btn.setTooltip('Switch to editing mode');
            btn.removeCls('active');
        }
        this.browser.selectState = btn.state;
        this.browser.fireEvent('SelectMode_Change', btn.state);
    },

    btnTSSetState : function(tagOrder) {
        try {
            var m = tagOrder.match(/"@(\w+)":(asc|desc|ASC|DESC)/),
                attr = m[1] || 'ts',
                ord = m[2].toUpperCase() || 'DESC',
                btn = this.getComponent('btnTS'),
                mnu = btn.menu.getComponent('btn_sort_'+attr);
        } catch (e) {
            return;
        }

        if (mnu) {
            mnu.setChecked(true);
            btn.sortAttribute = mnu.sortAttribute;
            btn.sortAttributeText = mnu.text.toLowerCase();
        }
        btn.sortOrder = ord;
        if (ord === 'DESC')
            btn.setIcon(BQ.Server.url('/core/js/ResourceBrowser/Images/desc.png'));
        else
            btn.setIcon(BQ.Server.url('/core/js/ResourceBrowser/Images/asc.png'));

        btn.setTooltip(Ext.String.format('Sorting by {0} in {1}cending order', btn.sortAttributeText.toLowerCase(), btn.sortOrder.toLowerCase()));
    },

    onSortAttribute : function(m) {
        var btn = this.getComponent('btnTS');
        if (btn.sortAttribute === m.sortAttribute) return;
        btn.sortAttribute = m.sortAttribute;
        btn.sortAttributeText = m.text.toLowerCase();
        this.updateSortOrder(btn);
    },

    onSortOrder : function(btn) {
        if (btn.sortOrder === 'ASC')
            btn.sortOrder = 'DESC';
        else
            btn.sortOrder = 'ASC';
        this.updateSortOrder(btn);
    },

    updateSortOrder : function(btn) {
        var tagOrder = (this.browser.browserState.tag_order || '').split(',');

        // remove attributes
        tagOrder = tagOrder.filter(function(item) {
            var m = item.match(/"@(\w+)":(asc|desc|ASC|DESC)/);
            return !m || m.length!==3;
            //return item.indexOf('@')<0;
        });

        tagOrder.push(Ext.String.format('"{0}":{1}', btn.sortAttribute, btn.sortOrder.toLowerCase()));
        tagOrder = tagOrder.join(',');
        this.btnTSSetState(tagOrder);

        this.msgBus.fireEvent('Browser_ReloadData', {
            offset : 0,
            tag_order : tagOrder,
        });
    },

    btnSearch : function() {
        var uri = {
            offset : 0,
            tag_query : this.getComponent('searchBar').getValue()
        };
        this.msgBus.fireEvent('Browser_ReloadData', uri);
    },

    btnDatasetClick : function() {
        this.westPanel.removeAll(false);

        this.datasetCt = this.datasetCt || new Bisque.ResourceBrowser.DatasetManager({
            parentCt : this.westPanel,
            browser : this.browser,
            msgBus : this.msgBus
        });

        this.westPanel.setWidth(this.datasetCt.width).show().expand();
        this.westPanel.add(this.datasetCt);
        this.westPanel.doComponentLayout(null, null, true);
    },

    btnOrganizerClickTreeNew : function(reload) {
        this.westPanel.setWidth(300).show().expand();
        if (!this.organizerCt) {
            this.organizerCt = Ext.create('BQ.tree.organizer.Panel', {
                title: 'Organizer',
                itemId: 'organizer',
                browserParams : this.browser.browserParams,
                url: this.browser.browserState['baseURL'],
                listeners : {
                    scope : this,
                    selected : function(url, organizer) {
                        this.msgBus.fireEvent('Browser_ReloadData', {
                            baseURL : organizer.getUrl(),
                            offset: 0,
                            tag_query: organizer.getQuery(),
                            tag_order: organizer.getOrder(),
                        });
                    },
                },
            });
            this.westPanel.add(this.organizerCt);
        }
        this.westPanel.setActiveTab(0);
    },

    btnOrganizerClickFiles : function(reload) {
        if (this.filesCt) return;
        this.westPanel.setWidth(300).show().expand();
        //this.westPanel.queryById('files').removeAll(false);
        this.filesCt = this.westPanel.add({
            xtype: 'bq-tree-files-panel',
            itemId: 'files',
            title: 'Files',
            tag_order : this.browser.browserParams.tagOrder,
            listeners : {
                scope : this,
                selected : function(url, files) {
                    this.msgBus.fireEvent('Browser_ReloadData', {
                        baseURL : url.slice(-1)!=='/' ? url+'/value' : url+'value',
                        offset : 0,
                        tag_query : '',
                        tag_order : files.tag_order,
                        //wpublic : false,
                    });
                }
            },
        });
    },

    btnOrganizerClick : function(reload) {
        // dima: choose type of organizer here
        //this.btnOrganizerClickTree(reload);
        this.btnOrganizerClickTreeNew(reload);
        //this.btnOrganizerClickOriginal(reload);
        if (this.browser.dataset && this.browser.dataset instanceof BQDataset)
            return;
        this.btnOrganizerClickFiles(reload);
    },

    btnLayoutClick : function(item) {
        switch (item.itemId) {
            case 'btnThumb' :
                this.browser.changeLayoutThrottled(Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Compact);
                break;
            case 'btnCard' :
                //this.browser.changeLayoutThrottled(Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Card);
                this.browser.changeLayoutThrottled(Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Annotator);
                break;
            case 'btnGrid' :
                this.browser.changeLayoutThrottled(Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Grid);
                break;
            case 'btnFull' :
                this.browser.changeLayoutThrottled(Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Full);
                break;
        }
    },

    toggleLayoutBtn : function() {
        switch(this.browser.layoutKey) {
            case Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Compact :
                this.getComponent('btnThumb').toggle(true, false);
                break;
            //case Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Card :
            case Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Annotator :
                this.getComponent('btnCard').toggle(true, false);
                break;
            case Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Grid :
                this.getComponent('btnGrid').toggle(true, false);
                break;
            case Bisque.ResourceBrowser.LayoutFactory.LAYOUT_KEYS.Full :
                this.getComponent('btnFull').toggle(true, false);
                break;
        }
    },

    btnActivateSetState : function(state) {
        var btn = this.getComponent('btnActivate');
        btn.state = (state == 'ACTIVATE') ? 'SELECT' : 'ACTIVATE';
        this.btnActivate(btn);
    },

    btnSearchSetState : function(tagQuery) {
        this.getComponent('searchBar').setValue(decodeURIComponent(tagQuery));
    },

    setStatus : function(status) {
        if (this.slider.rendered)
            this.slider.setStatus(status);
    },

    applyPreferences : function() {
        if (this.rendered)
            this.toggleLayoutBtn();
        this.setResourceVisibilityUI(this.browser.browserParams.wpublic);
    },

    onWpublicCheck : function(chkbox, value) {
        var uri = {
            offset : 0
        };
        this.browser.browserParams.wpublic = this.getResourceVisibilityUI();
        this.browser.msgBus.fireEvent('Browser_ReloadData', uri);
        if (this.organizerCt)
            this.organizerCt.reset();
        //BQ.Preferences.set('user', 'ResourceBrowser/Browser/Default visibility', this.browser.browserParams.wpublic);
    },

    setResourceVisibilityUI: function(v) {
        var btnGear = this.getComponent('btnGear');
        if (!btnGear) return;
        var menu = this.getComponent('btnGear').menu;
        v = String(v) || '';
        //menu.getComponent('btnWpublic').setChecked(this.browser.browserParams.wpublic, true);
        if (v.indexOf('owner')>=0 || v === 'false' || v === '0' || v === 'true' || v === '1')
            menu.getComponent('btn_show_owner').setChecked(true);
        if (v.indexOf('shared')>=0 || v === 'false' || v === '0' || v === 'true' || v === '1')
            menu.getComponent('btn_show_shared').setChecked(true);
        if (v.indexOf('public')>=0 || v === 'true' || v === '1')
            menu.getComponent('btn_show_public').setChecked(true);
    },

    getResourceVisibilityUI: function() {
        var menu = this.getComponent('btnGear').menu,
            v = [],
            c = null,
            elems = {'btn_show_owner':null, 'btn_show_shared':null, 'btn_show_public':null};

        for (var e in elems) {
           c = menu.getComponent(e);
           if (c.checked)
               v.push(c.value);
        }
        return v.join(',');
    },

    onFullScreen: function() {
        this.browser.doFullScreen();
    },

});
