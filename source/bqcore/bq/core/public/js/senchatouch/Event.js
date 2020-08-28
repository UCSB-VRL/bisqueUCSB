ExtTouch.TouchEventObjectImpl = ExtTouch.ExtTouchend(Object, {
    constructor : function(e, args) {
        if (e) {
            this.setEvent(e, args);
        }
    },

    setEvent : function(e, args) {
        ExtTouch.apply(this, {
            event: e,
            time: e.timeStamp
        });

        this.touches = e.touches || [e];
        this.changedTouches = e.changedTouches || [e];
        this.targetTouches = e.targetTouches || [e];
        
        if (args) {
            this.target = args.target;
            ExtTouch.apply(this, args);
        }
        else {
            this.target = e.target;
        }
        return this;
    },

    stopEvent : function() {
        this.stopPropagation();
        this.preventDefault();
    },

    stopPropagation : function() {
        this.event.stopped = true;
    },

    preventDefault : function() {
        this.event.preventDefault();
    },

    getTarget : function(selector, maxDepth, returnEl) {
        if (selector) {
            return ExtTouch.fly(this.target).findParent(selector, maxDepth, returnEl);
        }
        else {
            return returnEl ? ExtTouch.get(this.target) : this.target;
        }
    }
});

ExtTouch.TouchEventObject = new ExtTouch.TouchEventObjectImpl();