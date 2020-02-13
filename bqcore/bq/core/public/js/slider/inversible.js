/* 
  Inversible Slider is an extension to the default ExtJS Slider adding
  ability to invert the max and min values, useful for vertical sliders 
  that should start at the top and not at the bottom.
    
  Author: Dima Fedorov <dimin@dimin.net> <http://www.dimin.net/>
  Copyright (C) Center for BioImage Informatics <www.bioimage.ucsb.edu>
  GNU General Public License Usage

  History:
    2011-08-17 15:40:08 - first creation
      
  Ver: 1 
*/ 

/**
 * @class BQ.slider.Inversible
 * @extends Ext.slider.Single
 * Example usage:
<pre><code>
    Ext.create('BQ.slider.Inversible', {
        width: 200,
        value: 50,
        increment: 10,
        minValue: 0,
        maxValue: 100,
        inversed: true, 
        renderTo: Ext.getBody()
    });
</code></pre>
*/

Ext.define('BQ.slider.Inversible', {
    extend: 'Ext.slider.Single',
    alias: ['widget.inversibleslider'],
    alternateClassName: ['BQ.InversibleSlider', 'BQ.ui.InversibleSlider', 'BQ.slider.Inversible'],

    inversed: false,

    constructor: function(config) {
        if (arguments.length<1) arguments.push({});
        if (arguments[0].inversed) {
            arguments[0].value = arguments[0].value || 0;
            arguments[0].minValue = arguments[0].minValue || 0;
            arguments[0].maxValue = arguments[0].maxValue || 100; 
            arguments[0].value = arguments[0].maxValue-arguments[0].value+arguments[0].minValue;
        }
        return this.callParent(arguments);        
    },

    getValue: function() {
        if (this.inversed)
            return this.maxValue-this.callParent()+this.minValue;
        else
            return this.callParent();
    },

    setValue: function(value, animate) {        
        if (this.inversed) {
            var args = Ext.toArray(arguments),
                len  = args.length;
            if (!(len<=3 && typeof arguments[1] == 'number'))
                args[0] = this.maxValue-args[0]+this.minValue;
            return this.callParent(args);
        } else
            return this.callParent(arguments);     
    },

});

