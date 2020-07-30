/*
***GMAP Window***
8/11
Google Map in ExtJS 4 Wrapper

This file is derived from the Google Maps Wrapper Class Demo from http://www.sencha.com/.
The Demo uses Google Maps API V2, but this class updates to Google Maps API V3.

This class extends Ext.panel.Panel to be a container filled with two main items: a Google Map and a Select list. In the afterRender function, a
a default query (var index_uri) AJAX Request is made to the server to get a list of images. Then the function imLoadAjax iterates through the list
and sends AJAX Requests That XML document will contain
GPS data (about a photo) which is passed to the map. The map sets a marker and centers on that location.
*/
/**
 * @class Ext.ux.GMapPanel
 * @extends Ext.Panel
 * @author Shea Frederick
 * @revised Alex Tovar
 * @revised Dmitry Fedorov
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

    initComponent : function() {
        this.addListener( 'resize', this.resized, this );
        this.callParent();
    },

    afterRender : function(){
        this.callParent();

        this.gmap = new google.maps.Map(this.body.dom, {
            zoom: 1,
            center: new google.maps.LatLng(42.6507,14.866),
            mapTypeId: google.maps.MapTypeId.ROADMAP,
        });
        this.infoWindow = new google.maps.InfoWindow({content:null, maxWidth: 450}); // make one info window
        this.bound = new google.maps.LatLngBounds();


        if (this.resource instanceof BQDataset) {
            // load dataset values
            Ext.Ajax.request({
                url: this.resource.uri + '/value',
                callback: function(opts, succsess, response) {
                    if (response.status>=400)
                        BQ.ui.error(response.responseText);
                    else
                        this.onImagesLoaded(response.responseXML);
                },
                scope: this,
                disableCaching: false,
                listeners: {
                    scope: this,
                    beforerequest   : function() { this.setLoading('Loading images...'); },
                    requestcomplete : function() { this.setLoading(false); },
                    requestexception: function() { this.setLoading(false); },
                },
            });
        } else if (this.resource instanceof BQImage) {
            var id  = this.resource.resource_uniq;
            var uri_meta = '/image_service/' + id + '?meta';
            var image = {
                id: id,
                name: this.resource.name,
                uri: this.resource.uri,
                thumbnail : '/image_service/' + id + '?thumbnail=280,280',
                view: '/client_service/view?resource=/data_service/'+id, 
            };
            this.requestEmbeddedMeta(uri_meta, image);
        }
    },

    resized: function() {
        if (this.gmap)
            google.maps.event.trigger(this.gmap, 'resize');
    },

    onImagesLoaded : function(xml) {
        var nodes = BQ.util.xpath_nodes(xml, "*/image");
        for (var i=0; i<nodes.length; ++i) {
            var id  = nodes[i].getAttribute('resource_uniq');
            var uri_meta = '/image_service/' + id + '?meta';
            var image = {
                id: id,
                name: nodes[i].getAttribute('name'),
                uri: nodes[i].getAttribute('uri'),
                thumbnail : '/image_service/' + id + '?thumbnail=280,280',
                view: '/client_service/view?resource=/data_service/'+id, 
            };
            this.requestEmbeddedMeta(uri_meta, image);
        }
    },

    requestEmbeddedMeta: function(uri, image) {
        var me = this;
        Ext.Ajax.request({
            url: uri,
            scope: this,
            disableCaching: false,
            callback: function(opts, succsess, response) {
                if (response.status>=400)
                    BQ.ui.error(response.responseText);
                else
                    me.onEmbeddedMeta(response.responseXML, image);
            },
        });
    },

    onEmbeddedMeta: function(xml, image) {
        var point = this.findGPS(xml);
        if (point)
            this.addMarker(point, image);
        else
            this.requestUserMeta(image.uri, image);
    },

    requestUserMeta: function(uri, image) {
        var me = this;
        Ext.Ajax.request({
            url: uri+'?view=deep',
            scope: this,
            disableCaching: false,
            callback: function(opts, succsess, response) {
                if (response.status>=400)
                    BQ.ui.error(response.responseText);
                else
                    me.onUserMeta(response.responseXML, image);
            },
        });
    },

    onUserMeta: function(xml, image) {
        var point = this.findUserGPS(xml);
        if (point)
            this.addMarker(point, image);
    },

    addMarker : function(point, image){
        this.bound.extend(point);
        var marker = new google.maps.Marker({
            position: point,
            map: this.gmap,
            image: image,
        });
        this.gmap.fitBounds(this.bound); // dima: this might have to be activated on timeout with histerisis
        var me = this;
        google.maps.event.addListener(this.gmap, 'click', function() { me.infoWindow.close(); });
        google.maps.event.addListener(marker, 'click', function() { me.onMarkerClick(this); } );
    },

    positionMarker : function(pt) {
        var point = new google.maps.LatLng(pt[0], pt[1]);
        this.bound.extend(point);

        if (!this.marker_position) {
            //var color = "FE7569",
            //    icon = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + color);
            var icon = 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png';
            this.marker_position = new google.maps.Marker({
                position: point,
                map: this.gmap,
                icon: icon,
            });
        } else {
            this.marker_position.setPosition(point);
        }

        this.gmap.fitBounds(this.bound); // dima: this might have to be activated on timeout with histerisis
    },

    onMarkerClick : function(marker) {
        var map = this.gmap;
        var s = Ext.String.format('<div><img style="height:150px; width:150px;" src="{0}" /></div><div style="padding-top: 5px; text-align: center;"><a href="{1}">{2}</a></div>', 
            marker.image.thumbnail, marker.image.view, marker.image.name);
        this.infoWindow.setContent(s);
        this.infoWindow.open(map, marker);
        map.panTo(marker.position);
    },

    gpsExifParser : function(gpsString, direction) {
        if (!gpsString || gpsString.length<1) return null;
        var coordinates=gpsString[0].value.match(/[\d\.]+/g);
        var Deg = parseInt(coordinates[0]);
        var Min = parseFloat(coordinates[1]);
        var Sec = parseFloat(coordinates[2]);
        // iPhone pix will only have two array entries, extra-precise "minutes"
        if(coordinates.length <3) Sec = 0;
        var ref = direction[0].value;
        var gps = Deg + (Min / 60) + (Sec / 3600);
        if (ref == "South" || ref =="West") gps = -1*gps;
        return gps;
    },

    gpsGeoParser : function(str) {
        if (!str) return;
        var coordinates = str.split(',');
        if (!coordinates || coordinates.length<2) {
            return;
        }
        return [parseFloat(coordinates[0]), parseFloat(coordinates[1])];
    },

    findGPS : function(xmlDoc){
        if(!xmlDoc) return;

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

    findUserGPS : function(xmlDoc){
        if(!xmlDoc) return;

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
            return new google.maps.LatLng(thelat,thelon);
        } catch (e) {
            return;
        }
    },

});