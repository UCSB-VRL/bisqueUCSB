/*******************************************************************************

@author John Delaney


 *******************************************************************************/

/*
LICENSE

Center for Bio-Image Informatics, University of California at Santa Barbara

Copyright (c) 2007-2014 by the Regents of the University of California
All rights reserved

Redistribution and use in source and binary forms, in whole or in parts, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright
notice, this list of conditions, and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions, and the following disclaimer in
the documentation and/or other materials provided with the
distribution.

Use or redistribution must display the attribution with the logo
or project name and the project URL link in a location commonly
visible by the end users, unless specifically permitted by the
license holders.

THIS SOFTWARE IS PROVIDED BY THE REGENTS OF THE UNIVERSITY OF CALIFORNIA ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OF THE UNIVERSITY OF CALIFORNIA OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


function gObjectBuffer(volume) {
	this.volume = volume
	this.position = new Array(); //this stores vertices
	this.index = new Array(); //this stores indices into the vertex set
	this.colors = new Array(); //this stores colors

    this.rindex = new Array(); //reverse index stores the
    this.shapeIndex = new Array(); //this stores an index for each g-object shape
};

gObjectBuffer.prototype.rescale = function (scale) {
	//var scale = this.volume.currentScale.clone();
    //var mat = new THREE.Matrix4().scale(scale);

    /*var dims = this.volume.dims;
    var min = Math.min(dims.pixel.x, Math.min(dims.pixel.y,dims.pixel.z));
    var max = Math.max(dims.pixel.x, Math.max(dims.pixel.y,dims.pixel.z));
    var boxMin = Math.min(dims.slice.x, Math.min(dims.slice.y,dims.slice.z));
    var boxMax = Math.max(dims.slice.x, Math.max(dims.slice.y,dims.slice.z));
    */
    this.mesh.scale.copy(new THREE.Vector3(2.0*scale.x,
                                           2.0*scale.y,
                                           2.0*scale.z));
};

gObjectBuffer.prototype.pushPosition = function (p, x, positions) {
    var slice = this.volume.phys; //var slice = this.volume.dims.slice;
	//var dims = this.volume.dims;
    //var min = Math.min(dims.pixel.x, Math.min(dims.pixel.y,dims.pixel.z));
    //var max = Math.max(dims.pixel.x, Math.max(dims.pixel.y,dims.pixel.z));

    positions[x * 3 + 0] = (p.x / slice.x - 0.5); //positions[x * 3 + 0] = (p.x / slice.x/max - 0.5);
	positions[x * 3 + 1] = (0.5 - p.y / slice.y); //positions[x * 3 + 1] = (0.5 - p.y / slice.y/max);
	positions[x * 3 + 2] = (0.5 - p.z / slice.z); //positions[x * 3 + 2] = (0.5 - p.z / slice.z/max);
};

gObjectBuffer.prototype.push = function (poly) {}
gObjectBuffer.prototype.allocateMesh = function () {}


gObjectBuffer.prototype.getColor = function (color) {
    if(typeof color === 'string'){
        var cutHex = function(h) {return (h.charAt(0)=="#") ? h.substring(1,7):h}
        var hexToR = function(h) {return parseInt((cutHex(h)).substring(0,2),16)}
        var hexToG = function(h) {return parseInt((cutHex(h)).substring(2,4),16)}
        var hexToB = function(h) {return parseInt((cutHex(h)).substring(4,6),16)}
        color = {r: hexToR(color)/255 - 0.25,
                 g: hexToG(color)/255 - 0.25,
                 b: hexToB(color)/255 - 0.25};

    }
    else if(typeof color === 'undefined'){
        color = {r: 1.0, g: 0.0, b: 0.0};
    }

    return color;
};

gObjectBuffer.prototype.build = function(gObject, ftor){
    var g = ftor(gObject),
        c = gObject.getColor();
    g.gObject = gObject;
    gObject.shape3D = g;
    g.color = {r: c.r/255.0, g: c.g/255.0, b: c.b/255.0, a: c.a}; //this.getColor(gObject.color_override);
    this.push(g);
}

gObjectBuffer.prototype.buildBuffer = function () {
	var geometry = new THREE.BufferGeometry();
	geometry.addAttribute('index', new THREE.BufferAttribute(new Uint32Array(this.index.length), 1));
	geometry.addAttribute('position', new THREE.BufferAttribute(new Float32Array(this.position.length * 3), 3));
	geometry.addAttribute('color', new THREE.BufferAttribute(new Float32Array(this.colors.length * 3), 3));
	var gpositions = geometry.getAttribute('position').array;
	var gindex = geometry.getAttribute('index').array;
	var gcolor = geometry.getAttribute('color').array;
	//var check0 = index.slice(0);

	for (var i = 0; i < this.index.length; i++) {
		gindex[i] = this.index[i];
	}

	for (var i = 0; i < this.position.length; i++) {
		this.pushPosition(this.position[i], i, gpositions);
	}

	for (var i=0, j=0; i < this.colors.length; i++, j+=3) {
		gcolor[j + 0] = this.colors[i].r;
		gcolor[j + 1] = this.colors[i].g;
		gcolor[j + 2] = this.colors[i].b;
	}

	this.mesh = this.allocateMesh(geometry, this.material);
	this.mesh.geometry.dynamic = true;
	this.mesh.geometry.computeBoundingBox();
	this.mesh.geometry.verticesNeedUpdate = true;

};

gObjectBuffer.prototype.getShape = function(id){
    return this.shapeIndex[id];
};

gObjectBuffer.prototype.setColorBase = function(id, color){

    var shape = this.getShape(id);
    var i0 = shape.index3DStart;
    var i1;
    if(id + 1 == this.shapeIndex.length)
        i1 = this.index.length; //this means that we go to the last index
    else
        i1 = this.getShape(id + 1).index3DStart; //otherwise we take the stored index

    for(var i = i0; i < i1; i++){
        var cid = this.index[i];
        this.mesh.geometry.attributes.color.array[3*cid + 0] = color.r;
        this.mesh.geometry.attributes.color.array[3*cid + 1] = color.g;
        this.mesh.geometry.attributes.color.array[3*cid + 2] = color.b;
    }
    this.mesh.geometry.attributes.color.needsUpdate = true;
};


gObjectBuffer.prototype.setColor = function(id, color){
    this.setColorBase(id, color);
};

gObjectBuffer.prototype.highlight = function(toHighlight){
    var shape = this.getShape(toHighlight);
    var col = shape.color;
    this.setColor(toHighlight,{r: col.r + .5, g: col.g + .5, b: col.b + .5});
    this.mesh.geometry.dynamic = true;
};

gObjectBuffer.prototype.unhighlight = function(toHighlight){
    var shape = this.getShape(toHighlight);
    var col = shape.color;
    this.setColor(toHighlight, shape.color);
    this.mesh.geometry.dynamic = true;
};

gObjectBuffer.prototype.update = function(toSelect){
    this.mesh.geometry.attributes.color.needsUpdate = true;
};


function pointBuffer(volume) {
	this.volume = volume;
    //this.base = gObjectBuffer;
	//this.base(volume);
    gObjectBuffer.call(this, volume);
};

pointBuffer.prototype = new gObjectBuffer();

pointBuffer.prototype.setColor = function(id, color){
    var idp = this.getShape(id);
    var shape = this.shapeIndex[id];

    this.mesh.geometry.attributes.color.array[3*idp + 0] = color.r;
    this.mesh.geometry.attributes.color.array[3*idp + 1] = color.g;
    this.mesh.geometry.attributes.color.array[3*idp + 2] = color.b;

    this.backGeom.attributes.color.array[3*id + 0] = color.r;
    this.backGeom.attributes.color.array[3*id + 1] = color.g;
    this.backGeom.attributes.color.array[3*id + 2] = color.b;
    this.mesh.geometry.attributes.color.needsUpdate = true;
};

pointBuffer.prototype.push = function (g) {

    var lcolor = g.color ? g.color : {r: 255, g: 0, b: 0};
    var shapeID = this.shapeIndex.length;
    var idStart = this.index.length == 0 ? 0 : this.index.length;

    g.index3D = shapeID;
    g.index3DStart = idStart;
    this.shapeIndex.push(g);

	this.colors.push(lcolor);
	this.position.push(g.vertices[0]); // = positions.concat(poly)
	this.index.push(this.index.length);
    this.rindex[this.index.length-1] = shapeID;

	//index.push(lindex);// = index.concat(lindex);
	//console.log('local: ', lindex, 'localpoly: ', poly, 'global: ', index, 'global p: ',positions);
	//triCounter += polys[i].vertices.length;
};

gObjectBuffer.prototype.initBackBuffer = function () {
	this.backGeom = new THREE.BufferGeometry();
	this.backGeom.addAttribute('index', new THREE.BufferAttribute(new Uint32Array(this.index.length), 1));
	this.backGeom.addAttribute('position', new THREE.BufferAttribute(new Float32Array(this.position.length * 3), 3));
	this.backGeom.addAttribute('color', new THREE.BufferAttribute(new Float32Array(this.colors.length * 3), 3));
}

pointBuffer.prototype.allocateMesh = function (geometry, material) {
	var cloud = new THREE.PointCloud(geometry, material);
	return cloud;
};

pointBuffer.prototype.initPermutationArray = function(){
    if(!this.backGeom)
        this.initBackBuffer();

    var gpositions = this.mesh.geometry.getAttribute('position').array;
	var gindex     = this.mesh.geometry.getAttribute('index').array;
	var gcolor     = this.mesh.geometry.getAttribute('color').array;

	var bpositions = this.backGeom.getAttribute('position').array;
	var bindex     = this.backGeom.getAttribute('index').array;
	var bcolor     = this.backGeom.getAttribute('color').array;

    //var shape = this.shapeIndex
	if (!this.permutation) {
		//preallocate the distance array and fill the back buffer positions
		this.permutation = new Array(gindex.length);
		for (var i = 0; i < this.permutation.length; i++) {
			this.permutation[i] = {
				i : i,
				dist : 0.0,
				visited : false
			};
		}
        for(var i = 0; i < gpositions.length; i++){
            bpositions[i] = gpositions[i];
        }
        for(var i = 0; i < gindex.length; i++){
            bindex[i] = gindex[i];
        }
        for(var i = 0; i < gcolor.length; i++){
            bcolor[i] = gcolor[i];
        }
	}
};

pointBuffer.prototype.sortParticles = function (pos) {
	if(!this.backGeom)
        this.initBackBuffer();

    var gpositions = this.mesh.geometry.getAttribute('position').array;
	var gindex     = this.mesh.geometry.getAttribute('index').array;
	var gcolor     = this.mesh.geometry.getAttribute('color').array;

	var bpositions = this.backGeom.getAttribute('position').array;
	var bindex     = this.backGeom.getAttribute('index').array;
	var bcolor     = this.backGeom.getAttribute('color').array;

    //var shape = this.shapeIndex
	if (!this.permutation) {
		//preallocate the distance array and fill the back buffer positions
		this.permutation = new Array(gindex.length);
		for (var i = 0; i < this.permutation.length; i++) {
			this.permutation[i] = {
				i : i,
				dist : 0.0,
				visited : false
			};
		}
        for(var i = 0; i < gpositions.length; i++){
            bpositions[i] = gpositions[i];
        }
        for(var i = 0; i < gindex.length; i++){
            bindex[i] = gindex[i];
        }
        for(var i = 0; i < gcolor.length; i++){
            bcolor[i] = gcolor[i];
        }
	}

	for (var i = 0, j=0; i < this.permutation.length; i++, j+=3) {
		this.permutation[i].i = i;
		var d0 = pos.x - bpositions[j + 0];
		var d1 = pos.y - bpositions[j + 1];
		var d2 = pos.z - bpositions[j + 2];
		this.permutation[i].dist = d0 * d0 + d1 * d1 + d2 * d2;
	}
	this.permutation.sort(function (a, b) {
		return b.dist - a.dist
	}); //sort the permutations in descending order

/*
	var assign = function (i, bigArr, tmpArr, sz) {
		for (y = 0; y < sz; y++) {
			bigArr[sz * i + y] = tmpArr[y];
		}
	};
  */
	var assign = function (i1, bigArr1, i0, bigArr0, sz) {
		for (y = 0; y < sz; y++) {
			bigArr1[sz * i1 + y] = bigArr0[sz * i0 + y];
		}
	};


	var getSet = function (i, index, pos, col) {
		//var pi = perm[i].i;
		var set = {
			ind : [index[i]],
			col : [col[3 * i + 0],
				col[3 * i + 1],
				col[3 * i + 2]],
			pos : [pos[3 * i + 0],
				pos[3 * i + 1],
				pos[3 * i + 2]],
		};
		return set;
	};

	//debugger;

	for (var i = 0; i < this.permutation.length; i++) {
        var ii = this.permutation[i].i;
        assign(i, gpositions, ii, bpositions,3);
        assign(i, gindex, ii, bindex,1);
        assign(i, gcolor, ii, bcolor,3);
    }
    /*
      //recursive permute in place algorithm which didn't work to well

	for (var i = 0; i < this.permutation.length; i++) {
		var begin = getSet(i, gindex, gpositions, gcolor)
			var k = 0;
		var iterating = true;
		var ci = i;
		if (this.permutation[i].visited == true)
			continue;
		while (iterating == 1) {
			var swapVars = getSet(this.permutation[ci].i, gindex, gpositions, gcolor);

			assign(ci, gindex, swapVars.ind, 1);
			assign(ci, gpositions, swapVars.pos, 3);
			assign(ci, gcolor, swapVars.col, 3);

			if (this.permutation[ci].i == i) {
				assign(ci, gindex, begin.ind, 1);
				assign(ci, gpositions, begin.pos, 3);
				assign(ci, gcolor, begin.col, 3);
				iterating = false;
				continue;
			}
			ci = this.permutation[ci].i;
			this.permutation[ci].visited = true;
			k++;
		    }
	    }
    */

	var logOut = '';
	for (var i = 0; i < gpositions.length / 3; i++) {
		var d0 = pos.x - gpositions[3 * i + 0];
		var d1 = pos.y - gpositions[3 * i + 1];
		var d2 = pos.z - gpositions[3 * i + 2];
		logOut += d0 * d0 + d1 * d1 + d2 * d2 + ' ';
	}
	this.mesh.geometry.dynamic = true;
	this.mesh.geometry.verticesNeedUpdate = true;
	this.mesh.geometry.attributes.index.needsUpdate = true;
	this.mesh.geometry.attributes.position.needsUpdate = true;
	this.mesh.geometry.attributes.color.needsUpdate = true;
	//console.log(logOut);
}

function lineBuffer(volume) {
	gObjectBuffer.call(this, volume);
};

lineBuffer.prototype = new gObjectBuffer();
/*
lineBuffer.prototype.push = function(poly){

var lcolor = {r: Math.random(),g: Math.random(),b: Math.random()}

for(var i = 0; i < poly.length; i++){
this.colors.push(lcolor);
this.index.push(this.position.length, this.position.length + 1);// = positions.concat(poly)
//this.index.push(this.position.length + 1);// = positions.concat(poly)

this.position.push(poly[i]);// = positions.concat(poly)
};

//index.push(lindex);// = index.concat(lindex);
//console.log('local: ', lindex, 'localpoly: ', poly, 'global: ', index, 'global p: ',positions);
//triCounter += polys[i].vertices.length;
};
 */

lineBuffer.prototype.push = function (g) {
	//poly is any object with an x and a y.
	//loads necessary data onto the vertex buffer

    var poly = g.vertices;

    var lindex = [];
    var lcolor = g.color ? g.color : {r: 255, g: 0, b: 0};
    var shapeID = this.shapeIndex.length;
    var idStart = this.index.length == 0 ? 0 : this.index.length;


    g.index3D = shapeID;
    g.index3DStart = idStart;

    this.shapeIndex.push(g);

	for (var i = 0; i < poly.length - 1; i++) {
		lindex.push(i);
		lindex.push(i + 1);
	}

	for (var j = 0; j < lindex.length; j++) {
		lindex[j] += this.position.length;
	}

	for (var j = 0; j < poly.length; j++) {
		this.colors.push(lcolor);
	}

	for (var i = 0; i < poly.length; i++) {
		this.position.push(poly[i]); // = positions.concat(poly)
	};

	for (var i = 0; i < lindex.length; i++) {
		this.index.push(lindex[i]); // = positions.concat(poly)
        this.rindex[lindex[i]] = shapeID;
	};

};

lineBuffer.prototype.allocateMesh = function (geometry, material) {
	return new THREE.Line(geometry, material, THREE.LinePieces);
};

function polyBuffer(volume) {
    gObjectBuffer.call(this, volume);
};

polyBuffer.prototype = new gObjectBuffer();

polyBuffer.prototype.isClockWise = function (poly) {
	//use shoelace determinate
	var det = 0;
	for (var i = 0; i < poly.length; i++) {
		var cur = poly[i];
		var nex = poly[(i + 1) % poly.length];
		det += cur.x * nex.y - cur.y * nex.x;
	}
	return det > 0;
};

polyBuffer.prototype.push = function (g) {
	//poly is any object with an x and a y.
	//loads necessary data onto the vertex buffer
    var poly = g.vertices;

	var lindex = [];
    var lcolor = g.color ? g.color : {r: 255, g: 0, b: 0};
    var shapeID = this.shapeIndex.length;
    var idStart = this.index.length == 0 ? 0 : this.index.length;


    g.index3D = shapeID;
    g.index3DStart = idStart;

    this.shapeIndex.push(g);
	if (!this.isClockWise(poly)){
        try{
		    lindex = POLYGON.tessellate(poly, []);
        }
        catch(e){
            BQ.ui.error("some polygons could not be renderered: <BR/> " +
                        e.message);
        }
    }
	else{
        try{
		    lindex = POLYGON.tessellate(poly.reverse(), []);
        }

        catch(e){
            BQ.ui.error("some polygons could not be renderered: <BR/> " +
                        e.message);
        }
    }
	for (var j = 0; j < lindex.length; j++) {
		lindex[j] += this.position.length;
	}

	for (var j = 0; j < poly.length; j++) {
		this.colors.push(lcolor);
	}

	for (var i = 0; i < poly.length; i++) {
		this.position.push(poly[i]); // = positions.concat(poly)
	}

	for (var i = 0; i < lindex.length; i++) {
		this.index.push(lindex[i]); // = positions.concat(poly)
        this.rindex[lindex[i]] = shapeID;
	}
};


polyBuffer.prototype.allocateMesh = function (geometry, material) {
	return new THREE.Mesh(geometry, material);
};

/*
polyBuffer.prototype.buildBuffer = function(){
var geometry = new THREE.BufferGeometry();
geometry.addAttribute( 'index',    new THREE.BufferAttribute( new Uint32Array( this.index.length ), 1 ));
geometry.addAttribute( 'position', new THREE.BufferAttribute( new Float32Array(this. position.length * 3 ), 3 ) );
geometry.addAttribute( 'color',    new THREE.BufferAttribute( new Float32Array( this.colors.length * 3 ), 3 ) );
var gpositions = geometry.getAttribute('position').array;
var gindex     = geometry.getAttribute('index').array;
var gcolor     = geometry.getAttribute('color').array;
//var check0 = index.slice(0);

for(var i = 0; i < this.index.length; i++){
gindex[i] = this.index[i];
}

for(var i = 0; i < this.position.length; i++){
this.pushPosition(this.position[i], i, gpositions);
}

for(var i = 0; i < this.colors.length; i++){
gcolor[3*i + 0] = this.colors[i].r;
gcolor[3*i + 1] = this.colors[i].g;
gcolor[3*i + 2] = this.colors[i].b;
}

this.mesh = new THREE.Mesh( geometry, this.material);

this.mesh.geometry.dynamic = true;
this.mesh.geometry.computeBoundingBox();
this.mesh.geometry.verticesNeedUpdate = true;
};
 */

function BQFactory3D(){
};

BQFactory3D.set = function(pointBuffer, lineBuffer, polyBuffer){
    this.PointBuffer = pointBuffer;
    this.LineBuffer = lineBuffer;
    this.PolyBuffer = polyBuffer;

    BQFactory3D.buffermap = {
        gobject  : this.PointBuffer,
        point    : this.PointBuffer,
        rectangle: this.PolyBuffer,
        square   : this.PolyBuffer,
        ellipse  : this.PolyBuffer,
        circle   : this.PolyBuffer,
        polygon  : this.PolyBuffer,
        polyline : this.LineBuffer,
        line     : this.LineBuffer,
        label    : this.PointBuffer,
    }
};

BQFactory3D.ftormap = {
    point     : function(g) { return g;},
    label     : function(g) { return g;},
    gobject   : function(g) { return g;},
    rectangle : function(g) {
        var p0 = g.vertices[0];
        var p1 = g.vertices[1];
        var vertices = [{x: p0.x, y: p0.y, z: p0.z},
                        {x: p1.x, y: p0.y, z: p0.z},
                        {x: p1.x, y: p1.y, z: p0.z},
                        {x: p0.x, y: p1.y, z: p0.z}
                       ];
        return  {vertices: vertices, color: g.color};
    },
    square    : function(g) {
        var p0 = g.vertices[0];
        var p1 = g.vertices[1];
        var dx = g.vertices[1].x - g.vertices[0].x;
        var vertices = [{x: p0.x,    y: p0.y,    z: p0.z},
                        {x: p0.x+dx, y: p0.y,    z: p0.z},
                        {x: p0.x+dx, y: p0.y+dx, z: p0.z},
                        {x: p0.x,    y: p0.y+dx, z: p0.z}
                       ];
        return  {vertices: vertices, color: g.color};
    },
    ellipse    : function(g) {
        var p0 = g.vertices[0];
        var p1 = g.vertices[1];
        var p2 = g.vertices[2];

        var dp0 = {x:p1.x - p0.x,
                   y:p1.y - p0.y,
                   z:p1.z - p0.z};


        var dp1 = {x:p2.x - p0.x,
                   y:p2.y - p0.y,
                   z:p2.z - p0.z};

        var vertices = [];
        var r0 = Math.sqrt(dp0.x*dp0.x + dp0.y*dp0.y + dp0.z*dp0.z);
        var r1 = Math.sqrt(dp1.x*dp1.x + dp1.y*dp1.y + dp1.z*dp1.z);

        var u = {x: dp0.x/r0, y: dp0.y/r0, z: dp0.z/r0};
        var v = {x:-u.y, y: u.x, z: u.z};

        var N = 16;
        var phase = 0;
        var npi = 2.0*Math.PI/N;

        for(var i = 0; i < 16; i++){
            vertices.push({x: p0.x + r0*u.x*Math.cos(phase) + r1*v.x*Math.sin(phase),
                           y: p0.y + r0*u.y*Math.cos(phase) + r1*v.y*Math.sin(phase),
                           z: p0.z});
            /*
              vertices.push({x: p0.x + r0*Math.cos(phase),
              y: p0.y + r1*Math.sin(phase),
              z: p0.z});
            */
            phase += npi;
        }
        return  {vertices: vertices, color: g.color};
    },

    circle    : function(g) {
        var p0 = g.vertices[0];
        var p1 = g.vertices[1];
        var dp = {x:p1.x - p0.x,
                  y:p1.y - p0.y,
                  z:p1.z - p0.z};

        var vertices = [];
        var r = Math.sqrt(dp.x*dp.x + dp.y*dp.y + dp.z*dp.z);
        var N = 16;
        var phase = 0;
        var npi = 2.0*Math.PI/N;
        for(var i = 0; i < 16; i++){
            vertices.push({x: p0.x + r*Math.cos(phase),
                           y: p0.y + r*Math.sin(phase),
                           z: p0.z});
            phase += npi;
        }
        return  {vertices: vertices, color: g.color};
    },
    polygon   : function(g) { return g;},
    polyline  : function(g) { return g;},
    polyline  : function(g) { return g;},
    line      : function(g) { return g;},
    //label    : BQGObject,
};



BQFactory3D.make = function(g){
    var buffer = BQFactory3D.buffermap[g.type];
    var ftor   = BQFactory3D.ftormap[g.type];
    buffer.build(g, ftor);
};


function gObjectTool(volume, cls) {
	//renderingTool.call(this, volume);
	this.cls = 'gButton';
	this.label = 'Graphical Annotations';

    this.no_controls = false;
    this.base = renderingTool;
    this.name = 'gobjects';
    this.base(volume, this.cls);
    try {
        this.gobjects = this.volume.phys.image.gobjects;
    } catch (e) {
    	this.gobjects = [];
    }
};

gObjectTool.prototype = new renderingTool();

gObjectTool.prototype.addUniforms = function(){
    this.uniforms['opacity'] = {name: 'BRIGHTNESS',
                                type: 'f',
                                val: 1.0,
                                slider: true,
                                min: 0,
                                max: 100,
                                def: 100.0,
                                K: 0.01,
                                tipText: function (thumb){
                                    return (thumb.value/100).toString();
                                },
                                updateSlider : function (slider, value) {
                                    this.volume.volumeObject.polyShaderMaterial.uniforms.opacity.value = value/100;
                                    this.volume.rerender();
                                }
                               };
};

gObjectTool.prototype.toggle = function(button){

	if (button.pressed) {
		this.setVisible(true);
        this.state = 1;
	} else {
		this.setVisible(false);
        this.state = 0;
	}

    this.base.prototype.toggle.call(this,button);
	this.volume.rerender();

    if(!this.currentSet) return;
	//this.rescalePoints();
};

gObjectTool.prototype.buildCube = function (sz) {
	var geometry = new THREE.BufferGeometry();
	geometry.addAttribute('index', new THREE.BufferAttribute(new Uint32Array(36), 1));
	geometry.addAttribute('position', new THREE.BufferAttribute(new Float32Array(8 * 3), 3));

	var gpositions = geometry.getAttribute('position').array;
	var gindex = geometry.getAttribute('index').array;

	gindex[0] = 0;
	gindex[1] = 2;
	gindex[2] = 1;
	gindex[3] = 2;
	gindex[4] = 3;
	gindex[5] = 1;
	gindex[6] = 4;
	gindex[7] = 6;
	gindex[8] = 5;
	gindex[9] = 6;
	gindex[10] = 7;
	gindex[11] = 5;
	gindex[12] = 4;
	gindex[13] = 5;
	gindex[14] = 1;
	gindex[15] = 5;
	gindex[16] = 0;
	gindex[17] = 1;

	gindex[18] = 7;
	gindex[19] = 6;
	gindex[20] = 2;
	gindex[21] = 6;
	gindex[22] = 3;
	gindex[23] = 2;
	gindex[24] = 5;
	gindex[25] = 7;
	gindex[26] = 0;
	gindex[27] = 7;
	gindex[28] = 2;
	gindex[29] = 0;
	gindex[30] = 1;
	gindex[31] = 3;
	gindex[32] = 4;
	gindex[33] = 3;
	gindex[34] = 6;
	gindex[35] = 4;

	gpositions[0] = sz;
	gpositions[1] = sz;
	gpositions[2] = sz;
	gpositions[3] = sz;
	gpositions[4] = sz;
	gpositions[5] = -sz;
	gpositions[6] = sz;
	gpositions[7] = -sz;
	gpositions[8] = sz;
	gpositions[9] = sz;
	gpositions[10] = -sz;
	gpositions[11] = -sz;

	gpositions[12] = -sz;
	gpositions[13] = sz;
	gpositions[14] = -sz;
	gpositions[15] = -sz;
	gpositions[16] = sz;
	gpositions[17] = sz;
	gpositions[18] = -sz;
	gpositions[19] = -sz;
	gpositions[20] = -sz;
	gpositions[21] = -sz;
	gpositions[22] = -sz;
	gpositions[23] = sz;

	/*
	  for(var i = 0; i < this.colors.length; i++){
	  gcolor[3*i + 0] = this.colors[i].r;
	  gcolor[3*i + 1] = this.colors[i].g;
	  gcolor[3*i + 2] = this.colors[i].b;
	  }
	*/
	return geometry;

};

gObjectTool.prototype.rescalePoints = function (scale) {
	if(!this.currentSet) return;

    this.currentSet.points.rescale(scale);
	this.currentSet.polylines.rescale(scale);
	this.currentSet.polygons.rescale(scale);
	//console.log(this.points);
};

gObjectTool.prototype.setVisible = function (vis) {
	var t = this.volume.currentTime;
	this.currentSet = this.gObjectBuffers[t];
	for (var item in this.currentSet) {
		if (!item)
			continue;
		var curMesh = this.currentSet[item].mesh;
		curMesh.visible = vis;
	}
};



gObjectTool.prototype.removeSet = function (set, scene) {

	for (var item in set) {
		if (!item)
			continue;

		var curMesh = set[item].mesh;
		if (curMesh){
			scene.remove(curMesh); // remove current point set
            //curMesh.visible = false;
        }
	}
};

gObjectTool.prototype.addSet = function (set, scene) {
	for (var item in set) {
		if (!item)
			continue;
		var curMesh = set[item].mesh;
		if (curMesh) {
			scene.add(curMesh); // remove current point set
			if (this.state === 1)
				curMesh.visible = true;
			else
				curMesh.visible = false;
		}
	}
};

gObjectTool.prototype.updateScene = function () {
	var t = this.volume.currentTime;
    var scene = this.volume.volumeObject.sceneData;
	if (!this.currentSet)
		this.currentSet = this.gObjectBuffers[t];

    this.removeSet(this.currentSet, scene);

    this.currentSet = this.gObjectBuffers[t];

    this.addSet(this.currentSet, scene);

	this.points = this.currentSet.points.mesh; //set current pointer to loaded set

    if(!this.pointclouds)
        this.pointclouds = new Array();

    while(this.pointclouds.length > 0) {
        this.pointclouds.pop();
    }
    //
	for (var c in this.currentSet) {
		if (this.currentSet[c])
			this.pointclouds.push(this.currentSet[c].mesh);
	}
};

gObjectTool.prototype.initBuffers = function(){
    var t = this.volume.currentTime;
	//if (this.gObjectBuffers[t]) { //load points in lazily
	//	this.updateScene();
	//	return;
	//}

	this.gObjectBuffers[t] = {};

	var pBuffer = new polyBuffer(this.volume);
	pBuffer.material = this.volume.volumeObject.polyShaderMaterial;
	this.gObjectBuffers[t].polygons = pBuffer;

	var lBuffer = new lineBuffer(this.volume);
	lBuffer.material = this.volume.volumeObject.polyShaderMaterial;
	this.gObjectBuffers[t].polylines = lBuffer;

	var cBuffer = new pointBuffer(this.volume);
	cBuffer.material = this.volume.volumeObject.pointShaderMaterial;
	this.gObjectBuffers[t].points = cBuffer;

	this.gObjectBuffers[t].polygons = pBuffer;
	//todo: I think we want to build buffers for every frame right here,
	//      rather than load lazily... if we have 10 million gobjects to
	//      sift through, then this will get pretty slow

    BQFactory3D.set(cBuffer, lBuffer, pBuffer);
};

gObjectTool.prototype.loadGObjects = function () {
    var t = this.volume.currentTime;
    //if the scene has been built, just update the objects in the scene and return/
    if(this.gObjectBuffers[t]){
        this.updateScene();
        return;
    }

    this.initBuffers();
    var tStack = [this];
    while(tStack.length > 0){
        var context = tStack[tStack.length-1];
		for (var i = 0; i < context.gobjects.length; i++) {
			var g = context.gobjects[i];
            if(g.gobjects.length > 0) tStack.unshift(g);
            else if (g.vertices.length === 0)    continue;
            else if (g.vertices[0].t   === null) BQFactory3D.make(g);
            else if (g.vertices[0].t   === t)    BQFactory3D.make(g);
		}
        tStack.pop();
    }

	this.gObjectBuffers[t].points.buildBuffer();
	this.gObjectBuffers[t].polylines.buildBuffer();
	this.gObjectBuffers[t].polygons.buildBuffer();
    this.gObjectBuffers[t].points.initPermutationArray();
	this.updateScene();
	this.rescalePoints(this.volume.scale);
    this.volume.rerender();
};

gObjectTool.prototype.sortPoints = function(renderer){
    if(!this.currentSet) return;
    var camPos = renderer.camera.position;
    this.currentSet.points.sortParticles(camPos)
};

gObjectTool.prototype.initControls = function(){

	this.title = 'show points';
	var me = this;
	this.dist = 1.0;
	this.state = 0;
    this.selectedSet = new Array();
/*
	this.lighting = Ext.create('Ext.form.field.Checkbox', {
		boxLabel : 'show points',
		checked : false,
		handler : function () {
			this.state ^= 1;
			if ((this.state & 1) === 1) {
				this.setVisible(true);
			} else {
				this.setVisible(false);
			}
			this.rescalePoints(me.volume.scale);
			this.volume.rerender();
		},
		scope : me,
	});
*/
	var me = this;
	this.plane = new THREE.Mesh(new THREE.PlaneBufferGeometry(2000, 2000, 8, 8),
				                new THREE.MeshBasicMaterial({
					                color : 0x808080,
					                opacity : 0.25,
					                transparent : true,
					                wireframe : true
				                }));
	this.plane.visible = false;

	this.volume.scene.add(this.plane);
	//this.volume.sceneVolume.scene.add(this.lightObject);


    /////////////////////////////////////////////////////////
    //if gobjects are available we append a few methods to the viewer
    /////////////////////////////////////////////////////////


    this.resourceMap = {
        //gobject  : this.PointBuffer,
        point    : 'points',
        rectangle: 'polygons',
        square   : 'polygons',
        ellipse  : 'polygons',
        circle   : 'polygons',
        polygon  : 'polygons',
        polyline : 'polylines',
        line     : 'polylines',
        //label    : this.PointBuffer,
    };

    this.volume.color_gobjects = function(g, color){
        var resource = me.currentSet[me.resourceMap[g.type]];
        if(!g.shape3D || !resource) return;
        var id = g.shape3D.index3D;
        color = resource.getColor(color);
        g.shape3D.color = color;
        resource.setColor(id, color);
        resource.update();
        this.rerender(); //this being volume...
    };

    this.volume.highlight_gobject = function(g){
        var resource = me.currentSet[me.resourceMap[g.type]];
        if(!g.shape3D || !resource) return;
        var id = g.shape3D.index3D;
        resource.highlight(id);
        resource.update();
        this.rerender(); //this being volume...
    };


    this.volume.unhighlight_gobject = function(g){
        var resource = me.currentSet[me.resourceMap[g.type]];
        if(!g.shape3D || !resource) return;
        var id = g.shape3D.index3D;
        resource.unhighlight(id);
        resource.update();
        this.rerender(); //this being volume...
    };

	var onAnimate = function () {
		if(!this.currentSet) return;
        if(!this.volume.sceneData) return;
		var panel = this.volume;
		//move this to background plug-in
		var camPos = this.volume.canvas3D.camera.position;
		//this.currentSet.points.sortParticles(camPos);
		panel.canvas3D.renderer.clearTarget(this.accumBuffer0,
				                            true, true, true);
		var buffer = this.accumBuffer0;
		var bufferColor = this.accumBuffer1;

		this.pointShaderMaterial.uniforms.USE_COLOR.value = 0;
		this.polyShaderMaterial.uniforms.USE_COLOR.value = 0;
		this.backGroundShaderMaterial.uniforms.USE_COLOR.value = 0;
		//this.useColor = 0;
		panel.canvas3D.renderer.render(panel.sceneData,
				                       panel.canvas3D.camera,
				                       this.depthBuffer);

		this.pointShaderMaterial.transparent = true;
		this.pointShaderMaterial.uniforms.USE_COLOR.value = 1;
		this.polyShaderMaterial.uniforms.USE_COLOR.value = 1;
		this.backGroundShaderMaterial.uniforms.USE_COLOR.value = 1;
		panel.canvas3D.renderer.render(panel.sceneData,
				                       panel.canvas3D.camera,
				                       this.colorBuffer);


		panel.volumeObject.setUniformNoRerender('BACKGROUND_DEPTH', this.depthBuffer, false);
		panel.volumeObject.setUniformNoRerender('BACKGROUND_COLOR', this.colorBuffer, false);
        panel.setPass(0);

		panel.canvas3D.renderer.render(panel.scene,
				                       panel.canvas3D.camera,
				                       this.passBuffer);

        panel.volumeObject.setUniformNoRerender('BACKGROUND_COLOR', this.passBuffer, false);
        panel.setPass(1);

        /*


		panel.canvas3D.renderer.render(panel.scene,
				                       panel.canvas3D.camera,
				                       this.colorBuffer);
        */
	};

	var onMouseUp = function () {
		this.selectLight = false;
	};

	var onMouseDown = function (event) {
		if (this.state === 0)
			return;
		var width = this.volume.canvas3D.getWidth();
		var height = this.volume.canvas3D.getHeight();
		var cx = this.volume.canvas3D.getX();
		var cy = this.volume.canvas3D.getY();
		var x = ((event.clientX - cx) / width) * 2 - 1;
		var y =  - ((event.clientY - cy) / height) * 2 + 1;

		var vector = new THREE.Vector3(x, y, 0.5);
		var camera = this.volume.canvas3D.camera;

		//this.volume.canvas3D.projector.unprojectVector(vector, camera);
		vector.unproject(camera);
		this.raycaster.ray.set(camera.position, vector.sub(camera.position).normalize());

		var intersections = this.raycaster.intersectObjects(this.pointclouds);
		intersection = (intersections.length) > 0 ? intersections[0] : null;
		if (intersection !== null) {
			//this.sphere.position.copy( intersection.point );
			var gindex = intersections[0].object.geometry.getAttribute('index').array;
			//var pos = canvas.projector.projectVector(intersection.point.clone(), camera);
            var pos = intersection.point.project(camera);
			var index;
            if (intersection.index !== null)
				index = gindex[intersection.index];
			if (intersection.face)
				index = intersection.face;

            //this.currentSet.polygons.setSelected(id);
            //this.currentSet.polygons.highlight(id);
            if(index.a){
                var id = this.currentSet.polygons.rindex[index.a];
                this.volume.fireEvent('select_gobject', this.volume,
                                      this.currentSet.polygons.shapeIndex[id].gObject);
            }
            else{
                var id = this.currentSet.points.permutation[index].i;
                this.volume.fireEvent('select_gobject', this.volume,
                                      this.currentSet.points.shapeIndex[index].gObject);
            }

            this.volume.rerender();
            /*
              this.label.style.top = '' + 0.5 * height * (1.0 - pos.y) + cy + 'px';
			  this.label.style.left = '' + 0.5 * width * (1.0 + pos.x) - cx + 'px';
			  this.label.textContent = [index].join(", ");
		    */
        }
	};

	var onMouseMove = function (event) {
        /*
		event.preventDefault();
		if (!this.points) return;
        if (this.points.visible === false) return;

        var canvas = this.volume.canvas3D;
		var width = canvas.getWidth();
		var height = canvas.getHeight();
		var cx = canvas.getX();
		var cy = canvas.getY();
		var x = ((event.clientX - cx) / width) * 2 - 1;
		var y =  - ((event.clientY - cy) / height) * 2 + 1;

		var camera = canvas.camera;

		var vector = new THREE.Vector3(x, y, 0.5);
		//canvas.projector.unprojectVector(vector, camera);
        vector.unproject(camera);
		this.raycaster.ray.set(camera.position, vector.sub(camera.position).normalize());

		var intersections = this.raycaster.intersectObjects(this.pointclouds);
		intersection = (intersections.length) > 0 ? intersections[0] : null;
		if (intersection !== null) {
			//this.sphere.position.copy( intersection.point );
			var gindex = intersections[0].object.geometry.getAttribute('index').array;
			//var pos = canvas.projector.projectVector(intersection.point.clone(), camera);
            var pos = intersection.point.project(camera);
			var index;
            if (intersection.index)
				index = gindex[intersection.index];
			if (intersection.face)
				index = intersection.face;

            if(index.a){ //test to see if its a face
                var id = this.currentSet.polygons.rindex[index.a];
                //this.currentSet.polygons.setSelected(id);
                this.currentSet.polygons.highlight(id);

            }
            this.volume.rerender();
        }
        else{
            this.currentSet.polygons.resetColors();

        }
        */
        //console.log(this.label);
		/*

          if (!this.label) {
		  this.label = document.createElement('div');
		  this.label.style.backgroundColor = 'white';
		  this.label.style.position = 'absolute';
		  this.label.style.padding = '1px 4px';
		  this.label.style.borderRadius = '2px';
		  this.volume.getEl().dom.appendChild(this.label);
		  }
        */

		//this.panel3D.rerender();
	};


	this.volume.canvas3D.getEl().dom.addEventListener('mousemove', onMouseMove.bind(this), true);
	this.volume.canvas3D.getEl().dom.addEventListener('mouseup', onMouseUp.bind(this), true);
	this.volume.canvas3D.getEl().dom.addEventListener('mousedown', onMouseDown.bind(this), true);

	this.gObjectSets = new Array();
	this.gObjectBuffers = new Array();
	//this.loadGObjects();

	this.volume.on({
        scope: this,
        time: this.loadGObjects,
        scale: this.rescalePoints,
        loaded: this.loadGObjects,
    });

	this.raycaster = new THREE.Raycaster();
	this.raycaster.params.PointCloud.threshold = 0.005;

	this.addUniforms();
	this.isLoaded = true;
    //this.volume.canvas3D.animate_funcs[0] = callback(this, this.sortPoints);

	//this.updateScene();


    this.button.tooltip = 'Show graphical annotations';

	//this.items = [slider];
};

gObjectTool.prototype.loadPreferences = function(path, resource_uniq){
    var show = BQ.Preferences.get(resource_uniq, path+'/show', true);
    this.button.toggle(show);
};

gObjectTool.prototype.updateColor = function(){
    var me = this;
    visit_array(this.gobjects, function(g, args) {
        if (g.shape3D) {
            var c = g.getColor(),
                resource = me.currentSet[me.resourceMap[g.type]];
            g.shape3D.color = { r: c.r/255.0, g: c.g/255.0, b: c.b/255.0, a: c.a };
            resource.setColor(g.shape3D.index3D, g.shape3D.color);
        }
    });
    for (var i in this.currentSet) {
        var r = this.currentSet[i];
        r.mesh.geometry.dynamic = true;
        r.mesh.geometry.attributes.color.needsUpdate = true;
        r.mesh.geometry.needsUpdate = true;
        r.update();
    }
};
