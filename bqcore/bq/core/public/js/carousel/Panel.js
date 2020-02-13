
Ext.define('Ext.carousel.Panel', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.carouselpanel',
    alternateClassName: ['Ext.CarouselPanel'],

    tabPosition : 'bottom',
    plain: true,
    baseCls: Ext.baseCSSPrefix + 'carousel',        
    itemCls: 'x-carousel-child',
    border: 0,
    defaults: { border: 0, },
    
    tabBar: {
        baseCls: Ext.baseCSSPrefix + 'carousel-bar',
        plain: true,
    },

    onAdd: function(item, index) {
        var me = this;
        item.on({
            scope : me,
            enable: me.onItemEnable,
            disable: me.onItemDisable,
            iconchange: me.onItemIconChange,
            titlechange: me.onItemTitleChange,

            beforeshow: me.onItemBeforeShow,
            show: me.onItemShow,
            beforehide: me.onItemBeforeHide,                        
        });
        this.callParent(arguments);    
        item.tab.setText('');
        item.tab.setTooltip(item.title);
    },
    
    onItemBeforeShow: function(item) {
        item.stopAnimation();
        item.el.setStyle('opacity', 0);   
        this.callParent(arguments);    
    },
    
    onItemShow: function(me) { 
        me.animate({
            duration: 500,
            from: { opacity: 0, left: -100, },
            to: { opacity: 1, left: 0, },
        });
    }, 

    onItemBeforeHide: function(me) { 
        /*
        var op = me.el.getStyle('opacity');
        if (op==0) return true;
        if (me == this.activeTab) return true;        
        //me.stopAnimation();            
        me.animate({
            duration: 300,
            to: { opacity: 0, },
            listeners: {
                afteranimate: function() {
                    this.hide();
                },
                scope: me,
            },
        });
        return false;
        */
    },     
    
});

