/*
  Bisque Slider is a slider for Bisque image viewer, it has auto play button and
  advance by 1 buttons, allows horizontal and vertical layout and adds hysteresis.

  Author: Dima Fedorov <dimin@dimin.net> <http://www.dimin.net/>
  Copyright (C) Center for BioImage Informatics <www.bioimage.ucsb.edu>
  GNU General Public License Usage

  History:
    2011-08-17 15:40:08 - first creation

  Ver: 1
*/

/**
 * @class BQ.slider.Slider
 * @extends Ext.container.Container
 * Example usage:
<pre><code>
    Ext.create('BQ.slider.Slider', {
        value: 50,
        increment: 1,
        minValue: 0,
        maxValue: 100,
        hysteresis: 250, // in ms
        resolution: 0.13,
        unit: 'microns',
        renderTo: Ext.getBody(),
        listeners: { scope: this, change: function(newValue) {
          // do stuff
        } },
    });

</code></pre>
*/

Ext.define('BQ.slider.Slider', {
    extend: 'Ext.container.Container',
    alias: ['widget.playslider'],
    alternateClassName: ['BQ.Slider', 'BQ.ui.Slider', 'BQ.slider.Slider'],

    requires: [
        'BQ.slider.Inversible',
        'Ext.slider.Single',
        'Ext.button.Button',
    ],

    cls: 'slider',

    config: {
      //resolution: 1.0,
      //unit: '',
      interval: 1000,
      orientation: 'horizontal',
      hysteresis: 500,  // delay before firing change event to the listner
      tooltip_play: 'Autoplay',
      tooltip_next: 'Next',
      tooltip_prev: 'Previous',
    },

    tipText: function(thumb){
        return Ext.String.format('<b>Position: {0}, </b>', this.slider.getValue());
    },

    constructor: function(config) {
        config = config || {};

        //Ext.apply(config, {
        //  layout  : config.layout || 1,
        //});

        Ext.apply(this, {
          items : [],
          listeners : config.listeners || {},
        }, config);

        this.initConfig(config);

        if (!this.orientation || this.orientation != 'vertical')
            this.width = this.width || 200;

        //this.self.instanceCount ++;
        return this.callParent(arguments);
    },



    initComponent: function() {
        var me = this;

        me.orientation = me.orientation || 'horizontal';
        if (me.orientation === 'vertical') {
            me.layout = {
                type : 'vbox',
                align: 'center',
                clearInnerCtOnLayout: true,
                bindToOwnerCtContainer: false
            };

        } else {
            me.layout = {
                type : 'hbox',
                align: 'middle',
                clearInnerCtOnLayout: true,
                bindToOwnerCtContainer: false
            };
        }

        // create components

        me.items = me.items || [];
        var btn_sz = 31;
        var spacing = 2;
        var isvertical = (me.orientation == 'vertical')?true:false;
        var cssmargin = isvertical?'0 0 '+spacing+'px 0':'0 0 0 '+spacing+'px';
        var slider_length = me.width - btn_sz*3 - (spacing*4*2);
        if (isvertical) slider_length = me.height - btn_sz*3 - (spacing*4*2);

        me.button_play = Ext.widget('button', {
            width: btn_sz,
            height: btn_sz,
            text: null,
            cls: isvertical?'button play-vertical':'button play',
            pressedCls: isvertical?'play-vertical-selected':'play-selected',
            overCls: isvertical?'x-play-vertical-selected':'x-play-selected',
            enableToggle: true,
            margin: cssmargin,
            tooltip: this.tooltip_play,
            listeners: {
                scope: me,
                click: function(btn, e, opt) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.togglePlay();
                },
            },
        });

        me.button_next = Ext.widget('button', {
            width: btn_sz,
            height: btn_sz,
            text: null,
            cls: isvertical?'button next-vertical':'button next',
            overCls: isvertical?'x-next-vertical-selected':'x-next-selected',
            tooltip: this.tooltip_next,
            margin: cssmargin,
            listeners: {
                scope: me,
                click: function(btn, e, opt) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.goNext();
                },
            },
        });

        me.button_prev = Ext.widget('button', {
            width: btn_sz,
            height: btn_sz,
            text: null,
            cls: isvertical?'button prev-vertical':'button prev',
            overCls: isvertical?'x-prev-vertical-selected':'x-prev-selected',
            margin: cssmargin,
            tooltip: this.tooltip_prev,
            listeners: {
                scope: me,
                click: function(btn, e, opt) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.goPrev();
                },
            },
        });

        me.slider = Ext.create('BQ.slider.Inversible', {
            width: isvertical?undefined:slider_length,
            height: isvertical?slider_length:undefined,
            increment: 1,
            animate: false,
            minValue: me.minValue,
            maxValue: me.maxValue,
            value: this.value || 0,
            margin: cssmargin,
            vertical: isvertical,
            inversed: isvertical,
            hideLabel: true,
            tipText: function(thumb) { return me.tipText(thumb); },
            listeners: {
                scope: me,
                change: function(slider, newValue, thumb, options) {
                    //this.fireEvent('change', newValue);
                    //this.queueFireChangeEvent(newValue);
                    this.queueFireChangeEvent(this.slider.getValue()); // dima, here fix in inversible change event
                },
            },
        });

        me.items.push(me.button_play);
        me.items.push(me.button_prev);
        me.items.push(me.slider);
        me.items.push(me.button_next);


        this.callParent();
    },

/*
    onRender: function() {
        this.callParent(arguments);
        this.createButtons();
    }, */

    goNext: function() {
        this.slider.stopAnimation();
        var v = this.slider.getValue();
        if (v!=undefined && !isNaN(v)) {
          if (v>=this.slider.maxValue) v=this.slider.minValue-1;
          this.slider.setValue(v+1);
        }
    },

    goPrev: function() {
        this.slider.stopAnimation();
        var v = this.slider.getValue();
        if (v!=undefined && !isNaN(v)) {
          if (v<=this.slider.minValue) v=this.slider.maxValue+1;
          this.slider.setValue(v-1);
        }
    },

    togglePlay: function() {
        if (this.player) {
          clearTimeout(this.player);
          this.player = null;
        } else {
          this.play();
        }
    },

    play: function() {
        this.goNext();
        this.player = setTimeout(callback(this, this.play), this.interval);
    },

    queueFireChangeEvent: function(val) {
        if (this.event_timeout) clearTimeout (this.event_timeout);
        var me = this;
        this.event_timeout = setTimeout(function(){ me.fireChangeEvent(val); }, this.hysteresis );
    },

    fireChangeEvent: function(val) {
        this.event_timeout = null;
        this.fireEvent('change', val);
    },

    setValue: function(v) {
        this.slider.stopAnimation();
        this.slider.setValue(v);
    },
});

