/*
  ZSlider is a specialization of BQ.slider.Slider for Z axis.
  it will be automatically rendered in horizontal and provide a proper tip string

  Author: Dima Fedorov <dimin@dimin.net> <http://www.dimin.net/>
  Copyright (C) Center for BioImage Informatics <www.bioimage.ucsb.edu>
  GNU General Public License Usage

  History:
    2011-08-17 15:40:08 - first creation

  Ver: 1
*/

/**
 * @class BQ.slider.ZSlider
 * @extends BQ.slider.Slider
 * Example usage:
<pre><code>
    Ext.create('BQ.slider.ZSlider', {
        value: 50,
        increment: 1,
        minValue: 0,
        maxValue: 100,
        renderTo: Ext.getBody()
    });
</code></pre>
*/

Ext.define('BQ.slider.ZSlider', {
    extend: 'BQ.slider.Slider',
    alias: ['widget.slider_z'],
    alternateClassName: ['BQ.ZSlider', 'BQ.ui.ZSlider', 'BQ.slider.ZSlider'],

    cls: 'slider zslider',

    config: {
      //resolution: 1.0,
      unit: 'mu',
      orientation: 'vertical',
      height: 200,
      tooltip_play: 'Autoplay over depth (Z)',
      tooltip_next: 'Next Z position',
      tooltip_prev: 'Previous Z position'
    },

    tipText: function(thumb) {
        if (this.resolution && this.unit) {
            return Ext.String.format('<b>Z position: {0} or {1} {2} from first frame</b>',
                this.slider.getValue(), this.slider.getValue()*this.resolution, this.unit);
        } else {
            return Ext.String.format('<b>Z position: {0}</b>', this.slider.getValue());
        }
    },

});
