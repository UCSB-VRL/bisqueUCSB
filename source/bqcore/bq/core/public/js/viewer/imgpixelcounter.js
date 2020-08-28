//modification to imageview
/*
*	ImgPixelCounter Viewer Plugin
*
*	Instantiates a ImgCurrentView for snap shots of the current 
*	view to build. A pixel counter button is added to the operations
*	menu.
*
*	@param: viewer - 
*	@param: name - 
*/
function ImgPixelCounter(viewer, name) {

    this.base = ViewerPlugin;
    this.base(viewer, name);

    var p = viewer.parameters || {};
    this.default_threshold        = p.threshold || 0;
    this.default_autoupdate       = false;
	
	this.imgCurrentView = new ImgCurrentView(viewer, {
		wGobjects: false,
		wBorders: true,
		wScaleBar: false,
	});
	
    var tb = this.viewer.toolbar;
    if (!tb) return;
    var operations = tb.queryById('menu_viewer_operations'); 
    if (!operations) return;
    operations.menu.insert(1, {
        xtype  : 'menuitem',
        itemId : 'menu_viewer_pixel_counting',
        text   : 'Pixel Counter',
        handler: this.pixelCounter,
        scope  : this,
    });
	
	//set all the counts to 0
	this.r0px = 0;//number of pixels equal or below the threshold (red)
	this.r1px = 0;//number of pixels above the threshold
	this.g0px = 0;//number of pixels equal or below the threshold (green)
	this.g1px = 0;//number of pixels above the threshold
	this.b0px = 0;//number of pixels equal or below the threshold (blue)
	this.b1px = 0;//number of pixels above the threshold
}


ImgPixelCounter.prototype = new ViewerPlugin();


ImgPixelCounter.prototype.create = function (parent) {
    this.parent = parent;
    return parent;
};

/*
*	pixelCounter
*
*	Initializes the panels for the pixel counter and
*	Hides the Tag Panel and attaches a close listener
*	to the Pixel Counter Panel to destroy the Pixel
*	Counter Panel and show the Tag Panel.
*
*/
ImgPixelCounter.prototype.pixelCounter = function () {
    if (!this.pixelCounterPanel) { //check if the pixel counter panel exists
	
        
        var viewerTagPanel = this.viewer.parameters.main.queryById('tabs');
        viewerTagPanel.setVisible(false);
        var pixelcounterButton = this.viewer.toolbar.queryById('menu_viewer_pixel_counting');
        pixelcounterButton.setDisabled(true);
		
        var me = this;
        //disable pixel counter menu
        this.pixelCounterPanel = Ext.create('BQ.Panel.PixelCounter',{
            pixelCounter: this,
            viewer: this.viewer,
            phys: this.viewer.imagephys,
            autoDestroy: false,
			itemId: 'pixelcounter-panel',
			id: 'pixelcounter-panel',
        });
		
		// When close is called on the panel this listener will
		// break down the panel and call back the tag viewer into
		// view.
        this.pixelCounterPanel.on('close', function() {
            this.destroyPixelCounterDisplay(); //destroys display when closed
            delete this.pixelCounterPanel; //remove the panel from ImgPixelCounter
            viewerTagPanel.setVisible(true);
            pixelcounterButton.setDisabled(false); //enable pixel counter menu
            //brings back the metadata panel
		}, this);
        this.viewer.parameters.main.queryById('viewer_container').add(this.pixelCounterPanel); //create panel
		this.initCanvas();
		
		// Adds a resize listener to the window to destroy the panel
		// when a resize occurs. The pixel counter only takes a snap
		// shot of a current view so any-time the view is changed the
		// pixel counter will be destroyed.
		window.addEventListener('resize', function() {
			if (me.pixelCounterPanel) {
                Ext.MessageBox.show({
                   title: 'Notification',
                   msg: 'Resizing the page will disable to pixel counter. If you need to adjust the view, close the pixel counter, set the desired view in the viewer and open the pixel counter again.',
                   buttons: Ext.MessageBox.OK,
               });
				me.pixelCounterPanel.close();
			}
		});
    }
};


/*
*	initCanvas
*	
*	Creates and overlays 4 panels over the images viewer
*
*	1. The canvas image - an image constructed from 
*	all the tiles in the view
*	2. The canvas threshold - the threshold image of the
*	canvas image
*	3. The canvas mask - a mask that handles the clicks
*	and shows the regions that have been selected.
*	4. The SVG layer - shows the highlighted elements tag.
*
*/
ImgPixelCounter.prototype.initCanvas = function() {
    
	var control_surface_size = this.viewer.viewer_controls_surface.getBoundingClientRect();
	
    if (!this.canvas_mask) {
        this.canvas_mask = document.createElement('canvas');
        this.canvas_mask.setAttributeNS(null, 'class', 'pixel_counter_canvas_mask');
        this.canvas_mask.setAttributeNS(null, 'id', 'pixel_counter_canvas_mask');
        this.canvas_mask.height = control_surface_size.height;
        this.canvas_mask.width = control_surface_size.width;
        this.canvas_mask.style.zIndex = 310;
        this.canvas_mask.style.top = "0px";
        this.canvas_mask.style.left = "0px";
        this.canvas_mask.style.position = "absolute";
        this.ctx_imgmask = this.canvas_mask.getContext("2d");
        this.canvas_mask.addEventListener("click", this.onClick.bind(this), false);
        this.parent.appendChild(this.canvas_mask);
    }

    if (!this.canvas_image) {
        this.canvas_image = document.createElement('canvas');
        this.canvas_image.setAttributeNS(null, 'class', 'pixel_counter_canvas_image');
        this.canvas_image.setAttributeNS(null, 'id', 'pixel_counter_canvas_image');
        this.canvas_image.height = control_surface_size.height;
        this.canvas_image.width = control_surface_size.width;
        this.canvas_image.style.zIndex = 300;
        this.canvas_image.style.top = "0px";
        this.canvas_image.style.left = "0px";
        this.canvas_image.style.position = "absolute";
        this.ctx_img = this.canvas_image.getContext("2d");
        this.parent.appendChild(this.canvas_image);
    }

	if (!this.canvas_theshold) {
        this.canvas_theshold = document.createElement('canvas');
        this.canvas_theshold.setAttributeNS(null, 'class', 'pixel_counter_canvas_threshold');
        this.canvas_theshold.setAttributeNS(null, 'id', 'pixel_counter_canvas_threshold');
        this.canvas_theshold.height = control_surface_size.height;
        this.canvas_theshold.width = control_surface_size.width;
        this.canvas_theshold.style.zIndex = 305;
        this.canvas_theshold.style.top = "0px";
        this.canvas_theshold.style.left = "0px";
        this.canvas_theshold.style.position = "absolute";
        this.ctx_thresh = this.canvas_theshold.getContext("2d");
        this.parent.appendChild(this.canvas_theshold);
    }

    //marking of the ids
    //needs to be above everything
    if (!this.svgdoc) {
        this.svgdoc = document.createElementNS('http://www.w3.org/2000/svg', "svg");
        this.svgdoc.setAttributeNS(null, 'class', 'pixel_counter_svg_id_label_surface');
        this.svgdoc.setAttributeNS(null, 'id', 'pixel_counter_svg_id_label_surface');
        this.svgdoc.setAttribute('height', control_surface_size.height);
        this.svgdoc.setAttribute('width', control_surface_size.width);
        this.svgdoc.style.position = "absolute";
        this.svgdoc.style.top = "0px";
        this.svgdoc.style.left = "0px";
        this.svgdoc.style.zIndex = 315;
        this.svgdoc.addEventListener("click",this.onClick.bind(this),false);
        this.parent.appendChild(this.svgdoc);
    }
	
	this.updateCanvas();
};


//updates when rescaling the images
//pulls in the tiled images from the tile render
//initalizes only on enable select
//updates new canvas when enable select is disabled and enabled
/*
*	updateCanvas
*
*	Grabs the current view saves it in the image canvas and 
*	applies a threshold and save the filtered image to the
* 	threshold canvas.
*/
ImgPixelCounter.prototype.updateCanvas = function() {
    if (!this.canvas_image||!this.canvas_mask) {
        this.initCanvas();
    }

    // load image from data url
    this.viewer.parameters.main.viewerContainer.setLoading(true);
    var me = this;

	var level = this.imgCurrentView.getCurrentLevel();
	this.imgCurrentView.setLevel(level);
	
	//get canvas back and build threshold
	function callback(canvas_view) {
	
		me.viewer.parameters.main.viewerContainer.setLoading(false);
		var ctx_img = me.canvas_image.getContext("2d");
		ctx_img.drawImage(canvas_view, 0, 0, me.canvas_image.width, me.canvas_image.height)
		me.updateThresholdCanvas();
		
	}
	
	this.imgCurrentView.returnCurrentView(callback); // expensive
};

/*
*	updateThresholdCanvas
*
*	Resets the threshold canvas by setting all the pixel values to
* 	gray, opacity 0. The opacity is set to 1 for all the pixels
*	on the tileviewer.
*/
ImgPixelCounter.prototype.updateThresholdCanvas = function() {
	if (this.canvas_theshold) {
        //var renderer = this.viewer.plugins_by_name['renderer'];
        var tiled_viewer = this.viewer.plugins_by_name['tiles'].tiled_viewer;
        var view_scale = this.viewer.view().scale;
        var width = Math.floor(tiled_viewer.image_size.width * view_scale);
        var height = Math.floor(tiled_viewer.image_size.height * view_scale);
        var left = tiled_viewer.x;
        var top = tiled_viewer.y;
        
        
		//getting the viewer offsets
		var xoffset = left>0?left:0;
        var yoffset = top>0?top:0;
        
		if (top + height > tiled_viewer.height) {
			var height = height - (top + height - tiled_viewer.height);
		}
		
		if (left + width > tiled_viewer.width) {
			var width = width - (left + width - tiled_viewer.width);
		}

		var ctx_thresh = this.canvas_theshold.getContext("2d");
		ctx_thresh.fillStyle = 'rgba(67, 67, 67, 0)';
		ctx_thresh.fillRect(0, 0, this.canvas_theshold.width, this.canvas_theshold.height); //set all transparent		
		ctx_thresh.fillStyle = 'rgba(67, 67, 67, 1)';
		ctx_thresh.fillRect(xoffset, yoffset, width, height); //set view none transparent
		this.thresholdImage(this.pixelCounterPanel.thresholdValue);
	}
}

/*
*	thresholdImage
*	
*	Thresholds Image and write it to the threshold canvas and resets the global pixel counts
*
*	@param: value_th - the threshold value
*/
ImgPixelCounter.prototype.thresholdImage = function(value_th) {
	
	var ctx_thresh = this.canvas_theshold.getContext("2d");
	var threshData = ctx_thresh.getImageData(0, 0, this.canvas_theshold.width, this.canvas_theshold.height);
	var td = threshData.data;
	
	var ctx_img = this.canvas_image.getContext("2d");
	var imageData = ctx_img.getImageData(0, 0, this.canvas_image.width, this.canvas_image.height);
	var id = imageData.data;
	
	//reset global pixel counters
	this.r0px = 0;
	this.r1px = 0;
	this.g0px = 0;
	this.g1px = 0;
	this.b0px = 0;
	this.b1px = 0;
	
	//threshold and count the pixels
	for (var i=0; i<id.length; i+=4) {
		if (td[i+3] > 0) { // alpha
			if (id[i] > value_th) { //red
				td[i] = 255;
				this.r1px += 1;
			} else {
				td[i] = 0;
				this.r0px += 1;
			}
			if (id[i+1] > value_th) { //green
				td[i+1] = 255
				this.g1px += 1;
			} else {
				td[i+1] = 0;
				this.g0px += 1;	
			}
			if (id[i+2] > value_th) { //blue
				td[i+2] = 225
				this.b1px += 1;
			} else {
				td[i+2] = 0;
				this.b0px += 1;	
			}
		}
	}
	ctx_thresh.putImageData(threshData, 0, 0);
	
	var scale = this.viewer.view().scale;
	
	//scale the pixels by the view at the time
	this.r0px *= scale;
	this.r1px *= scale;
	this.g0px *= scale;
	this.g1px *= scale;
	this.b0px *= scale;
	this.b1px *= scale;
	
	
	if (this.pixelCounterPanel) {
		this.pixelCounterPanel.updataGlobalPanel();
	}
};


/*
*	destroyPixelCounterDisplay
*
*	Removes all the 4 elements from the viewer
*/
ImgPixelCounter.prototype.destroyPixelCounterDisplay = function() {
    if (this.canvas_mask) {
        this.canvas_mask.remove();
        delete this.canvas_mask;
    }
    if (this.canvas_image){
        this.canvas_image.remove();
        delete this.canvas_image;
    }
    if (this.canvas_theshold){
        this.canvas_theshold.remove();
        delete this.canvas_theshold;
    }
    if (this.svgdoc){
        this.svgdoc.remove();
        delete this.svgdoc;
    }
};


ImgPixelCounter.prototype.newImage = function () {
    this.phys_inited = false;
};

/*
*	updateImage
*
*	A callback when the image in the viewer is changed.
*
*/
ImgPixelCounter.prototype.updateImage = function () {
};


ImgPixelCounter.prototype.getParams = function () {
    return this.params || {};
};

//check if threshold mode is on to redraw image
//or if selection mode is on the redraw canvas and push it to the front
ImgPixelCounter.prototype.updateView = function (view) {
    ///if (this.pixelCounterPanel && this.pixelCounterPanel.thresholdMode)
    //    view.addParams('threshold='+this.pixelCounterPanel.thresholdValue+',both');
};


/*
*	onClick
*
*	Retrieves the points from a click event and maps
*	it to the tile viewer. If that point has not been
*	selected indicated by the mask a connected components
* 	is run from that point on the threshold filtered image and 
* 	written to the mask.
*/
ImgPixelCounter.prototype.onClick = function(e) {

    //find the offsets to canvas
    //set loading when clicked
	
	var ctx_imgmask = this.canvas_mask.getContext("2d");
    var maskData = ctx_imgmask.getImageData(0, 0, this.canvas_mask.width, this.canvas_mask.height);
    var mask_data = maskData.data;	

	var ctx_thresh = this.canvas_theshold.getContext("2d")
    var threshData = ctx_thresh.getImageData(0, 0, this.canvas_theshold.width, this.canvas_theshold.height);
    var thresh_data = threshData.data;	

    var xClick = e.pageX-parseInt(this.canvas_mask.style.left)-this.viewer.plugins_by_name['tiles'].tiled_viewer.left; //clicks mapped to canvas
    var yClick = e.pageY-parseInt(this.canvas_mask.style.top)-this.viewer.plugins_by_name['tiles'].tiled_viewer.top; //clicks mapped to canvas

	if (thresh_data[4*(yClick*this.canvas_mask.width+xClick)+3]==255) {
        if (mask_data[4*(yClick*this.canvas_mask.width+xClick)+3]!=255) { //check to see if region has already been selected
            this.viewer.parameters.main.viewerContainer.setLoading(true);
            var me = this;
            setTimeout(function(){ //set time out to allow for the loading screen to be shown
               me.connectedComponents(xClick,yClick);
               me.viewer.parameters.main.viewerContainer.setLoading(false);
            },5);
        }
    }
};


/*************************************
 *
 *      Connected components
 *
 *************************************/
 
/*
*	index2xy
*
*	Converts a single index value to (x,y)
*	coordinates on the canvas.
*
*	@param: index - the index of a pixel on the canvas
*	plain
*
*	@return: {x: - x coordinate in canvas
*			 y: - y coordinate in canvas}
*/
ImgPixelCounter.prototype.index2xy = function(index) {

    index = parseInt(index);
    var x = parseInt(parseInt(index)/4)%this.canvas_image.width;
    var y = parseInt(parseInt(parseInt(index)/4)/this.canvas_image.width)%this.canvas_image.height;
    return {x:x,y:y};

};

/*
*	setText2SVG
*	
*	Creates a new text element and attaches 
* 	provided attributes with style : 
*		font-family:Arial;font-size: 14; fill:blue; text-shadow: #FFFFFF 1px 1px 1px
*	to the SVG Document
*
*	@param: text - text to be applied at given 
*	@param: id - set element id
*	@param: x - set x coordinate in the SVG space
*	@param: y = set y coordinate in the SVG space
*
*/
ImgPixelCounter.prototype.setText2SVG = function(text,id,x,y) {
    var textelement = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    textelement.setAttribute("id", id);
    textelement.setAttribute("x", x);
    textelement.setAttribute("y", y);
    textelement.setAttribute('style', "font-family:Arial;font-size: 14; fill:blue; text-shadow: #FFFFFF 1px 1px 1px ;");//rgba(0,0,0,0.1) #FFFFFF
    textelement.textContent = text;
    this.svgdoc.appendChild(textelement);
};



/*
*	connectedComponents
*
*	Set the region defined by the connected components to magenta with
*	an opacity of 1 and set the place where the click occurred with to 
*	the current idcount of selected elements.
*
*	@param: x  - x coordinate of the point to seed the connected components
*	@param: y  - y coordinate of the point to seed the connected components
*/
ImgPixelCounter.prototype.connectedComponents = function(x,y) {

    var maskColor = {r:255, g:0, b:255, a:225}; //magenta

	var ctx_imgmask = this.canvas_mask.getContext("2d");
    var maskData = ctx_imgmask.getImageData(0, 0, this.canvas_mask.width, this.canvas_mask.height);
    var mask_data = maskData.data;
	
	var ctx_thresh = this.canvas_theshold.getContext("2d")
    var threshData = ctx_thresh.getImageData(0, 0, this.canvas_theshold.width, this.canvas_theshold.height);
    var thresh_data = threshData.data;

    var edge_points_queue = new Array();

    var seed = 4*(y*this.canvas_image.width+x); //enforce channel zero

    edge_points_queue.push(seed);
    var label_list = {
        r:(thresh_data[seed] >= 128),
        g:(thresh_data[seed+1] >= 128),
        b:(thresh_data[seed+2] >= 128)
    };
	
    var count = 0;
    while (edge_points_queue.length>0) {
        this.checkNeighbors(edge_points_queue, label_list, maskColor, thresh_data, mask_data);
        count+=1;
    }

    ctx_imgmask.putImageData(maskData, 0, 0);
	
    // remap
    var tiled_viewer = this.viewer.plugins_by_name['tiles'].tiled_viewer; //finding tiled viewer in the plugin list
    var p = tiled_viewer.toImageFromViewer({x: x - tiled_viewer.x, y: y - tiled_viewer.y});

    //scaling the counts
    var scale = this.viewer.view().scale;
    var scaled_count = (count/(scale*scale)).toFixed(0);
    var phys = this.viewer.imagephys;

    if (phys.isPixelResolutionValid()) {
        var area = (parseFloat(scaled_count)*parseFloat(phys.pixel_size[0])*parseFloat(phys.pixel_size[1])).toFixed(2);
        this.pixelCounterPanel.regionCount.push({index:this.pixelCounterPanel.idCount, pixels:scaled_count, x:p.x, y:p.y, xclick:x, yclick:y,svgid:'svg_text_element_' + (this.pixelCounterPanel.idCount), area:area});
    } else {
        this.pixelCounterPanel.regionCount.push({index:this.pixelCounterPanel.idCount, pixels:scaled_count, x:p.x, y:p.y, xclick:x, yclick:y, svgid:'svg_text_element_' + (this.pixelCounterPanel.idCount)});
    }

    //update svg element
    this.setText2SVG((this.pixelCounterPanel.idCount).toString(),'svg_text_element_'+(this.pixelCounterPanel.idCount),x,y)
    this.pixelCounterPanel.idCount += 1; //setting for the next region
    this.pixelCounterPanel.updateRegionPanel();
};


//removing the connected component marked region
/*
*	undoConnectedComponents
*
*	Set the region defined by the connected components to black with
*	an opacity of 0 and removed the tag from the SVG layer of the provided
*	id.
*
*	@param: x  - x coordinate of the point to seed the connected components
*	@param: y  - y coordinate of the point to seed the connected components
*	@param: id - the id of the tag in the SVG layer
*/
ImgPixelCounter.prototype.undoConnectedComponents = function(x,y,id) {

    var maskColor = {r:0, g:0, b:0, a:0}; //set to black
	
	var ctx_imgmask = this.canvas_mask.getContext("2d");
    var maskData = ctx_imgmask.getImageData(0, 0, this.canvas_mask.width, this.canvas_mask.height);
    var mask_data = maskData.data;
	
	var ctx_thresh = this.canvas_theshold.getContext("2d")
    var threshData = ctx_thresh.getImageData(0, 0, this.canvas_theshold.width, this.canvas_theshold.height);
    var thresh_data = threshData.data;
	
    var edge_points_queue = new Array();
    var seed = 4*(y*this.canvas_image.width+x); //enforce channel zero

    edge_points_queue.push(seed);
    var label_list = {
        r : (thresh_data[seed] >= 128),
        g : (thresh_data[seed+1] >= 128),
        b : (thresh_data[seed+2] >= 128)
    };
	
    while (edge_points_queue.length>0) {
        this.checkNeighbors(edge_points_queue, label_list, maskColor, thresh_data, mask_data);
    }
    this.removeTextFromSVG(id);
    ctx_imgmask.putImageData(maskData, 0, 0);
    this.pixelCounterPanel.updateRegionPanel();
};

/*
*	checkNeighbors
*
*	
*
*	@param: edge_points_queue
*	@param: label_list
*	@param: maskColor
* 	@param: threshold_data
*	@param: mask_data
*/
ImgPixelCounter.prototype.checkNeighbors = function(edge_points_queue, label_list, maskColor, threshold_data, mask_data) {
    //Find the connected component
    //uses the transparency as a marker for past check pixels
	
    var edge_index = parseInt(edge_points_queue.shift());

    //set color of the mask
    mask_data[edge_index]   = maskColor.r;
    mask_data[edge_index+1] = maskColor.g;
    mask_data[edge_index+2] = maskColor.b;
	mask_data[edge_index+3] = maskColor.a;
	
    var edge_value = this.index2xy(edge_index);

    //check neighbors
	var new_edge_index = edge_index + 4; //check right
    if (threshold_data[new_edge_index+3] == 255) { //check if out of the image
        if ((threshold_data[new_edge_index]>=128) == label_list.r &&
            (threshold_data[new_edge_index+1]>=128) == label_list.g &&
            (threshold_data[new_edge_index+2]>=128) == label_list.b &&
            mask_data[new_edge_index+3] != maskColor.a ) { //has been put in the queue at sometime
            edge_points_queue.push(new_edge_index); //check transparency to see if it
            mask_data[new_edge_index+3] = maskColor.a; //set transparency
        }
    }
	
	var new_edge_index = edge_index-4; //check left
    if (threshold_data[new_edge_index+3] == 255) { //check if out of the image
        if ((threshold_data[new_edge_index]>=128) == label_list.r &&
            (threshold_data[new_edge_index+1]>=128) == label_list.g &&
            (threshold_data[new_edge_index+2]>=128) == label_list.b &&
            mask_data[new_edge_index+3] != maskColor.a ) {
            edge_points_queue.push(new_edge_index);
            mask_data[new_edge_index+3] = maskColor.a; //set transparency
        }
    }
	
	var new_edge_index = edge_index+this.canvas_image.width*4; //check above
    if (threshold_data[new_edge_index+3] == 255) { //check if out of the image
        if ((threshold_data[new_edge_index]>=128) == label_list.r &&
            (threshold_data[new_edge_index+1]>=128) == label_list.g &&
            (threshold_data[new_edge_index+2]>=128) == label_list.b &&
            mask_data[new_edge_index+3] != maskColor.a  ) {
            edge_points_queue.push(new_edge_index);
            mask_data[new_edge_index+3] = maskColor.a; //set transparency
        }
    }

	var new_edge_index = edge_index-this.canvas_image.width*4; //check below
    if (threshold_data[new_edge_index+3] == 255) { //check if out of the image
        if ((threshold_data[new_edge_index]>=128) == label_list.r &&
            (threshold_data[new_edge_index+1]>=128) == label_list.g &&
            (threshold_data[new_edge_index+2]>=128) == label_list.b &&
            mask_data[new_edge_index+3] != maskColor.a )  {
            edge_points_queue.push(new_edge_index);
            mask_data[new_edge_index+3] = maskColor.a; //set transparency
        }
    }
};


/******************************
*
*	Reset Elements
*
*******************************/


//resets all the elements to the base level
/*
*	resetPixelRegionCounter
*
*	Resets mask, svg layer, and resets the region count.
*/
ImgPixelCounter.prototype.resetPixelRegionCounter = function() {
    this.resetsvg();
    this.resetmask();
    if(this.pixelCounterPanel.regionCount) this.pixelCounterPanel.regionCount = []; //reset region counter table
    this.pixelCounterPanel.idCount = 0; //resets the ids
};


//removes all child elements
/*
*	resetsvg
*
*	Iterates through the children of the SVG
*	elements and removes them.
*/
ImgPixelCounter.prototype.resetsvg = function() {
    if(this.svgdoc) {
        while(this.svgdoc.firstChild) {this.svgdoc.removeChild(this.svgdoc.firstChild);}
    }
};


//sets all values in the mask to 0
/*
*	resetmask
*
*	Sets mask to black and the opacity to 0.
*/
ImgPixelCounter.prototype.resetmask = function() {
    if (this.canvas_mask) {
		var ctx_imgmask = this.canvas_mask.getContext("2d");
		ctx_imgmask.fillStyle = "rgba(0, 0, 0, 0)";
		ctx_imgmask.clearRect(0, 0, this.canvas_mask.width, this.canvas_mask.height); //set all transparent	
    }
};

/*
*	removeTextFromSVG
*
*	Removes the id tag from the SVG layer based on it id value.
*
*	@param: id - the id number of the SVG element being removed
*/
ImgPixelCounter.prototype.removeTextFromSVG = function(id){
    var svgTextElement = this.svgdoc.getElementById(id);
    if(svgTextElement) this.svgdoc.removeChild(svgTextElement);
};


ImgPixelCounter.prototype.changed = function () {
    this.viewer.need_update();
};


ImgPixelCounter.prototype.loadPreferences = function (p) {
    this.default_threshold      = 'threshold'      in p ? p.threshold      : this.default_threshold;
};

/*
*   BQ.Panel.PixelCounter
*
*   The panel to display information and to change the
*   threshold value
*/
Ext.define('BQ.Panel.PixelCounter', {
    extend: 'Ext.Panel',
    itemId: 'pixelcounter-panel',
    title : 'Pixel Counter',
    region : 'east',
    layout: { type: 'vbox', pack: 'start', align: 'stretch' },
    viewer: null,//requiered viewer initialized object
    activeTab : 0,
    bodyBorder : 0,
    //split : true,
	fixed: true,
    width : 400,
    plain : true,
    autoScroll: true,
    thresholdValue: 128,
    //channel_names: { 0: 'red', 1: 'green', 2: 'blue' },
    regionCount: [],
    idCount: 0, //keeps track of the ids for each region

    initComponent : function() {

        this.items = []; //reset panel items
        this.regionCount = []; //reset regionCount

        this.thresholdSlider = Ext.create('Ext.slider.Single',{
            width: '85%',
            fieldLabel: 'Threshold Value',
            value: this.thresholdValue,
            increment: 1,
            minValue: 0, //needs to adjust with the image
            maxValue: 256,    //needs to adjust with the image
            hysteresis: 250,  // delay before firing change event to the listener
			padding: '16px',
            listeners: {
                scope: this,
                afterrender: function() { //populate panel
                },
                change : function(self,event,thumb){
                    //set a delay to refresh the values on the panel
                    if (this.thresholdSlider.event_timeout) clearTimeout (this.thresholdSlider.event_timeout);
                    var me = this;
                    this.thresholdSlider.event_timeout = setTimeout(function(){
						//clear the regional pixel count store
						me.pixelCounter.resetPixelRegionCounter();
						me.updateRegionPanel();
                        me.thresholdValue = thumb.value.toString(); //set pixel counter value
						me.pixelCounter.thresholdImage(me.thresholdValue);
                    },  this.thresholdSlider.hysteresis );
                }
            }
        });

        this.globalCountInfo = Ext.create('Ext.container.Container',{
            itemId : 'px_threshold_panel',
            borders: false,
            frame: false,
            cls: 'thresholdelements',
			padding: '8px',
            items: [{
				xtype: 'box',
				html: '<h2>Global Counts</h2><p>Move the slider to set a threshold value. The pixel counts above and below the threshold will be computed from the fused RGB image in the viewer per channel.</p>',
				cls: 'threshold',
            },
             ],
        });


        //GRID
        var fieldList = ['index','x','y','pixels'];
        var columns = [{
            header: 'id',
            dataIndex: 'index',
        },{
            header: 'x',
            dataIndex: 'x',
        },{
            header: 'y',
            dataIndex: 'y',
        },{
            header: 'pixels',
            dataIndex: 'pixels',
        }];
		
        var fields = [
            {name: 'index', type: 'float'},
            {name: 'x', type: 'float'},
            {name: 'y', type: 'float'},
            {name: 'pixels', type: 'float'}
        ];
		
        if (this.phys.isPixelResolutionValid()) {
            fieldList.push('area');
            columns.push({
                header: this.phys.pixel_units[0]+'<sup>2</sup>',
                dataIndex: 'area',
            });
            fields.push({name: 'area', type: 'float'});
        }

        Ext.define('bq.pixelcount.RegionCounts', {
            extend: 'Ext.data.Model',
            fields: fields,
        });

        this.regionCountStore = Ext.create('Ext.data.Store', {
            model: 'bq.pixelcount.RegionCounts',
            storeId: 'regionCountStore',
            fields: fieldList,
            allowDeslect: true,
            proxy: {
                type: 'memory',
                reader: {
                    root: 'items'
                }
            },
            sorters: [{
                property: 'index',
                direction: 'desc'
            }]
        });

		this.regionCountInfo = Ext.create('Ext.container.Container', {
            //layout: 'fit',
			padding: '8px',
            html : '<h2>Regional Counts</h2><p>Click on any part of the image to segment out a region. The pixel count will be displayed below.</p>',
            cls: 'threshold',
            //layout: 'anchor',
        });
		
        this.regionCountGrid = Ext.create('Ext.grid.Panel', {
            itemId : 'px_regioncount_grid',
            store: this.regionCountStore,
            multiSelect: true,
            minHeight: 300,
            columns: {
                items: columns,
                defaults: {flex: 1},
            },
            flex: 2,
            border : false,
            renderTo: Ext.getBody(),
            tbar: [{ //Delete button
                itemId : 'px_delete_button',
                xtype: 'button',
                text: 'Delete',
                iconCls: 'icon-delete',
                scale: 'large',
                disabled: true,
                listeners : {
                    scope: this,
                    click: function() {
                        //deletes selected elements
                        var grid = this.queryById('px_regioncount_grid');
                        var selectedRecord = grid.getSelectionModel().getSelection()
                        var deleteRows = [];
                        for (var i = 0; i<selectedRecord.length; i++){
                            deleteRows.push(selectedRecord[i].data.index);
                        }
                        var regionCountDeletes = [];
                        var regionCount = [];
                        for (var i = 0; i<this.regionCount.length;i++) {
                            if (deleteRows.indexOf(this.regionCount[i].index) >= 0) {
                                regionCountDeletes.push(this.regionCount[i])
                            }
                            else {
                                regionCount.push(this.regionCount[i])
                            }
                        }

                        //delete all the rows at once
                        this.pixelCounter.canvas_mask.style.visibility = 'hidden';
                        this.viewer.parameters.main.viewerContainer.setLoading(true);
                        var me = this;
                        var regionCountElement = this.regionCount[i];
                        setTimeout(function(){ //set time out to allow for the loading screen to be shown
                           for (var i=0; i<regionCountDeletes.length; i++) {
                               me.pixelCounter.undoConnectedComponents(regionCountDeletes[i].xclick,regionCountDeletes[i].yclick,regionCountDeletes[i].svgid);
                           }
                           me.viewer.parameters.main.viewerContainer.setLoading(false);
                           me.pixelCounter.canvas_mask.style.visibility = 'visible';
                        }, 5);
                        this.regionCount = regionCount;
                        this.updateRegionPanel();
                    }
                },
            }, { //Resets Button
                itemId : 'px_reset_button',
                iconCls: 'converter',
                xtype: 'button',
                text: 'Reset',
                scale: 'large',
                disabled: true,
                listeners : {
                    scope: this,
                    click: function() {
                        //clears table and displayed segmentation
                        this.pixelCounter.resetPixelRegionCounter();
                        //this.pixelCounter.changed();
						this.updateRegionPanel();
                    }
                }
            }, '->', { //Export Button
                itemId : 'px_export_button',
                xtype: 'button',
                text: 'Export CSV',
                iconCls: 'external',
                scale: 'large',
                disabled: true,
                listeners : {
                    scope: this,
                    click: function() {
                        if(this.regionCount.length>0) {
                            this.exportCSV();
                        }
                    },
                },
            }],
        });

        this.tbar= ['->',{//close button
                xtype: 'button',
                text: 'Close',
                scale: 'large',
                iconCls: 'icon-close',
                itemId : 'pixelcounter_close_button',
                listeners: {
                    scope: this,
                    click: function() {
                        this.close(); //closes panel
                    }
                },
            },
        ];
		this.items.push(this.thresholdSlider);
		this.items.push(this.globalCountInfo);
        this.items.push(this.regionCountInfo);
        this.items.push(this.regionCountGrid);

        return this.callParent(arguments);
    },


	/*
	*	updataGlobalPanel
	*
	*	Writes global pixel information obtained by the threshold.
	*	If pixel resolution containing physical pixel information
	*	the scale factor will be applied.
	*/
    updataGlobalPanel : function() {
        var globalTitle = '<tr><th>channel</th><th >threshold</th><th>pixels</th>';

        if (this.phys.isPixelResolutionValid()) {
            globalTitle += '<th>'+this.phys.pixel_units[0]+'<sup>2</sup>'+'</th>';
        }
		
        globalTitle = globalTitle + '</tr>';
        var globalRows = '';
		var globalRowAbove = '<td>red</td><td>above</td><td >'+this.pixelCounter.r1px.toString()+'</td>';
		var globalRowBelow = '<td>red</td><td>below</td><td >'+this.pixelCounter.r0px.toString()+'</td>';		
		if (this.phys.isPixelResolutionValid()) {
			var area_above = (parseFloat(this.pixelCounter.r1px)*parseFloat(this.phys.pixel_size[0])*parseFloat(this.phys.pixel_size[1])).toFixed(2);
			var area_below = (parseFloat(this.pixelCounter.r0px)*parseFloat(this.phys.pixel_size[0])*parseFloat(this.phys.pixel_size[1])).toFixed(2);
			globalRowAbove += '<td>'+area_above.toString()+'</td>';
			globalRowBelow += '<td>'+area_below.toString()+'</td>';
		}
		globalRows += '<tr>'+globalRowAbove+'</tr><tr>'+globalRowBelow+'</tr>';		

		var globalRowAbove = '<td>green</td><td>above</td><td >'+this.pixelCounter.g1px.toString()+'</td>';
		var globalRowBelow = '<td>green</td><td>below</td><td >'+this.pixelCounter.g0px.toString()+'</td>';		
		if (this.phys.isPixelResolutionValid()) {
			var area_above = (parseFloat(this.pixelCounter.g1px)*parseFloat(this.phys.pixel_size[0])*parseFloat(this.phys.pixel_size[1])).toFixed(2);
			var area_below = (parseFloat(this.pixelCounter.g0px)*parseFloat(this.phys.pixel_size[0])*parseFloat(this.phys.pixel_size[1])).toFixed(2);
			globalRowAbove += '<td>'+area_above.toString()+'</td>';
			globalRowBelow += '<td>'+area_below.toString()+'</td>';
		}
		globalRows += '<tr>'+globalRowAbove+'</tr><tr>'+globalRowBelow+'</tr>';		
		
		var globalRowAbove = '<td>blue</td><td>above</td><td >'+this.pixelCounter.b1px.toString()+'</td>';
		var globalRowBelow = '<td>blue</td><td>below</td><td >'+this.pixelCounter.b0px.toString()+'</td>';		
		if (this.phys.isPixelResolutionValid()) {
			var area_above = (parseFloat(this.pixelCounter.b1px)*parseFloat(this.phys.pixel_size[0])*parseFloat(this.phys.pixel_size[1])).toFixed(2);
			var area_below = (parseFloat(this.pixelCounter.b0px)*parseFloat(this.phys.pixel_size[0])*parseFloat(this.phys.pixel_size[1])).toFixed(2);
			globalRowAbove += '<td>'+area_above.toString()+'</td>';
			globalRowBelow += '<td>'+area_below.toString()+'</td>';
		}
		globalRows += '<tr>'+globalRowAbove+'</tr><tr>'+globalRowBelow+'</tr>';		
        var html = '<center><table cellspacing="8">'+globalTitle+globalRows+"</table></center>";

        this.globalCountInfo.update(html); 
    },

	/*
	*	updateRegionPanel
	*
	*	Reloads the region panel and populates the graph with elements
	*	if the count is 0 for number of elements in the graph all the 
	*	buttons in the tool bar will be disabled.
	*/
    updateRegionPanel : function(){
	
		var regionCountGrid = this.queryById('px_regioncount_grid').setVisible(true);
		regionCountGrid.store.loadData(this.regionCount);
		regionCountGrid.getView().refresh();

		//set usability of the buttons
		if (this.regionCount.length>0){
			this.queryById('px_reset_button').setDisabled(false);
			this.queryById('px_export_button').setDisabled(false);
			this.queryById('px_delete_button').setDisabled(false);
		} else {
			this.queryById('px_reset_button').setDisabled(true);
			this.queryById('px_export_button').setDisabled(true);
			this.queryById('px_delete_button').setDisabled(true);
		}
	},

	/*
	*	exportCSV
	*
	*	Downloads a csv document containing all the information
	* 	contained in the region count panel.
	*/
    exportCSV : function() {
        //writes the region count info to csv
        if (this.regionCount.length>0) {
            var scale = this.viewer.view().scale;
            var CsvDocument = '';
            CsvDocument +=  'index,x,y,pixels'//title
            if (this.phys.isPixelResolutionValid()) {
                CsvDocument += ','+this.phys.pixel_units[0]+'^2';
            }
            CsvDocument += '\r\n';
            for (var r = 0; r<this.regionCount.length; r++) {
                //row
                CsvDocument += this.regionCount[r].index + ',' + this.regionCount[r].x + ',' + this.regionCount[r].y + ',' + this.regionCount[r].pixels;
                if (this.phys.isPixelResolutionValid()) {
                    CsvDocument += ','+this.regionCount[r].area;
                }
                CsvDocument += '\r\n';
            }

            window.open('data:text/csv;charset=utf-8,' + encodeURIComponent(CsvDocument), 'areas.csv'); //download

        }
    },
});

