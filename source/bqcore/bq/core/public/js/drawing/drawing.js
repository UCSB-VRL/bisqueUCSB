const stepSize = 40  // number of pixels a panning operation will move (WASD)
const numUndos = 10  // The depth of the undo stack


// Default colors assigned to each channel. Channel 1 is red, 2 is green, etc
defaultColorArray = [[255,   0,   0],
                     [  0, 255,   0],
                     [  0,   0, 255],
                     [255, 255,   0],
                     [255,   0, 255],
                     [  0, 255, 255],
                     [255, 255, 255],
]

// Converts the 2D int color array to hex strings
defaultColorOrder = []  // used by this JS , ex: [['ff', '00', '00'], ...]
defaultFuseOrder = []  // passed to the bisque image_service fuse key word
for (const row of defaultColorArray) {
  v = ""
  for (const i of row) {
	v += i.toString(16).padStart(2, '0')
  }
  defaultColorOrder.push(v)
  defaultFuseOrder.push(row[0] + ',' + row[1] + ',' + row[2])
}


// HTML contained in the workspace. All items are m,anipulated in JS
canvas_html = '<div id="drawing_canvas_background">' +
              '<img id="drawing_img_seg">' +
              '<canvas id="drawing_canvas" height="0" width="0"></canvas>' +
              '<img id="drawing_img_orig">' +
              '<div id="drawing_cursor2"></div>' + 
              '<div id="drawing_cursor1"></div>' +
              '</div>'


// Panel containing the toolbar and editing window
Ext.define('BQ.viewer.Drawing', {
  extend: 'Ext.panel.Panel',
  title: 'Mask Editor',
  height: '90%',
  width: '90%',
  resizable: true,
  layout: 'border',
  floating: true,
  closable: true,
  autoscroll: false,
  draggable: true,
  itemId: 'drawing_cont',
  //resource: null,
  //prevSlice: 1,  // check if i can remove these
  //drawingStack: [""],

  items: [{
    xtype: 'toolbar',
    itemId: 'mask_tools',
    dock: 'left',  // items in the toolbar will be pushed towards the left
    region: 'west', // will occupy the left portion of the Panel
    defaults: {
      scale: 'large'
    },

    items: [{
      xtype: 'combobox',
        queryMode: 'local',
        valueField: 'color',
        value: 'ff0000',
        editable: false,
        tpl: Ext.create('Ext.XTemplate', '<tpl for=".">',
		  '<div class="x-boundlist-item">' +
		  '<font color="#{color}">&#11044</font> {name}</div>', '</tpl>'
	    ), //html code for the menu items. Will show the color label and a       
        // circle of the corresponding color.

        beforeSubTpl: 'Selected Label',

	    fieldLabel: '<div style="width:20px; height:20px; ' + 
		'border-radius: 50%"></div>', // circle seen to the left of the menu

	    labelWidth: 23,
	    labelSeparator: '',
	    labelPad: 0,

        // show only the name, not the hex color code
        displayTpl: Ext.create('Ext.XTemplate',
            '<tpl for=".">', '{name}', '</tpl>'),

	    listeners: {
		  render: function() { this.ownerCt.label = this },  // register to parent
		  change: function() { this.ownerCt.ownerCt.updateLabel() },
	    },

        // A weird extjs thing, define the data structure for the items. Here
        // only the background class (black) is added to the list, once the
        // mask is loaded, the appropriate number additional labels will be
        // added.
        store: Ext.create('Ext.data.Store', {
          fields: ['name', 'color'],
              data: [
		        { 'name': 'Background', 'color': '000000'},
              ]
          })
	}, {
        xtype: 'numberfield',
        itemId: 'brush_size',
        minValue: 1,
        value: 20,
        beforeSubTpl: 'Brush Diameter (px)',
        listeners: {
          render: function() { this.ownerCt.brush = this },
          change: function() { this.ownerCt.ownerCt.updateCursor() }
	    },
    }, {
        xtype: 'tbtext',
        itemId: 'cursor_pos',
        text: '(0, 0)',
	    listeners: {
		  render: function() { this.ownerCt.cursorPosText = this },
	    },
    }, {
        xtype: 'numberfield',
        itemId: 'slice',
        beforeSubTpl: 'Slice Number ',
        minValue: 1,
        value: 1, // maxValue set when image metadata is loaded
        listeners: {
          render: function() { this.ownerCt.slice = this },
          change: function() { this.ownerCt.ownerCt.updateSlice() },
	    },
	}, {
        xtype: 'slider',
        text: 'Overlay Opacity',
        beforeSubTpl: 'Image Overlay Opacity',
        itemId: 'img_alpha',
        minValue: 0,
        maxValue: 255,
	    value: 85,
        increment: 5,
	    listeners: {
          render: function() { this.ownerCt.imgAlpha = this },
          change: function() { this.ownerCt.ownerCt.moveCanvas() },
	    },
    }, {
        xtype: 'button',
        text: 'Save and Quit',
        listeners: {
          click: function() {this.ownerCt.ownerCt.save() }
        },
    }, {
        xtype: 'button', 
        text: 'Clear',
        listeners: {
          click: function() { this.ownerCt.ownerCt.clear() }
        },
    }, {
        xtype: 'tbtext',
        text: '',
        listeners: {
          render: function() {this.ownerCt.loadingText = this }
        }

    }, {
        xtype: 'tbtext',
        text: '<h3>Controls</h3>' + 
              '<h4>Mouse</h4>' + 
              ' <b>Click / Click+Move:</b> Draw on canvas<br>' + 
              ' <b>Scroll Wheel:</b> Change brush diameter<br>' + 
              '<h4>Keyboard</h4>' +
              ' <b>W/A/S/D:</b> Pan up/left/down/right<br>' + 
              ' <b>E/Q:</b> Zoom in/out<br>' +
              ' <b>R/F:</b> Switch label<br>' + 
              ' <b>C/X:</b> Next/previous slice<br>' + 
              ' <b>1/2/3/4:</b> Change overlay opacity<br>' + 
              ' <b>Z:</b> Undo'


//'hello world' +
//                'foo bar 123'

    }],

    listeners: {
      render: function() { this.ownerCt.toolbar = this }
    },

  // END OF TOOLBAR DEFINITIONS
  // BEGIN CANVAS PANEL DEFINITION
  }, {
    xtype: 'panel',
    region: 'center',
    layout: 'fit',
    itemId: 'mask_canvas',
    html: canvas_html,
	drawing: false,  // denotes if mouse has been pressed down to draw
        // a continuous stroke

    canvasLocation: { 'x': 0, 'y': 0, 'scale': 1 }, // variable to store
        // location and scale of the canvas after pan and zoom

    listeners: {
        // Calling changeSlice with no args keeps the slice the same, but
        // redraws the canvas, segmentation mask, etc. When the Panel is
        // resized, the location at the center of the panel should not change.
	    onResize: function() { this.ownerCt.changeSlice() },

        render: function() {
          this.ownerCt.imgPanel = this
          me = this

          // Get all of the elements in the HTML code
          me.cursor1 = document.getElementById("drawing_cursor1")
          me.cursor2 = document.getElementById("drawing_cursor2")
          me.ownerCt.imgOrig = document.getElementById("drawing_img_orig")
          me.ownerCt.imgSeg = document.getElementById("drawing_img_seg")
          me.ownerCt.canvas = document.getElementById("drawing_canvas")
          me.ownerCt.canvasCtx = me.ownerCt.canvas.getContext('2d')

          // This will switch to true the first time an image is loaded. This
          // will indicate that the canvas size needs to be changed.
          me.canvasInit = false

          // Run when the segmentation image is loaded
          me.ownerCt.imgSeg.onload = function() {
            // If the canvas has not yet been set to the correct size
            if (!me.canvasInit) {
              me.ownerCt.canvas.width = me.ownerCt.imgSeg.naturalWidth
              me.ownerCt.canvas.height = me.ownerCt.imgSeg.naturalHeight
              me.ownerCt.moveCanvas()
              me.canvasInit = true
            }
          }

          me.ownerCt.imgOrig.onload = function() {
            if (!me.canvasInit) {
              me.ownerCt.canvas.width = me.ownerCt.imgOrig.naturalWidth
              me.ownerCt.canvas.height = me.ownerCt.imgOrig.naturalHeight
              me.ownerCt.moveCanvas()
              me.canvasInit = true
            }
          }

          // An empty image for the canvas. Used to loaded cached canvases
          me.ownerCt.canvasImage = new Image()

          // When the canvas image src is changed and loaded, draw that image
          // on the canvas.
          me.ownerCt.canvasImage.onload = function() {
            me.ownerCt.canvasCtx.drawImage(me.ownerCt.canvasImage, 0, 0)
          }

          // Initialization steps. Select the first slice and move the cursor.
          me.ownerCt.changeSlice(0)
          me.ownerCt.updateCursor()

          // When mouse is moved, update the cursor position, location text,
          // and if "me.drawing" is set (mouse is down), draw a circle.
          me.body.on('mousemove', function(e) {
            mouseX = e.browserEvent.clientX
            mouseY = e.browserEvent.clientY
            var [canvasX, canvasY] = me.ownerCt.mousePosToCanvas(mouseX,
                mouseY)
            me.ownerCt.updateCursor(mouseX, mouseY)
            me.ownerCt.toolbar.cursorPosText.setText("(" + 
            	Math.floor(canvasX) + ", " + Math.floor(canvasY) + ")")
            if (me.drawing) { me.ownerCt.drawCircle(canvasX, canvasY) }
          })

          // Call cacheCanvas to push the current canvas onto the undo stack.
          // Draw a circle and register that the mouse has been pressed.
          me.body.on('mousedown', function(e) {
		    me.ownerCt.cacheCanvas()
		    mouseX = e.browserEvent.clientX
                    mouseY = e.browserEvent.clientY
                    var [canvasX, canvasY] = me.ownerCt.mousePosToCanvas(
                        mouseX, mouseY)
		    me.drawing = true
		    me.ownerCt.drawCircle(canvasX, canvasY)
		})

        // Register that the mouse is no longer down.
		me.body.on('mouseup', function(e) { me.drawing = false })

        // Also register to stop drawing, if the mouse leaves.
		me.body.on('mouseleave', function(e) { me.drawing = false })

		// Capture keyboard events when mouse is over canvas.
        me.body.on('mouseenter', function(e) { me.ownerCt.focus()})

        // Scrolling changes brush size.
		me.body.on('wheel', function(e) {
		    val = Math.sign(e.browserEvent.wheelDeltaY)
		    brush = me.ownerCt.toolbar.brush
		    val = Math.max(1, brush.value + val)
		    brush.setValue(val)
		})
	  },
	},
    }],

    // Listeners for Panel
    listeners: {
        // Gets image metadata
        beforerender: { fn: function() { this.fetchMeta() } },

        // Brings current panel into focus, so key events are captured.
        render: { fn: function() { this.focus() } },

        // Set the keyboard mapping
        afterrender: {
            fn: function() {
                this.keyMap = Ext.create('Ext.util.KeyMap', this.el, {
                    scope: this,
                    key: 'wasdqexcrfz1234', // A list of all of the keys used
                    fn: this.keypressHandler
                })
            }
        },

        // Initialize label selection
        show: {
          fn: function() {
            this.changeLabel(0)
            this.updateLabel()
          }
	    },
    },


    // Initialize undo stack to be empty
    undoStack: [],

    // Stores the current canvas in the undoStack
    cacheCanvas: function() {
      // Push to stack
      this.undoStack.push(this.canvas.toDataURL('image/png'))
      // Pop the oldest element if the length is too long
      if (this.undoStack.length > numUndos) {
        this.undoStack.shift()
      }
    },

    // Clear out all drawings, called by toolbar Clear button
    clear: function() {
      this.cacheCanvas()
      this.canvasCtx.clearRect(0, 0, this.canvas.width, this.canvas.height)
    },

    // Save and redirect, called by toolbar Save button
    save: function() {
      this.toolbar.loadingText.setText('Ingesting.<br>Will redirect when finished...')
      val = this.toolbar.slice.value
      // Add current drawing to drawingStack
      this.drawingStack[val-1] = this.canvas.toDataURL('image/png')
      // Create a list of URLs for the original image, to send back
      orig_urls = []
      for (i=1; i <= this.numSlices; i++) {
        orig_urls.push(this.getImageURL(i))
      }
      base_url = document.location.origin
      var xhr = new XMLHttpRequest()
      xhr.open("POST", base_url + "/client_service/mask_receiver", true)
      xhr.setRequestHeader('Content-Type', 'application/json')
      // Send the POST request to the server
      xhr.send(JSON.stringify({
          stack: this.drawingStack,
          orig_urls: orig_urls,
      }))
      // Once readyState == 4 (this means it is done), redirect to view image
      xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          window.location.replace(base_url + 
              "/client_service/view?resource=" + xhr.responseText
	      )
        }
      }
    },

    // Undo last stroke
    undo: function() {
      if (this.undoStack.length > 0) {
        // Clear out canvas
        this.canvasCtx.clearRect(0, 0, this.canvas.width,
            this.canvas.height)
        // Draw last image from the undoStack on canvas
        this.canvasImage.src = this.undoStack.pop()
      }
    },

    // Utility function to convert slice number to the bisque image URL
    getImageURL: function(slice) {
        if (this.no_mask) {
          return ""
        }
        if (this.sliceAxis === 'time') {
            z = 1
            t = slice
        } else {
            z = slice
            t = 1
        }
	return this.resource.src + '?slice=,,' + z + ',' + t +
	    '&depth=8,d,u,cs&fuse=' + this.fuseLine + ':m&format=png'
    },

    // Similar to getImageURL, but for the image overlay
    getOrigURL: function(slice) {
        if (this.sliceAxis === 'time') {
            z = 1
            t = slice
        } else {
            z = slice
            t = 1
        }
        return this.origSrc + '?slice=,,' + z + ',' + t +
            '&depth=8,d,u,cs&format=png'
    },

    // Called when the label is changed
    updateLabel: function() {
      label = this.toolbar.label
      // change color of circle in toolbar
      label.setFieldLabel('<div style="background-color:#' + label.value +
          '; width:20px; height:20px; border-radius: 50%"></div>')
      // change color of cursor
      this.imgPanel.cursor1.style.color = '#' + label.value
    },

    // Re-draw cursor. Called when the cursor is moved or the color is changed.
    updateCursor: function(x=null, y=null) {
      for (const cursor of [this.imgPanel.cursor1, this.imgPanel.cursor2]) {
        if (x != null) {
          cursor.style.top = y + 'px'
          cursor.style.left = x + 'px'
        }
        brush_size = this.toolbar.brush.value
        rad = this.imgPanel.canvasLocation['scale'] * brush_size
        cursor.style.width = rad + 'px'
        cursor.style.height = rad + 'px'
      }
    },

    // Triggered when slice index is changed via keyboard only
    // delta = 1 would be next slice, delta = -1 is previous
    changeSlice: function(delta) {
      val = parseInt(this.toolbar.slice.value)
      val = val + delta
      // handle edge cases (wrap around modulo numSlices)
      if (val == 0) {
        val = this.numSlices
      } else if (val > this.numSlices) {
        val = 1
      }
      this.toolbar.slice.setValue(val)
    },

    // Called when slice is changed via keyboard or the toolbar
    updateSlice: function() {
      val = this.toolbar.slice.value
      // Save the current canvas
      this.drawingStack[this.prevSlice-1] = this.canvas.toDataURL('image/png')
      // Draw new image from the array. By default, layers which have not yet
      // been saved to have a value of "" (empty string). This will mean there
      // is nothing drawn on the canvas to start.
      this.canvasCtx.clearRect(0, 0, this.canvas.width, this.canvas.height)
      this.canvasImage.src = this.drawingStack[val - 1]
      this.prevSlice = val
      // Replace underlying images with new slice images
      this.imgSeg.src = this.getImageURL(val)
      this.imgOrig.src = this.getOrigURL(val)
      // Undo stack is cleared
      this.undoStack = []
    },	    


    fetchMeta: function() {
      url = document.location.origin + '/data_service/mex?tag_query=%22' +
        this.resource.src.replace('image_service', 'data_service') + '%22'
 
      Ext.Ajax.request({
        scope: this,
        url: url, 
        callback: this.callbackMex
      })
    },


    callbackMex: function(opts, success, response) {
      xmlDoc = response.responseXML
      if (!xmlDoc) {
        return
      }
      // Have the URL of the module execution (mex). Now need the image URL
      mex_url = BQ.util.xpath_nodes(xmlDoc, 'resource/mex')
      if (mex_url.length == 0) {
        this.no_mask = true
        this.origSrc = this.resource.src
        Ext.Ajax.request({
          scope: this,
          url: this.resource.src + '?meta',
          callback: this.callbackMeta
        })
      } else {
        mex_url = mex_url[0].getAttribute('uri') + '?view=inputs'
        Ext.Ajax.request({
          scope: this,
          url: mex_url,
          callback: this.callbackInputs
        })
      }
    },

    callbackInputs: function(opts, success, response) {
      xmlDoc = response.responseXML
      if (!xmlDoc) {
       console.log('A weird error occurred')
       return
      }
      // The queries below get the image URL
      orig = BQ.util.xpath_nodes(xmlDoc,
          'mex/tag[@name="inputs"]/tag[@name="resource_url"]')[0]
      this.origSrc = orig.getAttribute('value').replace('data_service',
          'image_service')
      Ext.Ajax.request({
        scope: this,
        url: this.resource.src + '?meta',
        callback: this.callbackMeta
      })
    },


    callbackMeta: function(opts, success, response) {
      xmlDoc = response.responseXML
      if (!xmlDoc) {
        return
      }
      try {
        t = parseInt(BQ.util.xpath_nodes(xmlDoc,
          "//tag[@name='image_num_t']/@value")[0].value);
        z = parseInt(BQ.util.xpath_nodes(xmlDoc,
            "//tag[@name='image_num_z']/@value")[0].value);
        this.numChannels = parseInt(BQ.util.xpath_nodes(xmlDoc,
          "//tag[@name='image_num_c']/@value")[0].value);
      } catch (e) {
        alert("Could not find image shape from metadata")
      }
      if (this.no_mask) {
        this.numChannels = 7
      }

      if (t==1) {
        this.numSlices = z
        this.sliceAxis = 'z'
      } else {
        this.numSlices = t
        this.sliceAxis = 'time'
      }
      // Initialize current slice to be 1
      this.slice = 1
      addArray = []
      if (this.numChannels > defaultColorOrder.length) {
        alert("number of channels is too large")
      }

      this.fuseLine = ""
      for (let i=0; i < this.numChannels; i++) {
        this.toolbar.label.store.add({
          'name': 'Label ' + (i+1),
          'color': defaultColorOrder[i]
        })
        this.fuseLine += defaultFuseOrder[i] + ';'
      }
      this.prevSlice = 1
      this.drawingStack = Array(this.numSlices).fill("")
      this.imgSeg.src = this.getImageURL(0)
      this.imgOrig.src = this.getOrigURL(0)
      this.moveCanvas()
    },




    // Redraws the canvas images. All parameters are deltas. Meaning, if the
    // zoom argument is 2, and the previous zoom was 4, zoom will now be 8.
    moveCanvas: function(deltaX = 0, deltaY = 0, zoom = 1) {
      loc = this.imgPanel.canvasLocation
      loc['x'] += deltaX
      loc['y'] += deltaY
      loc['x'] *= zoom
      loc['y'] *= zoom
      loc['scale'] *= zoom

      h = this.imgPanel.getHeight()
      w = this.imgPanel.getWidth()

      this.imgOrig.style.opacity = this.toolbar.imgAlpha.getValue() / 255
	
      // Reposition the canvas and both images
      for (const item of [this.imgSeg, this.canvas, this.imgOrig]) {
        item.style.top = Math.floor(h/2) + loc['y'] + 'px'
        item.style.left = Math.floor(w/2) + loc['x'] + 'px'
        item.style.width = Math.round(loc['scale'] *
            this.canvas.width) + 'px'
//            this.imgSeg.naturalWidth) + 'px'
        item.style.height = Math.round(loc['scale'] *
            this.canvas.height) + 'px'
//            this.imgSeg.naturalHeight) + 'px'
      }
      // Redraw cursor, since zoom may have changed
      this.updateCursor()
    },


    // Called when a keypress changes the label
    changeLabel: function(delta) {
      store = this.toolbar.label.getStore()
      cur_val = this.toolbar.label.getValue()
      index = store.find('color', cur_val)
      index_new = Math.min(store.data.length-1, Math.max(0, index + delta))
      val_new = store.getAt(index_new).data.color
      this.toolbar.label.setValue(val_new)
    },


    // Maps all keys to their corresponding function calls
    keypressHandler: function(e) {
      key = String.fromCharCode(e)
      switch (key) {
        case 'A': this.moveCanvas(stepSize, 0, 1); break
        case 'D': this.moveCanvas(-stepSize, 0, 1); break
        case 'W': this.moveCanvas(0, stepSize, 1); break
        case 'S': this.moveCanvas(0, -stepSize, 1); break
        case 'Q': this.moveCanvas(0, 0, 1/2); break
        case 'E': this.moveCanvas(0, 0, 2); break            
        case 'X': this.changeSlice(-1); break
        case 'C': this.changeSlice(1); break
        case 'R': this.changeLabel(-1); break
        case 'F': this.changeLabel(1); break
        case 'Z': this.undo(); break
        case '1': this.toolbar.imgAlpha.setValue(0); break
        case '2': this.toolbar.imgAlpha.setValue(85); break		
        case '3': this.toolbar.imgAlpha.setValue(170); break
        case '4': this.toolbar.imgAlpha.setValue(255); break
      }
    },

    // Maps mouse location on screen to the coordinates on the canvas
    mousePosToCanvas: function(mouseX, mouseY) {
      var [ox, oy] = this.imgPanel.getXY()
      x = mouseX - ox - (this.imgPanel.getWidth()/2)
      y = mouseY - oy - (this.imgPanel.getHeight()/2)
      x -= this.imgPanel.canvasLocation['x']
      y -= this.imgPanel.canvasLocation['y']
      x = (x/this.imgPanel.canvasLocation['scale']) + this.canvas.width/2
      y = (y/this.imgPanel.canvasLocation['scale']) + this.canvas.height/2
      return [x, y]
    },

    // Draws a circle at canvas coordinate (x, y)
    drawCircle: function(x, y) {

      d = this.toolbar.brush.value
      ctx = this.canvasCtx
      ctx.fillStyle = '#' + this.toolbar.label.value
      ctx.beginPath()

      // HTML canvas does not seem to support drawing without bilinear
      // interpolation. It is critical for the mask drawing that all lines
      // be binary, not smoothed out. All drawing is done using rectanges,
      // aligned exactly with the coordinate system, so no bilinear interp
      // is done.

      // Large circles are drawn using a number of rectangles, to make an
      // approximate circle.

      // Circles 3px and smaller are drawn as rectangles, with special switch
      // cases.

      switch (d) {
        case 1: 
	      ctx.rect(Math.floor(x), Math.floor(y), 1, 1); break;

        case 2:
          ctx.rect(Math.round(x) - 1, Math.round(y) - 1, 2, 2); break;

        case 3:
          ctx.rect(Math.floor(x)-1, Math.floor(y)-1, 3, 3); break;

        default:
          // 8 points on the radius of a unit circle from 0 to 90 degrees.
          // Used to approximate a circle and many rectangles overlayed.
          const coords = [[0.1736, 0.9848], [0.3420, 0.9397],
                          [0.5000, 0.8660], [0.6428, 0.7660],
                          [0.7660, 0.6428], [0.8660, 0.5000],
                          [0.9397, 0.3420], [0.9848, 0.1736]]

          for (const coord of coords) {
            var lx = d * coord[0]
            var ly = d * coord[1]
            xi = Math.round(x-lx/2)
            yi = Math.round(y-ly/2)
            ctx.rect(xi, yi, Math.round(lx), Math.round(ly))
          }
      }
      ctx.fill()
    },	
})
