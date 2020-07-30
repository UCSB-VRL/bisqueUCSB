/*
  TSlider is a specialization of BQ.slider.Slider for time axis.
  it will be automatically rendered in vertical and provide a proper tip string

  Author: Dima Fedorov <dimin@dimin.net> <http://www.dimin.net/>
  Copyright (C) Center for BioImage Informatics <www.bioimage.ucsb.edu>
  GNU General Public License Usage

  History:
    2011-08-17 15:40:08 - first creation

  Ver: 1
*/

/**
 * @class BQ.slider.TSlider
 * @extends BQ.slider.Slider
 * Example usage:
<pre><code>
    Ext.create('BQ.slider.TSlider', {
        value: 50,
        increment: 1,
        minValue: 0,
        maxValue: 100,
        renderTo: Ext.getBody()
    });
</code></pre>
*/

Ext.define('BQ.slider.TSlider', {
    extend: 'BQ.slider.Slider',
    alias: ['widget.slider_t'],
    alternateClassName: ['BQ.TSlider', 'BQ.ui.TSlider', 'BQ.slider.TSlider'],

    cls: 'slider tslider',

    config: {
      //resolution: 1.0,
      unit: 'ms',
      tooltip_play: 'Autoplay over time',
      tooltip_next: 'Next time point',
      tooltip_prev: 'Previous time point'
    },

    tipText: function(thumb) {
        if (this.resolution && this.unit) {
            return Ext.String.format('<b>Time point: {0} or {1} {2} from first frame</b>',
                this.slider.getValue(), this.slider.getValue()*this.resolution, this.unit);
        } else {
            return Ext.String.format('<b>T position: {0}</b>', this.slider.getValue());
        }
    },

});
