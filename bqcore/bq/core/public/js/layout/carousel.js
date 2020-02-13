Ext.define('carouselContainer', {
    extend: 'Ext.container.Container'
    , alias: 'widget.carousel'
    
    , layout: {
        type: 'hbox'
        , align: 'stretch'
    }
    , defaults: { flex: 1 }
    , style: {
        background: 'url(http://3.bp.blogspot.com/-kanvyoXSOSs/Tsi0W496bzI/AAAAAAAAAG8/-Bq53wJqaqM/s320/carbonfibre.png)'
    }
    
    , initComponent: function () {
        var me = this;
        
        me.addEvents('carouselchange');
        
        me.callParent(arguments);
    }
    , onDocMouseup: function () {
        var me = this;
        me.drag = false;
        var children = me.items.items;
        var parentLeft = me.ownerCt.el.getLeft();
        var rule = 1000000;
        var target;
        Ext.each(children, function (div, i) {
            l = Math.abs(div.el.getLeft() - parentLeft);
            if (l < rule) {
                rule = l;
                target = div;
            };
        });
        me.showChild(target);
    }
    , onMousedown: function (e) {
        e.stopEvent();    // prevents selecting the underlying text and whatnot
        var me = this;
        me.drag = true;
        me.startX = e.getX();
        var par = me.el.first();
        par.on({
            mousemove: function (e) {
                e.stopEvent();    // prevents selecting the underlying text and whatnot
                if (me.drag) {
                    var rate = 1;
                    if (par.getLeft() > me.ownerCt.el.getLeft() || par.getRight() < me.ownerCt.el.getRight()) {
                        rate = 2;
                    }
                    par.move('l', (me.startX - e.getX()) / rate, false);
                    me.startX = e.getX();
                }
            }
        });
    }
    , syncSizeToOwner: function () {
        var me = this;
        if (me.ownerCt) {
            me.setSize(me.ownerCt.el.getWidth() * me.items.items.length, me.ownerCt.el.getHeight());
        }
    }
    , showChild: function (item) {
        var me = this
            , left = item.el.getLeft() - me.el.getLeft();
        me.el.first().move('l', left, true);
        me.currentItem = item;
        me.fireEvent('carouselchange', me, item);
    }
    , nextChild: function () {
        var me = this;
        var next = me.currentItem.nextSibling();
        me.showChild(next || me.items.items[0]);
    }
    , previousChild: function () {
        var me = this;
        var next = me.currentItem.previousSibling();
        me.showChild(next || me.items.items[me.items.items.length - 1]);
    }
    , onRender: function () {
        var me = this;
        
        me.currentItem = me.items.items[0];
        
        if (me.ownerCt) {
            me.relayEvents(me.ownerCt, ['resize'], 'owner');
            me.on({
                ownerresize: me.syncSizeToOwner
            });
        }
        
        me.mon(Ext.getBody(), 'mouseup', me.onDocMouseup, me);
        me.mon(Ext.fly(me.el.dom), 'mousedown', me.onMousedown, me);
        
        me.callParent(arguments);
    }
});

Ext.define('carouselTb', {
    extend: 'Ext.toolbar.Toolbar'
    , alias: 'widget.carouseltb'
    
    , directionals: true
    
    , initComponent: function () {
        var me = this;
        
        me.items = [{
            xtype: 'tbfill'
        }, {
            xtype: 'tbfill'
        }]
            
        me.callParent(arguments);
    }
    , handleCarouselEvents: function (carousel) {
        var me = this;
        me.relayEvents(carousel, ['carouselchange']);
        me.on('carouselchange', me.onCarouselChange, me, {buffer: 20});
    }
    , onCarouselChange: function (carousel, item) {
        var me = this;
        console.log(me);
        var navSprites = me.down('draw').surface.getGroup('carousel');
        navSprites.setAttributes({opacity: .2}, true);
        var i = carousel.items.indexOf(item);
        navSprites.each(function (s) {
            if (s.index == i) {
                s.animate({
                    to: {
                        opacity: .7
                    }
                });
            }
        });
    }
    , onRender: function () {
        var me = this;
        
        var prev = {
            text: '<'
            , handler: function () {
                me.ownerCt.down('carousel').previousChild();
            }
        };
        
        var next = {
            text: '>'
            , handler: function () {
                me.ownerCt.down('carousel').nextChild();
            }
        };
        
        Ext.suspendLayouts(); 
        if (me.directionals) {
            me.insert(0, prev);
            me.insert(me.items.items.length, next);
        }
    
        var index = me.items.indexOf(me.down('tbfill'));
        var circles = [];
        var x = 0;
        var i = 0;
        Ext.each(me.ownerCt.down('carousel').items.items, function (item) {
            var config = {
                type: 'circle'
                , x: x
                , y: 0
                , index: i
                , radius: 1
                , fill: 'black'
            , opacity: i == 0 ? .7 : .2
                , group: 'carousel'
            }
            circles.push(config);
            x += 3;
            i++;
        });
        me.insert(index + 1, {
            xtype: 'draw'
            , height: 12
            , items: circles
        });
    
        Ext.resumeLayouts();
        
        Ext.defer(function () {
            var c = me.down('draw').surface.getGroup('carousel');
            c.each(function (s) {
                s.on({
                    click: function (s) {
                        c.setAttributes({opacity: .2}, true);
                        var carousel = me.ownerCt.down('carousel');
                        carousel.showChild(carousel.items.items[s.index]);
                    }
                });
            });
        }, 2);
        
        var carousel = me.ownerCt.down('carousel');
        if (carousel) {
            me.handleCarouselEvents(carousel);
        }
                        
        me.callParent(arguments);
    }
});

