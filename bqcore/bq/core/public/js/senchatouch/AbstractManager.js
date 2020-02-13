/**
 * @class ExtTouch.AbstractManager
 * @ExtTouchends Object
 * @ignore
 * Base Manager class - ExtTouchended by ComponentMgr and PluginMgr
 */
ExtTouch.AbstractManager = ExtTouch.ExtTouchend(Object, {
    typeName: 'type',

    constructor: function(config) {
        ExtTouch.apply(this, config || {});

        /**
         * Contains all of the items currently managed
         * @property all
         * @type ExtTouch.util.MixedCollection
         */
        this.all = new ExtTouch.util.HashMap();

        this.types = {};
    },

    /**
     * Returns a component by {@link ExtTouch.Component#id id}.
     * For additional details see {@link ExtTouch.util.MixedCollection#get}.
     * @param {String} id The component {@link ExtTouch.Component#id id}
     * @return ExtTouch.Component The Component, <code>undefined</code> if not found, or <code>null</code> if a
     * Class was found.
     */
    get : function(id) {
        return this.all.get(id);
    },

    /**
     * Registers an item to be managed
     * @param {Mixed} item The item to register
     */
    register: function(item) {
        this.all.add(item);
    },

    /**
     * Unregisters a component by removing it from this manager
     * @param {Mixed} item The item to unregister
     */
    unregister: function(item) {
        this.all.remove(item);
    },

    /**
     * <p>Registers a new Component constructor, keyed by a new
     * {@link ExtTouch.Component#xtype}.</p>
     * <p>Use this method (or its alias {@link ExtTouch#reg ExtTouch.reg}) to register new
     * subclasses of {@link ExtTouch.Component} so that lazy instantiation may be used when specifying
     * child Components.
     * see {@link ExtTouch.Container#items}</p>
     * @param {String} xtype The mnemonic string by which the Component class may be looked up.
     * @param {Constructor} cls The new Component class.
     */
    registerType : function(type, cls) {
        this.types[type] = cls;
        cls[this.typeName] = type;
    },

    /**
     * Checks if a Component type is registered.
     * @param {ExtTouch.Component} xtype The mnemonic string by which the Component class may be looked up
     * @return {Boolean} Whether the type is registered.
     */
    isRegistered : function(type){
        return this.types[type] !== undefined;
    },

    /**
     * Creates and returns an instance of whatever this manager manages, based on the supplied type and config object
     * @param {Object} config The config object
     * @param {String} defaultType If no type is discovered in the config object, we fall back to this type
     * @return {Mixed} The instance of whatever this manager is managing
     */
    create: function(config, defaultType) {
        var type        = config[this.typeName] || config.type || defaultType,
            Constructor = this.types[type];

        if (Constructor == undefined) {
            throw new Error(ExtTouch.util.Format.format("The '{0}' type has not been registered with this manager", type));
        }

        return new Constructor(config);
    },

    /**
     * Registers a function that will be called when a Component with the specified id is added to the manager. This will happen on instantiation.
     * @param {String} id The component {@link ExtTouch.Component#id id}
     * @param {Function} fn The callback function
     * @param {Object} scope The scope (<code>this</code> reference) in which the callback is executed. Defaults to the Component.
     */
    onAvailable : function(id, fn, scope){
        var all = this.all;

        all.on("add", function(index, o){
            if (o.id == id) {
                fn.call(scope || o, o);
                all.un("add", fn, scope);
            }
        });
    },
    
    /**
     * Executes the specified function once for each item in the collection.
     * Returning false from the function will cease iteration.
     * 
     * The paramaters passed to the function are:
     * <div class="mdetail-params"><ul>
     * <li><b>key</b> : String<p class="sub-desc">The key of the item</p></li>
     * <li><b>value</b> : Number<p class="sub-desc">The value of the item</p></li>
     * <li><b>length</b> : Number<p class="sub-desc">The total number of items in the collection</p></li>
     * </ul></div>
     * @param {Object} fn The function to execute.
     * @param {Object} scope The scope to execute in. Defaults to <tt>this</tt>.
     */
    each: function(fn, scope){
        this.all.each(fn, scope || this);    
    },
    
    /**
     * Gets the number of items in the collection.
     * @return {Number} The number of items in the collection.
     */
    getCount: function(){
        return this.all.getCount();
    }
});
