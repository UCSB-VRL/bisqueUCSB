/*
 *	ImgCurrentView	
 *
 * 	Downloads a scaled view of the view currently being presented in the
 * 	viewer.
 *
 *	@param viewer - the viewer object
 *	@param opt - {wGobjects: default - false, (gobjects do not work right now)
 *				  wBorders: default - false,
 *				  wScaleBar: default - true}
 *
 *
 *	ex. of getting a current view and returning it to a new window
 *
 *		var currentview = ImgCurrentView(viewer,{wGobject: true, wBorders: false, wScalebar:true});
 *
 *		var level = currentview.getCurrentLevel();
 * 
 *		function callback(canvas_view) {
 *			var url = canvas_view.toDataURL("image/png");
 *			window.open(url);
 *		}
 *		currentview.returnCurrentView(callback);
 *
 */
function ImgCurrentView(viewer, opt){
    this.base = ViewerPlugin;
    this.base (viewer, name);
	
	if (opt==undefined) var opt={};
	
	this.opt = {} //set up options if not provided a default is given
	
	this.opt.wGobjects = (typeof opt.wGobjects === 'boolean')  ?  opt.wGobjects:true;
	this.opt.wBorders = (typeof opt.wBorders === 'boolean')  ?  opt.wBorders:false;
	this.opt.wScaleBar = (typeof opt.wScaleBar === 'boolean')  ?  opt.wScaleBar:true;
};

/*
*	drawGobjects
*
*	@param: canvas_view - 
*	@return - canvas with the gobject overlaid 
*/
ImgCurrentView.prototype.drawGobjects = function(canvas_view) {
	var logScale = this.getlogScale();
	var scale = Math.pow(2,logScale);
	var renderer = this.viewer.plugins_by_name['renderer'];
    gobject_view = renderer.getMergedCanvas();
    var ctx_view = canvas_view.getContext('2d');
	ctx_view.drawImage(gobject_view, 0, 0, scale*gobject_view.width,scale*gobject_view.height);
	return canvas_view;
};

/*
*	cropBorders
*
*	Removes the edges from the current view so only the image
*	is shown.
*
*	@param canvas_view - a canvas of the viewers current view
*	@return canvas containing only the tileviewer
*/
ImgCurrentView.prototype.cropBorders = function (canvas_view) {

	var logScale = this.getlogScale();
	var scale = Math.pow(2, logScale);
	var tiled_viewer = this.viewer.plugins_by_name['tiles'].tiled_viewer; //finding tiled viewer in the plug-in list
	
    var tile_height = parseInt(tiled_viewer.height);
    var tile_width = parseInt(tiled_viewer.width);
    var view_scale = this.viewer.view().scale;
	var width = Math.floor(tiled_viewer.image_size.width * view_scale); 
	var height = Math.floor(tiled_viewer.image_size.height * view_scale);
    var left = tiled_viewer.x; 
    var top = tiled_viewer.y; 
    
    var canvas_width = width;
	var canvas_height = height
    
    //crop left
	if (left>0) {
		var xoffset = -left;
	} else {
		var xoffset = 0;
		canvas_width = canvas_width + left;
	}
	
    //crop top
	if (top>0) {
		var yoffset = -top;
	} else {
		var yoffset = 0;
		canvas_height = canvas_height + top;
	}
	
    //crop bottom
	if ((top + canvas_height) > tile_height) {
		canvas_height = canvas_height - (top + height - tile_height);
	}
	
    //crop right
	if ((left + canvas_width) > tiled_viewer.width) {
		canvas_width = canvas_width - (left + width - tile_width);
	}
	
    //create cropped canvas
	var canvas_border = document.createElement('canvas');
	canvas_border.width = scale*canvas_width;
	canvas_border.height = scale*canvas_height;
    
    //apply image to cropped canvas
	var ctx_border = canvas_border.getContext('2d');
	ctx_border.drawImage(canvas_view, scale*xoffset, scale*yoffset, scale*tile_width, scale*tile_height);
	return canvas_border;
};

/*
*	drawScaleBar
*
*	If a scalebar is rendered over the tileviewer it will be rendered onto the
*	canvas just as it looks in the view
*
*	@param: canvas_view - a canvas of the viewers current view
*	@return: canvas with scalebar if provided
*/
ImgCurrentView.prototype.drawScaleBar = function(canvas_view) {

	//check is scale bar is in the image
	var scalebar = this.viewer.plugins_by_name['scalebar'];
	if (scalebar.scalebar) { //no scalebar found
		var scalebar_size = scalebar.scalebar.widget.getBoundingClientRect();
		var viewer_size = this.viewer.viewer_controls_surface.getBoundingClientRect();
        var tiled_viewer = this.viewer.plugins_by_name['tiles'].tiled_viewer;
		var viewer_top = tiled_viewer.y;
		var viewer_left = tiled_viewer.x;
		var viewer_right = viewer_left + tiled_viewer.width;
		var viewer_bottom = viewer_top + tiled_viewer.height;
		
		if (viewer_top - viewer_size.top <= scalebar_size.top - viewer_size.top &&
			viewer_left - viewer_size.left <= scalebar_size.left - viewer_size.left &&
			viewer_right - viewer_size.left >= scalebar_size.right - viewer_size.left &&
			viewer_bottom - viewer_size.top >= scalebar_size.bottom - viewer_size.top) {
			
			//check if image leave the view
			if (viewer_top < 0) {
				var offsetY = scalebar_size.top - viewer_size.top;
			} else {
				var offsetY = scalebar_size.top - viewer_top - viewer_size.top;
			}
			
			if (viewer_left < 0) {
				var offsetX = scalebar_size.left - viewer_size.left;
			} else {
				var offsetX = scalebar_size.left - viewer_left - viewer_size.left;
			}

			var logScale = this.getlogScale();
			var scale = Math.pow(2,logScale);
			var canvas_scalebar = scalebar.scalebar.renderCanvas(scale);
			var ctx_view = canvas_view.getContext('2d');
			ctx_view.globalAlpha = scalebar.scalebar.opacity;
			ctx_view.drawImage(canvas_scalebar, scale*offsetX, scale*offsetY, scale*scalebar_size.width, scale*scalebar_size.height);
		}
	}
	return canvas_view;
};

/*
*	getTilesInView
*
*	Looks into the tile viewer well to find elements that are in the current view
*	and returns a list of them
*
*	@return: list of elements from the well in the view
*/
ImgCurrentView.prototype.getTilesInView = function() {
	//iterate through all the tiles to find the tiles in the viewer
    var inViewImages = [];
	var control_surface_size = this.viewer.viewer_controls_surface.getBoundingClientRect();
	var tiled_viewer = this.viewer.plugins_by_name['tiles'].tiled_viewer; //finding tiled viewer in the plugin list
    for (var i = 0; i<tiled_viewer.well.childElementCount; i++) {
        var tile_size = tiled_viewer.well.children[i].getBoundingClientRect();
        if (
            //if edge
            ((tile_size.right <= control_surface_size.right && tile_size.right >= control_surface_size.left)||
            (tile_size.left >= control_surface_size.left && tile_size.left <= control_surface_size.right)) &&
            ((tile_size.bottom <= control_surface_size.bottom && tile_size.bottom >= control_surface_size.top) ||
            (tile_size.top >= control_surface_size.top && tile_size.top <= control_surface_size.bottom)) ||
            //if line
            (tile_size.right <= control_surface_size.right && tile_size.right >= control_surface_size.left &&
             tile_size.top <= control_surface_size.top && tile_size.bottom >= control_surface_size.bottom) ||
            (tile_size.bottom <= control_surface_size.bottom && tile_size.bottom >= control_surface_size.top &&
             tile_size.left <= control_surface_size.left && tile_size.right >= control_surface_size.right) ||
            (tile_size.left >= control_surface_size.left && tile_size.left <= control_surface_size.right &&
             tile_size.top <= control_surface_size.top && tile_size.bottom >= control_surface_size.bottom) ||
            (tile_size.top >= control_surface_size.top && tile_size.top <= control_surface_size.bottom &&
             tile_size.left <= control_surface_size.left && tile_size.right >= control_surface_size.right) ||
            //if inside
            (tile_size.right >= control_surface_size.right && tile_size.left <= control_surface_size.left &&
             tile_size.bottom >= control_surface_size.bottom && tile_size.top <= control_surface_size.top)

            ) {

            if (tiled_viewer.well.children[i].className == 'tile') {
                inViewImages.push(tiled_viewer.well.children[i]); //add to the list
            }
        }
    }
	return inViewImages;
};


/*
*	getCurrentLevel
*	
*	Checks the well for a tile with the level value and returns it
*
*	@return: level
*/
ImgCurrentView.prototype.getCurrentLevel = function() {
    var scale = this.viewer.view().scale;
    if (scale>1){ //if scale is greater than 1 no tile scaling is used any more
        var level = 0;
    } else {
        var level = Math.log(1/scale)/Math.log(2);
    }
	return level;
};

/*
*	setLevel
*
*	Sets the level for the current view. Level only scales up, must be in integer
*	and level must be greater then zero.
*
*	@param: level - the newly set level
*/
ImgCurrentView.prototype.setLevel = function(level) {
	if (level<0) var level = 0; //level cannot be below zero
	this.opt.level = level;
};

/*
*	getlogScale
*
*	@param: level
*	@return: log scale of level
*
*/
ImgCurrentView.prototype.getlogScale = function(level) {
	var currentLevel = this.getCurrentLevel();
	if (this.opt.level===undefined) this.opt.level = currentLevel;
	if (this.opt.level>=0) {
		var logScale = currentLevel - this.opt.level;
		if (logScale<0) var logScale = 0; //only scale up
	} else {
		this.opt.level = currentLevel;
		var logScale = 0;
	}
	return logScale;
};

//divides tiles into 4 quadrants scaling the tile up by one
/*
*	divideTile
*
*	Tries to break the tile into 4 quadrant unless a tile is outside of the image plan
* 	then no tile is returned for that region.
*
*	@param: tile - an element or an object in the format {style:{top,left},width,height}
*
*	@return: tiles of the same format 
*/
ImgCurrentView.prototype.divideTile = function(tile) {
	var tileviewer = this.viewer.plugins_by_name['tiles'].tiled_viewer;
	var yoffsetTile = parseInt(tile.style.top);
	var xoffsetTile = parseInt(tile.style.left);
	var scaled_imgwidth = tile.width;
	var scaled_imgheight = tile.height;	
	var src = tile.src;
	var u = parseUri(src);
	var url_query = u.query;
	var tile_args = url_query.match(/tile=(\d*),(\d*),(\d*),(\d*)/); //return the value only	
	var level = parseInt(tile_args[1]);
	var xtile = parseInt(tile_args[2]);
	var ytile = parseInt(tile_args[3]);
	var tiles_size = parseInt(tile_args[4]);
	var current_view_state = this.viewer.view();
	
	function createNewTile(xOffset, yOffset, width, height, lvl, xTile, yTile) {
		return {
			style : {
                top: yOffset, 
                left: xOffset
            },
			width: width,
			height: height,
			level: lvl,
			src: u.protocol+'://'+u.authority+u.path+'?'+url_query.replace(/tile=(\d*),(\d*),(\d*),/, 'tile=' + lvl + ','+ xTile +','+ yTile +','),
		};
	};
	
	//returning root level
	if (level<=this.opt.level) return [createNewTile(xoffsetTile, yoffsetTile, scaled_imgwidth, scaled_imgheight, level, xtile, ytile)];
	
	//drop a level and reducing the image into at most 4 smaller images
    var tiles = [];
	var level = level - 1;
	var xoffset = 2*xoffsetTile;
	var yoffset = 2*yoffsetTile;
    var scaleDiff = Math.pow(2,this.getCurrentLevel()-level);
    var xTileViewerOffset = scaleDiff*tileviewer.x;
    var yTileViewerOffset = scaleDiff*tileviewer.y;
    
    var current_view_state_width = current_view_state.width*scaleDiff;
    var current_view_state_height = current_view_state.height*scaleDiff;
    
	
	//top left
    if ((xoffset + tiles_size - xTileViewerOffset) < current_view_state_width) var scaled_imgwidth = tiles_size;
    else var scaled_imgwidth = current_view_state_width + xTileViewerOffset - xoffset;
    
    if ((yoffset + tiles_size - yTileViewerOffset) < current_view_state_height) var scaled_imgheight = tiles_size;
    else var scaled_imgheight = current_view_state_height + yTileViewerOffset - yoffset;
    
    tiles.push(createNewTile(xoffset, yoffset, scaled_imgwidth, scaled_imgheight, level, 2*xtile, 2*ytile));
    
    
	//top right
	if ((xoffset + tiles_size - xTileViewerOffset) < current_view_state_width) {
		if ((xoffset + 2*tiles_size - xTileViewerOffset) < current_view_state_width) var scaled_imgwidth = tiles_size;
		else var scaled_imgwidth = current_view_state_width + xTileViewerOffset - xoffset - tiles_size;
		
		if ((yoffset + tiles_size - yTileViewerOffset) < current_view_state_height) var scaled_imgheight = tiles_size;
		else var scaled_imgheight = current_view_state_height + yTileViewerOffset - yoffset;
		
		tiles.push(createNewTile(xoffset + tiles_size, yoffset, scaled_imgwidth, scaled_imgheight, level, 2*xtile+1, 2*ytile));
	}
	
	//bottom left 
	if ((yoffset + tiles_size - yTileViewerOffset) < current_view_state_height) {
		if (xoffset + tiles_size - xTileViewerOffset < current_view_state_width) var scaled_imgwidth = tiles_size;
		else var scaled_imgwidth = current_view_state_width + xTileViewerOffset - xoffset;
		
		if (yoffset + 2*tiles_size - yTileViewerOffset < current_view_state_height) var scaled_imgheight = tiles_size;
		else var scaled_imgheight = current_view_state_height + yTileViewerOffset - yoffset - tiles_size;	
		
		tiles.push(createNewTile(xoffset, yoffset + tiles_size, scaled_imgwidth, scaled_imgheight, level, 2*xtile, 2*ytile+1));
	}
	
	//bottom right
	if (
		((xoffset + tiles_size - xTileViewerOffset) < current_view_state_width ) &&
		((yoffset + tiles_size - yTileViewerOffset) < current_view_state_height)
	) {
		if (xoffset + 2*tiles_size - xTileViewerOffset < current_view_state_width) var scaled_imgwidth = tiles_size;
		else var scaled_imgwidth = current_view_state_width + xTileViewerOffset - xoffset - tiles_size;
		
		if (yoffset + 2*tiles_size - yTileViewerOffset < current_view_state_height) var scaled_imgheight = tiles_size;
		else var scaled_imgheight = current_view_state_height + yTileViewerOffset - yoffset - tiles_size;
		
		tiles.push(createNewTile(xoffset + tiles_size, yoffset + tiles_size, scaled_imgwidth, scaled_imgheight, level, 2*xtile+1, 2*ytile+1));
	}
	return tiles;
};


/*
*	returnCurrentView
*
*	Main function of imgcurrentview. Scales the image and adds gobject, crops,
*	and scalebar.
*
*	@param: cb - callback(canvas_view) function after the canvas has been returned 
*
*/
ImgCurrentView.prototype.returnCurrentView = function(cb) {
	
	var inViewImages = this.getTilesInView();
	var logScale = this.getlogScale();
	
    //create canvas
    var canvas_view = document.createElement('canvas');
	var control_surface_size = this.viewer.viewer_controls_surface.getBoundingClientRect();
    canvas_view.height = Math.pow(2,logScale)*control_surface_size.height;
    canvas_view.width = Math.pow(2,logScale)*control_surface_size.width;
    var ctx_view = canvas_view.getContext("2d");
    ctx_view.fillStyle = 'rgba(67, 67, 67, 1)'; //the background of the image
    ctx_view.fillRect(0, 0, canvas_view.width, canvas_view.height);

    
	//scaled images in view
	var inViewImagesScaled = [];
	while (inViewImages.length>0) {
		var tile = inViewImages.shift();
		var tileList = this.divideTile(tile);
		for (var t=0; t < tileList.length; t++) {
			if (tileList[t].level <= this.opt.level) { //done scaling the image
				inViewImagesScaled.push(tileList[t]);
			} else { //still needs to be scaled more levels
				inViewImages.push(tileList[t]);
			}
		}
	}
	
	var me = this;
	var request_queue = {}
	var count = 0;
	for (var i = 0; i < inViewImagesScaled.length; i++) {
		var img = new Image();
		img.yoffset = parseInt(inViewImagesScaled[i].style.top);
		img.xoffset = parseInt(inViewImagesScaled[i].style.left);
		img.scaled_imgwidth = inViewImagesScaled[i].width;
		img.scaled_imgheight = inViewImagesScaled[i].height;
		img.id = i;
		request_queue[i] = img;
		
		img.addEventListener("load", function() {
			ctx_view.drawImage( this, this.xoffset, this.yoffset, this.scaled_imgwidth, this.scaled_imgheight);
			delete request_queue[this.id];
			if (Object.getOwnPropertyNames(request_queue).length===0) {
				if (me.opt.wGobjects) canvas_view = me.drawGobjects(canvas_view);
				if (!me.opt.wBorders) canvas_view = me.cropBorders(canvas_view);
				if (me.opt.wScaleBar) canvas_view = me.drawScaleBar(canvas_view);
				if (cb) cb(canvas_view); //run call back
			}
		}.bind(img));
		
		img.addEventListener("error", function() { //error handling
            BQ.ui.error('Image did not return correctly');
		}.bind(img))
		img.src = inViewImagesScaled[i].src;
	
	}
	
};