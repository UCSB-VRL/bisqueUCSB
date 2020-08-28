
function ResourceCard(node, resource, flags) {
    this.resource = resource;
    this.node = node;
    this.fields = [];
    this.cardType = 'mex';   // TODO: change to some generic graph node style
    this.cardTitle = node ? node.name : 'node';
};


ResourceCard.prototype.populateFields = function (xnode) {};

ResourceCard.prototype.addField = function (field, attribute, className) {
    this.fields.push({fieldName:field, attribute: attribute, className:className});
};

ResourceCard.prototype.findField = function (fieldName) {
    for (var i = 0; i < this.fields.size(); i++) {
        if (this.fields[i].fieldName == fieldName) {
            return this.fields[i];
        }
    }
    return null;
};

ResourceCard.prototype.getSpan = function (field) {
    var cname = this.fields[field].className;
    var fname = this.fields[field].fieldName;
    var attr  = this.fields[field].attribute;
    var max = 50;
    if(attr.length > max){
        var sub = attr.substring(0,max);
        sub += '...';
        var attr = sub;
    }
    return "<span>"+fname+ ":  <em class="+cname+">"  + attr + "</em></span>";
};

ResourceCard.prototype.buildHtml = function () {
    var html = "<div class="+this.cardType+" id="+this.resource+">";
    //html += "<span class=status></span>";

    html += "<span class=resource>"  + this.cardTitle + "</span>";
    for(var i = 0; i < this.fields.length; i++){
        html += this.getSpan(i);
    }
    /*
    html += "<span> module:   <em class=name>"  + this.fields['name'] + "</em></span>";
    html += "<span> status:   <em class=value>" + this.fields['name'] xnode.getAttribute('value') + "</em></span>";
    //html += "<span class=date><span class=counter>"+worker.count+"</span></span>";
    html += "<span> finished: <em class=date>" + xnode.getAttribute('ts') + "</em></span>";
    */
    html += "</div>";

    this.node.rx = this.node.ry = 5;
    this.node.labelType = "html";
    this.node.label = html;
};

ResourceCard.prototype.getUrl = function (resource_uniq) {
	return '/client_service/view?resource=/data_service/' + resource_uniq;
};


function MexCard(node, resource, flags) {
    ResourceCard.call(this, node, resource);
    this.cardType = 'mex';
    this.cardTitle = 'mex';
};

MexCard.prototype = new ResourceCard();

MexCard.prototype.populateFields = function (xnode) {
    this.addField('module', xnode.getAttribute('name'), 'name');
    this.addField('status', xnode.getAttribute('value'), 'value');
    this.addField('finished', xnode.getAttribute('ts').split('T')[0], 'date');
};

MexCard.prototype.getUrl = function (resource_uniq) {
	return '/module_service/' + this.findField('module')['attribute'] + '/?mex=/data_service/' + resource_uniq;
};

function DataSetCard(node, resource, flags) {
    ResourceCard.call(this, node, resource);
    this.cardType = 'dataset';
    this.cardTitle = 'dataset';
};

DataSetCard.prototype = new ResourceCard();

DataSetCard.prototype.populateFields = function (xnode) {
    this.addField('name', xnode.getAttribute('name'), 'name');
};


function ImageCard(node, resource, flags) {
    ResourceCard.call(this, node, resource);
    this.cardType = 'image';
    this.cardTitle = 'image';
};

ImageCard.prototype = new ResourceCard();

ImageCard.prototype.populateFields = function (xnode) {
    this.addField('name', xnode.getAttribute('name'), 'name');
};


function TableCard(node, resource, flags) {
    ResourceCard.call(this, node, resource);
    this.cardType = 'table';
    this.cardTitle = 'table';
};

TableCard.prototype = new ResourceCard();

TableCard.prototype.populateFields = function (xnode) {
    this.addField('name', xnode.getAttribute('name'), 'name');
};


function PipelineCard(node, resource, flags) {
    ResourceCard.call(this, node, resource);
    this.cardType = 'pipeline';
    this.cardTitle = 'pipeline';
};

PipelineCard.prototype = new ResourceCard();

PipelineCard.prototype.populateFields = function (xnode) {
    this.addField('name', xnode.getAttribute('name'), 'name');
};


function SummaryCard(node, resource, flags) {
    ResourceCard.call(this, node, resource);
    this.cardType = 'multi';
    this.cardTitle = node.label;
};

SummaryCard.prototype = new ResourceCard();

SummaryCard.prototype.populateFields = function () {
    this.addField('count', this.node.count, 'value');
};

SummaryCard.prototype.getUrl = function (resource_uniq) {
    return '/client_service/view?resource=/graph/' + resource_uniq;
};


function PipelineStepCard(node, resource, flags) {
    ResourceCard.call(this, node, resource);
    this.cardType = flags['type'];
    suffix = (flags['type'].endsWith('_ignored') ? ' (inactive)' : (flags['type'].endsWith('_incompatible') ? ' (incompatible)' : ''))
    this.cardTitle = node ? node.name + suffix : 'Unknown action';
};

PipelineStepCard.prototype = new ResourceCard();

PipelineStepCard.prototype.populateFields = function (xnode) {
    // For pipeline step, assume this xnode structure:
    // <tmpnode>
    //   <attribute name='attr_name' value='attr_value' />
    //   <attribute name='attr_name' value='attr_value' />
    //   ...
    // </tmpnode>
    for (var i = 0; i < xnode.children.length; i++) {
        attr_name = xnode.children[i].getAttribute('name');
        attr_value = xnode.children[i].getAttribute('value');
        var val = Ext.JSON.decode(attr_value);
        num_fields = this.recurseFields(val, attr_name, 0, 0);
        if (num_fields > 30) {
            this.addField('<<< SOME FIELDS OMITTED >>>', '', 'value');
            break;
        }
    }
};

PipelineStepCard.prototype.recurseFields = function (val, attr_name, depth, num_fields) {
    if (depth > 4 || num_fields > 30) {
        return num_fields;
    }
    var indent = Array(depth*3+1).join(":");
    if (typeof val == 'string' || typeof val == 'number' || typeof val == 'boolean') {
        var attr_value = String(val);
        attr_value = attr_value.replace(/</g, "{").replace(/>/g, "}")  // graph UI gets confused with '<'/'>'
        this.addField(indent+attr_name, attr_value, 'value');
        num_fields += 1;
    }
    else {
        if (Array.isArray(val) && (val.length != 1 || typeof val[0] != 'object')) {
            this.addField(indent+'[ '+attr_name+' ]', (depth == 4 ? '...' : ''), 'value');
            num_fields += 1;
            for (var ii = 0; ii < val.length; ii++) {
                num_fields = this.recurseFields(val[ii], ''+(ii+1), depth+1, num_fields);
                if (num_fields > 30) {
                    break;
                }
            }
        }
        else {
            if (Array.isArray(val)) {
                val = val[0];
            }
            this.addField(indent+'[ '+attr_name+' ]', (depth == 4 ? '...' : ''), 'value');
            num_fields += 1;
            for (let key of Object.keys(val).sort()) {
                if (val.hasOwnProperty(key)) {
                    num_fields = this.recurseFields(val[key], key, depth+1, num_fields);
                    if (num_fields > 30) {
                        break;
                    }
                }
            }
        }
    }
    return num_fields;
};

function BQFactoryGraph(){
};

BQFactoryGraph.make = function(node, resource){
    var buffermap = {
        image            : ImageCard,
        table            : TableCard,
    };
    flags = {};
    if (node.label.startsWith("multi ")) {
        card = SummaryCard;
    }
    else if (node.label.startsWith("mex")) {
        card = MexCard;
    }
    else if (node.label.startsWith("dataset")) {
        card = DataSetCard;
    }
    else if (node.label.indexOf("_pipeline") !== -1) {
        card = PipelineCard;
    }
    else if (node.label.startsWith("pipeline_step")) {
        card = PipelineStepCard;
        flags["type"] = node.label;
    }
    else {
        card = buffermap[node.label];
    }
    if (!card) {
        // for all other types, use ResourceCard
        card = ResourceCard;
    }
    return new card(node, resource, flags);
};


Ext.define('BQ.graphviewer', {
    //extend: 'Ext.container.Container',
    extend : 'BQ.graph.d3',
    alias : 'widget.bq_graphviewer',
    border : 0,
    frame : false,
    initComponent: function() {
        this.numLoaded = 0;
        this.loaded = false;
        this.callParent();
    },
    registerMouseEvents: function(){

    },

    fetchNode : function(resource_uniq, node){
        var me = this;
        var gnode = node;
        console.log(node);
        var g = this.g;
        if (resource_uniq.startsWith("00-") && resource_uniq.indexOf('/') == -1){
            // actual resource => fetch it and populate GUI card
            var resUniqueUrl = (this.hostName ? this.hostName : '') + '/data_service/' + resource_uniq;
            Ext.Ajax.request({
    			url : resUniqueUrl,
    			scope : this,
    			disableCaching : false,
    			callback : function (opts, succsess, response) {
    				if (response.status >= 400)
    					BQ.ui.error(response.responseText);
    				else {
    					if (!response.responseXML)
    						return;
    					var xmlDoc = response.responseXML;
                        console.log(xmlDoc);
                        var xnode = xmlDoc.childNodes[0];
                        if(gnode && gnode.card){
                            gnode.card.populateFields(xnode);
                            gnode.card.buildHtml();
                        }
                        me.fetchNodeDone();
    				}
    			},
    		});
    	}
    	else {
    	    // summary node (uniq='00-xxxx/id') or other node => only populate GUI card using fake XML doc
    	    if(gnode && gnode.card){
    	        var xmlDoc = document.implementation.createDocument(null, "tmpdoc");
    	        var xnode = xmlDoc.createElement("tmpnode");
    	        if ('extra_attr_Parameters' in gnode) {
    	            // add node attributes as children (because we may have duplicate attr names and order may matter)
    	            for (var attr in gnode['extra_attr_Parameters']) {
    	                if (gnode['extra_attr_Parameters'].hasOwnProperty(attr)) {
        	                var subnode = xmlDoc.createElement("attribute");
        	                // assume each attribute is a singleton hashtable {name:value}
        	                var name = Object.keys(gnode['extra_attr_Parameters'][attr])[0];
        	                subnode.setAttribute("name", name);
        	                subnode.setAttribute("value", Ext.JSON.encode(gnode['extra_attr_Parameters'][attr][name]));
        	                xnode.appendChild(subnode);
    	                }
    	            }
    	        }
                gnode.card.populateFields(xnode);
                gnode.card.buildHtml();
            }
            me.fetchNodeDone();
    	}
    },

    fetchNodeDone : function(){
        var me = this;
        var g = this.g;
        me.numLoaded++;
        if(me.numLoaded === g.nodes().length){
            me.render(me.group, g);
            me.forceRefresh(0);
            me.zoomExtents();
            var svgNodes = me.group.selectAll("g.node");
            var svgEdges = me.group.selectAll("g.edgePath");

            // pick as start index, based on availability: resource_uniq, "0", or first key
            var startIndex = (g.nodes().indexOf(me.resource.resource_uniq) != -1 ? me.resource.resource_uniq : (g.nodes().indexOf("0") != -1 ? "0" : g.nodes()[0]));
            me.highLightProvenance(g, startIndex, svgNodes, svgEdges, me);
            me.selection = me.highLightEdges(g, startIndex, svgNodes, svgEdges);

            me.fireEvent("loaded", me);
        }
    },

    fetchNodeInfo : function(){
        var me = this;
        var g = this.g;

        g.nodes().forEach(function(v) {
            var node = g.node(v);
            me.fetchNode(v,node);
            node.rx = node.ry = 5;
            node.padding = 1.5;
        });
    },

    traverse : function(g, i, func, scope){
        var stack = [i];
        var traversed = [];
        for(var i = 0; i < g.nodeCount(); i++)
            traversed[i] = false;

        while(stack.length > 0){
            var nIndex = stack.pop();
            var node = g.node(nIndex);
            var edges = g.nodeEdges(nIndex);
            if (edges) {
                edges.forEach(function(e, i, a){
                    var oIndex = e.v == nIndex ? e.w : e.v;
                    if(!traversed[oIndex] && func(oIndex, e, traversed[oIndex])){
                        stack.push(oIndex);
                    }
                    traversed[nIndex] = true;
                });
            }
        }
    },

    highLightProvenance : function(g, i, svgNodes, svgEdges, scope){
        var nodes = [];
        var edges = [];
        svgEdges.attr('class', 'edgePath');
        svgNodes.attr('class', function(v){return 'node ' + g.node(v).card.cardType});

        scope.traverse(g, i, function(n,e,t){
            if(n == e.v){
                if(!t){
                    nodes.push(n);
                }
                edges.push(e);
                return true;
            }
            return false;
        }, scope);
        scope.traverse(g, i, function(n,e, t){
            if(n == e.w) {
                if(!t)
                    nodes.push(n);

                edges.push(e);
                return true;
            }
            return false;
        }, scope);

        nodes.forEach(function(e,i,a){
            var localNodes = svgNodes
                .filter(function(d){return (d===e) ? this : null;});
            var node = g.node(e);
            var selCls = 'node ' + node.card.cardType + ' watershed';
            localNodes.attr('class', selCls);

        });


        edges.forEach(function(e,i,a){
            var localEdges = svgEdges
                .filter(function(d){return (d.v===e.v && d.w===e.w) ? this : null;});
            localEdges.attr('class', 'edgePathHighlighted');
        });

    },

    highLightEdges : function(g, i, svgNodes, svgEdges){
        var node = g.node(i);
        var nodeEdges = g.nodeEdges(i);
        var localEdgesIn = svgEdges
            .filter(function(d){
                return (d.w === i) ? this : null;});

        var localEdgesOut = svgEdges
            .filter(function(d){
                return (d.v === i) ? this : null;});

        var localNodes = svgNodes
            .filter(function(d){return (d===i) ? this : null;});


        var selCls = 'node ' + node.card.cardType + ' selected';
        localNodes.attr('class', selCls);

        localEdgesOut.attr('class', 'edgePathSelectedOut');
        localEdgesIn.attr('class', 'edgePathSelectedIn');
        return [localNodes,localEdgesIn,localEdgesOut];
    },

    forceRefresh : function(timeOutDuration){
        //unfortunatley there can be a refresh problem, so I refresh the div
        //during animation to enable smooth animation
        var me = this;
        var force = function(){
            var el = me.getEl().dom;
            el.style.cssText += ';-webkit-transform:rotateZ(0deg)';
            el.offsetHeight;
            el.style.cssText += ';-webkit-transform:none';

        };

        if(timeOutDuration === 0){
            force();
        }

        else{
            var refreshing = true;
            var refreshTimer = function(){
                requestAnimationFrame(function() {
                    if(refreshing){
                        force();
                        refreshTimer();
                    }
                });
            };
            refreshTimer();
            setTimeout(
                callback(this, function () {
			        refreshing = false;
                }), timeOutDuration);
        }
    },

    getTranslation : function(d3node){
        var trans = d3node.attr("transform");
        var ts = trans.indexOf("(");
        var te = trans.indexOf(")");
        trans = trans.slice(ts + 1, te);
        trans = trans.split(",");
        trans = [parseFloat(trans[0]),parseFloat(trans[1])];
        return trans;
    },

    zoomExtents : function(){
        var me = this;
        var el = this.getEl().dom;

        var margin = 50;
        var w = this.getWidth()  - margin;
        var h = this.getHeight() - margin;

        var bbox = this.group.selectAll("g").node().getBBox();
        var bbw = bbox.width;
        var bbh = bbox.height;
        var min = w/bbw < h/bbh ? w/bbw : h/bbh;
        var trans = [(w-min*bbw)/2 + margin/2, (h-min*bbh)/2 + margin/2];
        this.zoom.scale(min);
        this.scale = min;
        this.group
            .transition()
            .duration(750)
            .attr("transform", "translate(" + trans + ")" +
                        "scale(" + min + ")");
            this.forceRefresh(760);

    },

    zoomToCurrent : function(){
        if(!this.selection){
            this.zoomExtents();
            return;
        }
        var me = this;
        var el = this.getEl().dom;
        var bbox = this.group.selectAll("g").node().getBBox();
        var bboxSel =  this.selection[0].node().getBBox();

        var w = this.getWidth();
        var h = this.getHeight();

        var bbw = bboxSel.width;
        var bbh = bbox.height;

        var bbsw = bboxSel.width;
        var bbsh = bboxSel.height;
        //var bby = bboxSel.y;
        var elTrans = this.getTranslation(this.selection[0]);

        var min = w/bbw < h/bbh ? w/bbw : h/bbh;
        var mins = bbw/bbsw < bbh/bbsh ? bbw/bbsw : bbh/bbsh;
        var newScale = 2.0*mins;
        if(newScale < this.scale) newScale = this.scale;

        var trans = [w/2 - newScale*elTrans[0],
                     h/2 - newScale*elTrans[1]];

        this.zoom.scale(newScale);
        this.scale = newScale;
        this.group
            .transition()
            .duration(750)
            .attr("transform", "translate(" + trans + ")" +
                        "scale(" + newScale + ")");
        this.forceRefresh(760);

    },

    buildGraph : function(nodes, edges, members, rankdir){
        var me = this;
        var data1 = this.data;

        var svg = this.svg;
        var color = d3.scale.category20();

        var window = this.svg
            .insert("rect", "g")
            .attr("width", "100%")
            .attr("height","100%")
            .attr("fill", "rgb(200,200,200)")
            .attr("opacity", 0.5);

        var g = new dagreD3.graphlib.Graph()
            .setGraph({})
            .setDefaultEdgeLabel(function() {return {}; });

        this.g = g;

        nodes.forEach(function(e,i,t){
            var t = e['type'];
            var val = e['value'];
            var cnt = e['count'];
            var name = e['name'];
            var props = {label: t, count: cnt, name: name};
            for (var attr in e) {
                if (e.hasOwnProperty(attr) && attr.startsWith('extra_attr_')) {
                    props[attr] = e[attr];
                }
            }
            g.setNode(val, props);
        });

        edges.forEach(function(e,i,a){
            var val = e['value'].split(':');
            g.setEdge(val[0], val[1],{
                lineInterpolate: 'basis'
            });
        });

        members.forEach(function(e,i,a){
            var val = e['value'].split(':');
            g.setEdge(val[0], val[1],{
            	style: "stroke-dasharray: 5, 5; fill: none;",
            	arrowhead: "undirected"
            });
        });

        g.nodes().forEach(function(v) {
            var node = g.node(v);
            console.log(v, g.node(v));
            // Round the corners of the nodes
            node.rx = node.ry = 5;
            node.padding = 0.0;
            node.card = BQFactoryGraph.make(node, v);
        });


        g.graph().rankdir = rankdir;
        g.graph().nodeSep = 20;
        g.graph().edgeSep = 10;
        g.graph().rankSep = 20;
        // Create the renderer
        this.render = new dagreD3.render();

        // Set up an SVG group so that we can translate the final graph.
        //var svgGroup = svg.append("g");
        // Set up zoom support

        var svgGroup = this.group;
        this.trans = [0,0];

        var wheel = false;
        var smx, smy;
        this.zoom = d3.behavior.zoom().on("zoom", function() {

            var w = me.getWidth();
            var h = me.getHeight();
            var bbox = me.group.selectAll("g").node().getBBox();
            var bbw = bbox.width;
            var bbh = bbox.height;

            var dx = d3.event.sourceEvent.movementX;
            var dy = d3.event.sourceEvent.movementY;
            var mx = d3.event.sourceEvent.offsetX;
            var my = d3.event.sourceEvent.offsetY;
            var scale = d3.event.scale;

            var ctrans = me.getTranslation(me.group);
            ctrans[0] += dx;
            ctrans[1] += dy;

            //there is some drifting going on, so wheel lock the
            //if(!wheel){
            smx = (mx - ctrans[0]);
            smy = (my - ctrans[1]);
            smx = smx*scale/me.scale - smx;
            smy = smy*scale/me.scale - smy;
            me.scale = scale;
            //}
            //console.log(smx/scale, smy/scale, me.group.selectAll("g").node().getBBox());
            wheel = (d3.event.sourceEvent.type === "wheel");
            if(wheel){
                //var trans = [me.trans[0],[me.trans[1]];
                ctrans[0] -= smx;
                ctrans[1] -= smy;
                wheel = true;
            }

            svgGroup.attr("transform", "translate(" + ctrans + ")" +
                          "scale(" + scale + ")");


            //force refresh:
            me.forceRefresh(0);
        });
        this.svg.call(this.zoom);

        // Run the renderer. This is what draws the final graph.
        this.render(svgGroup, g);

        var svgNodes = svgGroup.selectAll("g.node");
        var svgEdges = svgGroup.selectAll("g.edgePath");

        this.selection;
        svgGroup.selectAll("g.node")
            //.attr("title", function(v) { return styleTooltip(v, g.node(v).description) })
            .on("mousedown", function(d){
                if(me.selection){
                    me.selection[0].attr('class', 'node ' + g.node(d).card.cardType);
                    me.selection[1].attr('class', 'edgePath');
                    me.selection[2].attr('class', 'edgePath');
                    selection = [];
                }
                me.highLightProvenance(g, d, svgNodes, svgEdges, me);
                me.selection = me.highLightEdges(g, d, svgNodes, svgEdges);
                //force refresh:
                me.forceRefresh(0);
                var div = this.getElementsByTagName('div')[1];
                var mouse = d3.event;
                if(mouse.button === 0){
                    me.fireEvent('mousedown', d, div, me);
                    //me.zoom.interrupt();
                }
                if(mouse.button === 2){
                    me.fireEvent('context', d, div, me);
                    //me.zoom.interrupt();
                }
            });

        /*
        svgGroup.selectAll("g.node")
            .attr("title", function(v) {
                return "tooltip";
                return styleTooltip(v, g.node(v).description)
            }).each(function(v) { $(this).tipsy({ gravity: "w", opacity: 1, html: true }); });;
            */

        svgGroup.selectAll("g.node")
            .attr("class", function(v) {
                return 'node ' + g.node(v).card.cardType;
            });

        //this.zoomExtents();
    },

    buildGraphForce : function(){
        var me = this;
        var data1 = this.data;

        var svg = this.svg;
        var color = d3.scale.category20();

        var window = this.svg
            .append("rect")
            .attr("width", "100%")
            .attr("height","100%")
            .attr("fill", "rgb(200,200,200)")
            .attr("opacity", 0.5);

        this.force = d3.layout.force()
            .charge(-120)
            .linkDistance(30)
            .linkStrength(2)
            .size([this.getWidth(), this.getHeight()]);

        this.force
            .nodes(this.graph.nodes)
            .links(this.graph.links)
            .start();

        var link = svg.selectAll(".link")
            .data(this.graph.links)
            .enter().append("line")
            .attr("class", "link")
            .style("stroke", "rgb(128,128,128)")
            .style("stroke-width", function(d) { return Math.sqrt(d.value); });

        var node = svg.selectAll(".node")
            .data(this.graph.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", 5)
            .style("fill", function(d) { return color(d.group); })
            .call(this.force.drag);

        node.append("title")
            .text(function(d) { return d.name; });

        this.force.on("tick", function() {
            link.attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; });

            node.attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; });
        });

    },

    findInterval : function(me) {
    },

    updateScale : function(){
    },

    redraw : function(){
    },

    updateGraph : function(dp){
    },

    afterRender : function() {
        this.callParent();
        this.gridSizeX = 1;
        this.gridSizeY = 1;
    },

    afterFirstLayout : function() {
        this.callParent();
        //this.initBrush();
        //this.buildGraph();

    },

});

Ext.define('BQ.viewer.Graph.Panel', {
	alias : 'widget.bq_basegraphviewer_panel',
	extend : 'Ext.panel.Panel',
	//border : 0,
	cls : 'bq-graph-panel',
	layout : 'fit',

    zoomExtents: function(){
        this.graphView.zoomExtents();
    },

    zoomToCurrent: function(){
        this.graphView.zoomToCurrent();
    },

    fetchGraphData : function(){
        // resource_type can be
        //   - 'graph_url': fetch graph from graph service
        //   - 'dataservice_url': fetch graph from data service (as a doc)
        //   - 'blobservice_url': fetch graph from pipeline service (as JSON doc)
        var resUniqueUrl = (this.hostName ? this.hostName : '') +
            (this.resourceType === 'blobservice_url' ? '/pipeline/' : (this.resourceType === 'dataservice_url' ? '/data_service/' : '/graph/')) +
            this.resource.resource_uniq; // !!! .split('@')[0];
        var rparams = (this.resourceType === 'blobservice_url' ? {} : { view: 'deep' });
        Ext.Ajax.request({
			url : resUniqueUrl,
			params : rparams,
			scope : this,
			disableCaching : false,
			callback : function (opts, succsess, response) {
				if (response.status >= 400)
					BQ.ui.error(response.responseText);
				else {
					if ((this.resourceType !== 'blobservice_url' && !response.responseXML) ||
					    (this.resourceType === 'blobservice_url' && !response.responseText)) {
						return;
					}

                    // nodes: [ {name:..., type:..., value:..., <addtl. attrib>}, ... ]
                    // edges: [ {value: "from:to"}, ...]
                    var nodes = [];
                    var edges = [];
                    var members = [];

					if (this.resourceType === 'blobservice_url') {
                        // Extract nodes/edges from a JSON document
                        // Assumes this structure:
                        // {
                        //     <node_id> : { <key>:<value>, ..., <key>:<value> },
                        //     ...
                        //     <node_id> : { <key>:<value>, ..., <key>:<value> },
                        //     "edges" :  [ { "from" : <node_id>, "to" : <node_id> },
                        //                  ...,
                        //                  { "from" : <node_id>, "to" : <node_id> } ],
                        //     ...
                        // }
					    var txt = response.responseText;
					    // parse json and extract nodes/edges
                        json = Ext.JSON.decode(txt);
                        var context =  {root:json, nodes:nodes, edges:edges };
                        this.extractNodesEdges( context );
					}
					else {
					    // Extract nodes/edges from an XML document
					    // Assumes this structure:
					    // <graph ...>
					    //    <node type="..." value="<node_id>" ... />
					    //    ...
					    //    <node type="..." value="<node_id>" ... />
					    //    <edge value="<from>:<to>"/>
					    //    ...
					    //    <edge value="<from>:<to>"/>
					    //    ...
					    // </graph>
					    var xmlDoc = response.responseXML;
					    // extract nodes/edges
                        var xnodes = BQ.util.xpath_nodes(xmlDoc, "graph/node");
                        var xedges = BQ.util.xpath_nodes(xmlDoc, "graph/edge");
                        var xmembers = BQ.util.xpath_nodes(xmlDoc, "graph/member");
                        // convert to objects
                        for (var i = 0; i < xnodes.length; i++) {
                            node = {};
                            for (var ai = 0; ai < xnodes[i].attributes.length; ai++) {
                                var attr = xnodes[i].attributes[ai];
                                node[attr.name] = attr.value;
                            }
                            nodes.push(node);
                        }
                        for (var i = 0; i < xedges.length; i++) {
                            edge = {};
                            for (var ai = 0; ai < xedges[i].attributes.length; ai++) {
                                var attr = xedges[i].attributes[ai];
                                edge[attr.name] = attr.value;
                            }
                            edges.push(edge);
                        }
                    }

                    this.graphView.buildGraph(nodes, edges, members, this.rankdir);
                    this.graphView.fetchNodeInfo();
                    /*
                    for(var prop in graph.childNodes){
                        //var nodes = BQ.util.xpath_nodes(xmlDoc, "//tag[@name='value']/@value");
                        if(graph.childNodes.hasOwnProperty(prop)){
                            var child = graph.childNodes[prop];
                            //var val = BQ.util.xpath_nodes(xmlDoc, "//tag[@name='value']/@value")
                            var t = child.getAttribute('type');
                            alert(prop + " = " + value);
                        }
                    }*/				}
			},
		});
    },

    extractNodesEdges: function(context) {
        // context: {root:..., nodes:..., edges:..., name_key:..., type_key:..., fixed_type:...}
        var fields = [];
        var root = context['root'];
        var nodes = context['nodes'];
        var edges = context['edges'];
        var name_key = context['name_key'];
        var type_key = context['type_key'];
        var fixed_type = context['fixed_type'];
        for (var key in root) {
            if (!isNaN(key)) {
                // key is a number => assume node id
                new_node = root[key];
                new_node["name"] = (name_key ? root[key][name_key] : ''+key);
                new_node["type"] = (type_key ? root[key][type_key] : fixed_type);
                new_node["value"] = ''+key;
                for (var attr in root[key]) {
                    if (root[key].hasOwnProperty(attr) && attr != "name" && attr != "type" && attr != "value" && !attr.startsWith("__") && !attr.endsWith("__")) {
                        //new_node["extra_attr_"+attr] = String(root[key][attr]);
                        new_node["extra_attr_"+attr] = root[key][attr];
                    }
                }
                nodes.push(new_node);
            }
            else {
                if (key === 'edges') {
                    // TODO!!!
                }
            }
        }
    },

    afterRender : function(){
        this.fetchGraphData();
        this.callParent();
    },

    //afterFirstLayout : function(){
    //    this.fetchGraphData();
    //    this.callParent();
    //}
});


Ext.define('BQ.viewer.ProvenanceGraph.Panel', {
    alias : 'widget.bq_graphviewer_panel',
    extend : 'BQ.viewer.Graph.Panel',

    initComponent: function(){
        var me = this;

        this.graphView = Ext.create('BQ.graphviewer', {
            resource : this.resource,
            listeners:{
                loaded: function(res, div, comp){
                    me.setLoading(false);
                },
                context: function(res,div,comp){
                    me.fireEvent('context',res, div, comp);
                },
                mousedown: function(res,div,comp){
                    me.fireEvent('mousedown',res, div, comp);
                }
            }
        });

        this.items = [ this.graphView, {
            xtype : 'component',
            itemId : 'button-extents',
            autoEl : {
                tag : 'span',
                cls : 'control zoomextents',
            },

            listeners : {
                scope : this,
                click : {
                    element : 'el', //bind to the underlying el property on the panel
                    fn : this.zoomExtents,
                    scope: me
                },
            }
        }, {
            xtype : 'component',
            itemId : 'button-tocurrent',
            autoEl : {
                tag : 'span',
                cls : 'control zoomtocurrent',
            },
            listeners : {
                scope : this,
                click : {
                    element : 'el', //bind to the underlying el property on the panel
                    fn : this.zoomToCurrent,
                    scope: me
                },
            },
        }];
        this.setLoading(true);
        this.callParent();
    },

});


Ext.define('BQ.viewer.Pipeline.Panel', {
    alias : 'widget.bq_pipelineviewer_panel',
    extend : 'BQ.viewer.Graph.Panel',

    initComponent: function(){
        var me = this;

        this.graphView = Ext.create('BQ.graphviewer', {
            resource : this.resource,
            listeners:{
                loaded: function(res, div, comp){
                    me.setLoading(false);
                },
            }
        });

        this.items = [ this.graphView, {
            xtype : 'component',
            itemId : 'button-extents',
            autoEl : {
                tag : 'span',
                cls : 'control zoomextents',
            },

            listeners : {
                scope : this,
                click : {
                    element : 'el', //bind to the underlying el property on the panel
                    fn : this.zoomExtents,
                    scope: me
                },
            }
        }, {
            xtype : 'component',
            itemId : 'button-tocurrent',
            autoEl : {
                tag : 'span',
                cls : 'control zoomtocurrent',
            },
            listeners : {
                scope : this,
                click : {
                    element : 'el', //bind to the underlying el property on the panel
                    fn : this.zoomToCurrent,
                    scope: me
                },
            },
        }];
        this.setLoading(true);
        this.callParent();
    },

    extractNodesEdges: function(context) {
        // overwrite to handle pipeline files without (i.e., with implicit) edge information
        var me = this;

        context['name_key'] = '__Label__';
        context['type_key'] = undefined;
        context['fixed_type'] = 'pipeline_step';
        me.callParent([context]);

        // now add edges between consecutively numbered nodes
        var sorted_nodes = context['nodes'].sort(function(a,b) { return parseInt(a.value)-parseInt(b.value); });
        var previous_node = undefined;
        for (var i = 0; i < sorted_nodes.length; i++) {
            if (previous_node) {
                context['edges'].push({value: previous_node.value + ':' + sorted_nodes[i].value});
            }
            previous_node = sorted_nodes[i];
            // mark special steps
            meta = context['root'][parseInt(sorted_nodes[i].value)]['__Meta__'];
            if ('__compatibility__' in meta) {
                sorted_nodes[i].type = 'pipeline_step_' +  meta['__compatibility__'];
            }
        }
    },
});

//--------------------------------------------------------------------------------------
// Dialogue Box
//--------------------------------------------------------------------------------------

Ext.define('BQ.viewer.graphviewer.Dialog', {
	extend : 'Ext.window.Window',
	alias : 'widget.bq_graphviewer_dialog',
	//border : 0,
	layout : 'fit',
	modal : true,
	border : 0,
	width : '75%',
	height : '75%',
	buttonAlign : 'center',
	autoScroll : true,
	title : 'volume viewer',

	constructor : function (config) {
		config = config || {};

		Ext.apply(this, {
			//title : 'Move for ' + config.resource.name,
			items : [{
				xtype : 'bq_graphviewer_panel',
                resource: config.resource,
                //xtype: 'bq_graphviewer',
				//hostName : config.hostName,
				//resource : config.resource
			}],
		}, config);

		this.callParent(arguments);
		this.show();
	},
});

/*
function showGraphTool(volume, cls) {
	//renderingTool.call(this, volume);

    this.name = 'autoRotate';
	this.base = renderingTool;
    this.base(volume, this.cls);
};

showGraphTool.prototype = new renderingTool();

showGraphTool.prototype.init = function(){
    //override the init function,
    var me = this;
    // all we need is the button which has a menu
    this.createButton();
};

showGraphTool.prototype.addButton = function () {
    this.volume.toolMenu.add(this.button);
};

showGraphTool.prototype.createButton = function(){
    var me = this;

    this.button = Ext.create('Ext.Button', {
        width : 36,
        height : 36,
        cls : 'volume-button',
		handler : function (item, checked) {
            Ext.create('BQ.viewer.graphviewer.Dialog', {
                title : 'gl info',
                height : 500,
                width : 960,
                layout : 'fit',
            }).show();
		},
        scope : me,
    });

    this.button.tooltip = 'graph viewer temp';
};
*/
