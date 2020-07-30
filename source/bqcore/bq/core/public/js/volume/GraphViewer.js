

Ext.define('BQ.graphviewer', {
    //extend: 'Ext.container.Container',
    extend : 'BQ.graph.d3',
    alias : 'widget.bq_graphviewer',
    border : 0,
    frame : false,

    graph: {
        "nodes":[
            {"name":"Myriel","group":1},
            {"name":"Napoleon","group":1},
            {"name":"Mlle.Baptistine","group":1},
            {"name":"Mme.Magloire","group":1},
            {"name":"CountessdeLo","group":1},
            {"name":"Geborand","group":1},
            {"name":"Champtercier","group":1},
            {"name":"Cravatte","group":1},
            {"name":"Count","group":1},
            {"name":"OldMan","group":1},
            {"name":"Labarre","group":2},
            {"name":"Valjean","group":2},
            {"name":"Marguerite","group":3},
            {"name":"Mme.deR","group":2},
            {"name":"Isabeau","group":2},
            {"name":"Gervais","group":2},
            {"name":"Tholomyes","group":3},
            {"name":"Listolier","group":3},
            {"name":"Fameuil","group":3},
            {"name":"Blacheville","group":3},
            {"name":"Favourite","group":3},
            {"name":"Dahlia","group":3},
            {"name":"Zephine","group":3},
            {"name":"Fantine","group":3},
            {"name":"Mme.Thenardier","group":4},
            {"name":"Thenardier","group":4},
            {"name":"Cosette","group":5},
            {"name":"Javert","group":4},
            {"name":"Fauchelevent","group":0},
            {"name":"Bamatabois","group":2},
            {"name":"Perpetue","group":3},
            {"name":"Simplice","group":2},
            {"name":"Scaufflaire","group":2},
            {"name":"Woman1","group":2},
            {"name":"Judge","group":2},
            {"name":"Champmathieu","group":2},
            {"name":"Brevet","group":2},
            {"name":"Chenildieu","group":2},
            {"name":"Cochepaille","group":2},
            {"name":"Pontmercy","group":4},
            {"name":"Boulatruelle","group":6},
            {"name":"Eponine","group":4},
            {"name":"Anzelma","group":4},
            {"name":"Woman2","group":5},
            {"name":"MotherInnocent","group":0},
            {"name":"Gribier","group":0},
            {"name":"Jondrette","group":7},
            {"name":"Mme.Burgon","group":7},
            {"name":"Gavroche","group":8},
            {"name":"Gillenormand","group":5},
            {"name":"Magnon","group":5},
            {"name":"Mlle.Gillenormand","group":5},
            {"name":"Mme.Pontmercy","group":5},
            {"name":"Mlle.Vaubois","group":5},
            {"name":"Lt.Gillenormand","group":5},
            {"name":"Marius","group":8},
            {"name":"BaronessT","group":5},
            {"name":"Mabeuf","group":8},
            {"name":"Enjolras","group":8},
            {"name":"Combeferre","group":8},
            {"name":"Prouvaire","group":8},
            {"name":"Feuilly","group":8},
            {"name":"Courfeyrac","group":8},
            {"name":"Bahorel","group":8},
            {"name":"Bossuet","group":8},
            {"name":"Joly","group":8},
            {"name":"Grantaire","group":8},
            {"name":"MotherPlutarch","group":9},
            {"name":"Gueulemer","group":4},
            {"name":"Babet","group":4},
            {"name":"Claquesous","group":4},
            {"name":"Montparnasse","group":4},
            {"name":"Toussaint","group":5},
            {"name":"Child1","group":10},
            {"name":"Child2","group":10},
            {"name":"Brujon","group":4},
            {"name":"Mme.Hucheloup","group":8}
        ],
        "links":[
            {"source":1,"target":0,"value":1},
            {"source":2,"target":0,"value":8},
            {"source":3,"target":0,"value":10},
            {"source":3,"target":2,"value":6},
            {"source":4,"target":0,"value":1},
            {"source":5,"target":0,"value":1},
            {"source":6,"target":0,"value":1},
            {"source":7,"target":0,"value":1},
            {"source":8,"target":0,"value":2},
            {"source":9,"target":0,"value":1},
            {"source":11,"target":10,"value":1},
            {"source":11,"target":3,"value":3},
            {"source":11,"target":2,"value":3},
            {"source":11,"target":0,"value":5},
            {"source":12,"target":11,"value":1},
            {"source":13,"target":11,"value":1},
            {"source":14,"target":11,"value":1},
            {"source":15,"target":11,"value":1},
            {"source":17,"target":16,"value":4},
            {"source":18,"target":16,"value":4},
            {"source":18,"target":17,"value":4},
            {"source":19,"target":16,"value":4},
            {"source":19,"target":17,"value":4},
            {"source":19,"target":18,"value":4},
            {"source":20,"target":16,"value":3},
            {"source":20,"target":17,"value":3},
            {"source":20,"target":18,"value":3},
            {"source":20,"target":19,"value":4},
            {"source":21,"target":16,"value":3},
            {"source":21,"target":17,"value":3},
            {"source":21,"target":18,"value":3},
            {"source":21,"target":19,"value":3},
            {"source":21,"target":20,"value":5},
            {"source":22,"target":16,"value":3},
            {"source":22,"target":17,"value":3},
            {"source":22,"target":18,"value":3},
            {"source":22,"target":19,"value":3},
            {"source":22,"target":20,"value":4},
            {"source":22,"target":21,"value":4},
            {"source":23,"target":16,"value":3},
            {"source":23,"target":17,"value":3},
            {"source":23,"target":18,"value":3},
            {"source":23,"target":19,"value":3},
            {"source":23,"target":20,"value":4},
            {"source":23,"target":21,"value":4},
            {"source":23,"target":22,"value":4},
            {"source":23,"target":12,"value":2},
            {"source":23,"target":11,"value":9},
            {"source":24,"target":23,"value":2},
            {"source":24,"target":11,"value":7},
            {"source":25,"target":24,"value":13},
            {"source":25,"target":23,"value":1},
            {"source":25,"target":11,"value":12},
            {"source":26,"target":24,"value":4},
            {"source":26,"target":11,"value":31},
            {"source":26,"target":16,"value":1},
            {"source":26,"target":25,"value":1},
            {"source":27,"target":11,"value":17},
            {"source":27,"target":23,"value":5},
            {"source":27,"target":25,"value":5},
            {"source":27,"target":24,"value":1},
            {"source":27,"target":26,"value":1},
            {"source":28,"target":11,"value":8},
            {"source":28,"target":27,"value":1},
            {"source":29,"target":23,"value":1},
            {"source":29,"target":27,"value":1},
            {"source":29,"target":11,"value":2},
            {"source":30,"target":23,"value":1},
            {"source":31,"target":30,"value":2},
            {"source":31,"target":11,"value":3},
            {"source":31,"target":23,"value":2},
            {"source":31,"target":27,"value":1},
            {"source":32,"target":11,"value":1},
            {"source":33,"target":11,"value":2},
            {"source":33,"target":27,"value":1},
            {"source":34,"target":11,"value":3},
            {"source":34,"target":29,"value":2},
            {"source":35,"target":11,"value":3},
            {"source":35,"target":34,"value":3},
            {"source":35,"target":29,"value":2},
            {"source":36,"target":34,"value":2},
            {"source":36,"target":35,"value":2},
            {"source":36,"target":11,"value":2},
            {"source":36,"target":29,"value":1},
            {"source":37,"target":34,"value":2},
            {"source":37,"target":35,"value":2},
            {"source":37,"target":36,"value":2},
            {"source":37,"target":11,"value":2},
            {"source":37,"target":29,"value":1},
            {"source":38,"target":34,"value":2},
            {"source":38,"target":35,"value":2},
            {"source":38,"target":36,"value":2},
            {"source":38,"target":37,"value":2},
            {"source":38,"target":11,"value":2},
            {"source":38,"target":29,"value":1},
            {"source":39,"target":25,"value":1},
            {"source":40,"target":25,"value":1},
            {"source":41,"target":24,"value":2},
            {"source":41,"target":25,"value":3},
            {"source":42,"target":41,"value":2},
            {"source":42,"target":25,"value":2},
            {"source":42,"target":24,"value":1},
            {"source":43,"target":11,"value":3},
            {"source":43,"target":26,"value":1},
            {"source":43,"target":27,"value":1},
            {"source":44,"target":28,"value":3},
            {"source":44,"target":11,"value":1},
            {"source":45,"target":28,"value":2},
            {"source":47,"target":46,"value":1},
            {"source":48,"target":47,"value":2},
            {"source":48,"target":25,"value":1},
            {"source":48,"target":27,"value":1},
            {"source":48,"target":11,"value":1},
            {"source":49,"target":26,"value":3},
            {"source":49,"target":11,"value":2},
            {"source":50,"target":49,"value":1},
            {"source":50,"target":24,"value":1},
            {"source":51,"target":49,"value":9},
            {"source":51,"target":26,"value":2},
            {"source":51,"target":11,"value":2},
            {"source":52,"target":51,"value":1},
            {"source":52,"target":39,"value":1},
            {"source":53,"target":51,"value":1},
            {"source":54,"target":51,"value":2},
            {"source":54,"target":49,"value":1},
            {"source":54,"target":26,"value":1},
            {"source":55,"target":51,"value":6},
            {"source":55,"target":49,"value":12},
            {"source":55,"target":39,"value":1},
            {"source":55,"target":54,"value":1},
            {"source":55,"target":26,"value":21},
            {"source":55,"target":11,"value":19},
            {"source":55,"target":16,"value":1},
            {"source":55,"target":25,"value":2},
            {"source":55,"target":41,"value":5},
            {"source":55,"target":48,"value":4},
            {"source":56,"target":49,"value":1},
            {"source":56,"target":55,"value":1},
            {"source":57,"target":55,"value":1},
            {"source":57,"target":41,"value":1},
            {"source":57,"target":48,"value":1},
            {"source":58,"target":55,"value":7},
            {"source":58,"target":48,"value":7},
            {"source":58,"target":27,"value":6},
            {"source":58,"target":57,"value":1},
            {"source":58,"target":11,"value":4},
            {"source":59,"target":58,"value":15},
            {"source":59,"target":55,"value":5},
            {"source":59,"target":48,"value":6},
            {"source":59,"target":57,"value":2},
            {"source":60,"target":48,"value":1},
            {"source":60,"target":58,"value":4},
            {"source":60,"target":59,"value":2},
            {"source":61,"target":48,"value":2},
            {"source":61,"target":58,"value":6},
            {"source":61,"target":60,"value":2},
            {"source":61,"target":59,"value":5},
            {"source":61,"target":57,"value":1},
            {"source":61,"target":55,"value":1},
            {"source":62,"target":55,"value":9},
            {"source":62,"target":58,"value":17},
            {"source":62,"target":59,"value":13},
            {"source":62,"target":48,"value":7},
            {"source":62,"target":57,"value":2},
            {"source":62,"target":41,"value":1},
            {"source":62,"target":61,"value":6},
            {"source":62,"target":60,"value":3},
            {"source":63,"target":59,"value":5},
            {"source":63,"target":48,"value":5},
            {"source":63,"target":62,"value":6},
            {"source":63,"target":57,"value":2},
            {"source":63,"target":58,"value":4},
            {"source":63,"target":61,"value":3},
            {"source":63,"target":60,"value":2},
            {"source":63,"target":55,"value":1},
            {"source":64,"target":55,"value":5},
            {"source":64,"target":62,"value":12},
            {"source":64,"target":48,"value":5},
            {"source":64,"target":63,"value":4},
            {"source":64,"target":58,"value":10},
            {"source":64,"target":61,"value":6},
            {"source":64,"target":60,"value":2},
            {"source":64,"target":59,"value":9},
            {"source":64,"target":57,"value":1},
            {"source":64,"target":11,"value":1},
            {"source":65,"target":63,"value":5},
            {"source":65,"target":64,"value":7},
            {"source":65,"target":48,"value":3},
            {"source":65,"target":62,"value":5},
            {"source":65,"target":58,"value":5},
            {"source":65,"target":61,"value":5},
            {"source":65,"target":60,"value":2},
            {"source":65,"target":59,"value":5},
            {"source":65,"target":57,"value":1},
            {"source":65,"target":55,"value":2},
            {"source":66,"target":64,"value":3},
            {"source":66,"target":58,"value":3},
            {"source":66,"target":59,"value":1},
            {"source":66,"target":62,"value":2},
            {"source":66,"target":65,"value":2},
            {"source":66,"target":48,"value":1},
            {"source":66,"target":63,"value":1},
            {"source":66,"target":61,"value":1},
            {"source":66,"target":60,"value":1},
            {"source":67,"target":57,"value":3},
            {"source":68,"target":25,"value":5},
            {"source":68,"target":11,"value":1},
            {"source":68,"target":24,"value":1},
            {"source":68,"target":27,"value":1},
            {"source":68,"target":48,"value":1},
            {"source":68,"target":41,"value":1},
            {"source":69,"target":25,"value":6},
            {"source":69,"target":68,"value":6},
            {"source":69,"target":11,"value":1},
            {"source":69,"target":24,"value":1},
            {"source":69,"target":27,"value":2},
            {"source":69,"target":48,"value":1},
            {"source":69,"target":41,"value":1},
            {"source":70,"target":25,"value":4},
            {"source":70,"target":69,"value":4},
            {"source":70,"target":68,"value":4},
            {"source":70,"target":11,"value":1},
            {"source":70,"target":24,"value":1},
            {"source":70,"target":27,"value":1},
            {"source":70,"target":41,"value":1},
            {"source":70,"target":58,"value":1},
            {"source":71,"target":27,"value":1},
            {"source":71,"target":69,"value":2},
            {"source":71,"target":68,"value":2},
            {"source":71,"target":70,"value":2},
            {"source":71,"target":11,"value":1},
            {"source":71,"target":48,"value":1},
            {"source":71,"target":41,"value":1},
            {"source":71,"target":25,"value":1},
            {"source":72,"target":26,"value":2},
            {"source":72,"target":27,"value":1},
            {"source":72,"target":11,"value":1},
            {"source":73,"target":48,"value":2},
            {"source":74,"target":48,"value":2},
            {"source":74,"target":73,"value":3},
            {"source":75,"target":69,"value":3},
            {"source":75,"target":68,"value":3},
            {"source":75,"target":25,"value":3},
            {"source":75,"target":48,"value":1},
            {"source":75,"target":41,"value":1},
            {"source":75,"target":70,"value":1},
            {"source":75,"target":71,"value":1},
            {"source":76,"target":64,"value":1},
            {"source":76,"target":65,"value":1},
            {"source":76,"target":66,"value":1},
            {"source":76,"target":63,"value":1},
            {"source":76,"target":62,"value":1},
            {"source":76,"target":48,"value":1},
            {"source":76,"target":58,"value":1}
        ]
    },

    initBrush: function(){
        //var rect = this.svg.select("#background-"+this.handle);
        var svgGroup = d3.select("#ext_svg-" + this.handle + " g");


    },

    initCrossHairs : function(){
        var me = this;
        var xMouse = this.svg.append("svg:line")
            .attr("stroke", "rgb(128,128,128)")
            .attr("x1", "0%")
            .attr("x2", "0%")
            .attr("y1", "0%")
            .attr("y2", "100%");

        var yMouse = this.svg.append("svg:line")
            .attr("stroke", "rgb(128,128,128)")
            .attr("x1", "0%")
            .attr("x2", "100%")
            .attr("y1", "0%")
            .attr("y2", "0%");

        var xText = this.svg.append("svg:text")
            .attr("fill", "rgb(128,128,128)")
            .attr("y", "2%")
            .attr("dy", ".71em")
            .attr("text-anchor", "right");

        var yText = this.svg.append("svg:text")
            .attr("fill", "rgb(128,128,128)")
            .attr("x", "2%")
            .attr("dy", ".71em")
            .attr("text-anchor", "right");

        this.svg
            .on("mousemove", function(){
                var xp = d3.event.clientX - me.getX();
                var yp = d3.event.clientY - me.getY();
                var offset = me.xScale.invert(xp);
                var alpha  = me.yScale.invert(yp);

                if(me.snap){
                    offset = Math.floor(offset/me.gridSizeX + 0.5)*me.gridSizeX;
                    alpha = Math.floor( alpha/me.gridSizeY  + 0.5)*me.gridSizeY;
                }

                xMouse
                    .attr("x1", me.xScale(offset))
                    .attr("x2", me.xScale(offset));
                yMouse
                    .attr("y1", me.yScale(alpha))
                    .attr("y2", me.yScale(alpha));

                xText
                    .attr("x", me.xScale(offset) + 2)
                    .text(offset.toFixed(4));
                yText
                    .attr("y", me.yScale(alpha) + 2)
                    .text(alpha.toFixed(4));
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
            edges.forEach(function(e, i, a){
                var oIndex = e.v == nIndex ? e.w : e.v;
                if(!traversed[oIndex] && func(oIndex, e, traversed[oIndex])){
                    stack.push(oIndex);
                }
                traversed[nIndex] = true;
            });
        }
    },

    highLightProvenance : function(g, i, svgNodes, svgEdges, scope){
        var nodes = [];
        var edges = [];
        svgEdges.attr('class', 'edgePath');
        svgNodes.attr('class', 'node');

        scope.traverse(g, i, function(n,e,t){
            if(n == e.v){
                if(!t){
                    nodes.push(n);
                    console.log(n, g.node(n));

                }
                console.log(e);

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
            localNodes.attr('class', 'nodeHighlighted');
        });


        edges.forEach(function(e,i,a){
            var localEdges = svgEdges
                .filter(function(d){return (d.v===e.v && d.w===e.w) ? this : null;});
            localEdges.attr('class', 'edgePathHighlighted');
        });

        console.log(nodes, edges);
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

        localNodes.attr('class', 'nodeSelected');
        localEdgesOut.attr('class', 'edgePathSelectedOut');
        localEdgesIn.attr('class', 'edgePathSelectedIn');
        return [localNodes,localEdgesIn,localEdgesOut];
    },


    buildGraph : function(){
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
        this.graph.nodes.forEach(function(e,i,a){
            //g.setNode(i, {label: e["name"], class: e["group"]});
            g.setNode(i, {label: e["name"]});

        });

        g.nodes().forEach(function(v) {
            var node = g.node(v);
            // Round the corners of the nodes
            node.rx = node.ry = 5;
            node.padding = 1.5;
        });

        this.graph.links.forEach(function(e,i,a){
            g.setEdge(e["source"], e["target"],{
                lineInterpolate: 'basis'
            });
        });
        g.graph().rankdir = "LR";
        g.graph().nodeSep = 10;
        g.graph().edgeSep = 5;
        g.graph().rankSep = 10;
        // Create the renderer
        var render = new dagreD3.render();

        // Set up an SVG group so that we can translate the final graph.
        //var svgGroup = svg.append("g");
        // Set up zoom support

        var svgGroup = this.group;
        var trans = [0,0];

        var zoom = d3.behavior.zoom().on("zoom", function() {
            me;
            var dx = d3.event.sourceEvent.movementX;
            var dy = d3.event.sourceEvent.movementY;
            trans[0] += dx;
            trans[1] += dy;
            svgGroup.attr("transform", "translate(" + trans[0] + ','+ trans[1] + ")" +
                          "scale(" + d3.event.scale + ")");


            //force refresh:
            var el = me.getEl().dom;
            el.style.cssText += ';-webkit-transform:rotateZ(0deg)'
            el.offsetHeight
            el.style.cssText += ';-webkit-transform:none'
        });
        this.svg.call(zoom);

        // Run the renderer. This is what draws the final graph.
        render(svgGroup, g);

        var svgNodes = svgGroup.selectAll("g.node");
        var svgEdges = svgGroup.selectAll("g.edgePath");

        var selection;
        svgGroup.selectAll("g.node")
            //.attr("title", function(v) { return styleTooltip(v, g.node(v).description) })
            .on("mousedown", function(d){
                if(selection){
                    selection[0].attr('class', 'node');
                    selection[1].attr('class', 'edgePath');
                    selection[2].attr('class', 'edgePath');
                    selection = [];
                }
                me.highLightProvenance(g, d, svgNodes, svgEdges, me);
                selection = me.highLightEdges(g, d, svgNodes, svgEdges);
                //force refresh:
                var el = me.getEl().dom;
                el.style.cssText += ';-webkit-transform:rotateZ(0deg)'
                el.offsetHeight
                el.style.cssText += ';-webkit-transform:none'
            });
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
        this.initBrush();
        this.buildGraph();

    },

});

Ext.define('BQ.viewer.Graph.Panel', {
	alias : 'widget.bq_graphviewer_panel',
	extend : 'Ext.panel.Panel',
	//border : 0,
	cls : 'bq-graph-panel',
	layout : 'fit',


    initComponent: function(){

        this.items = [ {
			xtype : 'bq_graphviewer',
			//hostName : config.hostName,
			//resource : config.resource
		},{
			xtype : 'component',
			itemId : 'button-extents',
			autoEl : {
				tag : 'span',
				cls : 'zoom-extents',
			},

			listeners : {
				scope : this,
				click : {
					element : 'el', //bind to the underlying el property on the panel
					fn : this.onMenuClick,
				},
			},

		}];


		this.callParent();
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
                //xtype: 'bq_graphviewer',
				//hostName : config.hostName,
				//resource : config.resource
			}],
		}, config);

		this.callParent(arguments);
		this.show();
	},
});

