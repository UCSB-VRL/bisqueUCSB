/**
 * @class Ext.ux.DataTip
 * @extends Ext.ToolTip.
 * <p>This plugin implements automatic tooltip generation for an arbitrary number of child nodes <i>within</i> a Component.</p>
 * <p>This plugin is applied to a high level Component, which contains repeating elements, and depending on the host Component type,
 * it automatically selects a {@link Ext.ToolTip#delegate delegate} so that it appears when the mouse enters a sub-element.</p>
 * <p>When applied to a GridPanel, this ToolTip appears when over a row, and the Record's data is applied
 * using this object's {@link Ext.Component#tpl tpl} template.</p>
 * <p>When applied to a DataView, this ToolTip appears when over a view node, and the Record's data is applied
 * using this object's {@link Ext.Component#tpl tpl} template.</p>
 * <p>When applied to a TreePanel, this ToolTip appears when over a tree node, and the Node's {@link Ext.tree.TreeNode#attributes attributes} are applied
 * using this object's {@link Ext.Component#tpl tpl} template.</p>
 * <p>When applied to a FormPanel, this ToolTip appears when over a Field, and the Field's <code>tooltip</code> property is used is applied
 * using this object's {@link Ext.Component#tpl tpl} template, or if it is a string, used as HTML content.</p>
 * <p>If more complex logic is needed to determine content, then the {@link Ext.Component#beforeshow beforeshow} event may be used.<p>
 * <p>This class also publishes a <b><code>beforeshowtip</code></b> event through its host Component. The <i>host Component</i> fires the
 * <b><code>beforeshowtip</code></b> event.
 */
Ext.ux.DataTip = Ext.extend(Ext.ToolTip, (function() {

    //  Target the body (if the host is a Panel), or, if there is no body, the main Element.
    function onHostRender() {
        var e = this.body || this.el;
        if (this.dataTip.renderToTarget) {
            this.dataTip.render(e);
        }
        this.dataTip.setTarget(e);
    }

    function updateTip(tip, data) {
        if (tip.rendered) {
            tip.update(data);
        } else {
            if (Ext.isString(data)) {
                tip.html = data;
            } else {
                tip.data = data;
            }
        }
    }

    function beforeTreeTipShow(tip) {
        var e = Ext.fly(tip.triggerElement).findParent('div.x-tree-node-el', null, true), node = e ? tip.host.getNodeById(e.getAttribute('tree-node-id', 'ext')) : null;
        if (node) {
            updateTip(tip, node.attributes);
        } else {
            return false;
        }
    }

    function beforeGridTipShow(tip) {
        var rec = this.host.getStore().getAt(tip.triggerElement.viewIndex);

        if (rec) {
            updateTip(tip, rec.data);
        } else {
            return false;
        }
    }

    function beforeViewTipShow(tip) {
        var rec = this.host.getRecord(tip.triggerElement);
        if (rec) {
            updateTip(tip, rec.data);
        } else {
            return false;
        }
    }

    function beforeFormTipShow(tip) {
        var el = Ext.fly(tip.triggerElement).child('input,textarea'), field = el ? this.host.getForm().findField(el.id) : null;
        if (field && (field.tooltip || tip.tpl)) {
            updateTip(tip, field.tooltip || field);
        } else {
            return false;
        }
    }

    function beforeComboTipShow(tip) {
        var rec = this.host.store.getAt(this.host.selectedIndex);
        if (rec) {
            updateTip(tip, rec.data);
        } else {
            return false;
        }
    }

    return {
        init : function(host) {
            host.dataTip = this;
            this.host = host;
            if ( host instanceof Ext.tree.TreePanel) {
                this.delegate = this.delegate || 'div.x-tree-node-el';
                this.on('beforeshow', beforeTreeTipShow);
            } else if ( host instanceof Ext.grid.GridPanel) {
                this.delegate = this.delegate || host.getView().itemSelector;
                this.on('beforeshow', beforeGridTipShow);
            } else if ( host instanceof Ext.DataView) {
                this.delegate = this.delegate || host.itemSelector;
                this.on('beforeshow', beforeViewTipShow);
            } else if ( host instanceof Ext.FormPanel) {
                this.delegate = 'div.x-form-item';
                this.on('beforeshow', beforeFormTipShow);
            } else if ( host instanceof Ext.form.ComboBox) {
                this.delegate = this.delegate || host.itemSelector;
                this.on('beforeshow', beforeComboTipShow);
            }
            if (host.rendered) {
                onHostRender.call(host);
            } else {
                host.onRender = Ext.Function.createSequence(host.onRender, onHostRender);
            }
        }
    };
})());
