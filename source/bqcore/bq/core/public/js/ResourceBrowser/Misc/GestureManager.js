Ext.define('Bisque.Misc.GestureManager', {

    constructor : function() {
        if ( typeof ExtTouch === 'undefined')
            return;
        ExtTouch.supports.init();
        ExtTouch.gesture.Manager.init();
    },

    addListener : function(listenerObj) {
        if ( typeof ExtTouch === 'undefined')
            return;
        if (Ext.isArray(listenerObj)) {
            Ext.Array.forEach(listenerObj, this.addListener, this);
            return;
        }

        if (Ext.getDom(listenerObj.dom))
            ExtTouch.gesture.Manager.addEventListener(listenerObj.dom, listenerObj.eventName, listenerObj.listener, listenerObj.options);
    },
});
