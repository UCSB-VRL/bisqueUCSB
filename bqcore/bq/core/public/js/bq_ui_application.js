/////////////////////////////////////////
// Bisque service and access

Ext.require(['Ext.util.Observable']);
Ext.require(['Ext.container.Viewport']);

Ext.define('BQ.Server', {
    //extend: 'Ext.util.Observable',
    singleton: true,

    title: 'BisQue',
    root: '/',
    baseCSSPrefix: 'bq-',

    url : function (base, params) {
        if (this.root && this.root !== "/")
            return this.root + base;
        return base;
    },
});

// instantiate a global variable, it might get owerwritten later
//var bq = Ext.create('BQ.Server');

Ext.namespace('BQ.Date');
BQ.Date.patterns = {
    BisqueTimestamp:'Y-m-dTH:i:s.uZ',
    ISO8601Long:"Y-m-d H:i:s",
    ISO8601Short:"Y-m-d",
    ShortDate: "n/j/Y",
    LongDate: "l, F d, Y",
    FullDateTime: "l, F d, Y g:i:s A",
    MonthDay: "F d",
    ShortTime: "g:i A",
    LongTime: "g:i:s A",
    SortableDateTime: "Y-m-d\\TH:i:s",
    UniversalSortableDateTime: "Y-m-d H:i:sO",
    YearMonth: "F, Y"
};

//--------------------------------------------------------------------------------------
// BQ.resources
//--------------------------------------------------------------------------------------

Ext.namespace('BQ.resources');

BQ.resources.system = {
    user: null,
    module: null,
    service: null,
    system: null,
    store: null
};

BQ.resources.required = {
    dataset: null,
    template: null
};

BQ.resources.ignore = {
    mex: null,
    user: null,
    image: null,
    module: null,
    service: null,
    system: null,
    file: null
};

BQ.resources.preferred = {
    image: null,
    dataset: null,
    template: null,
    mex: null,
    file: null
};

BQ.resources.known = {
    user: null,
    module: null,
    service: null,
    system: null,
    store: null,
    dataset: null,
    template: null,
    mex: null,
    image: null,
    file: null,
    image: null,
};

BQ.resources.all = BQ.resources.known;

//--------------------------------------------------------------------------------------
// BQ.Application
// Events:
//   signedin
//   signedout
//   gotuser
//   nouser
//   userListLoaded
//--------------------------------------------------------------------------------------

Ext.define('BQ.Application', {
    extend: 'Ext.util.Observable',

    constructor: function(config) {
        config = config || {};
        this.callParent();

        config.config = config.config || {};
        this.onReady();
        this.main = Ext.create('BQ.Application.Window', config.config);

        BQSession.initialize_session('', {
            onsignedin: callback(this, this.onSignedIn),
            onsignedout: callback(this, this.onSignedOut),
            ongotuser: callback(this, this.onGotUser),
            onnouser: callback(this, this.onNoUser),
        });

        return this;
    },

    onReady : function()
    {
        // Load user information for all users.
        this.userList = {}; //so there is a userList even if the users have not be populated
        BQFactory.request({
            uri :   BQ.Server.url('/data_service/user?view=deep&wpublic=true'),
            cb  :   Ext.bind(userInfoLoaded, this)
        });

        function userInfoLoaded(data)
        {
            //this.userList = {};

            for (var i=0; i<data.children.length;i++)
                this.userList[data.children[i].uri] = data.children[i];

            this.fireEvent('userListLoaded');
        }
    },

    onSignedIn: function() {
        this.session = BQSession.current_session;
        this.fireEvent( 'signedin', BQSession.current_session);
    },

    onSignedOut: function() {
        this.session = undefined;
        this.fireEvent( 'signedout');
        Ext.Msg.alert('Timeout', 'Your session has timed out...', function() {
            //window.location = BQ.Server.url( "/client_service" );
            location.reload();
        });
    },

    onGotUser: function() {
        this.user = BQSession.current_session.user;
        this.loadPreferences();
        this.fireEvent( 'gotuser', BQSession.current_session.user);
    },

    onNoUser: function() {
        this.user = null;
        this.loadPreferences();
        this.fireEvent( 'nouser');
    },

    hasUser: function() {
        return (this.session && this.user);
    },

    getUser: function() {
        return this.user;
    },

    loadPreferences: function() {
        if (!this.linked_prefs) {
            this.linked_prefs = true;
            BQ.Preferences.on('update_user_pref', this.onPreferences, this);
            BQ.Preferences.on('onerror_user_pref', this.onPreferences, this);
        }

        //checks to see if preference has been loaded already
        if (BQ.Preferences.isLoaded('user'))
            this.onPreferences();
        BQ.Preferences.load('user'); //loads on initialization of BQ.Preferences
    },

    onPreferences: function() {
        var level = BQ.Preferences.get('user', 'GraphicalAnnotations/Colors/type_hierarchy_level', 0),
            separator = BQ.Preferences.get('user', 'GraphicalAnnotations/Colors/type_hierarchy_separator', '');
        BQGObject.load_default_styles(BQGObject.unique_gobjects_xml, level, separator);
    },

    // UI elements --------------------------------------------------

    getCenterComponent: function() {
        if (this.main)
            return this.main.getCenterComponent();
    },

    setCenterComponent: function(c) {
        if (!this.main) return;
        this.main.setCenterComponent(c);
        this.fireEvent( 'center_component', c);
    },

    getToolbar: function() {
        if (this.main)
            return this.main.getToolbar();
    },

    add_to_toolbar_menu: function(menu_id, items, position) {
        var toolbar = this.getToolbar();
        if (toolbar) {
            toolbar.add_to_menu(menu_id, items, position);
        }
    },

    setLoading: function(load, targetEl) {
        if (!this.main) return;
        var w = this.getCenterComponent() || this.main;
        w.setLoading(load, targetEl);
    },

    setActiveHelpVideo: function(url) {
        if (!this.main) return;
        var tb = this.main.getToolbar();
        tb.setActiveHelpVideo(url);
    },

    setAnalysisQuery: function(q) {
        if (!this.main) return;
        var tb = this.main.getToolbar();
        if (!tb) {
            this.analysis_query = q;
        } else {
            tb.setAnalysisQuery(q);
        }
    },

});

//--------------------------------------------------------------------------------------
// BQ.Application.Window
//--------------------------------------------------------------------------------------

Ext.define('BQ.Application.Window', {
    extend: 'Ext.container.Viewport',
    requires: ['Ext.tip.QuickTipManager', 'Ext.tip.QuickTip', 'Ext.layout.container.Border'],

    id : 'appwindow',
    layout : 'border',
    border : false,

    initComponent : function() {
        Ext.tip.QuickTipManager.init();

        if (!(Ext.isChrome || Ext.firefoxVersion || Ext.isSafari)) {
            BQ.ui.warning('<b>BISQUE</b> runs best on Chrome, Firefox and Safari.', 15000);
        }

        // dima: the application should request preferences but right no toolbar does it
        // ideally we should check for welcome messages here, but currently we can do it in the toolbar

        var content = document.getElementById('content');
        if (content && content.children.length<1) {
          document.body.removeChild(content);
          content = undefined;
        }

        this.toolbar = Ext.create('BQ.Application.Toolbar', {
        	toolbar_opts: BQ.Server.toolbar_opts,
            hidden: BQ.config ? BQ.config.toolbar_visibility : false,
        });
        this.items = [
                this.toolbar, {
                    region : 'center',
                    id: 'centerEl',
                    layout: 'fit',
                    flex: 3,
                    border : false,
                    header : false,
                    contentEl : content,
                    autoScroll: true,
                }, {
                    id: 'help',
                    region : 'east',
                    collapsible: true,
                    split: true,
                    layout: 'fit',
                    hidden: true,
                    cls: 'help',
                    width: 320,
                    //flex: 1,
                    border : false,
                }, ];

        this.callParent();
        // set bisque overview help video
        //this.toolbar.setActiveHelpVideo('//www.youtube.com/embed/_tq62SJ8SCw?list=PLAaP7tKanFcyR5cjJsPTCa0CDmWp9unds');
    },

    // private
    onDestroy : function(){
        this.callParent();
    },

    removeWindowContent: function() {
        var c = this.getComponent('centerEl');
        c.removeAll();
        c.update('');
    },

    getCenterComponent: function() {
        return this.getComponent('centerEl');
    },

    setCenterComponent: function(c) {
        this.removeWindowContent();
        this.getComponent('centerEl').add(c);
    },

    getHelpComponent: function() {
        return this.getComponent('help');
    },

    getToolbar: function() {
        return this.toolbar;
    },

});

Ext.define('BisqueServices', {
    singleton : true,

    constructor : function()
    {
        BQFactory.request(
        {
            uri : '/services',
            cb : Ext.bind(this.servicesLoaded, this)
        });
    },

    servicesLoaded : function(list)
    {
        this.services=[];

        for (var i=0;i<list.tags.length;i++)
            this.services[list.tags[i].type.toLowerCase()]=list.tags[i];
    },

    getURL : function(serviceName)
    {
        var service = this.services[serviceName];
        return (service)?service.value:'';
    }
})

//--------------------------------------------------------------------------------------
// BisqueService
//--------------------------------------------------------------------------------------

BisqueService = function (urllist) {
    this.urls = urllist;
    if (this.urls.length)
        this.url = this.urls[0];
}

BisqueService.prototype.make_url  = function (path, params) {
    var url = this.url;
    if (path)
        url = url + '/' + path;
    if (params)
        url = url + '?' +  encodeParameters (params );
    return url;
}
BisqueService.prototype.xmlrequest  = function (path, params, cb, body) {
    var method = null;
    var url = this.make_url (path, params);
    if (body)
        method = 'post';
    xmlrequest (url, cb, method, body);
}
BisqueService.prototype.request  = function (path, params, cb, body) {
    var method = null;
    var url = this.make_url (path, params);
    if (body)
        method = 'post';
    BQFactory.request ({ uri:url, callback:cb, method:method, body:body});
}

Bisque = function () {
    this.services = {};
}

Bisque.prototype.init = function () {
    BQFactory.load ("/services", callback (this, 'on_init'));
}
Bisque.prototype.on_init = function (resource) {
    // Each each tag type to
    var tags = resource.tags;
    for (var i=0; i<tags.length; i++) {
        var ty = tags[i].type;
        var uri = tags[i].value;
        Bisque[ty] = new BisqueService (uri);
    }
}

Bisque.onReady  = function (f) {
    Ext.onReady (f);
}
Bisque.init_services = function (services) {
    for (var ty in services) {
        Bisque[ty] = new  BisqueService (services[ty]);
    }
}

