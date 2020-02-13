/*******************************************************************************
d3Compoenent - A ext compoenent that encapsulates d3;
@author John Delaney

Events:
mousedown     - event fired when the viewer is loaded
mousedup     - event fired when the viewer is loaded

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

Ext.define('BQ.graph.d3', {
    //extend: 'Ext.container.Container',
    extend : 'Ext.Component',
    alias : 'widget.d3_component',
    border : 0,
    frame : false,

    initD3 : function(){
        var me = this;

        function nozoom() {
            d3.event.preventDefault();
        }

        var thisDom = this.getEl().dom;
        this.handle = Math.floor(99999*Math.random());
        this.svg = d3.select('#' + thisDom.id)
            .on("touchstart", nozoom)
            .on("touchmove", nozoom)
            .append("svg:svg")
            .attr("id", "ext_svg-"+this.handle)
            .attr("width", "100%")
            .attr("height","100%")
            .on("mousedown", function(){me.fireEvent("mousedown");})
            .on("mouseup", function(){me.fireEvent("mouseup");});;

        this.group = this.svg.append("svg:g");
            //.on("mousedown", function(){me.findInterval(me); me.fireEvent("mousedown");})
            //735.on("mouseup", function(){me.fireEvent("mouseup");});

    },


    redraw : function(){
    },

    afterRender : function() {
        this.callParent();
    },

    afterFirstLayout : function() {
        this.callParent();
        this.addListener('resize', this.onresize, this);
        this.initD3();
    },

    onresize : function(){
        this.redraw();
    }
});
