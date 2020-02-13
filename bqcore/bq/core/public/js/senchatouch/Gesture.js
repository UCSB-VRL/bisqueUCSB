ExtTouch.gesture.Gesture = ExtTouch.ExtTouchend(Object, {    
    listenForStart: true,
    listenForEnd: true,
    listenForMove: true,
    
    disableLocking: false,
    
    touches: 1,
    
    constructor: function(config) {
        config = config || {};
        ExtTouch.apply(this, config);
        
        this.target = ExtTouch.getDom(this.target);
        this.listeners = {};
        
        // <debug>
        if (!this.target) {
            throw new Error('Trying to bind a ' + this.type + ' event to element that does\'nt exist: ' + this.target);
        }
        // </debug>
        
        this.id = this.target.id + '-' + this.type;
        
        ExtTouch.gesture.Gesture.superclass.constructor.call(this);
        ExtTouch.gesture.Manager.register(this);
    },
    
    addListener: function(name, listener) {
        this.listeners[name] = this.listeners[name] || [];
        this.listeners[name].push(listener);
    },
    
    removeListener: function(name, listener) {
        var listeners = this.listeners[name];
            
        if (listeners) {
            listeners.remove(listener);

            if (listeners.length == 0) {
                delete this.listeners[name];
            }

            for (name in this.listeners) {
                if (this.listeners.hasOwnProperty(name)) {
                    return;
                }
            }
            
            this.listeners = {};
        }
    },
    
    fire: function(type, e, args) {
        var listeners = this.listeners && this.listeners[type],
            ln = listeners && listeners.length,
            i;

        if (!this.disableLocking && this.isLocked(type)) {
            return false;
        }
        
        if (ln) {
            args = ExtTouch.apply(args || {}, {
                time: e.timeStamp,
                type: type,
                gesture: this,
                target: (e.target.nodeType == 3) ? e.target.parentNode: e.target
            });
            
            for (i = 0; i < ln; i++) {
                listeners[i](e, args);
            }
        }
        
        return true;
    },
    
    stop: function() {
        ExtTouch.gesture.Manager.stopGesture(this);
    },
    
    lock: function() {
        if (!this.disableLocking) {
            var args = arguments,
                ln = args.length,
                i;

            for (i = 0; i < ln; i++) {
                ExtTouch.gesture.Manager.locks[args[i]] = this.id;
            }            
        }
    },
    
    unlock: function() {
        if (!this.disableLocking) {
            var args = arguments,
                ln = args.length,
                i;

            for (i = 0; i < ln; i++) {
                if (ExtTouch.gesture.Manager.locks[args[i]] == this.id) {
                    delete ExtTouch.gesture.Manager.locks[args[i]]; 
                }
            }            
        }
    },
    
    isLocked : function(type) {
        var lock = ExtTouch.gesture.Manager.locks[type];
        return !!(lock && lock !== this.id);
    },
    
    getLockingGesture : function(type) {
        var lock = ExtTouch.gesture.Manager.locks[type];
        if (lock) {
            return ExtTouch.gesture.Manager.get(lock) || null;
        }
        return null;
    },
    
    onTouchStart: ExtTouch.emptyFn,
    onTouchMove: ExtTouch.emptyFn,
    onTouchEnd: ExtTouch.emptyFn,
    
    destroy: function() {
        this.stop();
        this.listeners = null;
        ExtTouch.gesture.Manager.unregister(this);
    }
});