/*
***UNIFIED MAP Window***
Updated to support both Google Maps and OpenStreetMap (Leaflet)
8/11
Google Map and OpenStreetMap in ExtJS 4 Wrapper

This file provides a unified interface for both Google Maps API V3 and OpenStreetMap using Leaflet.js.
The user can switch between map providers using a toggle button.

This class extends Ext.panel.Panel to be a container filled with two main items: a Map and a Select list. In the afterRender function, a
a default query (var index_uri) AJAX Request is made to the server to get a list of images. Then the function imLoadAjax iterates through the list
and sends AJAX Requests That XML document will contain
GPS data (about a photo) which is passed to the map. The map sets a marker and centers on that location.
*/
/**
 * @class BQ.map.Map
 * @extends Ext.Panel
 * @author Shea Frederick
 * @revised Alex Tovar
 * @revised Dmitry Fedorov
 * @revised Wahid Sadique Koly
 * @revised GitHub Copilot (Added OpenStreetMap support)
 */

Ext.define('BQ.map.Map', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.bqmap',
    //requires: ['Ext.window.MessageBox'],

    plain: true,
    zoomLevel: 3,
    yaw: 180,
    pitch: 0,
    zoom: 0,
    border: false,
    combo: false,

    // Force proper layout for maps
    layout: 'fit',

    // Add body style to ensure 100% dimensions
    bodyStyle: {
        width: '100%',
        height: '100%'
    },

    // Map provider configuration
    currentProvider: 'google', // 'google' or 'osm'

    // Map instances
    gmap: null,
    leafletMap: null,

    // Common properties
    markers: [],
    currentCenter: { lat: 42.6507, lng: 14.866 }, // Default center (Italy)
    currentZoom: 1,
    currentMapType: 'roadmap', // Track current map type

    initComponent: function () {
        // Set up global error handler FIRST, before anything else
        this.setupGlobalErrorHandler();
        this.addListener('resize', this.resized, this);

        // Add toolbar with map provider switcher
        this.tbar = this.createMapToolbar();

        this.callParent();
    },

    createMapToolbar: function () {
        var me = this;
        return [{
            text: 'Google Maps',
            id: 'map-provider-btn',
            iconCls: 'map-google-icon',
            enableToggle: true,
            pressed: true,
            toggleHandler: function (btn, pressed) {
                if (pressed) {
                    btn.setText('Google Maps');
                    btn.setIconCls('map-google-icon');
                    me.switchToProvider('google');
                } else {
                    btn.setText('OpenStreetMap');
                    btn.setIconCls('map-osm-icon');
                    me.switchToProvider('osm');
                }
            }
        }, '->', {
            text: 'Map Type',
            id: 'map-type-btn',
            hidden: false,
            menu: {
                items: [{
                    text: 'Roadmap',
                    checked: true,
                    group: 'maptype',
                    handler: function () { me.setMapType('roadmap'); }
                }, {
                    text: 'Satellite',
                    checked: false,
                    group: 'maptype',
                    handler: function () { me.setMapType('satellite'); }
                }, {
                    text: 'Terrain',
                    checked: false,
                    group: 'maptype',
                    handler: function () { me.setMapType('terrain'); }
                }]
            }
        }];
    },

    setupGlobalErrorHandler: function () {
        if (window.__bqMapErrorSuppressed) return;

        var originalError = window.onerror;
        window.onerror = function (msg, url, line, col, error) {
            // Suppress Google Maps internal errors
            if (msg && url &&
                (url.includes('maps.googleapis.com') || url.includes('maps.gstatic.com')) &&
                msg.match(/[a-zA-Z]\.\w+ is not a function/)) {
                console.warn('Google Maps internal error suppressed:', msg);
                return true;
            }
            if (msg === 'Script error.' && !url && !line) {
                console.warn('Cross-origin script error suppressed (likely Maps)');
                return true;
            }
            return originalError ? originalError.apply(this, arguments) : false;
        };

        window.addEventListener('error', function (event) {
            if (event.filename &&
                (event.filename.includes('maps.googleapis.com') ||
                    event.filename.includes('maps.gstatic.com') ||
                    event.filename.includes('leafletjs.com'))) {
                console.warn('Maps error event suppressed:', event.message);
                event.preventDefault();
                event.stopPropagation();
                return false;
            }
        }, true);

        window.addEventListener('unhandledrejection', function (event) {
            if (event.reason) {
                var stack = event.reason.stack || '';
                var message = event.reason.message || event.reason.toString();
                if ((stack.includes('maps.googleapis.com') || stack.includes('maps.gstatic.com') || stack.includes('leafletjs.com')) &&
                    message.match(/[a-zA-Z]\.\w+ is not a function/)) {
                    console.warn('Maps promise error suppressed:', message);
                    event.preventDefault();
                    return false;
                }
            }
        });

        window.__bqMapErrorSuppressed = true;
    },

    afterRender: function () {
        this.callParent();
        var me = this;

        // Ensure Leaflet CSS is loaded
        this.loadLeafletResources(function () {
            me.initializeMap();
        });
    },

    loadLeafletResources: function (callback) {
        var me = this;

        // Check if Leaflet is already loaded
        if (window.L) {
            callback();
            return;
        }

        // Load Leaflet CSS
        var css = document.createElement('link');
        css.rel = 'stylesheet';
        css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        css.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
        css.crossOrigin = '';
        document.head.appendChild(css);

        // Load Leaflet JS
        var script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
        script.crossOrigin = '';
        script.onload = function () {
            console.log('Leaflet loaded successfully');
            callback();
        };
        script.onerror = function () {
            console.error('Failed to load Leaflet, falling back to Google Maps only');
            me.currentProvider = 'google';
            callback();
        };
        document.head.appendChild(script);
    },

    initializeMap: function () {
        var me = this;

        setTimeout(function () {
            // Initialize with default provider
            if (me.currentProvider === 'google') {
                me.initGoogleMap();
            } else {
                me.initOpenStreetMap();
            }

            // Ensure markers array is initialized
            if (!me.markers) {
                me.markers = [];
            }

            // Load data
            if (me.resource instanceof BQDataset) {
                me.loadDataset();
            } else if (me.resource instanceof BQImage) {
                me.loadImage();
            }
        }, 100);
    },

    initGoogleMap: function () {
        var me = this;

        if (!window.google || !window.google.maps) {
            console.error('Google Maps API not loaded');
            return;
        }

        me.gmap = new google.maps.Map(me.body.dom, {
            zoom: me.currentZoom,
            center: new google.maps.LatLng(me.currentCenter.lat, me.currentCenter.lng),
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            mapTypeControl: false, // We handle this in toolbar
            zoomControl: true,
            streetViewControl: false,
            fullscreenControl: true
        });

        // Apply current map type if it's not roadmap
        if (me.currentMapType && me.currentMapType !== 'roadmap') {
            setTimeout(function () {
                me.setMapType(me.currentMapType);
                // Apply gray tiles fix after map type change
                setTimeout(function () {
                    me.fixGrayTiles();
                }, 200);
            }, 100);
        }

        // Fix for gray tiles when switching map types
        google.maps.event.addListener(me.gmap, 'maptypeid_changed', function () {
            me.fixGrayTiles();
        });

        me.infoWindow = new google.maps.InfoWindow({ content: null, maxWidth: 450 });
        me.bound = new google.maps.LatLngBounds();
        me.googleMarkers = [];
    },

    fixGrayTiles: function () {
        var me = this;
        if (!me.gmap) return;

        setTimeout(function () {
            var center = me.gmap.getCenter();
            var zoom = me.gmap.getZoom();

            // Zoom trick - forces complete tile reload
            me.gmap.setZoom(zoom + 1);
            setTimeout(function () {
                me.gmap.setZoom(zoom);
                google.maps.event.trigger(me.gmap, 'resize');
                me.gmap.setCenter(center);

                // Force bounds recalculation
                var bounds = me.gmap.getBounds();
                if (bounds) {
                    me.gmap.fitBounds(bounds);
                }
            }, 100);
        }, 50);
    },

    initOpenStreetMap: function () {
        var me = this;

        if (!window.L) {
            console.error('Leaflet not loaded, cannot initialize OpenStreetMap');
            return;
        }

        // Clear any existing content
        me.body.dom.innerHTML = '';

        me.leafletMap = L.map(me.body.dom, {
            center: [me.currentCenter.lat, me.currentCenter.lng],
            zoom: me.currentZoom,
            zoomControl: true,
            attributionControl: true
        });

        // Add default tile layer (roadmap)
        me.currentTileLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(me.leafletMap);

        // Apply current map type if it's not roadmap  
        if (me.currentMapType && me.currentMapType !== 'roadmap') {
            me.setMapType(me.currentMapType);
        }

        // Store reference for cleanup
        me.leafletMarkers = [];
    },

    switchToProvider: function (provider) {
        if (this.currentProvider === provider) return;

        var me = this;

        // Save current state
        if (me.currentProvider === 'google' && me.gmap) {
            var center = me.gmap.getCenter();
            if (center) {
                me.currentCenter = { lat: center.lat(), lng: center.lng() };
                me.currentZoom = me.gmap.getZoom();
            }
        } else if (me.currentProvider === 'osm' && me.leafletMap) {
            var center = me.leafletMap.getCenter();
            if (center) {
                me.currentCenter = { lat: center.lat, lng: center.lng };
                me.currentZoom = me.leafletMap.getZoom();
            }
        }

        // Ensure currentCenter is never null
        if (!me.currentCenter) {
            me.currentCenter = { lat: 42.6507, lng: 14.866 };
        }
        if (!me.currentZoom) {
            me.currentZoom = 1;
        }

        // Clear current map
        me.clearCurrentMap();

        // Switch provider
        me.currentProvider = provider;

        // Initialize new map
        if (provider === 'google') {
            me.initGoogleMap();
        } else {
            me.initOpenStreetMap();
        }

        // Restore markers
        me.restoreMarkers();

        // Update toolbar
        me.updateToolbarForProvider(provider);
    },

    clearCurrentMap: function () {
        // Clear any pending bounds timer
        if (this.boundsTimer) {
            clearTimeout(this.boundsTimer);
            this.boundsTimer = null;
        }

        if (this.gmap) {
            google.maps.event.clearInstanceListeners(this.gmap);
            this.gmap = null;
        }
        if (this.leafletMap) {
            this.leafletMap.remove();
            this.leafletMap = null;
        }

        // Clear marker arrays
        this.googleMarkers = [];
        this.leafletMarkers = [];

        this.body.dom.innerHTML = '';
    },

    updateToolbarForProvider: function (provider) {
        var mapTypeBtn = Ext.getCmp('map-type-btn');
        if (mapTypeBtn) {
            // Keep Map Type button visible for both providers
            mapTypeBtn.show();

            // Update menu items to reflect current map type
            var menu = mapTypeBtn.menu;
            if (menu && menu.items) {
                var currentType = this.currentMapType || 'roadmap';

                // Reset all menu items to unchecked first
                menu.items.each(function (item) {
                    if (item.setChecked) {
                        item.setChecked(false);
                    }
                });

                // Check the current map type
                var typeMap = {
                    'roadmap': 0,
                    'satellite': 1,
                    'terrain': 2
                };

                var itemIndex = typeMap[currentType];
                if (itemIndex !== undefined && menu.items.getAt(itemIndex)) {
                    menu.items.getAt(itemIndex).setChecked(true);
                }
            }
        }
    },

    setMapType: function (type) {
        // Store current map type for reference
        this.currentMapType = type;

        if (this.currentProvider === 'google' && this.gmap) {
            var mapTypeId;
            switch (type) {
                case 'roadmap': mapTypeId = google.maps.MapTypeId.ROADMAP; break;
                case 'satellite': mapTypeId = google.maps.MapTypeId.SATELLITE; break;
                case 'terrain': mapTypeId = google.maps.MapTypeId.TERRAIN; break;
                default: mapTypeId = google.maps.MapTypeId.ROADMAP;
            }
            this.gmap.setMapTypeId(mapTypeId);
        } else if (this.currentProvider === 'osm' && this.leafletMap) {
            // Remove current tile layer
            if (this.currentTileLayer) {
                this.leafletMap.removeLayer(this.currentTileLayer);
            }

            // Add new tile layer based on type
            var tileUrl, attribution, maxZoom = 19;
            switch (type) {
                case 'satellite':
                    // Use Esri World Imagery for satellite view
                    tileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
                    attribution = '© <a href="https://www.esri.com/" target="_blank">Esri</a>, Maxar, Earthstar Geographics';
                    maxZoom = 17;
                    break;
                case 'terrain':
                    // Use OpenTopoMap for terrain view
                    tileUrl = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png';
                    attribution = '© <a href="https://opentopomap.org/" target="_blank">OpenTopoMap</a> (CC-BY-SA) | Map data © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>';
                    maxZoom = 17;
                    break;
                case 'roadmap':
                default:
                    // Standard OpenStreetMap tiles
                    tileUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
                    attribution = '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors';
                    maxZoom = 19;
            }

            this.currentTileLayer = L.tileLayer(tileUrl, {
                attribution: attribution,
                maxZoom: maxZoom,
                subdomains: ['a', 'b', 'c'] // For servers that support subdomains
            }).addTo(this.leafletMap);
        }
    },

    loadDataset: function () {
        Ext.Ajax.request({
            url: this.resource.uri + '/value',
            callback: function (opts, succsess, response) {
                if (response.status >= 400)
                    BQ.ui.error(response.responseText);
                else
                    this.onImagesLoaded(response.responseXML);
            },
            scope: this,
            disableCaching: false,
            listeners: {
                scope: this,
                beforerequest: function () { this.setLoading('Loading images...'); },
                requestcomplete: function () { this.setLoading(false); },
                requestexception: function () { this.setLoading(false); },
            },
        });
    },

    loadImage: function () {
        var id = this.resource.resource_uniq;
        var uri_meta = '/image_service/' + id + '?meta';
        var image = {
            id: id,
            name: this.resource.name,
            uri: this.resource.uri,
            thumbnail: '/image_service/' + id + '?thumbnail=280,280',
            view: '/client_service/view?resource=/data_service/' + id,
        };
        this.requestEmbeddedMeta(uri_meta, image);
    },

    resized: function () {
        var me = this;
        if (this.gmap) {
            setTimeout(function () {
                if (me.gmap && me.gmap.getDiv()) {
                    var center = me.gmap.getCenter();
                    google.maps.event.trigger(me.gmap, 'resize');
                    if (center) me.gmap.setCenter(center);
                }
            }, 50);
        }
    },

    onImagesLoaded: function (xml) {
        var nodes = BQ.util.xpath_nodes(xml, "*/image");
        this.pendingImages = nodes.length;
        this.processedImages = 0;

        for (var i = 0; i < nodes.length; ++i) {
            var id = nodes[i].getAttribute('resource_uniq');
            var uri_meta = '/image_service/' + id + '?meta';
            var image = {
                id: id,
                name: nodes[i].getAttribute('name'),
                uri: nodes[i].getAttribute('uri'),
                thumbnail: '/image_service/' + id + '?thumbnail=280,280',
                view: '/client_service/view?resource=/data_service/' + id,
            };
            this.requestEmbeddedMeta(uri_meta, image);
        }
    },

    checkAndFitBounds: function () {
        this.processedImages = (this.processedImages || 0) + 1;
        if (this.pendingImages && this.processedImages >= this.pendingImages) {
            // All images processed, now fit bounds
            var me = this;
            setTimeout(function () {
                me.fitToMarkers();
            }, 300);
        }
    },

    requestEmbeddedMeta: function (uri, image) {
        var me = this;
        Ext.Ajax.request({
            url: uri,
            scope: this,
            disableCaching: false,
            callback: function (opts, succsess, response) {
                if (response.status >= 400)
                    BQ.ui.error(response.responseText);
                else
                    me.onEmbeddedMeta(response.responseXML, image);
            },
        });
    },

    onEmbeddedMeta: function (xml, image) {
        var point = this.findGPS(xml);
        if (point) {
            this.addMarker(point, image);
        } else {
            this.requestUserMeta(image.uri, image);
            return; // Don't check bounds yet, wait for user meta
        }
        this.checkAndFitBounds();
    },

    requestUserMeta: function (uri, image) {
        var me = this;
        Ext.Ajax.request({
            url: uri + '?view=deep',
            scope: this,
            disableCaching: false,
            callback: function (opts, succsess, response) {
                if (response.status >= 400)
                    BQ.ui.error(response.responseText);
                else
                    me.onUserMeta(response.responseXML, image);
            },
        });
    },

    onUserMeta: function (xml, image) {
        var point = this.findUserGPS(xml);
        if (point) {
            this.addMarker(point, image);
        }
        this.checkAndFitBounds();
    },

    addMarker: function (point, image) {
        var me = this;

        // Store marker data for provider switching
        var markerData = {
            lat: point.lat(),
            lng: point.lng(),
            image: image
        };
        this.markers.push(markerData);

        if (this.currentProvider === 'google' && this.gmap) {
            this.addGoogleMarker(point, image);
        } else if (this.currentProvider === 'osm' && this.leafletMap) {
            this.addLeafletMarker([markerData.lat, markerData.lng], image);
        }
    },

    addGoogleMarker: function (point, image) {
        var me = this;
        if (!this.bound) {
            this.bound = new google.maps.LatLngBounds();
        }
        if (!this.googleMarkers) {
            this.googleMarkers = [];
        }

        this.bound.extend(point);

        try {
            var marker = new google.maps.Marker({
                position: point,
                map: this.gmap,
                image: image,
            });

            // Store marker for bounds calculation
            this.googleMarkers.push(marker);

            // Event listeners
            this.safeEventListener(this.gmap, 'click', function () {
                me.infoWindow.close();
            });

            this.safeEventListener(marker, 'click', function () {
                me.onGoogleMarkerClick(this);
            });

            // Fit bounds only if this is the last marker or after a delay
            clearTimeout(this.boundsTimer);
            this.boundsTimer = setTimeout(function () {
                if (me.bound && me.gmap) {
                    me.gmap.fitBounds(me.bound);
                }
            }, 100);

        } catch (e) {
            console.error('Error adding Google marker:', e);
        }
    },

    addLeafletMarker: function (latLng, image) {
        var me = this;
        if (!this.leafletMarkers) {
            this.leafletMarkers = [];
        }

        try {
            var marker = L.marker(latLng).addTo(this.leafletMap);

            var popupContent = '<div style="text-align: center;">' +
                '<img style="height:150px; width:150px;" src="' + image.thumbnail + '" />' +
                '<div style="padding-top: 5px;"><a href="' + image.view + '">' + image.name + '</a></div>' +
                '</div>';

            marker.bindPopup(popupContent, { maxWidth: 450 });
            this.leafletMarkers.push(marker);

            // Auto fit bounds
            var group = new L.featureGroup(this.leafletMarkers);
            this.leafletMap.fitBounds(group.getBounds().pad(0.1));

        } catch (e) {
            console.error('Error adding Leaflet marker:', e);
        }
    },

    // Method to fit bounds to all markers - useful after all markers are loaded
    fitToMarkers: function () {
        if (this.currentProvider === 'google' && this.gmap && this.googleMarkers && this.googleMarkers.length > 0) {
            var bounds = new google.maps.LatLngBounds();
            for (var i = 0; i < this.googleMarkers.length; i++) {
                bounds.extend(this.googleMarkers[i].getPosition());
            }
            this.gmap.fitBounds(bounds);
        } else if (this.currentProvider === 'osm' && this.leafletMap && this.leafletMarkers && this.leafletMarkers.length > 0) {
            var group = new L.featureGroup(this.leafletMarkers);
            this.leafletMap.fitBounds(group.getBounds().pad(0.1));
        }
    },

    restoreMarkers: function () {
        if (!this.markers || this.markers.length === 0) return;

        // Clear any existing bounds timer to prevent conflicts
        if (this.boundsTimer) {
            clearTimeout(this.boundsTimer);
        }

        for (var i = 0; i < this.markers.length; i++) {
            var markerData = this.markers[i];

            if (this.currentProvider === 'google' && this.gmap) {
                var point = new google.maps.LatLng(markerData.lat, markerData.lng);
                this.addGoogleMarker(point, markerData.image);
            } else if (this.currentProvider === 'osm' && this.leafletMap) {
                this.addLeafletMarker([markerData.lat, markerData.lng], markerData.image);
            }
        }

        // Fit bounds after all markers are restored
        var me = this;
        setTimeout(function () {
            me.fitToMarkers();
        }, 200);
    },

    safeEventListener: function (instance, eventName, handler) {
        try {
            return google.maps.event.addListener(instance, eventName, function () {
                try {
                    return handler.apply(this, arguments);
                } catch (e) {
                    if (e.message && e.message.match(/b\.\w+ is not a function/)) {
                        console.warn('Google Maps event error suppressed for', eventName);
                    } else {
                        console.error('Map event error on', eventName, ':', e);
                    }
                }
            });
        } catch (e) {
            console.error('Error adding event listener for', eventName, ':', e);
            return null;
        }
    },

    positionMarker: function (pt) {
        if (this.currentProvider === 'google' && this.gmap) {
            this.positionGoogleMarker(pt);
        } else if (this.currentProvider === 'osm' && this.leafletMap) {
            this.positionLeafletMarker(pt);
        }
    },

    positionGoogleMarker: function (pt) {
        var point = new google.maps.LatLng(pt[0], pt[1]);
        if (!this.bound) {
            this.bound = new google.maps.LatLngBounds();
        }
        this.bound.extend(point);

        if (!this.marker_position) {
            var icon = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png';
            this.marker_position = new google.maps.Marker({
                position: point,
                map: this.gmap,
                icon: icon,
            });
        } else {
            this.marker_position.setPosition(point);
        }

        this.gmap.fitBounds(this.bound);
    },

    positionLeafletMarker: function (pt) {
        if (!this.leaflet_position_marker) {
            this.leaflet_position_marker = L.marker([pt[0], pt[1]], {
                icon: L.icon({
                    iconUrl: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                    iconSize: [32, 32],
                    iconAnchor: [16, 32]
                })
            }).addTo(this.leafletMap);
        } else {
            this.leaflet_position_marker.setLatLng([pt[0], pt[1]]);
        }

        this.leafletMap.setView([pt[0], pt[1]], this.leafletMap.getZoom());
    },

    onGoogleMarkerClick: function (marker) {
        var s = '<div style="text-align: center;">' +
            '<img style="height:150px; width:150px;" src="' + marker.image.thumbnail + '" />' +
            '<div style="padding-top: 5px;"><a href="' + marker.image.view + '">' + marker.image.name + '</a></div>' +
            '</div>';
        this.infoWindow.setContent(s);
        this.infoWindow.open(this.gmap, marker);
        this.gmap.panTo(marker.position);
    },

    resized: function () {
        var me = this;
        if (this.gmap) {
            setTimeout(function () {
                if (me.gmap && me.gmap.getDiv()) {
                    var center = me.gmap.getCenter();
                    google.maps.event.trigger(me.gmap, 'resize');
                    if (center) me.gmap.setCenter(center);
                }
            }, 50);
        } else if (this.leafletMap) {
            setTimeout(function () {
                me.leafletMap.invalidateSize();
            }, 50);
        }
    },

    gpsExifParser: function (gpsString, direction) {
        if (!gpsString || gpsString.length < 1) return null;
        var coordinates = gpsString[0].value.match(/[\d\.]+/g);
        var Deg = parseInt(coordinates[0]);
        var Min = parseFloat(coordinates[1]);
        var Sec = parseFloat(coordinates[2]);
        // iPhone pix will only have two array entries, extra-precise "minutes"
        if (coordinates.length < 3) Sec = 0;
        var ref = direction[0].value;
        var gps = Deg + (Min / 60) + (Sec / 3600);
        if (ref == "South" || ref == "West") gps = -1 * gps;
        return gps;
    },

    gpsGeoParser: function (str) {
        if (!str) return;
        var coordinates = str.split(',');
        if (!coordinates || coordinates.length < 2) {
            return;
        }
        return [parseFloat(coordinates[0]), parseFloat(coordinates[1])];
    },

    findGPS: function (xmlDoc) {
        if (!xmlDoc) return;

        // first try to find Geo center entry in embedded meta
        var geo_center = BQ.util.xpath_nodes(xmlDoc, "resource/tag[@name='Geo']/tag[@name='Coordinates']/tag[@name='center']/@value");
        if (geo_center && geo_center.length > 0) {
            var c = this.gpsGeoParser(geo_center[0].value);
            if (c) {
                return new google.maps.LatLng(c[0], c[1]);
            }
        }

        // next try EXIF GPS
        var latitude = BQ.util.xpath_nodes(xmlDoc, "//tag[@name='GPSLatitude']/@value");
        var latituderef = BQ.util.xpath_nodes(xmlDoc, "//tag[@name='GPSLatitudeRef']/@value");
        var longitude = BQ.util.xpath_nodes(xmlDoc, "//tag[@name='GPSLongitude']/@value");
        var longituderef = BQ.util.xpath_nodes(xmlDoc, "//tag[@name='GPSLongitudeRef']/@value");

        var lat = this.gpsExifParser(latitude, latituderef);
        var lon = this.gpsExifParser(longitude, longituderef);
        if (lat && lon) {
            return new google.maps.LatLng(lat, lon);
        }
    },

    findUserGPS: function (xmlDoc) {
        if (!xmlDoc) return;

        // first try to find Geo center entry in embedded meta
        var geo_center = BQ.util.xpath_nodes(xmlDoc, "*/tag[@name='Geo']/tag[@name='Coordinates']/tag[@name='center']/@value");
        if (geo_center && geo_center.length > 0) {
            var c = this.gpsGeoParser(geo_center[0].value);
            if (c) {
                return new google.maps.LatLng(c[0], c[1]);
            }
        }

        // then try CLEF standard
        var latitude = BQ.util.xpath_nodes(xmlDoc, "//tag[@name='GPSLocality']/tag[@name='Latitude']/@value");
        var longitude = BQ.util.xpath_nodes(xmlDoc, "//tag[@name='GPSLocality']/tag[@name='Longitude']/@value");

        try {
            var thelat = parseFloat(latitude[0].value);
            var thelon = parseFloat(longitude[0].value);
            if (!thelat || !thelon) return;
            return new google.maps.LatLng(thelat, thelon);
        } catch (e) {
            return;
        }
    },

    // Additional utility functions for map management
    clearMarkers: function () {
        if (this.currentProvider === 'google' && this.gmap) {
            // Clear Google Maps markers
            for (var i = 0; i < this.markers.length; i++) {
                if (this.markers[i].marker) {
                    this.markers[i].marker.setMap(null);
                }
            }
        } else if (this.currentProvider === 'osm' && this.leafletMap) {
            // Clear Leaflet markers
            for (var i = 0; i < this.markers.length; i++) {
                if (this.markers[i].marker) {
                    this.leafletMap.removeLayer(this.markers[i].marker);
                }
            }
        }
        this.markers = [];
    },

    // Get map bounds in standard format
    getBounds: function () {
        if (this.currentProvider === 'google' && this.gmap) {
            var bounds = this.gmap.getBounds();
            if (bounds) {
                var ne = bounds.getNorthEast();
                var sw = bounds.getSouthWest();
                return {
                    north: ne.lat(),
                    south: sw.lat(),
                    east: ne.lng(),
                    west: sw.lng()
                };
            }
        } else if (this.currentProvider === 'osm' && this.leafletMap) {
            var bounds = this.leafletMap.getBounds();
            return {
                north: bounds.getNorth(),
                south: bounds.getSouth(),
                east: bounds.getEast(),
                west: bounds.getWest()
            };
        }
        return null;
    },

    // Fit map to bounds
    fitBounds: function (bounds) {
        if (this.currentProvider === 'google' && this.gmap) {
            var googleBounds = new google.maps.LatLngBounds(
                new google.maps.LatLng(bounds.south, bounds.west),
                new google.maps.LatLng(bounds.north, bounds.east)
            );
            this.gmap.fitBounds(googleBounds);
        } else if (this.currentProvider === 'osm' && this.leafletMap) {
            this.leafletMap.fitBounds([
                [bounds.south, bounds.west],
                [bounds.north, bounds.east]
            ]);
        }
    },

    // Pan to location
    panTo: function (lat, lng) {
        if (this.currentProvider === 'google' && this.gmap) {
            this.gmap.panTo(new google.maps.LatLng(lat, lng));
        } else if (this.currentProvider === 'osm' && this.leafletMap) {
            this.leafletMap.panTo([lat, lng]);
        }
    },

});