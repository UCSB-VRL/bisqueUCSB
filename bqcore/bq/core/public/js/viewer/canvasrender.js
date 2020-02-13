
////////////////////////////////////////////////////////////////////
// check if you're on a mobile platform
////////////////////////////////////////////////////////////////////

window.mobileAndTabletcheck = function() {
  var check = false;
  (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))check = true})(navigator.userAgent||navigator.vendor||window.opera);
  return check;
}

window.mobilecheck = function() {
  var check = false;
  (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))check = true})(navigator.userAgent||navigator.vendor||window.opera);
  return check;
}

////////////////////////////////////////////////////////////////////
// ImageCache is a convenience object for handling
// a two dimensional array of image objects
// used for caching prerenderered nodes at given frames for
// time, t and depth, z.
////////////////////////////////////////////////////////////////////

function ImageCache(renderer){
    this.renderer = renderer;
    this.init();
};

ImageCache.prototype.init = function(){
    this.caches = {};
    this.nodeHashes = {};
};

ImageCache.prototype.getCurrentNodeHashes = function(node, shapeBbox){

    var z = this.renderer.viewer.tiles.cur_z;
    var t = this.renderer.viewer.tiles.cur_t;
    var bbox = node.bbox;

    var nHashes = [];
    var z0 = z;
    var z1 = z+1;
    var t0 = t;
    var t1 = t+1;

    if(shapeBbox){
        z0 = shapeBbox.min[2];
        z1 = shapeBbox.max[2]+1;
        t0 = shapeBbox.min[3];
        t1 = shapeBbox.max[3]+1;
    }

    for(var i  = z0; i < z1; i++)
        for(var j  = t0; j < t1; j++){
            var nHash =
                'mn: '  +  bbox.min[0] + "," + bbox.min[1] + "," + bbox.min[2] + "," +
                ' mx: ' +  bbox.max[0] + "," + bbox.max[1] + "," + bbox.max[2] + "," +
                ' z: '  + i + ', t: ' + j;
            nHashes.push(nHash);
        }

    var hashes = [];

    for(var i = 0; i < nHashes.length; i++){
        for (var key in this.nodeHashes[nHashes[i]]) {
            if (this.nodeHashes[nHashes[i]].hasOwnProperty(key)) {
                hashes.push(key);
            }
        }
    }
    return hashes;
}

ImageCache.prototype.getCurrentHash = function(node){
    var scale = this.renderer.stage.scale().x;

    var viewstate = this.renderer.viewer.current_view;
    var dim =       this.renderer.viewer.imagedim;
    var sz = dim.z;
    var st = dim.t;
    var z = this.renderer.viewer.tiles.cur_z;
    var t = this.renderer.viewer.tiles.cur_t;
    var maxLoc = sz*st;
    var loc = z + t*sz;
    var bbox = node.bbox;

    var proj = viewstate.imagedim.project,
    proj_gob = viewstate.gob_projection;



    var pHash = '';
    if (proj_gob==='all' || proj === 'projectmax' || proj === 'projectmin') {
        pHash = 'all';
    } else if (proj === 'projectmaxz' || proj === 'projectminz' || proj_gob==='Z') {
        pHash = 'Z';
    } else if (proj === 'projectmaxt' || proj === 'projectmint' || proj_gob==='T') {
        pHash = 'T';
    }
    var nHash =
        'mn: '  +  bbox.min[0] + "," + bbox.min[1] + "," + bbox.min[2] + "," +
        ' mx: ' +  bbox.max[0] + "," + bbox.max[1] + "," + bbox.max[2] + "," +
        ' z: '  + z + ', t: ' + t;

    var hash = nHash +','+ pHash + ', sc: ' + scale;
    if(!this.nodeHashes[nHash]) this.nodeHashes[nHash] = {};

    this.nodeHashes[nHash][hash] = hash;
    return hash;
}

ImageCache.prototype.createAtFrame = function(i,j){
    if(!this.caches[i]) this.caches[i] = [];

    if(window.location.hash == "#debug")
        this.caches[i][j] = new Kinetic.Image({stroke: 'red',
                                               strokeWidth: 2});
    else
        this.caches[i][j] = new Kinetic.Image({});
};

ImageCache.prototype.deleteAtFrame = function(i){

    if(this.caches[i]) {
        delete this.caches[i];
        this.caches[i] = null;
    }
};

ImageCache.prototype.getCacheAtFrame = function(i){
    return this.caches[i];
};

ImageCache.prototype.setPositionAtFrame = function(i, j, node, bbox){
    var
    cache = this.caches[i][j],
    scale = this.renderer.stage.scale().x,

    w = bbox.max[0] - bbox.min[0],
    h = bbox.max[1] - bbox.min[1],
    buffer = 0;

    cache.x(bbox.min[0] - buffer/scale);
    cache.y(bbox.min[1] - buffer/scale);
    cache.width(w + 2.0*buffer/scale);
    cache.height(h + 2.0*buffer/scale);
};

ImageCache.prototype.setImageAtFrame = function(i,j, img){
    this.caches[i][j].setImage(img);
};

ImageCache.prototype.createAtCurrent = function(node,j){
    var i = this.getCurrentHash(node);
    this.createAtFrame(i,j);
};

ImageCache.prototype.deleteAtCurrent = function(node){
    var i = this.getCurrentHash(node);
    this.deleteAtFrame(i);
}

ImageCache.prototype.getCacheAtCurrent = function(node){
    var i = this.getCurrentHash(node);
    return this.getCacheAtFrame(i);
}


ImageCache.prototype.setPositionAtCurrent = function(node, j, bbox){
    var i = this.getCurrentHash(node);
    this.setPositionAtFrame(i,j,node, bbox);
}

ImageCache.prototype.setImageAtCurrent = function(node,j,img){
    var i = this.getCurrentHash(node);
    this.setImageAtFrame(i,j,img);
}

ImageCache.prototype.clearAll = function(node, bbox){
    if(!node){
        delete this.caches;
        delete this.nodeHashes;
        this.init();
        return;
    }

    var nodeHashes = this.getCurrentNodeHashes(node, bbox);
    for(var i = 0; i < nodeHashes.length; i++){
        var hash = nodeHashes[i];
        delete this.caches[hash];
    }
}

function QuadTree(renderer, z, t){
    this.z = z;
    this.t = t;

    this.renderer = renderer;
    this.reset();
    this.maxChildren = 256;
    this.tilesPerNode = {x: 4, y: 4};

    this.imageCache = new ImageCache(renderer, this.tilesPerNode);
};

QuadTree.prototype.reset = function(){
    if(this.nodes){
        var collection = [];
        var collectLeaves = function(node){
            if(node.leaves.length > 0){
                collection = collection.concat(node.leaves);
            }
            return true;
        }
        this.traverseDown(this.nodes[0], collectLeaves);

        collection.forEach(function(e){
            e.inTree = false;
        });
    }
    var view = this.renderer.viewer.imagedim;
    if(!view)
        view = {x:0, y:0, z:0, t: 0};


    this.nodes = [{
        id: 0,
        parent: null,
        children:[],
        leaves: [],
        bbox: {min: [0,0,0,0], max: [view.x,view.y,view.z,view.t]},
        L: 0,
    }];

}

QuadTree.prototype.calcBoxVol = function(bb){
    //given two bounding boxes what is the volume
    var d = [0,0,0,0];
    for(var ii = 0; ii < 2; ii++){
        if(bb.max.length > ii)
            d[ii] = bb.max[ii] - bb.min[ii];
        //minimum distance is one unit
        d[ii] = Math.max(d[ii],1);
    }
    var vol = d[0]*d[1];

    return vol;
};

QuadTree.prototype.compositeBbox  = function(bbi,bbj){
    //given two bounding boxes what is the volume
    var
    min = [999999,999999,999999,999999],
    max = [-999999,-999999,-999999,-9999990];
    if(!bbi) debugger;
    if(!bbj) debugger;
    var N = Math.min(bbi.min.length, bbj.min.length);
    for(var i = 0; i < N; i++){

        min[i] = Math.min(bbi.min[i], bbj.min[i]);
        max[i] = Math.max(bbi.max[i], bbj.max[i]);
        min[i] = min[i] ? min[i] : 0;
        max[i] = max[i] ? max[i] : 0;
    }
    return {min:min, max:max};
};


QuadTree.prototype.calcBbox = function(gobs){
    //given a set of stored objects, find the maximum bounding volume
    var
    min = [9999999,9999999,9999999,9999999],
    max = [-9999999,-9999999,-9999999,-9999999];

    var nodei, nodej, maxVol = 0;

    if(!gobs) debugger;
    for(var i = 0; i < gobs.length; i++){
        var gbb = gobs[i].getBbox();
        var iiN = gbb.min.length;
        for(var ii = 0; ii < iiN; ii++){
            min[ii] = Math.min(min[ii], gbb.min[ii]);
            max[ii] = Math.max(max[ii], gbb.max[ii]);
            min[ii] = min[ii] ? min[ii] : 0;
            max[ii] = max[ii] ? max[ii] : 0;
        }
    }
    return {min: min, max: max};
};

QuadTree.prototype.findMaxVolPairs  = function(gobs){
    //given a set of stored objects, find the maximum bounding volume between pairs in the set
    //return an array of the two indices
    var nodei, nodej, maxVol = 0;
    for(var i = 0; i < gobs.length; i++){
        for(var j = i+1; j < gobs.length; j++){
            //if(i == j) continue;
            var ibb = gobs[i].getBbox();
            var jbb = gobs[j].getBbox();
            var cbb = this.compositeBbox(ibb,jbb);
            var vol = this.calcBoxVol(cbb);
            if(vol > maxVol){
                maxVol = vol;
                nodei = i;
                nodej = j;
            }
        }
    }
    return [gobs[nodei],gobs[nodej]];
};

QuadTree.prototype.hasOverlap  = function(bbox1, bbox2){
    var overlap = true,
    bb1 = bbox1,
    bb2 = bbox2;
    //for each dimension test to see if axis are seperate
    for(var i = 0; i < 4; i++){
        if      (bb1.max[i] <  bb2.min[i]) overlap = false;
        else if (bb1.min[i] >  bb2.max[i]) overlap = false;
    }
    //if(!overlap) debugger;
    return overlap;
};

QuadTree.prototype.calcVolumeChange  = function(obj, node){
    var nodebb = node.bbox;
    var compbb = this.compositeBbox(obj.bbox, nodebb);

    var nodeVol = this.calcBoxVol(nodebb);
    var compVol = this.calcBoxVol(compbb);
    return Math.abs(nodeVol - compVol);
}


QuadTree.prototype.traverseDownBB  = function(node, bb, func){
    var stack = [node];
    while(stack.length > 0){
        var cnode = stack.pop();
        if(!func(cnode)) continue;
        for (var i = 0; i < cnode.children.length; i++){
            var cbb = cnode.children[i].bbox;
            if(this.hasOverlap(bb, cbb))
                stack.push(cnode.children[i]);
        }
    }
};

QuadTree.prototype.traverseDown  = function(node, func){
    var stack = [node];
    while(stack.length > 0){
        var cnode = stack.pop();
        if(!func(cnode)) continue;
        for (var i = 0; i < cnode.children.length; i++){
            stack.push(cnode.children[i]);
        }
    }
};


QuadTree.prototype.traverseUp  = function(node, func){
    var stack = [node];
    while(stack.length > 0){
        var cnode = stack.pop();
        if(!func(cnode)) continue;
        if(cnode.parent){
            stack.push(cnode.parent);
        }
    }
};

QuadTree.prototype.allocateNode = function(){
    if(!this.currentAllocatedNode)
        this.currentAllocatedNode = this.nodes.length;

    var clength = 2*this.nodes.length;
    clength /= 2;
    if(this.currentAllocatedNode >= clength){
        this.nodes.length = 2*clength;
        for(var i = 0; i < clength; i++){
            this.nodes[clength + i] =
            {
                parent: null,
                children:[],
                leaves:[],
                bbox: {min:[0,0,0,0], max: [9999,9999,9999,9999]},
                L: -1
            };
        }
    }
    return this.nodes[this.currentAllocatedNode++];


}

QuadTree.prototype.splitNode  = function(node, stack){

    var nbb = node.bbox;
    var bbMin = [0,0,0];
    bbMin[0] = nbb.min[0];
    bbMin[1] = nbb.min[1];
    bbMin[2] = nbb.min[2];
    bbMin[3] = nbb.min[3];

    var bbw = nbb.max[0] - nbb.min[0];
    var bbh = nbb.max[1] - nbb.min[1];
    var bbz = nbb.max[2] - nbb.min[2];
    var bbt = nbb.max[3] - nbb.min[3];

    var mDim  = 0.5*Math.min(bbw, bbh);
    //var mDimZ = Math.min(bbz, bbt);
    //if(bbz === 1) mDimZ = bbt;
    //if(bbt === 1) mDimZ = bbz;
    var mDimZ = bbz <= 1 ? 1 : 0.5*bbz;
    var mDimT = bbt <= 1 ? 1 : 0.5*bbt;
    if( mDim/mDimZ < 5 ) var mDim = Math.min(mDim, mDimZ);

    //var K = (mDim === bbz || mDim === bbt) ? 1 : 2;
    var nXTiles = Math.max(bbw/mDim,1);
    var nYTiles = Math.max(bbh/mDim,1);
    var nZTiles = Math.max(bbz/mDimZ,1);
    var nTTiles = Math.max(bbt/mDimT,1);

    var tw = bbw/nXTiles; //tile width
    var th = bbh/nYTiles; //tile height
    var tz = bbz/nZTiles; //tile depth
    var tt = bbt/nTTiles; //tile depth

    if(!this.splits) this.splits = [];
    this.splits[node.L + 1] = [nXTiles, nYTiles, nZTiles, nTTiles];

    node.children = [];
    //debugger;
    for(var i = 0; i < nXTiles; i++){
        for(var j = 0; j < nYTiles; j++){
            for(var k = 0; k < nZTiles; k++){
                for(var l = 0; l < nTTiles; l++){

                    var ind = i + j*nXTiles + k*nXTiles*nYTiles + l*nXTiles*nYTiles*nZTiles;
                    /*
                    var newNode = {
                        parent: node,
                        children:[],
                        leaves:[],
                        bbox: {min:[0,0,0,0], max: [9999,9999,9999,9999]},
                        L: node.L+1
                    }
                    */
                    var newNode = this.allocateNode();
                    //node.children.push(newNode);
                    newNode.parent = node;
                    newNode.L = node.L+1;
                    var tMinX = bbMin[0] + i*tw;
                    var tMinY = bbMin[1] + j*th;
                    var tMinZ = bbMin[2] + k*tz;
                    var tMinT = bbMin[3] + l*tt;
                    newNode.bbox.min = [tMinX,      tMinY,      tMinZ,      tMinT];
                    newNode.bbox.max = [tMinX + tw, tMinY + th, tMinZ + tz, tMinT + tt ];
                    var id = this.nodes.length;
                    newNode.id = id;
                    if(window.location.hash == "#debug")
                        this.updateSprite(newNode);

                    node.children.push(newNode);
                    //this.nodes.push(newNode);
                }
            }
        }
    }

    for(var i = 0; i < node.leaves.length; i++){
        for(var j = 0; j < node.children.length; j++){
            var leaf = node.leaves[i];
            var cnode = node.children[j];
            if(leaf.hasOverlap(cnode.bbox)){
                var frame = {node: cnode, shape: leaf}
                stack.push(frame);
            }
        }
    }

    node.leaves = [];
};

QuadTree.prototype.calcMaxLevel = function(){
    this.maxLevel = 4;
    this.zoomLevel = 1;
    if(this.renderer.viewer.current_view){

        var view = this.renderer.viewer.current_view;
        var max = Math.max(view.width, view.height);
        this.zoomLevel = 4.0*512/max;
        var L = 0;

        while(max > 512){
            max /= 2;
            ++L;
        }
        this.maxLevel = L - 3;
    }
    return L - 3;
};

QuadTree.prototype.insertInNode  = function(gob, node, stack){
    var inSet = false;
    for(var i = 0; i < node.leaves.length; i++){
        if(gob.id() === node.leaves[i].id())
            inSet = true;
    }
    if(!inSet)
        node.leaves.push(gob);

    gob.page = node;
    //node.bbox = this.calcBbox(node.leaves);
    if(!this.maxLevel) this.calcMaxLevel();
    var maxLevel = this.maxLevel;
    var maxTileLevel = this.maxLevel;

    if((node.leaves.length >= this.maxChildren || node.L < maxTileLevel + 1)){
        this.splitNode(node, stack);
    }

    /*
    //make sure that the leaves are no larger than the client view
    var xc = this.renderer.viewer.tiles.div.clientWidth;
    var yc = this.renderer.viewer.tiles.div.clientHeight;
    var scale = Math.pow(2,node.L);
    var xn = (node.bbox.max[0] - node.bbox.min[0])*scale;
    var yn = (node.bbox.max[1] - node.bbox.min[1])*scale;

    //var fArea = this.calcBoxVol(this.renderer.viewFrustum);
    //var nArea = this.calcBoxVol(node.bbox);
    if(!node.children.length && xn*yn > 1.25*xc*yc){
        this.splitNode(node, stack);
    }
   */
};


QuadTree.prototype.insert = function(shape){
    //I like static integer pointer trees, but a dymanic pointer tree seems appropriate here, so
    // we can pull data on and off the tree without having to do our own
    //return;

    var z = this.renderer.viewer.tiles.cur_z;
    var t = this.renderer.viewer.tiles.cur_t;

    var view = this.renderer.viewer.imagedim;
    var nudge = 0.01;
    this.nodes[0].bbox = {
        min:[0,0,0,0],
        max: [view.x, view.y, view.z, view.t]
    };
    var stack = [{node: this.nodes[0], shape: shape}];

    //if(shape.id() === 15) debugger;
    //if(shape.page) return;  //if the shapeject has a page then we insert it
    //if(shape.inTree) return;
    shape.inTree = true;
    shape.bbox = shape.calcBbox(this.zoomLevel);

    //if(this.nodes.length > 10) return;
    var k = 0;
    while(stack.length > 0){
        k++;
        //if(l > 18) break;
        var frame = stack.pop();
        var fshape = frame.shape;
        var fnode = frame.node;
        fnode.dirty = true;
        this.imageCache.clearAll(fnode);
        //expand the bounding box of the current node on the stack
        //fnode.bbox = this.compositeBbox(shape.bbox, fnode.bbox);

        if(fnode.children.length === 0){

            if(fnode.leaves.length < this.maxChildren){
                this.insertInNode(fshape,fnode, stack);
            }
        }

        else{
            for(var i = 0; i < fnode.children.length; i++){
                var over = fshape.hasOverlap(fnode.children[i].bbox);
                if(over){

                    stack.push({node: fnode.children[i], shape: fshape});
                }
            }


        }
    }
};


QuadTree.prototype.remove = function(shape){
    var me = this;

    if(!shape || !shape.inTree) return;
    shape.inTree = false;
    var z = this.renderer.viewer.tiles.cur_z;
    var t = this.renderer.viewer.tiles.cur_t;

    //if(shape.id() === 15) debugger;
    var collection = [];
    var collectLeaves = function(node){
        if(node.leaves.length > 0)
            collection.push(node);
        return true;
    }
    this.traverseDownBB(this.nodes[0], shape.bbox, collectLeaves);

    for(var k = 0; k < collection.length; k++){
        var node = collection[k];
        var leaves = node.leaves;
        var pos = -1;
        for(var i= 0; i < leaves.length; i++){
            if(leaves[i].id() === shape.id()) pos = i;
        }
        if(pos > -1)
            leaves.splice(pos,1);
        //node.bbox = this.calcBbox(node.leaves);
        //this.updateSprite(node);
        //node = node.parent;

        while(node){
            //if(node.parent === null) break;
            if(!node.children)       continue;

            if(window.location.hash == "#debug")
                this.updateSprite(node);

            node.dirty = true;

            this.imageCache.clearAll(node, shape.bbox);
            node = node.parent;
            //
        }
        //shape.page = null;

    }
};


QuadTree.prototype.collectObjectsInRegion = function(frust, node){
    var me = this;
    var collection = [];
    var renderer = this.renderer;
    var z = this.renderer.viewer.tiles.cur_z;
    var t = this.renderer.viewer.tiles.cur_t;

    var collectSprite = function(node) {
        var leaf = null;
        if (node.leaves.length > 0) {
            for (var i=0; (leaf=node.leaves[i]); ++i) {
                if (leaf.collected || !leaf.isVisible(z, t)) continue;
                if (me.hasOverlap(frust, leaf.bbox)){
                    collection.push(leaf);
                    leaf.collected = true;
                }
            }
        }
        return true;
    };
    this.traverseDownBB(node, frust, collectSprite);
    collection.sort(function(a,b){
        var bbwa = a.bbox.max[0] - a.bbox.min[0];
        var bbha = a.bbox.max[1] - a.bbox.min[1];
        var bbwb = b.bbox.max[0] - b.bbox.min[0];
        var bbhb = b.bbox.max[1] - b.bbox.min[1];
        var aa = bbwa*bbha;
        var ab = bbwb*bbhb;
        if(aa === ab)
            return b.zindex - a.zindex;
        else
            return ab - aa;
    });
    var e = null;
    for (var i=0; (e=collection[i]); ++i) {
        e.collected = false;
    }
    return collection;
};

QuadTree.prototype.cull = function(frust){
    var me = this;
    var renderer = this.renderer;
    renderer.currentLayer.removeChildren();

    var leaves = this.collectObjectsInRegion(frust, this.nodes[0]);

    leaves.forEach(function(e){
        //e.setStroke();
        //if(e.text)
        //    renderer.currentLayer.add(e.text);
        //renderer.currentLayer.add(e.sprite);
        e.setLayer(renderer.currentLayer);
    });
    return leaves;
};


QuadTree.prototype.cache = function(frust, scale, onCache){
    var me = this;
    var fArea = this.calcBoxVol(frust);
    var me = this;
    var collection = [];
    var renderer = this.renderer;

    var cache = false;
    //var L = renderer.viewer.tiles.tiled_viewer.zoomLevel;

    //this.cachesDestroyed = 0;
    //this.cachesRendered = 0;

    var caching = false;
    var cacheSprite = function(node){
        var nArea = me.calcBoxVol(node.bbox);
        var cache = null;
        //if(L === node.L || node.leaves.length > 0){

        if(nArea <= 16.0*fArea || node.leaves.length > 0) {
            //if(!node.imageCache.getCacheAtCurrent()){

            if(!me.imageCache.getCacheAtCurrent(node)){
                //me.cachesDestroyed += 1;
                caching = true;
                me.cacheChildSprites(node, scale, onCache);
                cache = true;
                return false;
            }
            return false;
        }
        else return true;
    };
    this.traverseDownBB(this.nodes[0], frust, cacheSprite);
    if(!caching){
        onCache();
    }
};

QuadTree.prototype.cullCached = function(frust){
    var me = this;
    var fArea = this.calcBoxVol(frust);
    var me = this;
    var collection = [];
    var renderer = this.renderer;
    var scale = renderer.stage.scale().x;
    var cache = false;

    var z = this.renderer.viewer.tiles.cur_z;
    var t = this.renderer.viewer.tiles.cur_t;
    //var L = renderer.viewer.tiles.tiled_viewer.zoomLevel;

    var collectSprite = function(node){
        var nArea = me.calcBoxVol(node.bbox);
        var cache = null;
        //if(L === node.L || node.leaves.length > 0){
        if(nArea <= 16.0*fArea || node.leaves.length > 0) {

            cache = me.imageCache.getCacheAtCurrent(node);
            if(!cache) return false;

            for(var i = 0; i < cache.length; i++){
                if(!cache[i]) continue;
                var w = cache[i].width();
                var h = cache[i].height();
                var x = cache[i].x();
                var y = cache[i].y();
                var fnz = frust.min[2];
                var fnt = frust.min[3];
                var fxz = frust.max[2];
                var fxt = frust.max[3];

                var bb = {min: [x,y,fnz, fnt], max: [x+w,y+h,fxz, fxt]};
                if(me.hasOverlap(frust, bb)){
                    collection.push(cache[i]);
                }
            };
            return false;
        }

        else return true;
    };
    this.traverseDownBB(this.nodes[0], frust, collectSprite);
    renderer.currentLayer.removeChildren();
    collection.forEach(function(e){
        if(e)
            renderer.currentLayer.add(e);
    });
};



QuadTree.prototype.clearCache = function(frust){
    var me = this;
    this.imageCache.clearAll();
};

QuadTree.prototype.cacheScene = function(frust){
    var me = this;
    var fArea = this.calcBoxVol(frust);
    var collectSprite = function(node){
        var nArea = me.calcBoxVol(node.bbox);
        if(nArea < fArea) {
            me.cacheChildSprites(node);
            return false;
        }
        else return true;
    };
    this.traverseDownBB(this.nodes[0], frust, collectSprite);
};

QuadTree.prototype.cacheChildSprites = function(node, scale, onCache){
    //delete cache if it exists

    this.imageCache.deleteAtCurrent(node);

    //initialize a few variables;
    var me = this;
    var renderer = this.renderer;
    var bbox = node.bbox;
    var w = bbox.max[0] - bbox.min[0];
    var h = bbox.max[1] - bbox.min[1];

    var z = this.renderer.viewer.tiles.cur_z;
    var t = this.renderer.viewer.tiles.cur_t;

    var nbbox = {min: [bbox.min[0],bbox.min[1], z, t],
                 max: [bbox.max[0],bbox.max[1], z, t]};

    //console.log(bbox.min[2], bbox.max[2], z);

    node.scale = scale;
    var buffer = renderer.getPointSize();
    buffer = 0;


    //create a temp layer to capture the appropriate objects
    var nx = this.tilesPerNode.x;
    var ny = this.tilesPerNode.y;

    var bbw = bbox.max[0] - bbox.min[0];
    var bbh = bbox.max[1] - bbox.min[1];

    var tw = bbw/nx; //tile width
    var th = bbh/ny; //tile height

    for(var i = 0; i < nx; ++i){
        for(var j = 0; j < ny; ++j){
            var ind = i + j*nx;

            var tMinX = bbox.min[0] + i*tw;
            var tMinY = bbox.min[1] + j*th;

            var layer = new Kinetic.Layer({scale: {x:scale, y:scale},
                                           width: w,
                                           height: h});

            layer.removeChildren();
            var nbb =
            {min: [tMinX,      tMinY,      bbox.min[2], bbox.min[3]],
             max: [tMinX + tw, tMinY + th, bbox.max[2], bbox.max[3]]};
            var leaves = this.collectObjectsInRegion(nbb, node);
            leaves.forEach(function(e){
                //e.setStroke(1.0);
                e.updateLocal();
                e.getRenderableSprites().forEach(function(f){
                    layer.add(f);
                });
            });
            layer.draw();


            //create a new image, in the async callback assign the image to the node's imageCache
            //scale the image region

            var timeout = function(scope, cb){
                if(scope.timeout) clearTimeout(scope.timeout);
                scope.timeout = setTimeout(function(){
                    scope.cachesRendered = 0;
                    scope.cachesDestroyed = 0;
                   cb();
                }, 10);
            }

            var afterImage = function(img){
                //if(!node.dirty) return;
                //create a new image
                //this.imageCache.createAtCurrent(node);
                var scope = this.scope;
                this.node.image = img;
                scope.imageCache.createAtCurrent(this.node, this.index);
                scope.imageCache.setPositionAtCurrent(this.node, this.index, this.bbox);
                scope.imageCache.setImageAtCurrent(this.node, this.index, img);

                this.node.dirty = false;
                scope.cachesRendered += 1; //count the caches that have been rerendered since performing a cache call
                //console.log(img.src);
                timeout(scope, onCache);
            };

            var image = layer.toImage({
                callback: afterImage.bind({scope: this,
                                           index: ind,
                                           bbox: nbb,
                                           node: node}),
                x: nbb.min[0]*scale - buffer,
                y: nbb.min[1]*scale - buffer,
                width: tw*scale + 2.0*buffer,
                height:th*scale + 2.0*buffer,
            });
            //we have to do the timeout as well in case there is no image callback
            if(!image)
                timeout(this, onCache);

        }
    }

    //me.imageCache.setPositionAtCurrent(node);
};

QuadTree.prototype.setDirty = function(node){
    var me = this;
    var dirtFunc = function(node){
        node.dirty = true;
        return true;
    };
    this.traverseUp(node, dirtFunc);
};


QuadTree.prototype.updateSprite = function(node){
    var bbox = node.bbox;
    var w = bbox.max[0] - bbox.min[0];
    var h = bbox.max[1] - bbox.min[1];
    if(!node.sprite)
        node.sprite = new Kinetic.Rect({
            x: bbox.min[0],
            y: bbox.min[1],
            width: w,
            height: h,
            hasFill: false,
            listening: false,
            //fill: "rgba(128,128,128,0.2)",
            stroke: "rgba(128,255,255,0.4)",
            strokeWidth: 1.0,
        });

    node.sprite.x(bbox.min[0]);
    node.sprite.y(bbox.min[1]);
    node.sprite.width(w);
    node.sprite.height(h);
};


QuadTree.prototype.drawBboxes = function(frust){
    var me = this;

    var me = this;
    var collection = [];
    var renderer = this.renderer;
    var node = this.nodes[0];

    var collectSprite = function(node){
        if(node.sprite)
            me.renderer.currentLayer.add(node.sprite);
        return true;
    };

    this.traverseDownBB(node, frust, collectSprite);
};





////////////////////////////////////////////////////////////////
//Controller
////////////////////////////////////////////////////////////////

function CanvasControl(viewer, element) {
    this.viewer = viewer;

    if (typeof element == 'string')
        this.svg_element = document.getElementById(element);
    else
        this.svg_element = element;

    this.viewer.viewer.tiles.tiled_viewer.addViewerZoomedListener(this);
    this.viewer.viewer.tiles.tiled_viewer.addViewerMovedListener(this);
    this.viewer.viewer.tiles.tiled_viewer.addCursorMovedListener(this);
}

CanvasControl.prototype.setFrustum = function(e, scale){
     this.viewer.setFrustum(this.viewer.calcFrustum(e.x, e.y, scale));
};

CanvasControl.prototype.viewerMoved = function(e) {

    var scale = this.viewer.stage.scale();
    this.setFrustum(e, scale.x);

    this.viewer.stage.x(e.x);
    this.viewer.stage.y(e.y);
    var frust = this.viewer.viewFrustum;

    this.viewer.updateVisible();
    var me = this;

    if(0){
        var viewer = this.viewer;
        if(!viewer.frustRect){

            viewer.frustRect = new Kinetic.Rect({
                fill: 'rgba(200,200,200,0.1)',
                stroke: 'grey',
                strokeWidth: 1,
                listening: false,
            });

        }
        viewer.currentLayer.add(viewer.frustRect);
        var frust = this.viewer.calcFrustum(e.x, e.y, scale.x);

        viewer.frustRect.x(frust.min[0]);
        viewer.frustRect.y(frust.min[1]);
        viewer.frustRect.width(frust.max[0] - frust.min[0]);
        viewer.frustRect.height(frust.max[1] - frust.min[1]);
    }
    //this.viewer.draw();
    //this.viewer.stage.content.style.left = e.x + 'px';
    //this.viewer.stage.content.style.top = e.y + 'px';
};

CanvasControl.prototype.viewerZoomed = function(e) {
    //this.viewer.stage.content.style.left = e.x + 'px';
    //this.viewer.stage.content.style.top = e.y + 'px';

    this.viewer.stage.scale({x:e.scale,y:e.scale});
    this.setFrustum(e, e.scale);

    this.viewer.stage.x(e.x);
    this.viewer.stage.y(e.y);
    this.viewer.draw(true); //draw lower resolution annotation
    //this.viewer.currentLayer.removeChildren();

    this.viewer.updateVisible(150); //update visible has draw function
    //

    //this.viewer.draw();
};

CanvasControl.prototype.cursorMoved = function(e) {
    //if (this.viewer.mode !== 'navigate') return;

    var renderer = this.viewer,
        viewer = renderer.viewer,
        tiles = viewer.tiles,
        z = tiles.cur_z,
        t = tiles.cur_t,
        tpt = e;

    if (this.hoverTimeout)
        clearTimeout(this.hoverTimeout);

    this.hoverTimeout = setTimeout(function() {
        var shape = renderer.findNearestShape(tpt.x, tpt.y, z, t);
        if (shape) {
            viewer.parameters.onhover(shape.gob, e.event);
        } else {
            viewer.parameters.onhover(undefined, e.event);
        }
    }, 50);
};





////////////////////////////////////////////////////////////////
//interaction widgets
////////////////////////////////////////////////////////////////


function CanvasWidget(renderer) {
    this.renderer = renderer;
};

CanvasWidget.prototype.init = function(){};
CanvasWidget.prototype.update = function(shapes){};
CanvasWidget.prototype.select = function(shapes){};
CanvasWidget.prototype.unselect = function(shapes){};
CanvasWidget.prototype.destroy = function(shapes){};
CanvasWidget.prototype.toggle = function(fcn){};

function CanvasCorners(renderer) {
	this.renderer = renderer;
    this.name = 'corner';
    CanvasWidget.call(this, renderer);
};

CanvasCorners.prototype = new CanvasWidget();

CanvasCorners.prototype.update = function(){
    var me = this;
    var shapes = this.renderer.selectedSet;

    for(var i = 0; i < shapes.length; i++){
        shapes[i].updateCorners();
    }
};


CanvasCorners.prototype.toggle = function(fcn){

    this.update(this.renderer.selectedSet);
    if(this.manipulators)
        this.manipulators.forEach(function(e){
            e[fcn]();
        });
};


CanvasCorners.prototype.select = function(shapes){
    if(this.renderer.mode == 'navigate') return;

    if(this.renderer.selectedSet.length > 4) return;
    var me = this;
    this.manipulators = [];

    for(var i = 0; i < shapes.length; i++){
        var manipulators = shapes[i].getCornerManipulators();
        manipulators.forEach(function(e){
            me.renderer.editLayer.add(e);
        });
        this.manipulators = this.manipulators.concat(manipulators);
    }
    this.update(shapes);
};
/*
CanvasCorners.prototype.select = function(shapes){
    var manipMode = shapes.length > 1 ? 'multiple' : 'single';
    manipMode = shapes.length > 5 ? 'many' : manipMode;
    manipMode = this.renderer.viewer.parameters.showmanipulators ? 'multiple' : manipMode;

    var me = this;
    this.manipulators = [];

    for(var i = 0; i < shapes.length; i++){
        var manipulators = shapes[i].getManipulators(manipMode);
        manipulators.forEach(function(e){
            me.renderer.editLayer.add(e);
        });
        this.manipulators = this.manipulators.concat(manipulators);
    }
    this.update(shapes);
};
*/

CanvasCorners.prototype.unselect = function(shapes){
    if(this.renderer.mode == 'navigate') return;
    shapes.forEach(function(e,i,a){
        e.resetManipulators();
    });
};

CanvasCorners.prototype.destroy = function(shapes){

    if(this.manipulators){
        this.manipulators.forEach(function(e,i,d){
            e.remove(); //remove all current corners
            e.off('mousedown');
            e.off('dragmove'); //kill their callbacks
            e.off('mouseup');
        });
    }
}


function CanvasShapeColor(renderer) {
	this.renderer = renderer;
    this.name = 'shapecolor';
    CanvasWidget.call(this, renderer);
};

CanvasShapeColor.prototype = new CanvasWidget();

CanvasShapeColor.prototype.update = function(){
    var shapes = this.renderer.selectedSet;

    var me = this;
    for(var i = 0; i < shapes.length; i++){
        shapes[i].updateManipulators();
    }
};


CanvasShapeColor.prototype.toggle = function(fcn){

    this.update(this.renderer.selectedSet);
    if(this.manipulators)
        this.manipulators.forEach(function(e){
            e[fcn]();
        });
};

CanvasShapeColor.prototype.select = function(shapes){
    if(this.renderer.mode != 'edit') return;
    if(this.renderer.selectedSet.length > 4) return;

    var me = this;
    this.manipulators = [];

    for(var i = 0; i < shapes.length; i++){
        var manipulators = shapes[i].getColorManipulator();
        manipulators.forEach(function(e){
            me.renderer.editLayer.add(e);
        });
        this.manipulators = this.manipulators.concat(manipulators);
    }

    this.update(shapes);
};


CanvasShapeColor.prototype.unselect = function(shapes){
    if(this.renderer.mode == 'navigate') return;
    shapes.forEach(function(e,i,a){
        e.resetManipulators();
    });
};

CanvasShapeColor.prototype.destroy = function(shapes){
    if(this.manipulators){
        this.manipulators.forEach(function(e,i,d){
            e.remove(); //remove all current corners
            e.off('mousedown');
            e.off('dragmove'); //kill their callbacks
            e.off('mouseup');
        });
    }
}


function CanvasBbox(renderer) {
	this.renderer = renderer;
    this.name = 'bbox';
    CanvasWidget.call(this, renderer);
};

CanvasBbox.prototype = new CanvasWidget();

CanvasBbox.prototype.init = function(){
    this.bbRect = new Kinetic.Rect({
        fill: 'rgba(255,255,255,0.0)',
        stroke: 'grey',
        strokeWidth: 1,
        listening: false,
    });

    this.bbCorners = []
    for(var i = 0; i < 4; i++){
        this.bbCorners.push(
        new Kinetic.Rect({
            width: 6,
            height: 6,
            fill: 'grey',
            listening: true
        }));
    }

    this.bbCorners.forEach(function(e,i,d){
        e.setDraggable(true);
    });
};

CanvasBbox.prototype.update = function(){
    this.updateBbox(this.renderer.selectedSet);
}

CanvasBbox.prototype.editBbox = function(gobs,i, e) {
    //return;
    //this.renderer.updateManipulators(gobs);
    var scale = this.renderer.scale();

    var offx = 8/scale;
    var offy = 8/scale;

    var me = this;
    //var points = gobs.shape.getAttr('points');

   //ar x0 = shape.x();
    //var y0 = shape.y();
    var px0 = this.bbCorners[0].x() + offx/2;
    var py0 = this.bbCorners[0].y() + offy/2;
    var px1 = this.bbCorners[1].x() + offx/2;
    var py1 = this.bbCorners[1].y() + offy/2;
    var px2 = this.bbCorners[2].x() + offx/2;
    var py2 = this.bbCorners[2].y() + offy/2;
    var px3 = this.bbCorners[3].x() + offx/2;
    var py3 = this.bbCorners[3].y() + offy/2;
    var dx = e.evt.movementX;
    var dy = e.evt.movementY;
    var oCorner;

    if(i == 0){
        this.bbCorners[1].x(px0 - offx/2);
        this.bbCorners[2].y(py0 - offy/2);
        oCorner = [this.bbCorners[3].x() + offx/2,
                   this.bbCorners[3].y() + offy/2];

    }
    if(i == 1){
        this.bbCorners[0].x(px1 - offx/2);
        this.bbCorners[3].y(py1 - offy/2);
        oCorner = [this.bbCorners[2].x() + offx/2,
                   this.bbCorners[2].y() + offy/2];
    }
    if(i == 2){
        this.bbCorners[3].x(px2 - offx/2);
        this.bbCorners[0].y(py2 - offy/2);
        oCorner = [this.bbCorners[1].x() + offx/2,
                   this.bbCorners[1].y() + offy/2];

    }
    if(i == 3){
        this.bbCorners[2].x(px3 - offx/2);
        this.bbCorners[1].y(py3 - offy/2);
        oCorner = [this.bbCorners[0].x() + offx/2,
                   this.bbCorners[0].y() + offy/2];
    }

    var nWidth  = px3-px0;
    var nHeight = py3-py0;
    var sx = nWidth/this.bbRect.width();
    var sy = nHeight/this.bbRect.height();
    //var scale = this.stage.scale();
    //var off = 10/scale.x;

    this.bbRect.x(px0);
    this.bbRect.y(py0);
    this.bbRect.width(px3-px0);
    this.bbRect.height(py3-py0);


    gobs.forEach(function(shape,i,a){
        var sbbox = shape.getBbox();

        var sprite = shape.sprite;
        var x = shape.x();
        var y = shape.y();

        var sdx = x - oCorner[0];
        var sdy = y - oCorner[1];

        var nx = oCorner[0] + sx*sdx;
        var ny = oCorner[1] + sy*sdy;

        //KineticJS's scenegraph stretches shapes and outlines.
        //Manually resizing gobs then updating is simpler and I don't have to
        //worry about transforms

        shape.gob.vertices.forEach(function(v){
            var dx = v.x - x;
            var dy = v.y - y;
            v.x = nx + sx*dx;
            v.y = ny + sy*dy;
        });

        /* here is the code that uses KineticJS transform hierarchy
        sprite.scaleX(sprite.scaleX()*sx);
        sprite.scaleY(sprite.scaleY()*sy);

        sprite.x(oCorner[0] + sx*sdx);
        sprite.y(oCorner[1] + sy*sdy);
        */
        shape.dirty = true;
        shape.update();
        //var mx = 0.5*(px0 + px3);
        //var my = 0.5*(py0 + py3);
    });
};

CanvasBbox.prototype.updateBbox = function (gobs){

    //this.renderer.updateManipulators(gobs);

    var scale = this.renderer.scale();
    var min = [ 9999999, 9999999];
    var max = [-9999999,-9999999];

    for(var i = 0; i < gobs.length; i++){

        var shape = gobs[i];
        var bb = shape.getBbox();
        if(!bb) continue;
        min[0] = min[0] < bb.min[0] ? min[0] : bb.min[0];
        min[1] = min[1] < bb.min[1] ? min[1] : bb.min[1];

        max[0] = max[0] > bb.max[0] ? max[0] : bb.max[0];
        max[1] = max[1] > bb.max[1] ? max[1] : bb.max[1];
    }
    var pad = 8/scale;
    //pad the bbox
    min[0] -=  pad;
    min[1] -=  pad;
    max[0] +=  pad;
    max[1] +=  pad;

    var offx = 8/scale;
    var offy = 8/scale;

    this.bbRect.x(min[0]);
    this.bbRect.y(min[1]);

    this.bbWidth  = max[0] - min[0];
    this.bbHeight = max[1] - min[1];

    this.bbRect.width(this.bbWidth);
    this.bbRect.height(this.bbHeight);
    this.bbRect.strokeWidth(1.5/scale);

    this.bbCorners.forEach(function(e,i,a){
        e.width(offx);
        e.height(offy);
    });

    //offset the bbox vertices
    min[0] -= offx/2;
    min[1] -= offy/2;
    max[0] -= offx/2;
    max[1] -= offy/2;

    //console.log(scale, off);
    this.bbCorners[0].x(min[0]);
    this.bbCorners[0].y(min[1]);

    this.bbCorners[1].x(min[0]);
    this.bbCorners[1].y(max[1]);

    this.bbCorners[2].x(max[0]);
    this.bbCorners[2].y(min[1]);

    this.bbCorners[3].x(max[0]);
    this.bbCorners[3].y(max[1]);
    //this.updateDrawer();
};

CanvasBbox.prototype.select = function(gobs){
    var me = this;
    this.bbCorners.forEach(function(e,i,d){
        me.renderer.editLayer.add(e); //add corners

        e.on('mousedown', function(evt) {
            me.renderer.toggleWidgets('hide', 'bbox');
        });

        e.on('dragmove', function(evt) {
            me.editBbox(gobs,i,evt, e);
            e.moveToTop();

            me.renderer.editLayer.batchDraw(); // don't want to use default draw command, as it updates the bounding box
        });

        e.on('mouseup',function(evt){
            e.dirty = true;
            me.renderer.toggleWidgets('show', 'bbox');
            me.renderer.selectedSet.forEach(function(e,i,d){
                if(e.dirty)
                    me.renderer.move_shape(e.gob);
            });
        });
    });
    this.updateBbox(gobs);
    this.renderer.editLayer.add(this.bbRect);

}

CanvasBbox.prototype.unselect = function(gobs){

    this.bbCorners.forEach(function(e,i,d){
        e.remove(); //remove all current corners
        e.off('mousedown');
        e.off('dragmove');
        e.off('mouseup');
    });
};

CanvasBbox.prototype.destroy = function(gobs){

    this.bbCorners.forEach(function(e,i,d){
        e.remove(); //remove all current corners
        e.off('mousedown');
        e.off('dragmove');
        e.off('mouseup');
    });
};

CanvasBbox.prototype.toggle = function(fcn){
    this.updateBbox(this.renderer.selectedSet);
    this.bbCorners.forEach(function(e,i,a){
        e[fcn]();
    });

    this.bbRect[fcn]();

}



////////////////////////////////////////////////////////////////
//Renderer
////////////////////////////////////////////////////////////////


function CanvasRenderer (viewer,name) {
    var p = viewer.parameters || {};
    //this.default_showOverlay           = p.rotate          || 0;   // values: 0, 270, 90, 180

    this.default_showOverlay   = false;

    this.base = ViewerPlugin;
    this.base (viewer, name);
    this.events  = {};
    this.visit_render = new BQProxyClassVisitor (this);

    this.plug_ins = [];

    var me = this;
    if(viewer.parameters.render_plugins){
        viewer.parameters.render_plugins.forEach(function(e){
            if(e === 'color')
                me.plug_ins.push(new CanvasShapeColor(me));
            if(e === 'corners')
                me.plug_ins.push(new CanvasCorners(me));

            if(e === 'bbox')
                me.plug_ins.push(new CanvasBbox(me));
        });
    }
    else //default just loads corners.
        this.plug_ins.push(new CanvasCorners(this));

    //this.visit render

}
CanvasRenderer.prototype = new ViewerPlugin();

CanvasRenderer.prototype.focus = function (parent) {
    this.stage.content.focus();
};

CanvasRenderer.prototype.create = function (parent) {



    this.mousedownname   = 'mousedown';
    this.mouseupname   = 'mouseup';
    this.mousemovename = 'mousemove';
    //this.isMobile = window.mobileAndTabletcheck();
    this.isMobile = window.mobilecheck();

    if(this.isMobile){
        this.mousedownname = 'touchstart';
        this.mouseupname   = 'touchend';
        this.mousemovename = 'touchmove';
    }

    this.mode = 'navigate';
    this.shapes = {
        'ellipse': CanvasEllipse,
        'circle': CanvasCircle,
        'point': CanvasPoint,
        'polygon': CanvasPolyLine,
        'rectangle': CanvasRectangle,
        'square': CanvasSquare,
        'label': CanvasLabel,
    };

    // dima: kineticjs removes all other elements in the given container, create a wrapper for its sad sole existence
    this.wrapper = document.createElement("div");
    //this.wrapper.id =  'canvas_renderer_wrapper';
    this.wrapper.className = 'canvas_renderer_wrapper';
    this.wrapper.style.width = '100%';
    this.wrapper.style.height = '100%';
    parent.appendChild(this.wrapper);

    this.stage = new Kinetic.Stage({
        container: this.wrapper,
        listening: true,
    });

    this.stage._mousemove = Kinetic.Util._throttle( this.stage._mousemove, 10);
    this.stage.content.style.setProperty('z-index', 15);
    //this.stage.content.contentEditable=true;
    //this.stage.content.focus();


    this.initShapeLayer();
    this.initEditLayer();
    this.initSelectLayer();
    this.initPointImageCache();
    this.quadtree = new QuadTree(this);
    this.gobs = [];
    this.visitedFrame = [];
    this.selectedSet = [];
    this.cur_z = 0;


    return parent;
};


CanvasRenderer.prototype.initShapeLayer = function(){
    this.currentLayer = new Kinetic.Layer();
    this.defaultIntersection = this.currentLayer._getIntersection;
    this.noIntersection = function() {return {};};

    this.currentLayer._getIntersection = this.noIntersection;

    this.stage.add(this.currentLayer);
};

CanvasRenderer.prototype.initEditLayer = function(){
    var me = this;
    this.editLayer = new Kinetic.Layer();
    this.editLayer._getIntersection = this.noIntersection;

    this.stage.add(this.editLayer);
    this.editLayer.moveToTop();
    this.initUiShapes();
};

CanvasRenderer.prototype.initSelectLayer = function(){
    var me = this;
    this.selectLayer = new Kinetic.Layer();
    this.selectLayer._getIntersection = this.noIntersection;

    this.stage.add(this.selectLayer);
    this.selectLayer.moveToBottom();

    this.selectedSet = [];
    this.visibleSet = [];

    this.lassoRect = new Kinetic.Rect({
        fill: 'rgba(200,200,200,0.1)',
        stroke: 'grey',
        strokeWidth: 1,
        listening: false,
    });

    this.selectRect = new Kinetic.Rect({
        fill: 'rgba(0,0,0,0.0)',
        strokeWidth: 0,
        width: this.stage.width(),
        height: this.stage.height(),
        listening: true,
    });
    this.selectLayer.add(this.selectRect);

    var
    stage = this.stage,
    lassoRect = this.lassoRect;
    var mousemove = function(e) {
        if(me.mode != 'edit') return;
        var evt = e.evt;
        var scale = stage.scale();

        var stageX = stage.x();
        var stageY = stage.y();
        var x = evt.offsetX==undefined?evt.layerX:evt.offsetX;
        var y = evt.offsetY==undefined?evt.layerY:evt.offsetY;
        if(me.isMobile){
            x = evt.touches[0].clientX - evt.touches[0].radiusX/2;
            y = evt.touches[0].clientY - evt.touches[0].radiusY/2;
        }
        x = (x - stageX)/scale.x;
        y = (y - stageY)/scale.y;

        var x0 = lassoRect.x();
        var y0 = lassoRect.y();

        lassoRect.width((x - x0));
        lassoRect.height((y - y0));
        me.editLayer.draw();
    };
    var mousedown = function(e){
        if(me.mode != 'edit') return;
        me.unselect(me.selectedSet);

        var evt = e.evt;
        var scale = stage.scale();

        var stageX = stage.x();
        var stageY = stage.y();
        //var x = (evt.offsetX - stageX)/scale.x;
        //var y = (evt.offsetY - stageY)/scale.y;
        var x = evt.offsetX==undefined?evt.layerX:evt.offsetX;
        var y = evt.offsetY==undefined?evt.layerY:evt.offsetY;
        if(me.isMobile){
            x = evt.touches[0].clientX - evt.touches[0].radiusX/2;
            y = evt.touches[0].clientY - evt.touches[0].radiusY/2;
        }
        x = (x - stageX)/scale.x;
        y = (y - stageY)/scale.y;
        //console.log(evt);

        me.currentLayer.draw();
        me.editLayer.draw();
        me.selectedSet = []; //clear out current selection set

        me.editLayer.add(me.lassoRect);
        me.selectLayer.moveToTop();

        lassoRect.width(0);
        lassoRect.height(0);
        lassoRect.x(x);
        lassoRect.y(y);

        me.selectRect.on(me.mousemovename, mousemove);
    }

    var mouseup = function(e) {
        if(me.mode != 'edit') return;
        me.selectRect.off(me.mousemovename);
        me.lassoRect.remove();
        me.selectLayer.moveToBottom();

        var x0t = me.lassoRect.x();
        var y0t = me.lassoRect.y();
        var x1t = me.lassoRect.width() + x0t;
        var y1t = me.lassoRect.height() + y0t;

        var x0 = Math.min(x0t, x1t);
        var y0 = Math.min(y0t, y1t);
        var x1 = Math.max(x0t, x1t);
        var y1 = Math.max(y0t, y1t)
        var dx = x1 - x0;
        var dy = y1 - y0;
        if(dx*dy === 0) return;
        me.lassoSelect(x0,y0,x1,y1);
        me.select(me.selectedSet);
        me.default_select(me.selectedSet);
        me.editLayer.draw();

    } ;

    this.selectRect.on(this.mousedownname, mousedown);
    this.selectRect.on(this.mouseupname, mouseup);

    this.selectLayer.draw();
};

CanvasRenderer.prototype.lassoSelect = function(x0,y0, x1,y1){
    var me = this;
    /*
    var shapes = this.currentLayer.getChildren();
    shapes.forEach(function(e,i,d){
        var x = e.x();
        var y = e.y();
        if(!e.shape) return;
        var bbox = e.shape.getBbox();
        if(!bbox) return;
        if(bbox.min[0] > x0 && bbox.min[1] > y0 &&
           bbox.max[0] < x1 && bbox.max[1] < y1){
            me.addToSelectedSet(e.shape);
        }
    });
    */
    var node0 = this.quadtree.nodes[0];
    var shapes = this.quadtree.collectObjectsInRegion({min:[x0,y0],max:[x1,y1]},node0);
    shapes.forEach(function(e,i,d){
        var x = e.sprite.x();
        var y = e.sprite.y();
        //if(!e.shape) return;
        var bbox = e.getBbox();
        if(!bbox) return;
        if(bbox.min[0] > x0 && bbox.min[1] > y0 &&
           bbox.max[0] < x1 && bbox.max[1] < y1){
            me.addToSelectedSet(e);
        }
    });
}

CanvasRenderer.prototype.initUiShapes = function(){
    this.plug_ins.forEach(function(e){
        e.init();
    });



};

CanvasRenderer.prototype.scale = function (){
    return this.stage.scale().x;
};

CanvasRenderer.prototype.compareViewstate = function(vs0, vs1){
    return (vs0.x     === vs1.x &&
            vs0.y     === vs1.y &&
            vs0.scale === vs1.scale);
};

CanvasRenderer.prototype.draw = function (force){

    if(window.location.hash == "#debug")
        this.quadtree.drawBboxes(this.viewFrustum);

    //var viewstate = {scale : this.scale(), x: this.stage.x(), y: this.stage.y()};
    //if(!this.pastViewstate)
    //    this.pastViewstate = viewstate;
    //var cmp = this.compareViewstate(viewstate,this.pastViewstate);
    //if(!cmp || force)
        this.stage.draw();
    //this.pastViewstate = viewstate;
};

CanvasRenderer.prototype.updatePlugins = function(){
    this.plug_ins.forEach(function(e){
        e.update();
    });

};
CanvasRenderer.prototype.drawEditLayer = function (){
    this.updatePlugins();
    this.editLayer.draw();
};

CanvasRenderer.prototype.enable_edit = function (enabled) {

    this.viewer.current_view.edit_graphics = enabled?true:false;
    var gobs =  this.viewer.image.gobjects;
    //this.visit_render.visit_array(gobs, [this.viewer.current_view]);

    this.editLayer.moveToTop();
    this.rendered_gobjects = gobs;
};

CanvasRenderer.prototype.findNearestShape = function(x,y, z, t){
    //not really find nearest, rather find overlapping
    // dima: x and y are not scaled and thus w should not be rescaled
    var node = this.quadtree.nodes[0],
        //scale = this.stage.scale().x,
        w = 10, // dima: should be *scale not /scale;
        s = null,
        shapes = this.quadtree.collectObjectsInRegion(
            {min: [x-w, y-w, z-0.5, t-0.5],
             max: [x+w, y+w, z+0.5, t+0.5]}, node);

    for (var i=0; (s=shapes[i]); ++i) {
        if (s.isInside({x:x, y:y}))
            return s;
    }
    return null;
},

CanvasRenderer.prototype.getUserCoord = function (e ){
    var evt = e.evt ? e.evt : e;
    var x = evt.offsetX==undefined?evt.layerX:evt.offsetX;
    var y = evt.offsetY==undefined?evt.layerY:evt.offsetY;
    var scale = this.stage.scale();

    var stageX = this.stage.x();
    var stageY = this.stage.y();
    var x = (x - stageX);
    var y = (y - stageY);

    return {x: x, y: y};
	//return mouser.getUserCoordinate(this.svgimg, e);
    //the old command got the e.x, e.y and applied a transform to localize them to the svg area using a matrix transform.
};

CanvasRenderer.prototype.setMode = function (mode){
    var me = this;
    this.mode = mode;
    this.unselectCurrent();
    me.updateVisible(100);
    if(mode === 'add' || mode === 'delete' || mode === 'edit') {
        this.currentLayer._getIntersection = this.defaultIntersection;
        this.editLayer._getIntersection = this.defaultIntersection;
        this.selectLayer._getIntersection = this.defaultIntersection;

        this.lassoRect.width(0);
        this.lassoRect.height(0);
        this.selectLayer.moveToBottom();
        this.editLayer.moveToTop();
    }

    if(mode == 'navigate') {
        this.currentLayer._getIntersection = this.noIntersection;
        this.editLayer._getIntersection = this.noIntersection;
        this.selectLayer._getIntersection = this.noIntersection;
        this.lassoRect.width(0);
        this.lassoRect.height(0);
        this.selectLayer.moveToBottom();
        this.editLayer.moveToTop();
        if(this.editableObjects)
            for(var i = 0; i < this.editableObjects.length; i++){
                this.removeSpriteEvents(this.editableObjects[i]);
            }
    }


};

CanvasRenderer.prototype.addHandler = function (ty, cb){
    //console.log ("addHandler " + ty + " func " + cb);
    if (cb) {
        //tremovehis.svgimg.addEventListener (ty, cb, false);
        this.stage.on(ty,cb);
        this.events[ty] = cb;
    }else{
        this.stage.off(ty);
        //this.svgimg.removeEventListener (ty, this.events[ty], false);
    }
};

CanvasRenderer.prototype.setmousedown = function (cb ){
    this.addHandler (this.mousedownname, cb );
};

CanvasRenderer.prototype.setmouseup = function (cb, doadd ){
    this.addHandler (this.mouseupname, cb);
};

CanvasRenderer.prototype.setmousemove = function (cb, doadd ){
    var me = this;
    this.addHandler (this.mousemovename,cb );
};


CanvasRenderer.prototype.setdragstart = function (cb ){
    this.addHandler ("dragstart", cb );
};

CanvasRenderer.prototype.setdragmove = function (cb ){
    this.addHandler ("dragmove", cb );
};

CanvasRenderer.prototype.setdragend = function (cb ){
    this.addHandler ("dragend", cb );
};

CanvasRenderer.prototype.setclick = function (cb, doadd ){
    this.addHandler ("click", cb);
};

CanvasRenderer.prototype.setdblclick = function (cb, doadd ){
    this.addHandler ("dblclick", cb);
};

CanvasRenderer.prototype.setkeyhandler = function (cb, doadd ){
   var ty = 'keydown';
   if (cb) {
        document.documentElement.addEventListener(ty,cb,false);
        this.events[ty] = cb;
   } else {
       document.documentElement.removeEventListener(ty, this.events[ty],false);
   }
};

CanvasRenderer.prototype.newImage = function () {
    //var w = this.viewer.imagediv.offsetWidth;
    //var h = this.viewer.imagediv.offsetHeight;

    this.rendered_gobjects = [];
    if(!this.viewFrustum) this.initFrustum();
    this.quadtree.calcMaxLevel();

};

CanvasRenderer.prototype.updateView = function (view) {
    if (this.initialized) return;
    this.initialized = true;
//    this.loadPreferences(this.viewer.preferences);
//    if (this.showOverlay !== 'false')
//        this.populate_overlay(this.showOverlay);
};

CanvasRenderer.prototype.appendSvg = function (gob){
    if (gob.shape)
        this.svggobs.appendChild(gob.shape.svgNode);
};

CanvasRenderer.prototype.initFrustum = function(){

    if (!this.viewFrustum) {
        var scale = this.stage.scale().x;
        var w = this.viewer.tiles.tiled_viewer ? this.viewer.tiles.tiled_viewer.width : this.viewer.tiles.div.clientWidth;
        var h = this.viewer.tiles.tiled_viewer ? this.viewer.tiles.tiled_viewer.height : this.viewer.tiles.div.clientHeight;
        var x = w/scale;
        var y = h/scale;
        var z = 1;
        var t = 1;

        this.viewFrustum = {
            min: [0,0,z-0.5,t-0.5],
            max: [x,y,z+0.5,t+0.5]
        };
    }
};

CanvasRenderer.prototype.setFrustum = function(bb){
    if(!this.viewFrustum) this.initFrustum();
    if(!this.cursorRect)
        this.cursorRect = new Kinetic.Rect({
            //x: -20,
            //y: -20,
            width: 0,
            height: 0,
            fill: "rgba(128,255,128,0.2)",
            stroke: 'black',
            strokeWidth: 1,
        });
    //this.editLayer.add(this.cursorRect);
    this.viewFrustum.min[0] = bb.min[0];
    this.viewFrustum.min[1] = bb.min[1];
    this.viewFrustum.min[2] = bb.min[2];
    this.viewFrustum.min[3] = bb.min[3];

    this.viewFrustum.max[0] = bb.max[0];
    this.viewFrustum.max[1] = bb.max[1];
    this.viewFrustum.max[2] = bb.max[2];
    this.viewFrustum.max[3] = bb.max[3];

    this.cursorRect.x(bb.min[0]);
    this.cursorRect.y(bb.min[1]);
    this.cursorRect.width(bb.max[0] - bb.min[0]);
    this.cursorRect.height(bb.max[1] - bb.min[1]);
}

CanvasRenderer.prototype.cacheVisible = function(){
    this.quadtree.cacheScene(this.viewFrustum);
};

CanvasRenderer.prototype.getProjectionRange = function(zrange, trange){
    var viewstate = this.viewer.current_view;
    var dim = this.viewer.imagedim;

    var
    proj = viewstate.imagedim.project,
    proj_gob = viewstate.gob_projection;

    var
    z = dim.z,
    t = dim.t;

    if (proj_gob==='all' || proj === 'projectmax' || proj === 'projectmin') {
        trange[0] = 0;
        trange[1] = t;
        zrange[0] = 0;
        zrange[1] = z;
    } else if (proj === 'projectmaxz' || proj === 'projectminz' || proj_gob==='Z'){
        zrange[0] = 0;
        zrange[1] = z;
    } else if (proj === 'projectmaxt' || proj === 'projectmint' || proj_gob==='T') {
        trange[0] = 0;
        trange[1] = t;
    }
};

/*
CanvasRenderer.prototype.updateVisiblet = function(afterUpdate){
    var me = this;
    //console.log();
    if(this.uvTimeout) clearTimeout(this.uvTimeout);
    this.uvTimeout = setTimeout(function(){
        me.updateVisibleDelay();
        if(afterUpdate)
            afterUpdate();
    },1);

};*/

CanvasRenderer.prototype.startWait = function(fcn, delay){
    var me = this,
        el = this.viewer.viewer_controls_surface;

    if (el) {
        this.waiting = true;
        var waitCursor = function(){
            if (el) el.style.cursor = "wait";
            if (me.waiting){
                if(el) el.style.cursor = "wait";
                setTimeout(waitCursor, 100);
            } else{
                var pointer = PanoJS.GRAB_MOUSE_CURSOR;
                var move = PanoJS.GRABBING_MOUSE_CURSOR;
                var panojs = me.viewer.tiles.tiled_viewer;
                if(el) el.style.cursor = panojs.pressed ? move : pointer;

            }

        };
        waitCursor();
    }

    if(fcn){
        if(!delay)
            fcn();
        else
            setTimeout(fcn,delay);
    }
};


CanvasRenderer.prototype.endWait = function(){
    var me = this;
    this.waiting = false;
};

CanvasRenderer.prototype.updateVisible = function(delay){
    var me = this;
    //this.quadtree.cull(this.viewFrustum);
    var z = this.viewer.tiles.cur_z;
    var t = this.viewer.tiles.cur_t;

    var zrange = [z, z+1];
    var trange = [t, t+1];
    this.getProjectionRange(zrange, trange);
    var scale = this.scale();

    this.startWait(function(){
        if(me.mode == 'navigate'){
            me.quadtree.cache(me.viewFrustum, me.scale(), function(){
                me.quadtree.cullCached(me.viewFrustum);
                me.endWait();
                me.draw();
            });

            //this.quadtree.cache(this.viewFrustum);
            //this.quadtree.cullCached(this.viewFrustum);
        }
        else{
            //this.editableObjects = this.quadtree.cullLayers(this.viewFrustum);


            me.editableObjects = me.quadtree.cull(me.viewFrustum);
            for(var i = 0; i < me.editableObjects.length; i++){
                me.editableObjects[i].setStroke(1.0);
                me.addSpriteEvents(me.editableObjects[i]);
            }

            me.endWait();

            if(me.selectedSet.length > 0){
                me.unselect(me.selectedSet);
                me.select(me.selectedSet);
            }
            me.draw();
        }
    }, delay);
};

CanvasRenderer.prototype.resetTree = function (e) {
    //reset the quadtree and visible node references to tree
    this.visibleSet.forEach(function(e){
        e.page = null;
    });
    this.visibleSet =[]; //cleare the visible set.
    //quadtree reset
    this.quadtree.reset();
};

CanvasRenderer.prototype.calcFrustum = function(x,y, scale){
    var dim = this.viewer.imagedim,
    viewstate = this.viewer.current_view,
    z = this.viewer.tiles.cur_z,
    t = this.viewer.tiles.cur_t,
    sz = dim.z,
    st = dim.t,
    w = this.viewer.tiles.tiled_viewer ? this.viewer.tiles.tiled_viewer.width : this.viewer.imagediv.clientWidth,
    h = this.viewer.tiles.tiled_viewer ? this.viewer.tiles.tiled_viewer.height : this.viewer.imagediv.clientHeight,
    cw = w/scale,
    ch = h/scale,
    xp = x < 0 ? -x/scale : 0,
    yp = y < 0 ? -y/scale : 0,
    w = x < 0 ? dim.x + x/scale : cw - x/scale,
    h = y < 0 ? dim.y + y/scale : ch - y/scale;

    w = Math.min(cw, w);
    w = Math.min(dim.x, w);
    h = Math.min(ch, h);
    h = Math.min(dim.y, h);


    var
    tolerance_z = viewstate.gob_tolerance.z || 1.0,
    tolerance_t = viewstate.gob_tolerance.t || 1.0;

    var proj = viewstate.imagedim.project,
    proj_gob = viewstate.gob_projection;
    var z0 = z-0.5*tolerance_z;
    var z1 = z+0.5*tolerance_z;
    var t0 = t-0.5*tolerance_t;
    var t1 = t+0.5*tolerance_t;

    if (proj_gob==='all') {
        z0 = 0;
        z1 = sz;
        t0 = 0;
        t1 = st;
    } else if (proj === 'projectmaxz' || proj === 'projectminz' || proj_gob==='Z') {
        z0 = 0;
        z1 = sz;
    } else if (proj === 'projectmaxt' || proj === 'projectmint' || proj_gob==='T') {
        t0 = 0;
        t1 = st;
    } else if (proj === 'projectmax' || proj === 'projectmin') {
        z0 = 0;
        z1 = sz;
        t0 = 0;
        t1 = st;
    }

    if(0)
        return {
            min: [xp + 10,   yp + 10,   z0, t0],
            max: [xp+w - 10, yp+h - 10, z1, t1]
        };
    else

        return {
            min: [xp,   yp,   z0, t0],
            max: [xp+w, yp+h, z1, t1]
        };
}

CanvasRenderer.prototype.updateImage = function(e){
    var me = this;
    //console.log();
    if(this.uiTimeout) clearTimeout(this.uiTimeout);
    this.uiTimeout = setTimeout(function(){
        me.updateImageDelay(e);
    },20);

};


CanvasRenderer.prototype.updateImageDelay = function (e, fcn) {
    if(!this.viewer.imagedim) return;
    if(!this.viewer.tiles.tiled_viewer) return;

    var me = this;
    var viewstate = this.viewer.current_view;
    //var url = this.viewer.image_url();
    var scale = this.viewer.current_view.scale,
        tiled_viewer = this.viewer.tiles.tiled_viewer;

    var x = tiled_viewer.x;
    var y = tiled_viewer.y;
    var z = this.viewer.tiles.cur_z;
    var t = this.viewer.tiles.cur_t;

    this.gobsSlice = this.gobs[z];

    this.stage.scale({x: scale, y:scale});

    //this.initDrawer();
    /*
    if(this.selectedSet.length> 0){
        if(this.selectedSet[0].gob.vertices[0]){
            if(this.selectedSet[0].gob.vertices[0].z != z){
            }
        }
    }*/

    //this.unselect(this.selectedSet);
    //this.selectedSet = [];


    //this.stage.content.style.left = x + 'px';
    //this.stage.content.style.top = y + 'px';
    //var width = window.innerWidth;
    //var height = window.innerHeight;
    var frust = this.calcFrustum(x,y,scale);
    this.stage.x(x);
    this.stage.y(y);
    this.stage.setWidth(tiled_viewer.width);
    this.stage.setHeight(tiled_viewer.height);

    this.selectRect.width(this.viewer.tiles.pyramid.width);
    this.selectRect.height(this.viewer.tiles.pyramid.height);

    //this.stage.x(frust.min[0]);
    //this.stage.y(frust.min[1]);

    this.lassoRect.strokeWidth(1.0/scale);

    if(this.cur_z != z || this.cur_t != t){
        this.currentLayer.removeChildren();
    }
    this.cur_t = t
    this.cur_z = z;

    //dump the currently viewed objects
    //this.currentLayer.removeChildren();

    if(!this.addedListeners){
        this.addedListeners = true;
        this.myCanvasListener = new CanvasControl( this, this.stage );
    }
    this.setFrustum(frust);
    //this.myCanvasListener.setFrustum(e,scale);

    //get the gobs and walk the tree to rerender them
    //update visible objects in the tree... next iteration may be 3D.

    /*
    this.plug_ins.forEach(function(e){
        e.unselect(me.selectedSet);
    });

    this.plug_ins.forEach(function(e){
        e.select(me.selectedSet);
    });
    */
    this.updateVisible(300);
    me.unselect(me.selectedSet);
    me.select(me.selectedSet);
    //update visible has a draw call

    //this.draw();
};

CanvasRenderer.prototype.initPointImageCache = function () {
    var me = this;
    var point = new Kinetic.Circle({
            //radius: {x: rx, y: ry},
            x: 4,
            y: 4,
            fill:   'rgba(0,0,0,1.0)',
            stroke: 'rgba(255,255,255,0.5)',
            radius: 3,
            strokeWidth: 2,
        });
    var layer = new Kinetic.Layer({
        width: 8,
        height: 8
    }).add(point);
    layer.draw();

    this.pointImageCache;
    this.pointImageCacheOver;

    layer.toImage({
        callback: function(img){
            me.pointImageCache = img;
        }
    });
    point.fill('rgba(128,128,128,1.0)');
    layer.draw();

    layer.toImage({
        callback: function(img){
            me.pointImageCacheOver = img;
        }
    });
};

CanvasRenderer.prototype.mouseUp = function(){
    var me = this;
    this.endMove(this.selectedSet);
    this.selectedSet.forEach(function(e,i,d){
        me.move_poly(e.gob);
    });
};

CanvasRenderer.prototype.resetShapeCornerFill = function(){


    this.plug_ins.forEach(function(e,i,a){
        e.update();
    });
};

CanvasRenderer.prototype.resetSelectedSet = function(){
    this.selectedSet = [];
};


CanvasRenderer.prototype.removeFromSelectedSet = function(shape){
    var inSet = this.inSelectedSet(shape);
    if(inSet < 0) return;
    else {
        this.selectedSet.splice(inSet,1);
    }
    if(this.mode === 'navigate'){
        this.quadtree.remove(shape);
        shape.setStroke(1.0);
        this.quadtree.insert(shape);
        this.updateVisible(100);
    } else {
        this.quadtree.insert(shape);
        shape.setLayer(this.currentLayer);
        shape.sprite.moveToBottom();
        shape.resetManipulators();
    }
};

CanvasRenderer.prototype.addToSelectedSet = function(shape){
    var inSet = this.inSelectedSet(shape);
    if(inSet < 0)
        this.selectedSet.push(shape);
};

CanvasRenderer.prototype.inSelectedSet = function(shape){
    var inSet = -1;
    for(var i = 0; i < this.selectedSet.length; i++){
        //check _id for now, id() tries to fetch an attribute, which doesn't exist
        if(this.selectedSet[i].sprite._id === shape.sprite._id)
            inSet = i;
    }

    return inSet;
};

CanvasRenderer.prototype.initDrawer = function(){
    var me = this;
    if(!this.guidrawer)
        this.guidrawer = Ext.create('Ext.tip.Tip', {
		    anchor : this.viewer.viewer_controls_surface,
		    cls: 'bq-viewer-menu',

            header: {
                title: ' ',
                tools:[{
                    type: 'close',
                    handler: function(){
                        me.guidrawer.hide();
                    }
                }]},
            layout: {
                type: 'hbox',
                //align: 'stretch',
            },
            /*
              listeners: {
              close : function(){
              debugger;
              },
              show: function(){
              if(renderer.selectedSet.length === 0) this.hide();
              }
              },
            */
	    }).hide();
};

CanvasRenderer.prototype.updateDrawer = function(){
    if(!this.guidrawer) return;
    if(this.guidrawer.isHidden()) return;
    var xy0 = this.bbCorners[2].getAbsolutePosition();
    var xy1 = this.bbCorners[3].getAbsolutePosition();

    this.guidrawer.setWidth(xy1.x - xy0.x);
    this.guidrawer.setHeight(xy1.y - xy0.y);
    this.guidrawer.setX(xy0.x + 10);
    this.guidrawer.setY(xy0.y + 85);
};

CanvasRenderer.prototype.showDrawer = function(){
    if(!this.guidrawer) return;
    this.guidrawer.show();
    this.updateDrawer();
};

CanvasRenderer.prototype.hideDrawer = function(){
    if(!this.guidrawer) return;
    this.guidrawer.removeAll();
    this.guidrawer.hide();
};

CanvasRenderer.prototype.select = function (gobs) {
    var me = this;
    /*
    if(this.mode === 'navigate'){
        gobs.forEach(function(e){
            me.quadtree.remove(e);
            e.setStroke(2.0);
            me.quadtree.insert(e);
            me.updateVisible();
            //me.currentLayer.draw();

        });
        return;
    }
    */

    this.editLayer.removeChildren();

    //this.initManipulators(gobs);
    gobs.forEach(function(e,i,a){
        e.setLayer(me.editLayer);
        e.sprite.moveToBottom();
    });

    if(this.mode != 'add')
        this.plug_ins.forEach(function(e){
            e.select(gobs);
        });

    //this.showDrawer();
    this.currentLayer.draw();
    this.editLayer.draw();
};


CanvasRenderer.prototype.unselect = function (gobs) {
    //var shape = gobs.shape;
    var me = this;
    /*
    if(this.mode === 'navigate'){
        gobs.forEach(function(e){
            me.quadtree.remove(e);
            e.setStroke(1.0);
            me.quadtree.insert(e);
            me.updateVisible();

        });
        //return;
    }*/

    gobs.forEach(function(e,i,a){
        e.setLayer(me.currentLayer);
        e.sprite.moveToBottom();
        //e.resetManipulators();
    });

    this.plug_ins.forEach(function(e){
        e.unselect(gobs);
    });;
    /*
    if(this.manipulators){
        this.manipulators.forEach(function(e,i,d){
            e.remove(); //remove all current corners

        });
    }
    */
    this.selectedSet.forEach(function(e,i,d){
        if(e.dirty)
            me.move_shape(e.gob);
        me.quadtree.insert(e)
    });
    //this.hideDrawer();
    this.editLayer.removeChildren();
};

CanvasRenderer.prototype.destroy = function (gobs) {
    //var shape = gobs.shape;
    var me = this;
    this.plug_ins.forEach(function(e){
        e.destroy(gobs);
    });
    /*
    if(this.manipulators){
        this.manipulators.forEach(function(e,i,d){
            e.remove(); //remove all current corners
            e.off(this.mousedownname);
            e.off('dragmove'); //kill their callbacks
            e.off(this.mouseupname);
        });
    }
    */
    this.editLayer.removeChildren();

};


CanvasRenderer.prototype.unselectCurrent = function(){
    this.unselect(this.selectedSet);
    this.selectedSet = [];

};

CanvasRenderer.prototype.rerender = function (gobs, params) {
    if (!gobs)
        gobs = this.viewer.image.gobjects;
    if (!params)
        params = [this.viewer.current_view];

    var me = this;

    this.startWait(function(){
        me.visit_render.visit_array(gobs, params);
        me.endWait();

        me.quadtree.clearCache();
        me.updateVisible();
        me.draw();
    },100);

};

CanvasRenderer.prototype.visitall = function (gobs, show) {
    params = [this.viewer.current_view, show];
    this.visit_render.visit_array(gobs, params);
};

CanvasRenderer.prototype.is_selected = function (gob){
    if (gob.shape)
        return gob.shape.selected;
    return false;
};


//CanvasRenderer.prototype.set_hover_handler = function (callback){
    //this.select_callback = callback;
//};

CanvasRenderer.prototype.set_select_handler = function (callback){
    this.select_callback = callback;
};

CanvasRenderer.prototype.set_move_handler = function (callback){
    this.callback_move = callback;
};

CanvasRenderer.prototype.default_select = function (gob) {
    if (this.select_callback){
        this.select_callback(gob);
    }
};

CanvasRenderer.prototype.default_move = function (view, gob) {
    if (this.callback_move)
        this.callback_move(view, gob);
};


CanvasRenderer.prototype.toggleWidgets = function(fcn, exclude){
    this.plug_ins.forEach(function(e){
        if(e.name != exclude)
            e.toggle(fcn);
    });


    this.editLayer.draw();
    if(fcn === 'hide')
        //this.hideDrawer();
    if(fcn === 'show'){
        //this.showDrawer();
        //this.updateDrawer();
    }
};

CanvasRenderer.prototype.removeSpriteEvents = function(shape){
    var poly = shape.sprite;
    poly.off(this.mousedownname);
    poly.off('dragstart');
    poly.off('dragmove');
    poly.off('dragend');
    poly.off(this.mouseupname);

};

CanvasRenderer.prototype.addSpriteEvents = function(shape){
    var me = this;
    if(!this.dragCache) this.dragCache = [0,0];
    //poly.setDraggable(true);
    var polys = shape.getSprites();
    //if(!polys) polys = [shape.sprite]; // hack to work with single sprites

    var gob = shape.gob;
    polys.forEach(function(poly){
        poly.on(me.mousedownname, function(evt) {
            //select(view, gob);
            if(me.mode === 'delete' && shape.isDestroyed == false){
                //me.quadtree.remove(gob.shape);
                shape.isDestroyed = true;
                me.delete_fun(gob);
                return;
            }

            else if(me.mode != 'edit') return;

            evt.evt.cancelBubble = true;

            //poly.shape.clearCache();

            var inSet = me.inSelectedSet(gob.shape);

            if(inSet < 0){
                me.unselect(me.selectedSet);
                me.resetSelectedSet();
                me.selectedSet[0] = gob.shape;
            }

            poly.setDraggable(true);
            me.editLayer.moveToTop();

            me.mouseselect = true;
            me.select( me.selectedSet);
            me.default_select(me.selectedSet);

            var scale = me.stage.scale();
            me.dragCache[0] = evt.evt.offsetX/scale.x;
            me.dragCache[1] = evt.evt.offsetY/scale.y;

            //me.shapeCache = [];
            for(var j = 0; j < me.selectedSet.length; j++){
                me.selectedSet[j].dragStart();
                me.quadtree.remove(me.selectedSet[j]);
            };

            if(me.viewer.parameters.gobjectMoveStart)
                me.viewer.parameters.gobjectMoveStart(me.selectedSet);

        });

        poly.on('dragstart', function() {
            me.toggleWidgets('hide');
        });

        poly.on('dragmove', function(evt) {
            var scale = me.stage.scale();
            var pos = [evt.evt.offsetX/scale.x,
                       evt.evt.offsetY/scale.y];

            poly.shape.position.x = poly.x();
            poly.shape.position.y = poly.y();
            //console.log(pos, poly.x(), poly.y());
            var bbox, bboxCache, shape, shapeCache, gsprite, fsprite;
            var dxy = [0,0];
            for(var j = 0; j < me.selectedSet.length; j++){

                var
                fsprite = me.selectedSet[j],
                gsprite = gob.shape.sprite;

                fsprite.dirty = true;
                dxy[0] = pos[0] - me.dragCache[0];
                dxy[1] = pos[1] - me.dragCache[1];


                bbox = fsprite.bbox;
                bboxCache = fsprite.bboxCache;
                shapeCache = fsprite.spriteCache;

                bbox.min[0] = bboxCache.min[0] + dxy[0];
                bbox.max[0] = bboxCache.max[0] + dxy[0];
                bbox.min[1] = bboxCache.min[1] + dxy[1];
                bbox.max[1] = bboxCache.max[1] + dxy[1];

                if(fsprite._id != gsprite._id){
                    fsprite.x(shapeCache[0] + dxy[0]);
                    fsprite.y(shapeCache[1] + dxy[1]);
                }
            }
            //me.updateBbox(me.selectedSet);
            if(this.shape.selfAnchor)
                this.shape.drag(evt,this);
            //me.currentLayer.draw();
            if(me.viewer.parameters.gobjectMove)
                me.viewer.parameters.gobjectMove(me.selectedSet);
            me.editLayer.draw();
        });

        poly.on('dragend', function() {
            me.toggleWidgets('show');
        });

        poly.on(me.mouseupname, function() {
            poly.setDraggable(false);

            me.selectedSet.forEach(function(e,i,d){
                if(e.dirty)
                    me.move_shape(e.gob);

                //me.quadtree.in(f);
                me.quadtree.insert(e)
            });
            if(me.viewer.parameters.gobjectMoveEnd)
                me.viewer.parameters.gobjectMoveEnd(me.selectedSet);

            //me.selectedSet.forEach(function(e,i,d){
            //     me.move_shape(e.gob);
            //});
        });

    });

};

CanvasRenderer.prototype.viewShape = function (gob, move, select){
    var me = this;
    var r = this;
    var g = gob;
    if(!gob.shape) return;
    var poly = gob.shape.sprite;
    //this.currentLayer.add(poly);
    var dragMove = false;
    var dragStart = false;
    var dragEnd = false;

    //this.addSpriteEvents(poly, gob);
    //if(gob.shape.text)
    //    this.addSpriteEvents(gob.shape.text, gob);

    /*
    this.appendSvg ( gob );
    gob.shape.init(svgNode);
    gob.shape.update_callback = move;
    gob.shape.select_callback = select;
    gob.shape.callback_data = { view:view, gob:g };
    gob.shape.show(true);
    if (view.edit_graphics === true)
        gob.shape.realize();
    gob.shape.editable(view.edit_graphics);
    */
} ;

CanvasRenderer.prototype.hideShape = function (gobs, view) {
    if (!Array.isArray(gobs)) gobs = [gobs];
    var gob = null,
        shape = null,
        i=0;

    this.destroy(this.selectedSet);
    this.selectedSet = [];
    for (i=0; (gob=gobs[i]); ++i) {
        shape = gob.shape;
        if (shape) {
            this.removeSpriteEvents(shape);
            shape.sprite.hide();
            shape.destroy();
            delete shape;
        }
    }
    this.draw();
};

CanvasRenderer.prototype.highlight = function (gob, selection) {
    // visitall to enhance on the node and its children
    var me = this;


        if(!selection){
            me.removeFromSelectedSet(gob.shape);
        }
        else {
            visit_all(gob, function(g, args) {
                if (g.shape)
                    me.addToSelectedSet(g.shape);
            }, selection );
        }
        me.select(me.selectedSet);
    /*
    if(this.highTimeout) clearTimeout(this.highTimeout);
    this.highTimeout = setTimeout(highlight, 1);
    */
};

CanvasRenderer.prototype.setcolor = function (gob, color) {
    // visitall to enhance on the node and its children
    visit_all(gob, function(g, args) {
            g.color_override = args[0];
    }, color );
    //this.rerender([this.viewer.current_view, true]);
};

/*
CanvasRenderer.prototype.removeFromLayer = function (gobShape) {

};
*/
//----------------------------------------------------------------------------
// graphical primitives
//----------------------------------------------------------------------------


////////////////////////////////////////////////////////////
CanvasRenderer.prototype.makeShape = function ( gob,  viewstate, shapeDescription, visibility) {
    if(!gob.vertices[0]) return;
    var z = this.viewer.tiles.cur_z;

    visibility = typeof visibility == 'undefined' ? true : visibility;

    if(gob.shape){ //JD:Don't completely understand deleting process, but: for now deferred cleanup
        if(gob.shape.isDestroyed) {
            var shape = gob.shape
            delete shape;
            gob.shape = undefined;
            return;
        }
    }

    if (gob.shape == null ) {
        var poly = new this.shapes[shapeDescription](gob, this);
        gob.shape.viewstate = viewstate;
        gob.shape = poly;

        this.viewShape (gob,
                        callback(this,'move_shape'),
                        callback(this,'select_shape'));

    }
    gob.shape.visibility = visibility;

    if(!visibility) {
        this.quadtree.remove(gob.shape);
    } else{
        gob.shape.update();
        this.quadtree.insert(gob.shape);
    }

    if(gob.dirty)
        this.stage.draw();
};


CanvasRenderer.prototype.move_shape = function ( gob ) {
    gob.shape.move();
    this.default_move(gob);
};

CanvasRenderer.prototype.select_shape = function ( view, gob ) {
    //var gob = state.gob;
    this.default_select(view, gob);
};

////////////////////////////////////////////////////////////
// individual primitives
////////////////////////////////////////////////////////////

CanvasRenderer.prototype.polygon = function (visitor, gob , viewstate, visibility) {
    this.polyline (visitor, gob, viewstate, visibility);
    if (gob.shape)
        gob.shape.closed(true);
};

CanvasRenderer.prototype.polyline = function (visitor, gob,  viewstate, visibility) {
    this.makeShape(gob, viewstate, 'polygon', visibility);
};

CanvasRenderer.prototype.line = function (visitor, gob , viewstate, visibility) {
    this.polyline (visitor, gob, viewstate, visibility);
    if(gob.shape)
        gob.shape.closed(false);
};

CanvasRenderer.prototype.ellipse = function ( visitor, gob,  viewstate, visibility) {
    this.makeShape(gob, viewstate, 'ellipse', visibility);
};

CanvasRenderer.prototype.circle = function (visitor, gob,  viewstate, visibility) {
    this.makeShape(gob, viewstate, 'circle', visibility);
};

CanvasRenderer.prototype.rectangle = function (visitor, gob,  viewstate, visibility) {
    this.makeShape(gob, viewstate, 'rectangle', visibility);
};


CanvasRenderer.prototype.square = function (visitor, gob,  viewstate, visibility) {
    this.makeShape(gob, viewstate, 'square', visibility);
};

CanvasRenderer.prototype.point = function (visitor, gob,  viewstate, visibility) {
    this.pointSize = 5.0; //3.5;
    this.makeShape(gob, viewstate, 'point', visibility);
    if(gob.shape)
        gob.shape.setPointSize(this.pointSize);

};

CanvasRenderer.prototype.label = function (visitor, gob,  viewstate, visibility) {
    this.makeShape(gob, viewstate, 'label', visibility);
};

CanvasRenderer.prototype.getPointSize = function () {
    return this.pointSize;
};

CanvasRenderer.prototype.getMergedCanvas = function () {
    this.unselectCurrent();
    return this.currentLayer.canvas._canvas;
};

/*
///////////////////////////////////////
// LABEL is not really implemented .. need to extend 2D.js
// with SVG Text tag

CanvasRenderer.prototype.label = function ( visitor, gob, viewstate, visibility) {

    // Visibility of this gob (create/destroy gob.shape)
    // Create or destroy SVGElement for 2D.js
    // Update SVGElement with current view state ( scaling, etc )

    // viewstate
    // scale  : double (current scaling factor)
    // z, t, ch: current view planes (and channels)
    // svgdoc : the SVG document
    var offset_x  = viewstate.offset_x;
    var offset_y  = viewstate.offset_y;
    var pnt = gob.vertices[0];

    var visible = test_visible(pnt, viewstate);

    if (visibility!=undefined)
    	gob.visible=visibility;
    else if (gob.visible==undefined)
    	gob.visible=true;

    var label_text = gob.value || 'My label';

    if (visible && gob.visible) {
        if (gob.shape == null ) {
            var rect = document.createElementNS(svgns, "text");
            var innertext = document.createTextNode(label_text);
            rect.appendChild(innertext);
            rect.setAttributeNS(null, 'fill-opacity', 0.9);
            rect.setAttributeNS(null, "stroke", "black");
            rect.setAttributeNS(null, 'stroke-width', '0.5px');
            rect.setAttributeNS(null, 'stroke-opacity', 0.0);
            rect.setAttributeNS(null, 'font-size', '18px');
            rect.setAttributeNS(null, 'style', 'text-shadow: 1px 1px 4px #000000;');
            gob.shape = new Label(rect);
        }

		// scale to size
        var p = viewstate.transformPoint (pnt.x, pnt.y);
        var rect = gob.shape.svgNode;
		rect.setAttributeNS(null, "x", p.x);
		rect.setAttributeNS(null, "y", p.y);
        if (gob.color_override)
            rect.setAttributeNS(null, "fill", '#'+gob.color_override);
        else
            rect.setAttributeNS(null, "fill", "white");
        this.viewShape (viewstate, gob,
                        callback(this,"move_label"),
                        callback(this,"select_label"));

    } else {
        this.hideShape (gob, viewstate);
    }
};

CanvasRenderer.prototype.move_label = function (state){
    var gob = state.gob;
    var v   = state.view;
    //gob.shape.refresh();
    var x = gob.shape.svgNode.getAttributeNS(null,"x");
    var y = gob.shape.svgNode.getAttributeNS(null,"y");

    var newpnt = v.inverseTransformPoint (x, y);
    var pnt = gob.vertices[0] ;
    pnt.x = newpnt.x;
    pnt.y = newpnt.y;
    this.default_move(gob);
};

CanvasRenderer.prototype.select_label = function (state){
    var gob = state.gob;
    this.default_select(gob);
};
*/
