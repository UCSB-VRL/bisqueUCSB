Bisque.ResourceBrowser.ResourceQueue = function() {
};
Bisque.ResourceBrowser.ResourceQueue.prototype = new Array;

Ext.apply(Bisque.ResourceBrowser.ResourceQueue.prototype, {
    init : function(config) {
        Ext.apply(this, {
            browser : config.browser,
            layoutKey : config.browser.layoutKey,
            msgBus : config.browser.msgBus,
            uri : config.uri,
            callBack : config.callBack,

            prefetchFactor : 1, // (prefetchFactor X visibileElements) elements are prefetched
            dataLimit : 350, // Number of resource URIs fetched
            noUnloadClicks : 5, // Cache of the opposite direction will be unloaded after these many clicks in a given direction (right or left)

            hasMoreData : {
                left : true,
                right : true
            },
            loading : {
                left : false,
                right : false
            },
            dataHash : {},
            list : [],
            selectedRes : {},
            indRight : [], //Indexes of prefetched items on the right - prefetch cache
            indLeft : [], //Indexes of prefetched items on the left - prefetch cache
            dbOffset : {
                left : 0,
                center : parseInt(config.uri.offset),
                right : 0
            },
            currentDirection : 1, // 1=Right, 0=Left

            clicks : {
                right : 0,
                left : 0
            },
            rqOffset : 0
        });

        this.loadData();
    },

    loadData : function() {
        this.dbOffset.left = ((this.dbOffset.center - this.dataLimit) >= 0) ? this.dbOffset.center - this.dataLimit : 0;

        var uri = this.uri;
        uri.offset = this.dbOffset.left;
        uri.limit = 2 * this.dataLimit;

        BQFactory.request({
            uri : this.generateURI(uri),
            cb : callback(this, 'dataLoaded'),
            cache : false
        });
    },

    dataLoaded : function(resourceData) {
        this.rqOffset = this.dbOffset.center - this.dbOffset.left;
        this.dbOffset.right = this.dbOffset.left + resourceData.children.length;

        for (var i = 0; i < resourceData.children.length; i++)
            this.push(Bisque.ResourceFactory.getResource({
                resource : resourceData.children[i],
                layoutKey : this.layoutKey,
                msgBus : this.msgBus,
                resQ : this,
                browser : this.browser
            }));

        this.hasMoreData.left = (this.dbOffset.left > 0) ? true : false;
        this.hasMoreData.right = ((this.dbOffset.right - this.dbOffset.center) >= this.dataLimit) ? true : false;

        this.callBack();
    },

    loadDataRight : function(loaded, data) {
        if (!loaded) {
            this.loading.right = true;
            var uri = this.browser.getURIFromState();
            uri.offset = this.dbOffset.right;
            uri.limit = this.dataLimit;

            BQFactory.request({
                uri : this.generateURI(uri),
                cb : callback(this, 'loadDataRight', true),
                cache : false
            });

            this.browser.commandBar.getComponent('btnRight').setDisabled(true);
            this.browser.commandBar.getComponent('btnRight').setLoading({
                msg : ''
            });
        } else {
            this.browser.commandBar.getComponent('btnRight').setDisabled(false);
            this.browser.commandBar.getComponent('btnRight').setLoading(false);

            this.dbOffset.right += data.children.length;
            for (var i = 0; i < data.children.length; i++)
                this.push(Bisque.ResourceFactory.getResource({
                    resource : data.children[i],
                    layoutKey : this.layoutKey,
                    msgBus : this.msgBus,
                    resQ : this,
                    browser : this.browser
                }));

            this.hasMoreData.right = (data.children.length == this.dataLimit) ? true : false;
            this.loading.right = false;
            this.browser.changeLayoutThrottled(this.browser.layoutKey, 'Right');
        }
    },

    loadDataLeft : function(loaded, data) {
        if (!loaded) {
            this.loading.left = true;
            var oldLeft = this.dbOffset.left;
            this.dbOffset.left = ((this.dbOffset.left - this.dataLimit) >= 0) ? this.dbOffset.left - this.dataLimit : 0;

            var uri = this.browser.getURIFromState();
            uri.offset = this.dbOffset.left;
            uri.limit = oldLeft - this.dbOffset.left;

            BQFactory.request({
                uri : this.generateURI(uri),
                cb : callback(this, 'loadDataLeft', true),
                cache : false
            });

            this.browser.commandBar.getComponent('btnLeft').setDisabled(true);
            this.browser.commandBar.getComponent('btnLeft').setLoading({
                msg : ''
            });
        } else {
            this.browser.commandBar.getComponent('btnLeft').setDisabled(false);
            this.browser.commandBar.getComponent('btnLeft').setLoading(false);

            for (var i = 0; i < data.children.length; i++)
                this.unshift(Bisque.ResourceFactory.getResource({
                    resource : data.children[i],
                    layoutKey : this.layoutKey,
                    msgBus : this.msgBus,
                    resQ : this,
                    browser : this.browser
                }));

            this.hasMoreData.left = (data.children.length == this.dataLimit) ? true : false;
            this.loading.left = false;
            this.rqOffset = this.rqOffset + data.children.length;

            this.browser.changeLayoutThrottled(this.browser.layoutKey, 'Left');
        }
    },

    loadPrev : function(visLimit) {
        this.currentDirection = 0;

        if (this.rqOffset - visLimit > 0)
            this.rqOffset -= visLimit;
        else
            this.rqOffset = 0;

        this.clicks.left += 1;
        this.unloadRight();
    },

    loadNext : function(visLimit) {
        var noEl = visLimit || this.visLimit;
        this.currentDirection = 1;

        if (this.rqOffset + noEl < this.length)
            this.rqOffset += noEl;

        this.clicks.right += 1;
        this.unloadLeft();
    },

    prefetchPrev : function(layoutMgr) {
        //var prefetchFactor=(this.currentDirection==0)?this.prefetchFactor+1:this.prefetchFactor;
        var prefetchFactor = this.prefetchFactor;

        if (this.rqOffset - prefetchFactor * this.visLimit > 0)
            for ( i = this.rqOffset - prefetchFactor * this.visLimit; i < this.rqOffset; i++) {
                this[i].prefetch(layoutMgr);
                this.indLeft.push(this[i].resource.uri);
            }
        else {
            for ( i = 0; i < this.rqOffset; i++) {
                this[i].prefetch(layoutMgr);
                this.indLeft.push(this[i].resource.uri);
            }

            if (this.hasMoreData.left && !this.loading.left)
                this.loadDataLeft(false);
        }
    },

    prefetchNext : function(layoutMgr) {
        //var prefetchFactor=(this.currentDirection==1)?this.prefetchFactor+1:this.prefetchFactor;
        var prefetchFactor = this.prefetchFactor;

        if (this.rqOffset + (prefetchFactor + 1) * this.visLimit < this.length)
            for ( i = this.rqOffset; i <= this.rqOffset + (prefetchFactor + 1) * this.visLimit; i++) {
                this[i].prefetch(layoutMgr);
                this.indRight.push(this[i].resource.uri);
            }
        else {
            for ( i = this.rqOffset; i < this.length; i++) {
                this[i].prefetch(layoutMgr);
                this.indRight.push(this[i].resource.uri);
            }

            if (this.hasMoreData.right && !this.loading.right)
                this.loadDataRight(false);
        }
    },

    unloadRight : function() {
        if (this.clicks.left == this.noUnloadClicks) {
            //console.time("unloadRight");
            this.clicks.left = 0;
            var len = Math.floor(this.indRight.length / 2)
            for (var i = 0; i < len; i++)
                this.dataHash[this.indRight.shift()] = {};

            //console.timeEnd("unloadRight");
        }
    },

    unloadLeft : function() {
        if (this.clicks.right == this.noUnloadClicks) {
            //console.time("unloadLeft");
            this.clicks.right = 0;
            var len = Math.floor(this.indLeft.length / 2);
            for (var i = 0; i < len; i++)
                this.dataHash[this.indLeft.shift()] = {};

            //console.timeEnd("unloadLeft");
        }
    },

    prefetch : function(layoutMgr) {
        //console.time("prefetch");

        this.list = this.slice(this.rqOffset, this.rqOffset + this.visLimit);

        for (var i = 0; i < this.list.length; i++) {
            this.splice(i + this.rqOffset, 1, Bisque.ResourceFactory.getResource({
                resource : this[i + this.rqOffset].resource,
                layoutKey : this.layoutKey,
                msgBus : this.msgBus,
                resQ : this,
                browser : this.browser
            }));
            this.list[i].prefetch(layoutMgr);
        }

        if (this.currentDirection)
            window.setTimeout(Ext.bind(this.prefetchNext, this, [layoutMgr]), 400);
        else
            window.setTimeout(Ext.bind(this.prefetchPrev, this, [layoutMgr]), 400);

        //console.timeEnd("prefetch");
        return this.list;
    },

    getMainQ : function(visLimit, layoutMgr) {
        this.visLimit = visLimit;
        // Browser state change - reflect offset change
        this.browser.browserState['offset'] = this.rqOffset + this.dbOffset.left;
        return this.prefetch(layoutMgr);
    },

    getTempQ : function(visLimit, direction) {
        var leftOffset = this.rqOffset, tmp;

        if (direction == 'left') {
            leftOffset = ((leftOffset - visLimit) > 0) ? (leftOffset - visLimit) : 0;
            return this.slice(leftOffset, this.rqOffset).reverse();
        } else
            return this.slice(leftOffset, leftOffset + visLimit);
    },

    changeLayout : function(layoutObj) {
        //console.time("resourceQueue - changeLayout");

        if (this.layoutKey != layoutObj.key) {
            this.layoutKey = layoutObj.key;
            this.dataHash = {};

            for ( i = 0; i < this.length; i++)
                this.splice(i, 1, Bisque.ResourceFactory.getResource({
                    resource : this[i].resource,
                    layoutKey : this.layoutKey,
                    msgBus : this.msgBus,
                    resQ : this,
                    browser : this.browser
                }));
        }

        //console.timeEnd("resourceQueue - changeLayout");
    },

    /* Utility functions */
    getStatus : function() {
        var left = false, right = false, visLimit = this.visLimit;

        if (this.rqOffset == 0 && this.dbOffset.left == 0)
            left = true;
        if ((this.rqOffset + visLimit >= this.length) && !this.hasMoreData.right) {
            right = true;
            visLimit = this.length - this.rqOffset;
        }

        var st = Ext.String.format('Showing {0}-{1} of {2} {3}', this.dbOffset.left + this.rqOffset + (this.list.length ? 1 : 0), this.dbOffset.left + this.rqOffset + this.list.length, ((this.hasMoreData.left || this.hasMoreData.right) ? 'at least ' : 'total '), this.dbOffset.left + this.length);

        var sliderSt = {
            left : this.hasMoreData.left,
            right : this.hasMoreData.right,
            min : this.dbOffset.left + 1,
            max : this.dbOffset.left + this.length,
            value : this.dbOffset.left + this.rqOffset + 1,
            increment: this.visLimit,
        };

        return {
            status : st,
            left : left,
            right : right,
            sliderSt : sliderSt,
            loading : this.loading
        };
    },

    generateURI : function(uriObj) {
        var uri = '', baseURL = uriObj.baseURL;
        delete uriObj.baseURL;

        function unquote(string) {
            return (string.length < 2) ? string : string.substring(1, string.length - 1);
        }

        if (uriObj.tag_order) {
            var tagValuePair = uriObj.tag_order.split(','), tags = [], values = [], nextPair;

            for (var i = 0; i < tagValuePair.length; i++) {
                nextPair = tagValuePair[i].split(':');

                var m = tagValuePair[i].match(/"@(\w+)":(asc|desc|ASC|DESC)/);
                //if (nextPair[0].indexOf('@')<0)
                if (!m || m.length!==3) {
                    tags.push(unquote(nextPair[0]));
                }
            }

            if (tags.length>0)
                uriObj.view = tags.join(',');
        }

        for (var param in uriObj) {
            var v = uriObj[param];
            if (typeof v === 'undefined' || v === null || v === '')
                delete uriObj[param];
            else
                uri += '&' + param + '=' + v;
        }

        uri = (uri == '' ? uri : uri.substring(1, uri.length));
        return Ext.urlAppend(baseURL, uri);
    },

    uriStateToString : function(uriObj) {
        var uri = '', baseURL = uriObj.baseURL;
        delete uriObj.baseURL;

        for (var param in uriObj)
        uri += '&' + param + '=' + uriObj[param];

        var path = window.location.href.substr(0, window.location.href.lastIndexOf(window.location.search));

        if (path[path.length - 1] != '?')
            path = path + '?';

        return path + 'dataset=' + baseURL + uri + '&layout=' + this.layoutKey;
    },

    // Stores resource-specific data in a hash table (key on uri)
    storeMyData : function(uri, tag, value) {
        if (!Ext.isDefined(this.dataHash[uri]))
            this.dataHash[uri] = {};

        this.dataHash[uri][tag] = value;
    },

    // Retrieves resource-specific data (key on uri)
    getMyData : function(uri, tag) {
        if (Ext.isDefined(this.dataHash[uri]))
            if (Ext.isDefined(this.dataHash[uri][tag]))
                return this.dataHash[uri][tag];
        return 0;
    },

    find : function(uri) {
        var currentResource = false;
        for (var i = 0; i < this.length; i++) {
            if (this[i].resource.uri == uri) {
                currentResource = this[i].resource;
                break;
            }
        }
        return currentResource;
    }
});
