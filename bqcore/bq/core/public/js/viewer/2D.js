/*****
 *
 *   The contents of this file were written by Kevin Lindsey
 *   copyright 2006 Kevin Lindsey
 *
 *   modified for Bisquik by August Black, Kris Kvilekval
 *
 *****/

Array.prototype.foreach = function(func) {
    var length = this.length;
    for (var i = 0; i < length; i++) {
        func(this[i]);
    }
};

Array.prototype.grep = function(func) {
    var length = this.length;
    var result = [];
    for (var i = 0; i < length; i++) {
        var elem = this[i];
        if (func(elem)) {
            result.push(elem);
        }
    }
    return result;
};

Array.prototype.map = function(func) {
    var length = this.length;
    var result = [];
    for (var i = 0; i < length; i++) {
        result.push(func(this[i]));
    }
    return result;
};

Array.prototype.min = function() {
    var length = this.length;
    var min = this[0];
    for (var i = 0; i < length; i++) {
        var elem = this[i];
        if (elem < min)
            min = elem;
    }
    return min;
};

Array.prototype.max = function() {
    var length = this.length;
    var max = this[0];
    for (var i = 0; i < length; i++)
        var elem = this[i];
    if (elem > max)
        max = elem;
    return max;
};

EventHandler.VERSION = 1.0;

function EventHandler() {
    this.init();
};

EventHandler.prototype.init = function() {
};

EventHandler.prototype.handleEvent = function(e) {
    if (this[e.type] == null)
        throw new Error("Unsupported event type: " + e.type);
    this[e.type](e);
};

// get this from globals.js
//var svgns="http://www.w3.org/2000/svg";

Mouser.prototype = new EventHandler();
Mouser.prototype.constructor = Mouser;
Mouser.superclass = EventHandler.prototype;
function Mouser() {
    this.init();

    if (window.navigator) {
        if (window.navigator.appName.match(/Adobe/gi)) {
            this.navigator = "Adobe";
        }
        if (window.navigator.appName.match(/Netscape/gi)) {
            this.navigator = "Mozilla";
        }
        if (window.navigator.userAgent) {
            if (window.navigator.userAgent.match(/Opera/gi)) {
                this.navigator = "Opera";
            }
            if (window.navigator.userAgent.match(/AppleWebKit/gi) || window.navigator.userAgent.match(/Safari/gi)) {
                this.navigator = "Safari";
            }
        }
    }
}

Mouser.prototype.init = function() {
    this.svgNode = null;
    this.handles = new Array();
    this.shapes = new Array();
    this.lastPoint = null;
    this.currentNode = null;
    this.realize();
};

Mouser.prototype.realize = function() {
    if (this.svgNode == null) {
        var rect = document.createElementNS(svgns, "rect");
        this.svgNode = rect;
        rect.setAttributeNS(null, "x", "-16384");
        rect.setAttributeNS(null, "y", "-16384");
        rect.setAttributeNS(null, "width", "32767");
        rect.setAttributeNS(null, "height", "32767");
        rect.setAttributeNS(null, "fill", "none");
        rect.setAttributeNS(null, "pointer-events", "all");
        rect.setAttributeNS(null, "display", "none");
        _svgElement.appendChild(rect);
    }
};

Mouser.prototype.register = function(handle) {
    if (this.handleIndex(handle) == -1) {
        var owner = handle.owner;
        handle.select(true);
        this.handles.push(handle);
        if (owner != null && this.shapeIndex(owner) == -1)
            this.shapes.push(owner);
    }
};

Mouser.prototype.unregister = function(handle) {
    var index = this.handleIndex(handle);
    if (index != -1) {
        handle.select(false);
        this.handles.splice(index, 1);
    }
};

Mouser.prototype.registerShape = function(shape) {
    if (this.shapeIndex(shape) == -1) {
        shape.select(true);
        this.shapes.push(shape);
    }
};

Mouser.prototype.unregisterShape = function(shape) {
    var index = this.shapeIndex(shape);
    if (index != -1) {
        shape.select(false);
        shape.selectHandles(false);
        shape.showHandles(false);
        shape.unregisterHandles();
        this.shapes.splice(index, 1);
    }
};

Mouser.prototype.unregisterAll = function() {
    for (var i = 0; i < this.handles.length; i++) {
        this.handles[i].select(false);
    }
    this.handles = new Array();
};

Mouser.prototype.unregisterShapes = function() {
    var selected = this.shapes;
    for (var i = 0; i < this.shapes.length; i++) {
        var shape = this.shapes[i];
        shape.select(false);
        shape.selectHandles(false);
        shape.showHandles(false);
        shape.unregisterHandles();
    }
    this.shapes = new Array();
    return selected;
};

Mouser.prototype.handleIndex = function(handle) {
    var result = -1;
    for (var i = 0; i < this.handles.length; i++) {
        if (this.handles[i] === handle) {
            result = i;
            break;
        }
    }
    return result;
};

Mouser.prototype.shapeIndex = function(shape) {
    var result = -1;
    for (var i = 0; i < this.shapes.length; i++) {
        if (this.shapes[i] === shape) {
            result = i;
            break;
        }
    }
    return result;
};

Mouser.prototype.selectedShapes = function() {
    var selected = [];
    for (var i = 0; i < this.shapes.length; i++) {
        var shape = this.shapes[i];
        if (shape.selected) {
            selected.push(shape);
        }
    }
    return selected;
};

Mouser.prototype.selectShapes = function(selected, select) {
    var sv = select || true;
    for (var i = 0; i < selected.length; i++) {
        var shape = selected[i];
        shape.selected = sv;
        shape.selectHandles(sv);
        shape.showHandles(sv);
        if (sv)
            shape.registerHandles();
        else
            shape.unregisterHandles();
    }
};

Mouser.prototype.beginDrag = function(e) {
    var svgRoot = _svgElement;
    this.currentNode = e.target;
    var svgPoint = this.getUserCoordinate(this.currentNode, e);
    this.lastPoint = new Point2D(svgPoint.x, svgPoint.y);
    this.svgNode.addEventListener("mouseup", this, false);
    this.svgNode.addEventListener("mousemove", this, false);

    svgRoot.appendChild(this.svgNode);
    this.svgNode.setAttributeNS(null, "display", "inline");
};

Mouser.prototype.mouseup = function(e) {
    this.lastPoint = null;
    this.currentNode = null;
    this.svgNode.removeEventListener("mouseup", this, false);
    this.svgNode.removeEventListener("mousemove", this, false);
    this.svgNode.setAttributeNS(null, "display", "none");
};

Mouser.prototype.mousemove = function(e) {
    var svgPoint = this.getUserCoordinate(this.currentNode, e);
    var newPoint = new Point2D(svgPoint.x, svgPoint.y);
    var delta = newPoint.subtract(this.lastPoint);
    var updates = new Array();
    var updateId = new Date().getTime();
    this.lastPoint.setFromPoint(newPoint);
    for (var i = 0; i < this.handles.length; i++) {
        var handle = this.handles[i];
        var owner = handle.owner;
        handle.translate(delta);
        if (owner != null) {
            if (owner.lastUpdate != updateId) {
                owner.lastUpdate = updateId;
                updates.push(owner);
            }
        } else {
            updates.push(handle);
        }
    }
    for (var i = 0; i < updates.length; i++) {
        updates[i].update();
    }

    // dima, stop event propagation if handeled
    if (e.stopPropagation)
        e.stopPropagation();
    // DOM Level 2
    else
        e.cancelBubble = true;
    // IE
};

Mouser.prototype.getUserCoordinate = function(node, evt) {
    var svgRoot = _svgElement;
    var svgPoint = svgRoot.createSVGPoint();

    if (Ext.isChrome) {
        svgPoint.x = evt.x;
        svgPoint.y = evt.y;
    } else if (Ext.isSafari) {
        svgPoint.x = evt.pageX;
        svgPoint.y = evt.pageY;
    } else if (Ext.isIE) {
        svgPoint.x = evt.pageX;
        svgPoint.y = evt.pageY;
    } else {
        svgPoint.x = evt.clientX;
        svgPoint.y = evt.clientY;
    }

    //     if (node.convertClientXY) {
    //         clog ("using convert");
    //         return node.convertClientXY(svgPoint.x, svgPoint.y);
    //     }
    if (!svgRoot.getScreenCTM) {
        var matrix = this.getTransformToRootElement(evt.target);
    } else {
        //clog ("using ScreenCTM");
        var matrix = node.getScreenCTM();
    }
    //clog ("got point " + svgPoint.x + "," + svgPoint.y );
    svgPoint = svgPoint.matrixTransform(matrix.inverse());
    //clog ("now point " + svgPoint.x + "," + svgPoint.y );
    return svgPoint;
};

Mouser.prototype.getTransformToRootElement = function(node) {
    var svgRoot = _svgElement;
    try {
        //this part is for fully conformant players (like Opera, Batik, Firefox, Safari ...)
        var CTM = node.getTransformToElement(svgRoot);
        //clog("Using gettransformtElement");
    } catch (ex) {
        //clog ("caught " + ex);
        //this part is for ASV3 or other non-conformant players
        // Initialize our CTM the node's Current Transformation Matrix
        var CTM = node.getCTM();
        // Work our way through the ancestor nodes stopping at the SVG Document
        while (( node = node.parentNode ) != _svgElement) {
            // Multiply the new CTM to the one with what we have accumulated so far
            CTM = node.getCTM().multiply(CTM);
        }
    }

    return CTM;
};

function IntersectionParams(name, params) {
    if (arguments.length > 0)
        this.init(name, params);
}

IntersectionParams.prototype.init = function(name, params) {
    this.name = name;
    this.params = params;
};

function Point2D(x, y) {
    if (arguments.length > 0) {
        this.x = x;
        this.y = y;
    }
}

Point2D.prototype.clone = function() {
    return new Point2D(this.x, this.y);
};

Point2D.prototype.add = function(that) {
    return new Point2D(this.x + that.x, this.y + that.y);
};
Point2D.prototype.addEquals = function(that) {
    this.x += that.x;
    this.y += that.y;
    return this;
};
Point2D.prototype.offset = function(a, b) {
    var result = 0;
    if (!(b.x <= this.x || this.x + a.x <= 0)) {
        var t = b.x * a.y - a.x * b.y;
        var s;
        var d;
        if (t > 0) {
            if (this.x < 0) {
                s = this.x * a.y;
                d = s / a.x - this.y;
            } else if (this.x > 0) {
                s = this.x * b.y;
                d = s / b.x - this.y;
            } else {
                d = -this.y;
            }
        } else {
            if (b.x < this.x + a.x) {
                s = (b.x - this.x) * a.y;
                d = b.y - (this.y + s / a.x);
            } else if (b.x > this.x + a.x) {
                s = (a.x + this.x) * b.y;
                d = s / b.x - (this.y + a.y);
            } else {
                d = b.y - (this.y + a.y);
            }
        }
        if (d > 0) {
            result = d;
        }
    }
    return result;
};
Point2D.prototype.rmoveto = function(dx, dy) {
    this.x += dx;
    this.y += dy;
};
Point2D.prototype.scalarAdd = function(scalar) {
    return new Point2D(this.x + scalar, this.y + scalar);
};
Point2D.prototype.scalarAddEquals = function(scalar) {
    this.x += scalar;
    this.y += scalar;
    return this;
};
Point2D.prototype.subtract = function(that) {
    return new Point2D(this.x - that.x, this.y - that.y);
};
Point2D.prototype.subtractEquals = function(that) {
    this.x -= that.x;
    this.y -= that.y;
    return this;
};
Point2D.prototype.scalarSubtract = function(scalar) {
    return new Point2D(this.x - scalar, this.y - scalar);
};
Point2D.prototype.scalarSubtractEquals = function(scalar) {
    this.x -= scalar;
    this.y -= scalar;
    return this;
};
Point2D.prototype.multiply = function(scalar) {
    return new Point2D(this.x * scalar, this.y * scalar);
};
Point2D.prototype.multiplyEquals = function(scalar) {
    this.x *= scalar;
    this.y *= scalar;
    return this;
};
Point2D.prototype.divide = function(scalar) {
    return new Point2D(this.x / scalar, this.y / scalar);
};
Point2D.prototype.divideEquals = function(scalar) {
    this.x /= scalar;
    this.y /= scalar;
    return this;
};
Point2D.prototype.compare = function(that) {
    return (this.x - that.x || this.y - that.y);
};
Point2D.prototype.eq = function(that) {
    return (this.x == that.x && this.y == that.y);
};
Point2D.prototype.lt = function(that) {
    return (this.x < that.x && this.y < that.y);
};
Point2D.prototype.lte = function(that) {
    return (this.x <= that.x && this.y <= that.y);
};
Point2D.prototype.gt = function(that) {
    return (this.x > that.x && this.y > that.y);
};
Point2D.prototype.gte = function(that) {
    return (this.x >= that.x && this.y >= that.y);
};
Point2D.prototype.lerp = function(that, t) {
    return new Point2D(this.x + (that.x - this.x) * t, this.y + (that.y - this.y) * t);
};
Point2D.prototype.distanceFrom = function(that) {
    var dx = this.x - that.x;
    var dy = this.y - that.y;
    return Math.sqrt(dx * dx + dy * dy);
};
Point2D.prototype.min = function(that) {
    return new Point2D(Math.min(this.x, that.x), Math.min(this.y, that.y));
};
Point2D.prototype.max = function(that) {
    return new Point2D(Math.max(this.x, that.x), Math.max(this.y, that.y));
};
Point2D.prototype.toString = function() {
    return (isNaN(this.x) || isNaN(this.y)) ? '' : this.x + "," + this.y;
};
Point2D.prototype.setXY = function(x, y) {
    this.x = x;
    this.y = y;
};
Point2D.prototype.setFromPoint = function(that) {
    this.x = that.x;
    this.y = that.y;
};
Point2D.prototype.swap = function(that) {
    var x = this.x;
    var y = this.y;
    this.x = that.x;
    this.y = that.y;
    that.x = x;
    that.y = y;
};

function Vector2D(x, y) {
    if (arguments.length > 0) {
        this.x = x;
        this.y = y;
    }
}

Vector2D.prototype.length = function() {
    return Math.sqrt(this.x * this.x + this.y * this.y);
};
Vector2D.prototype.dot = function(that) {
    return this.x * that.x + this.y * that.y;
};
Vector2D.prototype.cross = function(that) {
    return this.x * that.y - this.y * that.x;
};
Vector2D.prototype.unit = function() {
    return this.divide(this.length());
};
Vector2D.prototype.unitEquals = function() {
    this.divideEquals(this.length());
    return this;
};
Vector2D.prototype.add = function(that) {
    return new Vector2D(this.x + that.x, this.y + that.y);
};
Vector2D.prototype.addEquals = function(that) {
    this.x += that.x;
    this.y += that.y;
    return this;
};
Vector2D.prototype.subtract = function(that) {
    return new Vector2D(this.x - that.x, this.y - that.y);
};
Vector2D.prototype.subtractEquals = function(that) {
    this.x -= that.x;
    this.y -= that.y;
    return this;
};
Vector2D.prototype.multiply = function(scalar) {
    return new Vector2D(this.x * scalar, this.y * scalar);
};
Vector2D.prototype.multiplyEquals = function(scalar) {
    this.x *= scalar;
    this.y *= scalar;
    return this;
};
Vector2D.prototype.divide = function(scalar) {
    return new Vector2D(this.x / scalar, this.y / scalar);
};
Vector2D.prototype.divideEquals = function(scalar) {
    this.x /= scalar;
    this.y /= scalar;
    return this;
};
Vector2D.prototype.perp = function() {
    return new Vector2D(-this.y, this.x);
};
Vector2D.prototype.perpendicular = function(that) {
    return this.subtract(this.project(that));
};
Vector2D.prototype.project = function(that) {
    var percent = this.dot(that) / that.dot(that);
    return that.multiply(percent);
};
Vector2D.prototype.toString = function() {
    return this.x + "," + this.y;
};
Vector2D.fromPoints = function(p1, p2) {
    return new Vector2D(p2.x - p1.x, p2.y - p1.y);
};




Shape.prototype = new EventHandler();
Shape.prototype.constructor = Shape;
Shape.superclass = EventHandler.prototype;

function Shape(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Shape.prototype.init = function(svgNode) {
    this.svgNode = svgNode;
    this.locked = false;
    this.visible = true;
    this.selected = false;
    this.callback_data = null;
    this.update_callback = null;
    this.select_callback = null;
    this.lastUpdate = null;
};

Shape.prototype.show = function(state) {
    var display = (state) ? "inline" : "none";
    this.visible = state;
    if (this.svgNode)
        this.svgNode.setAttributeNS(null, "display", display);
};

Shape.prototype.enhance = function(visible) {
    this.svgNode.setAttributeNS(null, "stroke-width", visible ? '4' : '1');
};

Shape.prototype.refresh = function() {
};

Shape.prototype.update = function() {
    this.refresh();
    if (this.owner)
        this.owner.update(this);
    if (this.update_callback != null)
        this.update_callback(this.callback_data);
};

Shape.prototype.translate = function(delta) {
};

Shape.prototype.select = function(state) {
    this.selected = state;
    if (this.selected && this.select_callback != null)
        this.select_callback(this.callback_data);
};

Shape.prototype.registerHandles = function() {
};

Shape.prototype.unregisterHandles = function() {
};

Shape.prototype.selectHandles = function(select) {
};

Shape.prototype.showHandles = function(state) {
};

Shape.prototype.mouseover = function(e) {
    if (this.svgNode != null) {
        this.enhance(true);
    }
};
Shape.prototype.mouseout = function(e) {
    if (this.svgNode != null) {
        this.enhance(false);
    }
};

Shape.prototype.mousemove = function(e) {
};

Shape.prototype.mousedown = function(e) {
    if (mouser == null)
        return;
    if (!this.locked) {
        if (e.shiftKey) {
            if (this.selected) {
                mouser.unregisterShape(this);
            } else {
                mouser.registerShape(this);
                this.showHandles(true);
                this.selectHandles(true);
                this.registerHandles();
            }
        } else {
            if (this.selected) {
                this.selectHandles(true);
                this.registerHandles();
            } else {
                mouser.unregisterShapes();
                mouser.registerShape(this);
                this.showHandles(true);
                this.selectHandles(false);
            }
        }
    }
};

Shape.prototype.editable = function(edit) {
    this.edit = edit;
    if (edit)
        this.addListeners();
    else
        this.remListeners();
};

Shape.prototype.addListeners = function() {
    this.svgNode.addEventListener("mousedown", this, false);
    //this.svgNode.addEventListener("mousemove",this,false);
    this.svgNode.addEventListener("mouseover", this, false);
    this.svgNode.addEventListener("mouseout", this, false);
};
Shape.prototype.remListeners = function() {
    this.svgNode.removeEventListener("mousedown", this, false);
    //this.svgNode.removeEventListener("mousemove",this,false);
    this.svgNode.removeEventListener("mouseover", this, false);
    this.svgNode.removeEventListener("mouseout", this, false);
};

Circle.prototype = new Shape();
Circle.prototype.constructor = Circle;
Circle.superclass = Shape.prototype;

function Circle(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Circle.prototype.init = function(svgNode) {
    if (svgNode.localName == "circle") {
        Circle.superclass.init.call(this, svgNode);
        var cx = parseFloat(svgNode.getAttributeNS(null, "cx"));
        var cy = parseFloat(svgNode.getAttributeNS(null, "cy"));
        var r = parseFloat(svgNode.getAttributeNS(null, "r"));
        this.center = new Handle(cx, cy, this);
        this.last = new Point2D(cx, cy);
        this.radius = new Handle(cx + r, cy, this);
    } else {
        throw new Error("Circle.init: Invalid SVG Node: " + svgNode.localName);
    }
};

Circle.prototype.mousemove = function(e) {
    if (this.svgNode) {

    }
};

Circle.prototype.enhance = function(visible) {
    this.svgNode.setAttributeNS(null, "stroke-width", visible ? '4' : '1');
};

Circle.prototype.realize = function() {
    if (this.svgNode) {
        this.center.realize();
        this.radius.realize();
        this.center.show(false);
        this.radius.show(false);
    }
};

Circle.prototype.unrealize = function() {
    if (this.svgNode) {
        this.center.unrealize();
        this.radius.unrealize();
        this.svgNode.parentNode.removeChild(this.svgNode);
    }
};

Circle.prototype.translate = function(delta) {
    this.center.translate(delta);
    this.radius.translate(delta);
    this.refresh();
};

Circle.prototype.refresh = function() {
    var r = this.radius.point.distanceFrom(this.center.point);
    this.svgNode.setAttributeNS(null, "cx", this.center.point.x);
    this.svgNode.setAttributeNS(null, "cy", this.center.point.y);
    this.svgNode.setAttributeNS(null, "r", r);
};

Circle.prototype.registerHandles = function() {
    mouser.register(this.center);
    mouser.register(this.radius);
};

Circle.prototype.unregisterHandles = function() {
    mouser.unregister(this.center);
    mouser.unregister(this.radius);
};

Circle.prototype.selectHandles = function(select) {
    this.center.select(select);
    this.radius.select(select);
};

Circle.prototype.showHandles = function(state) {
    this.center.show(state);
    this.radius.show(state);
};

Circle.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Circle", [this.center.point, parseFloat(this.svgNode.getAttributeNS(null, "r"))]);
};

Ellipse.prototype = new Shape();
Ellipse.prototype.constructor = Ellipse;
Ellipse.superclass = Shape.prototype;

function Ellipse(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Ellipse.prototype.init = function(svgNode) {
    if (!svgNode || svgNode.localName !== "ellipse")
        throw new Error("Ellipse.init: Invalid localName: " + svgNode.localName);
    Ellipse.superclass.init.call(this, svgNode);
    var cx = parseFloat(svgNode.getAttributeNS(null, "cx"));
    var cy = parseFloat(svgNode.getAttributeNS(null, "cy"));
    var rx = parseFloat(svgNode.getAttributeNS(null, "rx"));
    var ry = parseFloat(svgNode.getAttributeNS(null, "ry"));
    this.center = new Handle(cx, cy, this);
    this.last = new Point2D(cx, cy);
    this.radiusX = new Handle(cx + rx, cy, this);
    this.radiusY = new Handle(cx, cy + ry, this);
};

Ellipse.prototype.mousemove = function(e) {
    if (this.svgNode) {

    }
};

Ellipse.prototype.enhance = function(visible) {
    this.svgNode.setAttributeNS(null, "stroke-width", visible ? '4' : '1');
};

Ellipse.prototype.realize = function() {
    this.center.realize();
    this.radiusX.realize();
    this.radiusY.realize();
    this.center.show(false);
    this.radiusX.show(false);
    this.radiusY.show(false);
};

Ellipse.prototype.unrealize = function() {
    if (this.svgNode) {
        this.center.unrealize();
        this.radiusX.unrealize();
        this.radiusY.unrealize();
        this.svgNode.parentNode.removeChild(this.svgNode);
    }
};

Ellipse.prototype.translate = function(delta) {
    this.center.translate(delta);
    this.radiusX.translate(delta);
    this.radiusY.translate(delta);
    this.refresh();
};

Ellipse.prototype.refresh = function() {
    var p1 = this.center.point;
    var p2 = this.radiusX.point;
    var p3 = this.radiusY.point;
    var ang = Math.atan2(p1.y-p2.y, p1.x-p2.x) * 180.0/Math.PI;
    this.svgNode.setAttributeNS(null, 'transform', "rotate(" + ang + " " + this.center.point.x + " " + this.center.point.y +")");

    var rx = this.radiusX.point.distanceFrom(this.center.point);
    var ry = this.radiusY.point.distanceFrom(this.center.point);
    this.svgNode.setAttributeNS(null, "cx", this.center.point.x);
    this.svgNode.setAttributeNS(null, "cy", this.center.point.y);
    this.svgNode.setAttributeNS(null, "rx", rx);
    this.svgNode.setAttributeNS(null, "ry", ry);
};

Ellipse.prototype.registerHandles = function() {
    mouser.register(this.center);
    mouser.register(this.radiusX);
    mouser.register(this.radiusY);
};
Ellipse.prototype.unregisterHandles = function() {
    mouser.unregister(this.center);
    mouser.unregister(this.radiusX);
    mouser.unregister(this.radiusY);
};
Ellipse.prototype.selectHandles = function(select) {
    this.center.select(select);
    this.radiusX.select(select);
    this.radiusY.select(select);
};
Ellipse.prototype.showHandles = function(state) {
    this.center.show(state);
    this.radiusX.show(state);
    this.radiusY.show(state);
};
Ellipse.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Ellipse", [this.center.point, parseFloat(this.svgNode.getAttributeNS(null, "rx")), parseFloat(this.svgNode.getAttributeNS(null, "ry"))]);
};

Handle.prototype = new Shape();
Handle.prototype.constructor = Handle;
Handle.superclass = Shape.prototype;
Handle.NO_CONSTRAINTS = 0;
Handle.CONSTRAIN_X = 1;
Handle.CONSTRAIN_Y = 2;
Handle.SHAPE_SIZE = 8;
Handle.SHAPE_SIZE_HALF = 4;
function Handle(x, y, owner) {
    if (arguments.length > 0) {
        this.init(x, y, owner);
    }
}

Handle.prototype.init = function(x, y, owner) {
    Handle.superclass.init.call(this, null);
    this.point = new Point2D(x, y);
    this.owner = owner;
    this.constrain = Handle.NO_CONSTRAINTS;
};
Handle.prototype.realize = function() {
    if (this.svgNode == null) {
        var handle = document.createElementNS(svgns, "rect");
        var parent;
        if (this.owner != null && this.owner.svgNode != null) {
            parent = this.owner.svgNode.parentNode;
        } else {
            alert('Hanlde.realize svgelement');
            parent = _svgElement;
        }
        if (!isNaN(this.point.x))
            handle.setAttributeNS(null, "x", this.point.x - Handle.SHAPE_SIZE_HALF);
        if (!isNaN(this.point.y))
            handle.setAttributeNS(null, "y", this.point.y - Handle.SHAPE_SIZE_HALF);

        handle.setAttributeNS(null, "width", Handle.SHAPE_SIZE);
        handle.setAttributeNS(null, "height", Handle.SHAPE_SIZE);
        handle.setAttributeNS(null, "stroke", "black");
        handle.setAttributeNS(null, "fill", "white");
        handle.addEventListener("mousedown", this, false);
        parent.appendChild(handle);
        this.svgNode = handle;
        this.show(this.visible);
    }
};

Handle.prototype.unrealize = function() {
    this.svgNode.removeEventListener("mousedown", this, false);
    this.svgNode.parentNode.removeChild(this.svgNode);
};
Handle.prototype.translate = function(delta) {
    if (this.constrain == Handle.CONSTRAIN_X) {
        this.point.x += delta.x;
    } else if (this.constrain == Handle.CONSTRAIN_Y) {
        this.point.y += delta.y;
    } else {
        this.point.addEquals(delta);
    }
    this.refresh();
};

Handle.prototype.refresh = function() {
    if (!isNaN(this.point.x))
        this.svgNode.setAttributeNS(null, "x", this.point.x - 2);
    if (!isNaN(this.point.y))
        this.svgNode.setAttributeNS(null, "y", this.point.y - 2);
};

Handle.prototype.select = function(state) {
    Handle.superclass.select.call(this, state);
    if (state) {
        this.svgNode.setAttributeNS(null, "fill", "black");
        this.svgNode.setAttributeNS(null, "stroke", "white");
    } else {
        this.svgNode.setAttributeNS(null, "fill", "white");
        this.svgNode.setAttributeNS(null, "stroke", "black");
    }
};

Handle.prototype.mousedown = function(e) {
    if (!this.locked) {
        if (e.shiftKey) {
            if (this.selected) {
                mouser.unregister(this);
            } else {
                mouser.register(this);
                mouser.beginDrag(e);
            }
        } else {
            if (!this.selected) {
                var owner = this.owner;
                mouser.unregisterAll();
                mouser.register(this);
            }
            mouser.beginDrag(e);
        }
    }
};

Lever.prototype = new Shape();
Lever.prototype.constructor = Lever;
Lever.superclass = Shape.prototype;
function Lever(x1, y1, x2, y2, owner) {
    if (arguments.length > 0) {
        this.init(x1, y1, x2, y2, owner);
    }
}

Lever.prototype.init = function(x1, y1, x2, y2, owner) {
    Lever.superclass.init.call(this, null);
    this.point = new Handle(x1, y1, this);
    this.lever = new LeverHandle(x2, y2, this);
    this.owner = owner;
};

Lever.prototype.realize = function() {
    if (this.svgNode == null) {
        var line = document.createElementNS(svgns, "line");
        var parent;
        if (this.owner != null && this.owner.svgNode != null) {
            parent = this.owner.svgNode.parentNode;
        } else {
            alert('Lever.realize svgelement');
            parent = _svgElement;
        }
        line.setAttributeNS(null, "x1", this.point.point.x);
        line.setAttributeNS(null, "y1", this.point.point.y);
        line.setAttributeNS(null, "x2", this.lever.point.x);
        line.setAttributeNS(null, "y2", this.lever.point.y);
        line.setAttributeNS(null, "stroke", "black");
        parent.appendChild(line);
        this.svgNode = line;
        this.point.realize();
        this.lever.realize();
        this.show(this.visible);
    }
};

Lever.prototype.refresh = function() {
    this.svgNode.setAttributeNS(null, "x1", this.point.point.x);
    this.svgNode.setAttributeNS(null, "y1", this.point.point.y);
    this.svgNode.setAttributeNS(null, "x2", this.lever.point.x);
    this.svgNode.setAttributeNS(null, "y2", this.lever.point.y);
};
LeverHandle.prototype = new Handle();
LeverHandle.prototype.constructor = LeverHandle;
LeverHandle.superclass = Handle.prototype;
function LeverHandle(x, y, owner) {
    if (arguments.length > 0) {
        this.init(x, y, owner);
    }
}

LeverHandle.prototype.realize = function() {
    if (this.svgNode == null) {
        var handle = document.createElementNS(svgns, "circle");
        var parent;
        if (this.owner != null && this.owner.svgNode != null) {
            parent = this.owner.svgNode.parentNode;
        } else {
            parent = _svgElement;
        }
        handle.setAttributeNS(null, "cx", this.point.x);
        handle.setAttributeNS(null, "cy", this.point.y);
        handle.setAttributeNS(null, "r", 2.5);
        handle.setAttributeNS(null, "fill", "black");
        handle.addEventListener("mousedown", this, false);
        parent.appendChild(handle);
        this.svgNode = handle;
        this.show(this.visible);
    }
};

LeverHandle.prototype.refresh = function() {
    this.svgNode.setAttributeNS(null, "cx", this.point.x);
    this.svgNode.setAttributeNS(null, "cy", this.point.y);
};

LeverHandle.prototype.select = function(state) {
    LeverHandle.superclass.select.call(this, state);
    this.svgNode.setAttributeNS(null, "fill", "black");
};

Line.prototype = new Shape();
Line.prototype.constructor = Line;
Line.superclass = Shape.prototype;
function Line(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Line.prototype.init = function(svgNode) {
    if (svgNode == null || svgNode.localName != "line")
        throw new Error("Line.init: Invalid localName: " + svgNode.localName);
    Line.superclass.init.call(this, svgNode);
    var x1 = parseFloat(svgNode.getAttributeNS(null, "x1"));
    var y1 = parseFloat(svgNode.getAttributeNS(null, "y1"));
    var x2 = parseFloat(svgNode.getAttributeNS(null, "x2"));
    var y2 = parseFloat(svgNode.getAttributeNS(null, "y2"));
    this.p1 = new Handle(x1, y1, this);
    this.p2 = new Handle(x2, y2, this);
};
Line.prototype.realize = function() {
    this.p1.realize();
    this.p2.realize();
    this.p1.show(false);
    this.p2.show(false);
    this.svgNode.addEventListener("mousedown", this, false);
};
Line.prototype.refresh = function() {
    this.svgNode.setAttributeNS(null, "x1", this.p1.point.x);
    this.svgNode.setAttributeNS(null, "y1", this.p1.point.y);
    this.svgNode.setAttributeNS(null, "x2", this.p2.point.x);
    this.svgNode.setAttributeNS(null, "y2", this.p2.point.y);
};
Line.prototype.registerHandles = function() {
    mouser.register(this.p1);
    mouser.register(this.p2);
};
Line.prototype.unregisterHandles = function() {
    mouser.unregister(this.p1);
    mouser.unregister(this.p2);
};
Line.prototype.selectHandles = function(select) {
    this.p1.select(select);
    this.p2.select(select);
};
Line.prototype.showHandles = function(state) {
    this.p1.show(state);
    this.p2.show(state);
};
Line.prototype.cut = function(t) {
    var cutPoint = this.p1.point.lerp(this.p2.point, t);
    var newLine = this.svgNode.cloneNode(true);
    this.p2.point.setFromPoint(cutPoint);
    this.p2.update();
    if (this.svgNode.nextSibling != null)
        this.svgNode.parentNode.insertBefore(newLine, this.svgNode.nextSibling);
    else
        this.svgNode.parentNode.appendChild(newLine);
    var line = new Line(newLine);
    line.realize();
    line.p1.point.setFromPoint(cutPoint);
    line.p1.update();
};
Line.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Line", [this.p1.point, this.p2.point]);
};
function Token(type, text) {
    if (arguments.length > 0) {
        this.init(type, text);
    }
}

Token.prototype.init = function(type, text) {
    this.type = type;
    this.text = text;
};
Token.prototype.typeis = function(type) {
    return this.type == type;
};

Path.prototype = new Shape();
Path.prototype.constructor = Path;
Path.superclass = Shape.prototype;
Path.COMMAND = 0;
Path.NUMBER = 1;
Path.EOD = 2;
Path.PARAMS = {
    A : ["rx", "ry", "x-axis-rotation", "large-arc-flag", "sweep-flag", "x", "y"],
    a : ["rx", "ry", "x-axis-rotation", "large-arc-flag", "sweep-flag", "x", "y"],
    C : ["x1", "y1", "x2", "y2", "x", "y"],
    c : ["x1", "y1", "x2", "y2", "x", "y"],
    H : ["x"],
    h : ["x"],
    L : ["x", "y"],
    l : ["x", "y"],
    M : ["x", "y"],
    m : ["x", "y"],
    Q : ["x1", "y1", "x", "y"],
    q : ["x1", "y1", "x", "y"],
    S : ["x2", "y2", "x", "y"],
    s : ["x2", "y2", "x", "y"],
    T : ["x", "y"],
    t : ["x", "y"],
    V : ["y"],
    v : ["y"],
    Z : [],
    z : []
};
function Path(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Path.prototype.init = function(svgNode) {
    if (svgNode == null || svgNode.localName != "path")
        throw new Error("Path.init: Invalid localName: " + svgNode.localName);
    Path.superclass.init.call(this, svgNode);
    this.segments = null;
    this.parseData(svgNode.getAttributeNS(null, "d"));
};
Path.prototype.realize = function() {
    for (var i = 0; i < this.segments.length; i++) {
        this.segments[i].realize();
    }
};
Path.prototype.unrealize = function() {
    for (var i = 0; i < this.segments.length; i++) {
        this.segments[i].unrealize();
    }
    this.svgNode.parentNode.removeChild(this.svgNode);
};
;
Path.prototype.refresh = function() {
    var d = new Array();
    for (var i = 0; i < this.segments.length; i++) {
        d.push(this.segments[i].toString());
    }
    this.svgNode.setAttributeNS(null, "d", d.join(" "));
};

Path.prototype.registerHandles = function() {
    for (var i = 0; i < this.segments.length; i++) {
        this.segments[i].registerHandles();
    }
};

Path.prototype.unregisterHandles = function() {
    for (var i = 0; i < this.segments.length; i++) {
        this.segments[i].unregisterHandles();
    }
};

Path.prototype.selectHandles = function(select) {
    for (var i = 0; i < this.segments.length; i++) {
        this.segments[i].selectHandles(select);
    }
};

Path.prototype.showHandles = function(state) {
    Path.superclass.showHandles.call(this, state);
    for (var i = 0; i < this.segments.length; i++) {
        this.segments[i].showHandles(state);
    }
};

Path.prototype.appendPathSegment = function(segment) {
    segment.previous = this.segments[this.segments.length - 1];
    this.segments.push(segment);
};

Path.prototype.parseData = function(d) {
    var tokens = this.tokenize(d);
    var index = 0;
    var token = tokens[index];
    var mode = "BOD";
    this.segments = new Array();
    while (!token.typeis(Path.EOD)) {
        var param_length;
        var params = new Array();
        if (mode == "BOD") {
            if (token.text == "M" || token.text == "m") {
                index++;
                param_length = Path.PARAMS[token.text].length;
                mode = token.text;
            } else {
                throw new Error("Path data must begin with a moveto command");
            }
        } else {
            if (token.typeis(Path.NUMBER)) {
                param_length = Path.PARAMS[mode].length;
            } else {
                index++;
                param_length = Path.PARAMS[token.text].length;
                mode = token.text;
            }
        }
        if ((index + param_length) < tokens.length) {
            for (var i = index; i < index + param_length; i++) {
                var number = tokens[i];
                if (number.typeis(Path.NUMBER))
                    params[params.length] = number.text;
                else
                    throw new Error("Parameter type is not a number: " + mode + "," + number.text);
            }
            var segment;
            var length = this.segments.length;
            var previous = (length == 0) ? null : this.segments[length - 1];
            switch(mode) {
                case"A":
                    segment = new AbsoluteArcPath(params, this, previous);
                    break;
                case"C":
                    segment = new AbsoluteCurveto3(params, this, previous);
                    break;
                case"c":
                    segment = new RelativeCurveto3(params, this, previous);
                    break;
                case"H":
                    segment = new AbsoluteHLineto(params, this, previous);
                    break;
                case"L":
                    segment = new AbsoluteLineto(params, this, previous);
                    break;
                case"l":
                    segment = new RelativeLineto(params, this, previous);
                    break;
                case"M":
                    segment = new AbsoluteMoveto(params, this, previous);
                    break;
                case"m":
                    segment = new RelativeMoveto(params, this, previous);
                    break;
                case"Q":
                    segment = new AbsoluteCurveto2(params, this, previous);
                    break;
                case"q":
                    segment = new RelativeCurveto2(params, this, previous);
                    break;
                case"S":
                    segment = new AbsoluteSmoothCurveto3(params, this, previous);
                    break;
                case"s":
                    segment = new RelativeSmoothCurveto3(params, this, previous);
                    break;
                case"T":
                    segment = new AbsoluteSmoothCurveto2(params, this, previous);
                    break;
                case"t":
                    segment = new RelativeSmoothCurveto2(params, this, previous);
                    break;
                case"Z":
                    segment = new RelativeClosePath(params, this, previous);
                    break;
                case"z":
                    segment = new RelativeClosePath(params, this, previous);
                    break;
                default:
                    throw new Error("Unsupported segment type: " + mode);
            };
            this.segments.push(segment);
            index += param_length;
            token = tokens[index];
            if (mode == "M")
                mode = "L";
            if (mode == "m")
                mode = "l";
        } else {
            throw new Error("Path data ended before all parameters were found");
        }
    }
};

Path.prototype.tokenize = function(d) {
    var tokens = new Array();
    while (d != "") {
        if (d.match(/^([ \t\r\n,]+)/)) {
            d = d.substr(RegExp.$1.length);
        } else if (d.match(/^([aAcChHlLmMqQsStTvVzZ])/)) {
            tokens[tokens.length] = new Token(Path.COMMAND, RegExp.$1);
            d = d.substr(RegExp.$1.length);
        } else if (d.match(/^(([-+]?[0-9]+(\.[0-9]*)?|[-+]?\.[0-9]+)([eE][-+]?[0-9]+)?)/)) {
            tokens[tokens.length] = new Token(Path.NUMBER, parseFloat(RegExp.$1));
            d = d.substr(RegExp.$1.length);
        } else {
            throw new Error("Unrecognized segment command: " + d);
        }
    }
    tokens[tokens.length] = new Token(Path.EOD, null);
    return tokens;
};
/*  // DO WE NEED INTERESECTION ALGOS?
 Path.prototype.intersectShape=function(shape){
 var result=new Intersection("No Intersection");
 for(var i=0;i<this.segments.length;i++){
 var inter=Intersection.intersectShapes(this.segments[i],shape);
 result.appendPoints(inter.points);
 }
 if(result.points.length>0)
 result.status="Intersection";
 return result;
 };
 */
Path.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Path", []);
};

function AbsolutePathSegment(command, params, owner, previous) {
    if (arguments.length > 0)
        this.init(command, params, owner, previous);
};

AbsolutePathSegment.prototype.init = function(command, params, owner, previous) {
    this.command = command;
    this.owner = owner;
    this.previous = previous;
    this.handles = new Array();
    var index = 0;
    while (index < params.length) {
        var handle = new Handle(params[index], params[index + 1], owner);
        this.handles.push(handle);
        index += 2;
    }
};

AbsolutePathSegment.prototype.realize = function() {
    for (var i = 0; i < this.handles.length; i++) {
        var handle = this.handles[i];
        handle.realize();
        handle.show(false);
    }
};
AbsolutePathSegment.prototype.unrealize = function() {
    for (var i = 0; i < this.handles.length; i++) {
        this.handles[i].unrealize();
    }
};
AbsolutePathSegment.prototype.registerHandles = function() {
    for (var i = 0; i < this.handles.length; i++) {
        mouser.register(this.handles[i]);
    }
};
AbsolutePathSegment.prototype.unregisterHandles = function() {
    for (var i = 0; i < this.handles.length; i++) {
        mouser.unregister(this.handles[i]);
    }
};
AbsolutePathSegment.prototype.selectHandles = function(select) {
    for (var i = 0; i < this.handles.length; i++) {
        this.handles[i].select(select);
    }
};
AbsolutePathSegment.prototype.showHandles = function(state) {
    for (var i = 0; i < this.handles.length; i++) {
        this.handles[i].show(state);
    }
};
AbsolutePathSegment.prototype.toString = function() {
    var points = new Array();
    var command = "";
    if (this.previous == null || this.previous.constructor != this.constuctor)
        command = this.command;
    for (var i = 0; i < this.handles.length; i++) {
        points.push(this.handles[i].point.toString());
    }
    return command + points.join(" ");
};
AbsolutePathSegment.prototype.getLastPoint = function() {
    return this.handles[this.handles.length - 1].point;
};
AbsolutePathSegment.prototype.getIntersectionParams = function() {
    return null;
};

AbsoluteArcPath.prototype = new AbsolutePathSegment();
AbsoluteArcPath.prototype.constructor = AbsoluteArcPath;
AbsoluteArcPath.superclass = AbsolutePathSegment.prototype;
function AbsoluteArcPath(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("A", params, owner, previous);
    }
}

AbsoluteArcPath.prototype.init = function(command, params, owner, previous) {
    var point = new Array();
    var y = params.pop();
    var x = params.pop();
    point.push(x, y);
    AbsoluteArcPath.superclass.init.call(this, command, point, owner, previous);
    this.rx = parseFloat(params.shift());
    this.ry = parseFloat(params.shift());
    this.angle = parseFloat(params.shift());
    this.arcFlag = parseFloat(params.shift());
    this.sweepFlag = parseFloat(params.shift());
};
AbsoluteArcPath.prototype.toString = function() {
    var points = new Array();
    var command = "";
    if (this.previous.constructor != this.constuctor)
        command = this.command;
    return command + [this.rx, this.ry, this.angle, this.arcFlag, this.sweepFlag, this.handles[0].point.toString()].join(",");
};
AbsoluteArcPath.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Ellipse", [this.getCenter(), this.rx, this.ry]);
};
AbsoluteArcPath.prototype.getCenter = function() {
    var startPoint = this.previous.getLastPoint();
    var endPoint = this.handles[0].point;
    var rx = this.rx;
    var ry = this.ry;
    var angle = this.angle * Math.PI / 180;
    var c = Math.cos(angle);
    var s = Math.sin(angle);
    var TOLERANCE = 1e-6;
    var halfDiff = startPoint.subtract(endPoint).divide(2);
    var x1p = halfDiff.x * c + halfDiff.y * s;
    var y1p = halfDiff.x * -s + halfDiff.y * c;
    var x1px1p = x1p * x1p;
    var y1py1p = y1p * y1p;
    var lambda = (x1px1p / (rx * rx) ) + (y1py1p / (ry * ry));
    if (lambda > 1) {
        var factor = Math.sqrt(lambda);
        rx *= factor;
        ry *= factor;
    }
    var rxrx = rx * rx;
    var ryry = ry * ry;
    var rxy1 = rxrx * y1py1p;
    var ryx1 = ryry * x1px1p;
    var factor = (rxrx * ryry - rxy1 - ryx1) / (rxy1 + ryx1);
    if (Math.abs(factor) < TOLERANCE)
        factor = 0;
    var sq = Math.sqrt(factor);
    if (this.arcFlag == this.sweepFlag)
        sq = -sq;
    var mid = startPoint.add(endPoint).divide(2);
    var cxp = sq * rx * y1p / ry;
    var cyp = sq * -ry * x1p / rx;
    return new Point2D(cxp * c - cyp * s + mid.x, cxp * s + cyp * c + mid.y);
};

AbsoluteCurveto2.prototype = new AbsolutePathSegment();

AbsoluteCurveto2.prototype.constructor = AbsoluteCurveto2;

AbsoluteCurveto2.superclass = AbsolutePathSegment.prototype;

function AbsoluteCurveto2(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("Q", params, owner, previous);
    }
}

AbsoluteCurveto2.prototype.getControlPoint = function() {
    return this.handles[0].point;
};

AbsoluteCurveto2.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Bezier2", [this.previous.getLastPoint(), this.handles[0].point, this.handles[1].point]);
};

AbsoluteCurveto3.prototype = new AbsolutePathSegment();
AbsoluteCurveto3.prototype.constructor = AbsoluteCurveto3;
AbsoluteCurveto3.superclass = AbsolutePathSegment.prototype;
function AbsoluteCurveto3(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("C", params, owner, previous);
    }
}

AbsoluteCurveto3.prototype.getLastControlPoint = function() {
    return this.handles[1].point;
};
AbsoluteCurveto3.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Bezier3", [this.previous.getLastPoint(), this.handles[0].point, this.handles[1].point, this.handles[2].point]);
};
AbsoluteHLineto.prototype = new AbsolutePathSegment();
AbsoluteHLineto.prototype.constructor = AbsoluteHLineto;
AbsoluteHLineto.superclass = AbsolutePathSegment.prototype;
function AbsoluteHLineto(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("H", params, owner, previous);
    }
}

AbsoluteHLineto.prototype.init = function(command, params, owner, previous) {
    var prevPoint = previous.getLastPoint();
    var point = new Array();
    point.push(params.pop(), prevPoint.y);
    AbsoluteHLineto.superclass.init.call(this, command, point, owner, previous);
};
AbsoluteHLineto.prototype.toString = function() {
    var points = new Array();
    var command = "";
    if (this.previous.constructor != this.constuctor)
        command = this.command;
    return command + this.handles[0].point.x;
};
AbsoluteLineto.prototype = new AbsolutePathSegment();
AbsoluteLineto.prototype.constructor = AbsoluteLineto;
AbsoluteLineto.superclass = AbsolutePathSegment.prototype;
function AbsoluteLineto(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("L", params, owner, previous);
    }
}

AbsoluteLineto.prototype.toString = function() {
    var points = new Array();
    var command = "";
    if (this.previous.constructor != this.constuctor)
        if (this.previous.constructor != AbsoluteMoveto)
            command = this.command;
    return command + this.handles[0].point.toString();
};
AbsoluteLineto.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Line", [this.previous.getLastPoint(), this.handles[0].point]);
};
AbsoluteMoveto.prototype = new AbsolutePathSegment();
AbsoluteMoveto.prototype.constructor = AbsoluteMoveto;
AbsoluteMoveto.superclass = AbsolutePathSegment.prototype;
function AbsoluteMoveto(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("M", params, owner, previous);
    }
}

AbsoluteMoveto.prototype.toString = function() {
    return "M" + this.handles[0].point.toString();
};
AbsoluteSmoothCurveto2.prototype = new AbsolutePathSegment();
AbsoluteSmoothCurveto2.prototype.constructor = AbsoluteSmoothCurveto2;
AbsoluteSmoothCurveto2.superclass = AbsolutePathSegment.prototype;
function AbsoluteSmoothCurveto2(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("T", params, owner, previous);
    }
}

AbsoluteSmoothCurveto2.prototype.getControlPoint = function() {
    var lastPoint = this.previous.getLastPoint();
    var point;
    if (this.previous.command.match(/^[QqTt]$/)) {
        var ctrlPoint = this.previous.getControlPoint();
        var diff = ctrlPoint.subtract(lastPoint);
        point = lastPoint.subtract(diff);
    } else {
        point = lastPoint;
    }
    return point;
};
AbsoluteSmoothCurveto2.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Bezier2", [this.previous.getLastPoint(), this.getControlPoint(), this.handles[0].point]);
};
AbsoluteSmoothCurveto3.prototype = new AbsolutePathSegment();
AbsoluteSmoothCurveto3.prototype.constructor = AbsoluteSmoothCurveto3;
AbsoluteSmoothCurveto3.superclass = AbsolutePathSegment.prototype;
function AbsoluteSmoothCurveto3(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("S", params, owner, previous);
    }
}

AbsoluteSmoothCurveto3.prototype.getFirstControlPoint = function() {
    var lastPoint = this.previous.getLastPoint();
    var point;
    if (this.previous.command.match(/^[SsCc]$/)) {
        var lastControl = this.previous.getLastControlPoint();
        var diff = lastControl.subtract(lastPoint);
        point = lastPoint.subtract(diff);
    } else {
        point = lastPoint;
    }
    return point;
};
AbsoluteSmoothCurveto3.prototype.getLastControlPoint = function() {
    return this.handles[0].point;
};
AbsoluteSmoothCurveto3.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Bezier3", [this.previous.getLastPoint(), this.getFirstControlPoint(), this.handles[0].point, this.handles[1].point]);
};
RelativePathSegment.prototype = new AbsolutePathSegment();
RelativePathSegment.prototype.constructor = RelativePathSegment;
RelativePathSegment.superclass = AbsolutePathSegment.prototype;
function RelativePathSegment(command, params, owner, previous) {
    if (arguments.length > 0)
        this.init(command, params, owner, previous);
}

RelativePathSegment.prototype.init = function(command, params, owner, previous) {
    this.command = command;
    this.owner = owner;
    this.previous = previous;
    this.handles = new Array();
    var lastPoint;
    if (this.previous)
        lastPoint = this.previous.getLastPoint();
    else
        lastPoint = new Point2D(0, 0);
    var index = 0;
    while (index < params.length) {
        var handle = new Handle(lastPoint.x + params[index], lastPoint.y + params[index + 1], owner);
        this.handles.push(handle);
        index += 2;
    }
};
RelativePathSegment.prototype.toString = function() {
    var points = new Array();
    var command = "";
    var lastPoint;
    if (this.previous)
        lastPoint = this.previous.getLastPoint();
    else
        lastPoint = new Point2D(0, 0);
    if (this.previous == null || this.previous.constructor != this.constructor)
        command = this.command;
    for (var i = 0; i < this.handles.length; i++) {
        var point = this.handles[i].point.subtract(lastPoint);
        points.push(point.toString());
    }
    return command + points.join(" ");
};
RelativeClosePath.prototype = new RelativePathSegment();
RelativeClosePath.prototype.constructor = RelativeClosePath;
RelativeClosePath.superclass = RelativePathSegment.prototype;
function RelativeClosePath(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("z", params, owner, previous);
    }
}

RelativeClosePath.prototype.getLastPoint = function() {
    var current = this.previous;
    var point;
    while (current) {
        if (current.command.match(/^[mMzZ]$/)) {
            point = current.getLastPoint();
            break;
        }
        current = current.previous;
    }
    return point;
};
RelativeClosePath.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Line", [this.previous.getLastPoint(), this.getLastPoint()]);
};
RelativeCurveto2.prototype = new RelativePathSegment();
RelativeCurveto2.prototype.constructor = RelativeCurveto2;
RelativeCurveto2.superclass = RelativePathSegment.prototype;
function RelativeCurveto2(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("q", params, owner, previous);
    }
}

RelativeCurveto2.prototype.getControlPoint = function() {
    return this.handles[0].point;
};
RelativeCurveto2.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Bezier2", [this.previous.getLastPoint(), this.handles[0].point, this.handles[1].point]);
};
RelativeCurveto3.prototype = new RelativePathSegment();
RelativeCurveto3.prototype.constructor = RelativeCurveto3;
RelativeCurveto3.superclass = RelativePathSegment.prototype;
function RelativeCurveto3(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("c", params, owner, previous);
    }
}

RelativeCurveto3.prototype.getLastControlPoint = function() {
    return this.handles[1].point;
};
RelativeCurveto3.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Bezier3", [this.previous.getLastPoint(), this.handles[0].point, this.handles[1].point, this.handles[2].point]);
};
RelativeLineto.prototype = new RelativePathSegment();
RelativeLineto.prototype.constructor = RelativeLineto;
RelativeLineto.superclass = RelativePathSegment.prototype;
function RelativeLineto(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("l", params, owner, previous);
    }
}

RelativeLineto.prototype.toString = function() {
    var points = new Array();
    var command = "";
    var lastPoint;
    var point;
    if (this.previous)
        lastPoint = this.previous.getLastPoint();
    else
        lastPoint = new Point(0, 0);
    point = this.handles[0].point.subtract(lastPoint);
    if (this.previous.constructor != this.constuctor)
        if (this.previous.constructor != RelativeMoveto)
            cmd = this.command;
    return cmd + point.toString();
};
RelativeLineto.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Line", [this.previous.getLastPoint(), this.handles[0].point]);
};
RelativeMoveto.prototype = new RelativePathSegment();
RelativeMoveto.prototype.constructor = RelativeMoveto;
RelativeMoveto.superclass = RelativePathSegment.prototype;
function RelativeMoveto(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("m", params, owner, previous);
    }
}

RelativeMoveto.prototype.toString = function() {
    return "m" + this.handles[0].point.toString();
};
RelativeSmoothCurveto2.prototype = new RelativePathSegment();
RelativeSmoothCurveto2.prototype.constructor = RelativeSmoothCurveto2;
RelativeSmoothCurveto2.superclass = RelativePathSegment.prototype;
function RelativeSmoothCurveto2(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("t", params, owner, previous);
    }
}

RelativeSmoothCurveto2.prototype.getControlPoint = function() {
    var lastPoint = this.previous.getLastPoint();
    var point;
    if (this.previous.command.match(/^[QqTt]$/)) {
        var ctrlPoint = this.previous.getControlPoint();
        var diff = ctrlPoint.subtract(lastPoint);
        point = lastPoint.subtract(diff);
    } else {
        point = lastPoint;
    }
    return point;
};
RelativeSmoothCurveto2.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Bezier2", [this.previous.getLastPoint(), this.getControlPoint(), this.handles[0].point]);
};
RelativeSmoothCurveto3.prototype = new RelativePathSegment();
RelativeSmoothCurveto3.prototype.constructor = RelativeSmoothCurveto3;
RelativeSmoothCurveto3.superclass = RelativePathSegment.prototype;
function RelativeSmoothCurveto3(params, owner, previous) {
    if (arguments.length > 0) {
        this.init("s", params, owner, previous);
    }
}

RelativeSmoothCurveto3.prototype.getFirstControlPoint = function() {
    var lastPoint = this.previous.getLastPoint();
    var point;
    if (this.previous.command.match(/^[SsCc]$/)) {
        var lastControl = this.previous.getLastControlPoint();
        var diff = lastControl.subtract(lastPoint);
        point = lastPoint.subtract(diff);
    } else {
        point = lastPoint;
    }
    return point;
};
RelativeSmoothCurveto3.prototype.getLastControlPoint = function() {
    return this.handles[0].point;
};
RelativeSmoothCurveto3.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Bezier3", [this.previous.getLastPoint(), this.getFirstControlPoint(), this.handles[0].point, this.handles[1].point]);
};

Polygon.prototype = new Shape();
Polygon.prototype.constructor = Polygon;
Polygon.superclass = Shape.prototype;

function Polygon(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Polygon.prototype.init = function(svgNode) {
    if (svgNode.localName == "polygon") {
        Polygon.superclass.init.call(this, svgNode);

        var pointStr = svgNode.getAttributeNS(null, "points"), points = [];

        if (pointStr)
            points = pointStr.trim().split(/[\s,]+/);

        this.handles = new Array();
        for (var i = 0; i < points.length; i += 2) {
            var x = parseFloat(points[i]);
            var y = parseFloat(points[i + 1]);
            this.handles.push(new Handle(x, y, this));
        }
    } else {
        throw new Error("Polygon.init: Invalid SVG Node: " + svgNode.localName);
    }
};
Polygon.prototype.realize = function() {
    if (this.svgNode != null) {
        for (var i = 0; i < this.handles.length; i++) {
            this.handles[i].realize();
            this.handles[i].show(false);
        }
        //this.svgNode.addEventListener("mousedown",this,false);}
    }
};

Polygon.prototype.unrealize = function() {
    if (this.svgNode != null) {
        for (var i = 0; i < this.handles.length; i++) {
            this.handles[i].unrealize();
        }
        this.svgNode.parentNode.removeChild(this.svgNode);
    }
};

Polygon.prototype.refresh = function() {
    var points = new Array();
    for (var i = 0; i < this.handles.length; i++) {
        points.push(this.handles[i].point.toString());
    }
    this.svgNode.setAttributeNS(null, "points", points.join(" "));
};

Polygon.prototype.registerHandles = function() {
    for (var i = 0; i < this.handles.length; i++)
        mouser.register(this.handles[i]);
};

Polygon.prototype.unregisterHandles = function() {
    for (var i = 0; i < this.handles.length; i++)
        mouser.unregister(this.handles[i]);
};

Polygon.prototype.selectHandles = function(select) {
    for (var i = 0; i < this.handles.length; i++)
        this.handles[i].select(select);
};

Polygon.prototype.showHandles = function(state) {
    for (var i = 0; i < this.handles.length; i++)
        this.handles[i].show(state);
};

Polygon.prototype.pointInPolygon = function(point) {
    var length = this.handles.length;
    var counter = 0;
    var x_inter;
    var p1 = this.handles[0].point;
    for (var i = 1; i <= length; i++) {
        var p2 = this.handles[i % length].point;
        if (point.y > Math.min(p1.y, p2.y)) {
            if (point.y <= Math.max(p1.y, p2.y)) {
                if (point.x <= Math.max(p1.x, p2.x)) {
                    if (p1.y != p2.y) {
                        x_inter = (point.y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x;
                        if (p1.x == p2.x || point.x <= x_inter) {
                            counter++;
                        }
                    }
                }
            }
        }
        p1 = p2;
    }
    return (counter % 2 == 1);
};

Polygon.prototype.getIntersectionParams = function() {
    var points = new Array();
    for (var i = 0; i < this.handles.length; i++) {
        points.push(this.handles[i].point);
    }
    return new IntersectionParams("Polygon", [points]);
};

Polygon.prototype.getArea = function() {
    var area = 0;
    var length = this.handles.length;
    var neg = 0;
    var pos = 0;
    for (var i = 0; i < length; i++) {
        var h1 = this.handles[i].point;
        var h2 = this.handles[(i + 1) % length].point;
        area += (h1.x * h2.y - h2.x * h1.y);
    }
    return area / 2;
};

Polygon.prototype.getCentroid = function() {
    var length = this.handles.length;
    var area6x = 6 * this.getArea();
    var x_sum = 0;
    var y_sum = 0;
    for (var i = 0; i < length; i++) {
        var p1 = this.handles[i].point;
        var p2 = this.handles[(i + 1) % length].point;
        var cross = (p1.x * p2.y - p2.x * p1.y);
        x_sum += (p1.x + p2.x) * cross;
        y_sum += (p1.y + p2.y) * cross;
    }
    return new Point2D(x_sum / area6x, y_sum / area6x);
};

Polygon.prototype.isClockwise = function() {
    return this.getArea() < 0;
};

Polygon.prototype.isCounterClockwise = function() {
    return this.getArea() > 0;
};

Polygon.prototype.isConcave = function() {
    var positive = 0;
    var negative = 0;
    var length = this.handles.length;
    for (var i = 0; i < length; i++) {
        var p0 = this.handles[i].point;
        var p1 = this.handles[(i + 1) % length].point;
        var p2 = this.handles[(i + 2) % length].point;
        var v0 = Vector2D.fromPoints(p0, p1);
        var v1 = Vector2D.fromPoints(p1, p2);
        var cross = v0.cross(v1);
        if (cross < 0) {
            negative++;
        } else {
            positive++;
        }
    }
    return (negative != 0 && positive != 0);
};

Polygon.prototype.isConvex = function() {
    return !this.isConcave();
};

Polyline.prototype = new Polygon();
Polyline.prototype.constructor = Polyline;
Polyline.superclass = Polygon.prototype;

function Polyline(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Polyline.prototype.init = function(svgNode) {
    if (svgNode.localName == "polyline") {
        Polygon.superclass.init.call(this, svgNode);

        var pointStr = svgNode.getAttributeNS(null, "points"), points = [];

        if (pointStr)
            points = pointStr.trim().split(/[\s,]+/);

        this.handles = new Array();
        for (var i = 0; i < points.length; i += 2) {
            var x = parseFloat(points[i]);
            var y = parseFloat(points[i + 1]);
            this.handles.push(new Handle(x, y, this));
        }
    } else {
        throw new Error("Polyline.init: Invalid SVG Node: " + svgNode.localName);
    }
};

Pnt.prototype = new Shape();
Pnt.prototype.constructor = Pnt;
Pnt.superclass = Shape.prototype;

function Pnt(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Pnt.prototype.init = function(svgNode) {
    if (svgNode.localName == "rect") {
        Pnt.superclass.init.call(this, svgNode);
        var x = parseFloat(svgNode.getAttributeNS(null, "x"));
        var y = parseFloat(svgNode.getAttributeNS(null, "y"));
        var width = parseFloat(svgNode.getAttributeNS(null, "width"));
        var height = parseFloat(svgNode.getAttributeNS(null, "height"));
        this.p = new Handle(x + (width / 2.0), y + (height / 2.0), this);
    } else {
        throw new Error("Pnt.init: Invalid SVG Node: " + svgNode.localName);
    }
};

Pnt.prototype.enhance = function(visible) {
    if (visible) {
        this.svgNode.setAttributeNS(null, 'stroke', 'black');
        this.svgNode.setAttributeNS(null, "fill", 'yellow');
        this.svgNode.setAttributeNS(null, "stroke-width", '3');
    } else {
        //this.svgNode.setAttributeNS(null, 'fill-opacity', mode?1.0:0.7);
        this.svgNode.setAttributeNS(null, 'stroke', 'black');
        this.svgNode.setAttributeNS(null, "fill", 'orangered');
        this.svgNode.setAttributeNS(null, "stroke-width", '1');
    }
};

Pnt.prototype.unrealize = function() {
    if (this.svgNode != null) {
        this.p.unrealize();
        this.svgNode.parentNode.removeChild(this.svgNode);
    }
};
Pnt.prototype.realize = function() {
    if (this.svgNode != null) {
        this.p.realize();
        this.p.show(false);
    }
};

Pnt.prototype.refresh = function() {
    var x = this.p.point.x;
    var y = this.p.point.y;
    this.svgNode.setAttributeNS(null, "x", x - 3);
    this.svgNode.setAttributeNS(null, "y", y - 3);
};
Pnt.prototype.registerHandles = function() {
    mouser.register(this.p);
};
Pnt.prototype.unregisterHandles = function() {
    mouser.unregister(this.p);
};
Pnt.prototype.selectHandles = function(select) {
    this.p.select(select);
};
Pnt.prototype.showHandles = function(state) {
    this.p.show(state);
};



Rectangle.prototype = new Shape();
Rectangle.prototype.constructor = Rectangle;
Rectangle.superclass = Shape.prototype;

function Rectangle(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Rectangle.prototype.init = function(svgNode) {
    if (svgNode.localName == "rect") {
        Rectangle.superclass.init.call(this, svgNode);
        var x = parseFloat(svgNode.getAttributeNS(null, "x"));
        var y = parseFloat(svgNode.getAttributeNS(null, "y"));
        var width = parseFloat(svgNode.getAttributeNS(null, "width"));
        var height = parseFloat(svgNode.getAttributeNS(null, "height"));
        this.p1 = new Handle(x, y, this);
        this.p2 = new Handle(x + width, y + height, this);
    } else {
        throw new Error("Rectangle.init: Invalid SVG Node: " + svgNode.localName);
    }
};

Rectangle.prototype.realize = function() {
    if (this.svgNode != null) {
        this.p1.realize();
        this.p2.realize();
        this.p1.show(false);
        this.p2.show(false);
    }
};

Rectangle.prototype.unrealize = function() {
    if (this.svgNode != null) {
        this.p1.unrealize();
        this.p2.unrealize();
        this.svgNode.parentNode.removeChild(this.svgNode);
    }
};

Rectangle.prototype.refresh = function() {
    var min = this.p1.point.min(this.p2.point);
    var max = this.p1.point.max(this.p2.point);
    this.svgNode.setAttributeNS(null, "x", min.x);
    this.svgNode.setAttributeNS(null, "y", min.y);
    this.svgNode.setAttributeNS(null, "width", max.x - min.x);
    this.svgNode.setAttributeNS(null, "height", max.y - min.y);
};

Rectangle.prototype.registerHandles = function() {
    mouser.register(this.p1);
    mouser.register(this.p2);
};
Rectangle.prototype.unregisterHandles = function() {
    mouser.unregister(this.p1);
    mouser.unregister(this.p2);
};
Rectangle.prototype.selectHandles = function(select) {
    this.p1.select(select);
    this.p2.select(select);
};
Rectangle.prototype.showHandles = function(state) {
    this.p1.show(state);
    this.p2.show(state);
};
Rectangle.prototype.getIntersectionParams = function() {
    return new IntersectionParams("Rectangle", [this.p1.point, this.p2.point]);
};


// Square

Square.prototype = new Rectangle();
Square.prototype.constructor = Square;
Square.superclass = Rectangle.prototype;

function Square(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Square.prototype.init = function(svgNode) {
    if (svgNode.localName == "rect") {
        Rectangle.superclass.init.call(this, svgNode);
        var x = parseFloat(svgNode.getAttributeNS(null, "x"));
        var y = parseFloat(svgNode.getAttributeNS(null, "y"));
        var width = parseFloat(svgNode.getAttributeNS(null, "width"));
        var height = parseFloat(svgNode.getAttributeNS(null, "height"));
        this.p1 = new Handle(x, y, this);
        this.p2 = new Handle(x + width, y + height, this);
    } else {
        throw new Error("Rectangle.init: Invalid SVG Node: " + svgNode.localName);
    }
};

Square.prototype.refresh = function() {
    var min = this.p1.point.min(this.p2.point);
    var max = this.p1.point.max(this.p2.point);
    this.svgNode.setAttributeNS(null, "x", min.x);
    this.svgNode.setAttributeNS(null, "y", min.y);
    this.svgNode.setAttributeNS(null, "width", max.x - min.x);
    this.svgNode.setAttributeNS(null, "height", max.x - min.x);
};


// label

Label.prototype = new Shape();
Label.prototype.constructor = Label;
Label.superclass = Shape.prototype;

function Label(svgNode) {
    if (arguments.length > 0) {
        this.init(svgNode);
    }
}

Label.prototype.init = function(svgNode) {
    if (svgNode.localName == "text") {
        Label.superclass.init.call(this, svgNode);
        var x = parseFloat(svgNode.getAttributeNS(null, "x"));
        var y = parseFloat(svgNode.getAttributeNS(null, "y"));
        if (!isNaN(x) && !isNaN(y))
            this.p = new Handle(x, y, this);
    } else {
        throw new Error("Label.init: Invalid SVG Node: " + svgNode.localName);
    }
};

Label.prototype.enhance = function(visible) {
    this.svgNode.setAttributeNS(null, "stroke", visible ? 'orangered' : 'black');
    this.svgNode.setAttributeNS(null, "stroke-opacity", visible ? 1.0 : 0.0);
};

Label.prototype.unrealize = function() {
    if (this.svgNode != null) {
        this.p.unrealize();
        this.svgNode.parentNode.removeChild(this.svgNode);
    }
};
Label.prototype.realize = function() {
    if (this.svgNode != null) {
        this.p.realize();
        this.p.show(false);
    }
};

Label.prototype.refresh = function() {
    var x = this.p.point.x;
    var y = this.p.point.y;
    this.svgNode.setAttributeNS(null, "x", x);
    this.svgNode.setAttributeNS(null, "y", y);
};
Label.prototype.registerHandles = function() {
    mouser.register(this.p);
};
Label.prototype.unregisterHandles = function() {
    mouser.unregister(this.p);
};
Label.prototype.selectHandles = function(select) {
    this.p.select(select);
};
Label.prototype.showHandles = function(state) {
    this.p.show(state);
};

