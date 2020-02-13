ExtTouch.gesture.Manager = new ExtTouch.AbstractManager({
    eventNames: {
        start: 'touchstart',
        move: 'touchmove',
        end: 'touchend'
    },

    //defaultPreventedMouseEvents: ['click'],

    clickMoveThreshold: 5,

    init: function() {
        this.targets = [];

        this.followTouches = [];
        this.currentGestures = [];
        this.currentTargets = [];

        /*
        if (!ExtTouch.supports.Touch) {
            ExtTouch.apply(this.eventNames, {
                start: 'mousedown',
                move: 'mousemove',
                end: 'mouseup'
            });
        }
        */

        this.listenerWrappers = {
            start: ExtTouch.createDelegate(this.onTouchStart, this),
            move: ExtTouch.createDelegate(this.onTouchMove, this),
            end: ExtTouch.createDelegate(this.onTouchEnd, this),
            //mouse: ExtTouch.createDelegate(this.onMouseEvent, this)
        };

        this.attachListeners();
    },

    freeze: function() {
        this.isFrozen = true;
    },

    thaw: function() {
        this.isFrozen = false;
    },

    getEventSimulator: function() {
        if (!this.eventSimulator) {
            this.eventSimulator = new ExtTouch.util.EventSimulator();
        }

        return this.eventSimulator;
    },

    attachListeners: function() {
        ExtTouch.iterate(this.eventNames, function(key, name) {
            document.addEventListener(name, this.listenerWrappers[key], false);
        }, this);

        /*if (ExtTouch.supports.Touch) {
            this.defaultPreventedMouseEvents.forEach(function(name) {
                document.addEventListener(name, this.listenerWrappers['mouse'], true);
            }, this);
        }*/
    },

    detachListeners: function() {
        ExtTouch.iterate(this.eventNames, function(key, name) {
            document.removeEventListener(name, this.listenerWrappers[key], false);
        }, this);

        /*if (ExtTouch.supports.Touch) {
            this.defaultPreventedMouseEvents.forEach(function(name) {
                document.removeEventListener(name, this.listenerWrappers['mouse'], true);
            }, this);
        }*/
    },
/*
    onMouseEvent: function(e) {
        if (!e.isSimulated) {
            e.preventDefault();
            e.stopPropagation();
        }
    },
*/
    onTouchStart: function(e) {
        var targets = [],
            target = e.target;

        if (e.stopped === true) {
            return;
        }

        if (ExtTouch.is.Android) {
            if (!(target.tagName && ['input', 'tExtToucharea', 'select'].indexOf(target.tagName.toLowerCase()) !== -1)) {
                e.preventDefault();
            }
        }

        if (this.isFrozen) {
            return;
        }

        // There's already a touchstart without any touchend!
        // This used to happen on HTC Desire and HTC Incredible
        // We have to clean it up
        if (this.startEvent) {
            this.onTouchEnd(e);
        }

        this.locks = {};

        this.currentTargets = [target];

        while (target) {
            if (this.targets.indexOf(target) !== -1) {
                targets.unshift(target);
            }

            target = target.parentNode;
            this.currentTargets.push(target);
        }

        this.startEvent = e;
        this.startPoint = ExtTouch.util.Point.fromEvent(e);
        this.lastMovePoint = null;
        this.isClick = true;
        this.handleTargets(targets, e);
    },

    onTouchMove: function(e) {
        if (ExtTouch.is.MultiTouch) {
            e.preventDefault();
        }

        if (!this.startEvent) {
            return;
        }

        if (ExtTouch.is.Desktop) {
            e.target = this.startEvent.target;
        }

        if (this.isFrozen) {
            return;
        }

        var gestures = this.currentGestures,
            gesture,
            touch = e.changedTouches ? e.changedTouches[0] : e;

        this.lastMovePoint = ExtTouch.util.Point.fromEvent(e);

        if (ExtTouch.supports.Touch && this.isClick && !this.lastMovePoint.isWithin(this.startPoint, this.clickMoveThreshold)) {
            this.isClick = false;
        }

        for (var i = 0; i < gestures.length; i++) {
            if (e.stopped) {
                break;
            }

            gesture = gestures[i];

            if (gesture.listenForMove) {
                gesture.onTouchMove(e, touch);
            }
        }
    },

    // This listener is here to always ensure we stop all current gestures
    onTouchEnd: function(e) {
        if (ExtTouch.is.Blackberry) {
            e.preventDefault();
        }

        if (this.isFrozen) {
            return;
        }

        var gestures = this.currentGestures.slice(0),
            ln = gestures.length,
            i, gesture, endPoint,
            needsAnotherMove = false,
            touch = e.changedTouches ? e.changedTouches[0] : e;

        if (this.startPoint) {
            endPoint = ExtTouch.util.Point.fromEvent(e);
            if (!(this.lastMovePoint || this.startPoint)['equals'](endPoint)) {
                needsAnotherMove = true;
            }
        }

        for (i = 0; i < ln; i++) {
            gesture = gestures[i];

            if (!e.stopped && gesture.listenForEnd) {
                // The point has changed, we should execute another onTouchMove before onTouchEnd
                // to deal with the problem of missing events on Androids and alike
                // This significantly improves scrolling experience on Androids!
                if (needsAnotherMove) {
                    gesture.onTouchMove(e, touch);
                }

                gesture.onTouchEnd(e, touch);
            }

            this.stopGesture(gesture);
        }


        if (ExtTouch.supports.Touch && this.isClick) {
            this.isClick = false;
            //this.getEventSimulator().fire('click', this.startEvent.target, touch);
        }

        this.lastMovePoint = null;
        this.followTouches = [];
        this.startedChangedTouch = false;
        this.currentTargets = [];
        this.startEvent = null;
        this.startPoint = null;
    },

    handleTargets: function(targets, e) {
        // In handle targets we have to first handle all the capture targets,
        // then all the bubble targets.
        var ln = targets.length,
            i;

        this.startedChangedTouch = false;
        this.startedTouches = ExtTouch.supports.Touch ? e.touches : [e];

        for (i = 0; i < ln; i++) {
            if (e.stopped) {
                break;
            }

            this.handleTarget(targets[i], e, true);
        }

        for (i = ln - 1; i >= 0; i--) {
            if (e.stopped) {
                break;
            }

            this.handleTarget(targets[i], e, false);
        }

        if (this.startedChangedTouch) {
            this.followTouches = this.followTouches.concat((ExtTouch.supports.Touch && e.targetTouches) ? ExtTouch.toArray(e.targetTouches) : [e]);
        }
    },

    handleTarget: function(target, e, capture) {
        var gestures = ExtTouch.Element.data(target, 'x-gestures') || [],
            ln = gestures.length,
            i, gesture;

        for (i = 0; i < ln; i++) {
            gesture = gestures[i];
            if (
                (!!gesture.capture === !!capture) &&
                (this.followTouches.length < gesture.touches) &&
                ((ExtTouch.supports.Touch && e.targetTouches) ? (e.targetTouches.length === gesture.touches) : true)
            ) {
                this.startedChangedTouch = true;
                this.startGesture(gesture);

                if (gesture.listenForStart) {
                    gesture.onTouchStart(e, e.changedTouches ? e.changedTouches[0] : e);
                }

                if (e.stopped) {
                    break;
                }
            }
        }
    },

    startGesture: function(gesture) {
        gesture.started = true;
        this.currentGestures.push(gesture);
    },

    stopGesture: function(gesture) {
        gesture.started = false;
        this.currentGestures.remove(gesture);
    },

    addEventListener: function(target, eventName, listener, options) {
        target = ExtTouch.getDom(target);
        options = options || {};

        var targets = this.targets,
            name = this.getGestureName(eventName),
            gestures = ExtTouch.Element.data(target, 'x-gestures'),
            gesture;

        if (!gestures) {
            gestures = [];
            ExtTouch.Element.data(target, 'x-gestures', gestures);
        }

        // <debug>
        if (!name) {
            throw new Error('Trying to subscribe to unknown event ' + eventName);
        }
        // </debug>

        if (targets.indexOf(target) === -1) {
            this.targets.push(target);
        }

        gesture = this.get(target.id + '-' + name);

        if (!gesture) {
            gesture = this.create(ExtTouch.apply({}, options, {
                target: target,
                type: name
            }));

            gestures.push(gesture);
            // The line below is not needed, ExtTouch.Element.data(target, 'x-gestures') still reference gestures
            // ExtTouch.Element.data(target, 'x-gestures', gestures);
        }

        gesture.addListener(eventName, listener);

        // If there is already a finger down, then instantly start the gesture
        if (this.startedChangedTouch && this.currentTargets.contains(target) && !gesture.started && !options.subsequent) {
            this.startGesture(gesture);
            if (gesture.listenForStart) {
                gesture.onTouchStart(this.startEvent, this.startedTouches[0]);
            }
        }
    },

    removeEventListener: function(target, eventName, listener) {
        target = ExtTouch.getDom(target);

        var name = this.getGestureName(eventName),
            gestures = ExtTouch.Element.data(target, 'x-gestures') || [],
            gesture;

        gesture = this.get(target.id + '-' + name);

        if (gesture) {
            gesture.removeListener(eventName, listener);

            for (name in gesture.listeners) {
                return;
            }

            gesture.destroy();
            gestures.remove(gesture);
            ExtTouch.Element.data(target, 'x-gestures', gestures);
        }
    },

    getGestureName: function(ename) {
        return this.names && this.names[ename];
    },

    registerType: function(type, cls) {
        var handles = cls.prototype.handles,
            i, ln;

        this.types[type] = cls;

        cls[this.typeName] = type;

        if (!handles) {
            handles = cls.prototype.handles = [type];
        }

        this.names = this.names || {};

        for (i = 0, ln = handles.length; i < ln; i++) {
            this.names[handles[i]] = type;
        }
    }
});

ExtTouch.regGesture = function() {
    return ExtTouch.gesture.Manager.registerType.apply(ExtTouch.gesture.Manager, arguments);
};