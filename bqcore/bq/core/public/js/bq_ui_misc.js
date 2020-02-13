/*

Examples:

    BQ.ui.message('Attention', 'I have news', 1000);

    BQ.ui.error('Something happened...');
    BQ.ui.warning('You are not logged in! You need to log-in to run any analysis...');
    BQ.ui.notification('Seed detection done! Verify results...');

    BQ.ui.tip( 'my_id', 'Verify results...', {color: 'green', timeout: 10000} );
*/


Ext.namespace('BQ.ui');

function showTip( element, text, opts ) {
  opts = opts || {};
  if (!('color' in opts)) opts.color = 'red';
  if (!('timeout' in opts)) opts.timeout = 5000;
  opts.anchor = opts.anchor || 'top';

  var tip = new Ext.ToolTip({
      target: element,
      anchor: opts.anchor,
      bodyStyle: 'font-size: 160%; color: '+opts.color+';',
      html: text
  });
  tip.show();
  setTimeout( function () { tip.destroy(); }, opts.timeout );
}

BQ.ui = function(){
    var msgCt;

    function createBox(t, s, c){
       return '<div class="msg '+c+'"><img id="btn_close" src="/core/images/cancel.png" /><h3>' + t + '</h3><p>' + s + '</p></div>';
    }
    return {
        message: function(title, format, delay, css) {
            if (!msgCt) {
                msgCt = Ext.core.DomHelper.insertFirst(document.body, {id:'messagepopup'}, true);
            }
            if (delay == undefined) delay = 3000;
            if (css == undefined) css = '';
            var s = format; //Ext.String.format.apply(String, Array.prototype.slice.call(arguments, 1));
            var m = Ext.core.DomHelper.append(msgCt, createBox(title, s, css), true);
            m.hide();
            m.on('click', function(e, el) {
                    if (el.id==='btn_close' || el === this.dom) {
                        //this.stopAnimation();
                        //this.fadeOut( {remove: true} );
                        this.destroy();
                    }
                }, m, {
                //single: true,
                stopEvent : true,
            });
            m.slideIn('t').ghost("t", { delay: delay, remove: true});
        },

        popup: function(type, text, delay) {
            var t = BQ.ui.types[type] || BQ.ui.types['notification'];
            BQ.ui.message( t.title, text, delay || t.delay, t.cls );
        },

        notification: function(text, delay) {
            BQ.ui.popup('notification', text, delay );
        },

        attention: function(text, delay) {
            BQ.ui.popup('attention', text, delay );
        },

        warning: function(text, delay) {
            BQ.ui.popup('warning', text, delay );
        },

        error: function(text, delay) {
            BQ.ui.popup('error', text, delay );
        },

        tip: function( element, text, opts ) {
            opts = opts || {};
            if (!('color' in opts)) opts.color = 'red';
            if (!('timeout' in opts)) opts.timeout = 5000;
            opts.anchor = opts.anchor || 'top';
            var tip = new Ext.ToolTip({
              target: element,
              anchor: opts.anchor,
              bodyStyle: 'font-size: 160%; color: '+opts.color+';',
              html: text
            });
            tip.show();
            setTimeout( function () { tip.destroy(); }, opts.timeout );
        },

        highlight: function( element, text, opts ) {
            opts = opts || {};
            opts.timeout = opts.timeout || 5000;
            opts.anchor = opts.anchor || 'top';

            var w = Ext.create('Ext.ToolTip', Ext.apply({
              target: element,
              anchor: opts.anchor,
              cls: 'highlight',
              html: text,
              autoHide: false,
              shadow: false,
            }, opts));
            w.show();
            w.getEl().fadeOut({ delay: opts.timeout});//.fadeOut({ delay: opts.timeout, remove: true});
        },

    };
}();

BQ.ui.types = {
    'notification': { delay: 5000,  title: '',        cls: 'notification' },
    'attention':    { delay: 10000, title: '',        cls: 'warning' },
    'warning':      { delay: 10000, title: 'Warning', cls: 'warning' },
    'error':        { delay: 50000, title: 'Error',   cls: 'error' },
};

/*******************************************************************************
    BQ.window.MessageBox
*******************************************************************************/

Ext.define('BQ.window.MessageBox', {
    extend: 'Ext.window.MessageBox',
    alias: 'widget.bq-messagebox',

    reconfigure: function(cfg) {
        this.callParent(arguments);
        if (cfg.validator) {
            this.textField.validator = cfg.validator;
            this.textField.on('validitychange', function(parent, isValid) {
                if (this.msgButtons && this.msgButtons.length>0)
                    this.msgButtons[0].setDisabled(!isValid);
            }, this );
        } else {
            this.textField.validator = undefined;
        }
    },

    prompt : function(cfg, msg, fn, scope, multiline, value, validator){
        if (Ext.isString(cfg)) {
            cfg = {
                prompt: true,
                title: cfg,
                minWidth: this.minPromptWidth,
                msg: msg,
                buttons: this.OKCANCEL,
                callback: fn,
                scope: scope,
                multiline: multiline,
                value: value,
                validator: validator,
            };
        }
        return this.show(cfg);
    },
}, function() {
    /**
     * @class BQ.MessageBox
     * @extends BQ.window.MessageBox
     * @singleton
     * Singleton instance of {@link BQ.window.MessageBox}.
     */
    BQ.MessageBox = new this();
});

/*******************************************************************************
    BQ.window.Prompt - a generic prompt box that receives renderable items
    and a function that creates a dictionary with requested values
*******************************************************************************/

Ext.define('BQ.window.Prompt', {
    extend: 'Ext.window.Window',

    requires: [
        'Ext.toolbar.Toolbar',
        'Ext.button.Button',
        'Ext.layout.container.Anchor',
        'Ext.layout.container.HBox',
    ],

    alias: 'widget.bq-prompt',
    cls: 'bq-prompt',

    fields: undefined,
    func: undefined,
    callback: undefined,

    // hide it by offsets. Windows are hidden on render by default.
    hidden: true,
    modal: true,
    hideMode: 'offsets',
    closeAction: 'hide',
    resizable: false,
    title: '&#160;',

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    initComponent: function() {
        var me = this,
            baseId = me.id;

        me.items = this.fields;

        // Create the buttons based upon passed bitwise config
        me.bottomTb = Ext.create('Ext.toolbar.Toolbar', {
            id: baseId + '-toolbar',
            ui: 'footer',
            dock: 'bottom',
            layout: {
                pack: 'center'
            },
            items: [{
                handler: this.btnCallback,
                itemId: 'ok',
                scope: this,
                text: 'OK',
                minWidth: 75
            }, {
                handler: this.btnCallback,
                itemId: 'cancel',
                scope: this,
                text: 'Cancel',
                minWidth: 75
            }]
        });
        me.dockedItems = [me.bottomTb];
        me.on('close', me.onClose, me);
        me.callParent();
    },

    btnCallback: function(btn) {
        var me = this,
            scope = this.scope || me,
            value;

        if (me.func) {
            //value = me.func(me.topContainer.items);
            value = me.func(me);
        }

        // Component.onHide blurs the active element if the Component contains the active element
        me.hide();
        this.callback.apply(scope, [btn.itemId, value]);
    },

    onClose: function(){
        var btn = this.header.child('[type=close]');
        // Give a temporary itemId so it can act like the cancel button
        btn.itemId = 'cancel';
        this.btnCallback(btn);
        delete btn.itemId;
    },

    onPromptKey: function(textField, e) {
        var me = this;

        if (e.keyCode === e.RETURN || e.keyCode === 10) {
            if (me.msgButtons.ok.isVisible()) {
                me.msgButtons.ok.handler.call(me, me.msgButtons.ok);
            } else if (me.msgButtons.yes.isVisible()) {
                me.msgButtons.yes.handler.call(me, me.msgButtons.yes);
            }
        }
    },

    onShow: function() {
        this.callParent(arguments);
        this.center();
    },

    onEsc: function() {
        if (this.closable !== false) {
            this.callParent(arguments);
        }
    },

});


