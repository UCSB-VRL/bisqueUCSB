Ext.namespace('Bisque.Misc');

Ext.define('Bisque.Misc.Slider', {
    extend : 'Ext.panel.Panel',
    height : 32,
    width : 200,
    border : false,
    leftBtn : false,
    rightBtn : false,

    label : null,
    slider : null,

    bodyStyle : 'background:transparent;',
    layout : {
        type : 'vbox',
        align : 'stretch',
    },
    items : [{
        xtype : 'tbtext',
        text : 'Showing 0 of total 0',
        style : 'text-align:center'
    }, {
        xtype : 'slider',
        //increment: 1,  
        animate: true,      
        minValue : 0,
        hideLabel : true,
        maxValue : 100,
        margin : '0 10 10 10',
        cls : 'sliderBackground',
        tipText : function(thumb) {
            return Ext.String.format('<b>View resource: {0}</b>', thumb.value);
        },
    }],

    initComponent : function() {
        this.callParent(arguments);

        this.label = this.getLabel();
        this.slider = this.getSlider();

        this.slider.on("changecomplete", function(me, newValue) {
            /*if (newValue==me.maxValue && this.rightBtn)
             this.fireEvent('leftButtonClick', newValue-1);
             else if (newValue==me.minValue && this.leftBtn)
             this.fireEvent('rightButtonClick', newValue-1);
             else*/
            this.fireEvent('buttonClick', newValue - 1);
        }, this);
    },

    getLabel : function() {
        return this.getComponent(0);
    },

    getSlider : function() {
        return this.getComponent(1);
    },

    setStatus : function(st) {
        if (!this.hidden) {
            var mySt = st.sliderSt;

            this.label.setText(st.status);

            this.showLeftBtn(mySt.left);
            this.showRightBtn(mySt.right);

            this.slider.setMinValue(mySt.min);
            this.slider.setMaxValue(mySt.max);

            this.slider.setValue(mySt.value);
            if (mySt.increment) 
                this.slider.increment = mySt.increment;            
        }
    },

    showLeftBtn : function(show) {
        if (show) {
            this.slider.addCls("sliderLeftButton");

            if (this.rightBtn)
                this.slider.addCls("sliderBothButtons");

            this.leftBtn = true;
        } else {
            if (this.rightBtn)
                this.slider.removeCls("sliderBothButtons");

            this.slider.removeCls("sliderLeftButton");

            this.leftBtn = false;
        }
    },

    showRightBtn : function(show) {
        if (show) {
            this.slider.addCls("sliderRightButton");

            if (this.leftBtn)
                this.slider.addCls("sliderBothButtons");

            this.rightBtn = true;
        } else {
            if (this.leftBtn)
                this.slider.removeCls("sliderBothButtons");

            this.slider.removeCls("sliderRightButton");

            this.rightBtn = false;
        }
    },

    destroy : function() {
        if (this.rendered && !this.hidden)
            this.callParent(arguments);
    }
}); 