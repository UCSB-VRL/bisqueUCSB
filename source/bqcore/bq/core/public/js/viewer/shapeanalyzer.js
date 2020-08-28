
function ShapeAnalyzer(){
}


// ----------------------------------------------------------------------------
ShapeAnalyzer.prototype.dsyev2 = function(M)
// ----------------------------------------------------------------------------
// Calculates the eigensystem of a real symmetric 2x2 matrix
//    [ A  B ]
//    [ B  C ]
// in the form
//    [ A  B ]  =  [ cs  -sn ] [ rt1   0  ] [  cs  sn ]
//    [ B  C ]     [ sn   cs ] [  0   rt2 ] [ -sn  cs ]
// where rt1 >= rt2. Note that this convention is different from the one used
// in the LAPACK routine DLAEV2, where |rt1| >= |rt2|.
// ----------------------------------------------------------------------------
{
    var A = M[0][0];
    var B = M[0][1];
    var C = M[1][1];
    var cs, sn, rt1, rt2;
    var SQR = function(x){return x*x};
    var sm = A + C;
    var df = A - C;
    var rt = Math.sqrt(SQR(df) + 4.0*B*B);
    var t;

    if (sm > 0.0)
    {
            rt1 = 0.5 * (sm + rt);
        t = 1.0/(rt1);
            rt2 = (A*t)*C - (B*t)*B;
    }
    else if (sm < 0.0)
    {
            rt2 = 0.5 * (sm - rt);
        t = 1.0/(rt2);
            rt1 = (A*t)*C - (B*t)*B;
    }
    else       // This case needs to be treated separately to avoid div by 0
    {
            rt1 = 0.5 * rt;
            rt2 = -0.5 * rt;
    }

    // Calculate eigenvectors
    if (df > 0.0)
        cs = df + rt;
    else
        cs = df - rt;

    if (Math.abs(cs) > 2.0*Math.abs(B))
    {
        t   = -2.0 * B / cs;
            sn = 1.0 / Math.sqrt(1.0 + SQR(t));
            cs = t * (sn);
    }
    else if (Math.abs(B) == 0.0)
    {
            cs = 1.0;
            sn = 0.0;
    }
    else
    {
        t   = -0.5 * (cs) / B;
            cs = 1.0 / Math.sqrt(1.0 + SQR(t));
            sn = t * (cs);
    }

    if (df > 0.0)
    {
        t   = cs;
            cs = -(sn);
            sn = t;
    }
    return {
        vals: [rt1, rt2],
        vecs:[[cs,sn],[sn,-cs]]
    };
};

ShapeAnalyzer.prototype.PCA = function(shape){
    var cen = [0,0];
    var bbcen = [0,0];

    var n = shape.length;
    var bb =
        bb = {min: [99999999,99999999], max: [-9999999,-9999999]};
    for(var i = 0; i < shape.length; i++){

        bb.min[0] = Math.min(bb.min[0], shape[i].x);
        bb.min[1] = Math.min(bb.min[1], shape[i].y);
        bb.max[0] = Math.max(bb.max[0], shape[i].x);
        bb.max[1] = Math.max(bb.max[1], shape[i].y);
    }

    bbcen[0] = 0.5*(bb.min[0] + bb.max[0]);
    bbcen[1] = 0.5*(bb.min[1] + bb.max[1]);


    var A = 0;

    for(var i = 0; i < shape.length; i++){
        var i_n = (i+1)%n;

        var p0 = {x: bbcen[0], y: bbcen[1]};;
        var p1 = shape[i];
        var p2 = shape[i_n];

        var Ai = 0.5*((p1.x-p0.x)*(p2.y-p0.y) - (p1.y-p0.y)*(p2.x-p0.x));
        A += Ai;
        cen[0] += Ai*shape[i].x;
        cen[1] += Ai*shape[i].y;
    }
    //cen[0] /= A;
    //cen[1] /= A;

    cen[0] = bbcen[0];
    cen[1] = bbcen[1];

    var M = [[0,0],[0,0]];
    for(var i = 0; i < shape.length; i++){
        var i_n = (i+1)%n;
        var p0 = {x: cen[0], y: cen[1]};;
        var p1 = shape[i];
        var p2 = shape[i_n];
        var Ai = 0.5*((p1.x-p0.x)*(p2.y-p0.y) - (p1.y-p0.y)*(p2.x-p0.x));
        var dx = (shape[i].x - cen[0]);
        var dy = (shape[i].y - cen[1]);
        //M[0][0] += 2*Ai/A*dx*dx;
        //M[0][1] += 2*Ai/A*dx*dy;

        //M[1][0] += 2*Ai/A*dy*dx;
        //M[1][1] += 2*Ai/A*dy*dy;

        M[0][0] += 2*dx*dx/n;
        M[0][1] += 2*dx*dy/n;

        M[1][0] += 2*dy*dx/n;
        M[1][1] += 2*dy*dy/n;
    }
    var L = this.dsyev2(M);

    L.width  = bb.max[0] - bb.min[0];
    L.height = bb.max[1] - bb.min[1];
    L.bbox = bb;
    L.area = A;
    L.vals[0] = Math.sqrt(L.vals[0]);
    L.vals[1] = Math.sqrt(L.vals[1]);
    L.center = cen;
    return L;
};

ShapeAnalyzer.prototype.projectToLine = function(points, eigs, Ls){
    //projects points to an axis aligned bounding defined by the eigenvalues and returns a variance score
    var c = eigs.center;
    var r = eigs.vals;
    var v = eigs.vecs;

    var dLine = function(p, x1, r){
        //distance from a line described by a point, p, and two points x1 and x2.
        var x2 = [x1[0] + r[0], x1[1] + r[1]];
        var num =
            (x2[0] - x1[0])*(x1[1] - p.y  ) -
            (x1[0] - p.x  )*(x2[1] - x1[1]);
        var den = (x2[0] - x1[0])*(x2[0] - x1[0]) + (x2[1] - x1[1])*(x2[1] - x1[1]);
        return num*num/den;
    };

    var dtotal = 0;

    for(var i = 0; i < points.length; i++){
        var p = points[i];
        var d = dLine(p, c, v[0]);
        dtotal += d;
    }
    dtotal /= points.length;
    return dtotal;
}

ShapeAnalyzer.prototype.projectToRect = function(points, eigs, layer, scale){

    //projects points to an axis aligned bounding defined by the eigenvalues and returns a score
    var Ls = [];
    for(var i = 0; i < 4; i++){
        var line = new Kinetic.Line({
            points: [],
            stroke: 'rgb(0,256,0)',
            strokeWidth: 4/scale,
        });
        Ls.push(line);
        layer.add(line);
    }
    var c = eigs.center;
    var r = eigs.vals;
    var v = eigs.vecs;
    var r0 = [r[0]*v[0][0], r[0]*v[0][1]];
    var r1 = [r[1]*v[1][0], r[1]*v[1][1]];

    var x0p = [c[0] + r0[0], c[1] + r0[1]];
    var x0m = [c[0] - r0[0], c[1] - r0[1]];

    var x1p = [c[0] + r1[0], c[1] + r1[1]];
    var x1m = [c[0] - r1[0], c[1] - r1[1]];

    var cp = [[0,0],[0,0],[0,0],[0,0]];
    var cBin = [[],[],[],[]];
    var dm = [0,0,0,0];
    var im = [0,0,0,0];

    var dLine = function(p, x1, r){
        //distance from a line described by a point, p, and two points x1 and x2.
        var x2 = [x1[0] + r[0], x1[1] + r[1]];
        var num =
            (x2[0] - x1[0])*(x1[1] - p.y  ) -
            (x1[0] - p.x  )*(x2[1] - x1[1]);
        var den = (x2[0] - x1[0])*(x2[0] - x1[0]) + (x2[1] - x1[1])*(x2[1] - x1[1]);
        return num*num/den;
    };

    /*
    var dLine = function(p, x1, x2){
        //distance from a line described by a point, p, and two points x1 and x2.
        var num =
            (x2[1] - x1[1])*p.x - (x2[0] - x1[0])*p.y + x2[0]*x1[1] - x2[1]*x1[0];
        var den = (x2[0] - x1[0])*(x2[0] - x1[0]) + (x2[1] - x1[1])*(x2[1] - x1[1]);
        return num*num/den;
    };*/

    var dProj = function(p, x1, r){
        //project a point, p onto a ray x1 and r(unit).
        //r us unit
        var v = [p[0] - x1[0], p[1] - x1[1]];
        var C =
            v[0]*r[0] + v[1]*r[1];
        var out = [x1[0] + C*r[0], x1[1] + C*r[1]];
        return out;
    };

    for(var i = 0; i < points.length; i++){
        var p = points[i];
        var d = [dLine(p, x1m, v[0]),
                 dLine(p, x1p, v[0]),
                 dLine(p, x0m, v[1]),
                 dLine(p, x0p, v[1])];

        var min0 = d[0] < d[1] ? 0 : 1;
        var min1 = d[2] < d[3] ? 2 : 3;
        var min = d[min0] < d[min1] ? min0 : min1;
        dm[min] += d[min]*d[min];
        cBin[min].push(p);
        cp[min][0] += p.x;
        cp[min][1] += p.y;
        im[min]++;
    }
    //console.log(im);
    /*
    if(Ls){
        Ls[0].points([x1m[0],x1m[1], x1m[0]+200*v[0][0], x1m[1]+200*v[0][1]]);
        Ls[1].points([x1p[0],x1p[1], x1p[0]+200*v[0][0], x1p[1]+200*v[0][1]]);
        Ls[2].points([x0m[0],x0m[1], x0m[0]+200*v[1][0], x0m[1]+200*v[1][1]]);
        Ls[3].points([x0p[0],x0p[1], x0p[0]+200*v[1][0], x0p[1]+200*v[1][1]]);
    }*/

    var cL = [];
    for (var i = 0; i < 4; i++){
        var pca = this.PCA(cBin[i]);
        cL.push(pca.vecs[0]);
        dm[i] /= im[i];
        var cpi = [0,0];
        for(var j = 0; j < cBin[i].length; j++){
            cpi[0] += cBin[i][j].x;
            cpi[1] += cBin[i][j].y;
        }
        cpi[0] /= cBin[i].length;
        cpi[1] /= cBin[i].length;

        cp[i][0] = cpi[0];
        cp[i][1] = cpi[1];
    }
    //var cpt = [];

    cp[0] = dProj(cp[0], c, v[1]);
    cp[1] = dProj(cp[1], c, v[1]);
    cp[2] = dProj(cp[2], c, v[0]);
    cp[3] = dProj(cp[3], c, v[0]);

    /*
    if(Ls){
        Ls[0].points([cp[0][0],cp[0][1], cp[0][0]+200*v[0][0], cp[0][1]+200*v[0][1]]);
        Ls[1].points([cp[1][0],cp[1][1], cp[1][0]+200*v[0][0], cp[1][1]+200*v[0][1]]);
        Ls[2].points([cp[2][0],cp[2][1], cp[2][0]+200*v[1][0], cp[2][1]+200*v[1][1]]);
        Ls[3].points([cp[3][0],cp[3][1], cp[3][0]+200*v[1][0], cp[3][1]+200*v[1][1]]);
    }
    */

    var dm = [0,0,0,0];
    var im = [0,0,0,0];
    for(var i = 0; i < points.length; i++){
        var p = points[i];
        var d = [dLine(p, cp[0], cL[0]),
                 dLine(p, cp[1], cL[1]),
                 dLine(p, cp[2], cL[2]),
                 dLine(p, cp[3], cL[3])];

        var min0 = d[0] < d[1] ? 0 : 1;
        var min1 = d[2] < d[3] ? 2 : 3;
        var min = d[min0] < d[min1] ? min0 : min1;
        dm[min] += d[min];
        im[min]++;
    }

    for (var i = 0; i < 4; i++){
        dm[i] /= im[i];
    }
    /*
    if(Ls){
        Ls[0].points([cp[0][0],cp[0][1], cp[0][0]+r[0]*cL[0][0], cp[0][1]+r[0]*cL[0][1]]);
        Ls[1].points([cp[1][0],cp[1][1], cp[1][0]+r[0]*cL[1][0], cp[1][1]+r[0]*cL[1][1]]);
        Ls[2].points([cp[2][0],cp[2][1], cp[2][0]+r[1]*cL[2][0], cp[2][1]+r[1]*cL[2][1]]);
        Ls[3].points([cp[3][0],cp[3][1], cp[3][0]+r[1]*cL[3][0], cp[3][1]+r[1]*cL[3][1]]);

    }*/

    //eigs.width =
    //console.log(cp);
    //eigs.width = cp[1][0] - cp[0][0];
    //eigs.height = cp[3][1] - cp[2][1];
    return dm[0] + dm[1] + dm[2] + dm[3];
}

ShapeAnalyzer.prototype.projectToEllipse = function(points, eigs, ellipse){
    var c = eigs.center;
    var r = eigs.vals;
    var v = eigs.vecs;
    var thetav = Math.atan2(v[0][0], v[0][1]);
    var d = 0;
    var ppoints = [];
    for(var i = 0; i < points.length; i++){
        var p = points[i];
        var x0 = [p.x - c[0], p.y - c[1]];
        var thetap = Math.atan2(x0[0], x0[1]);
        var dtheta = thetap - thetav;
        var cos2 = r[1]*Math.cos(dtheta);
        cos2*= cos2;
        var sin2 = r[0]*Math.sin(dtheta);
        sin2*= sin2;
        var k = 1/Math.sqrt(cos2 + sin2);
        var xp = [k*r[0]*r[1]*Math.cos(dtheta)*v[0][0] + k*r[0]*r[1]*Math.sin(dtheta)*v[0][1],
                  k*r[0]*r[1]*Math.cos(dtheta)*v[1][0] + k*r[0]*r[1]*Math.sin(dtheta)*v[1][1]];
        ppoints.push(xp[0], xp[1]);
        var thetac = Math.atan2(xp[0], xp[1]);
        var d2 =
            (x0[0] - xp[0])*(x0[0] - xp[0]) +
            (x0[1] - xp[1])*(x0[1] - xp[1]);
        d += d2;
    }
    if(ellipse)
        ellipse.points(ppoints);
    return d/points.length;
}


// Copyright 2000 softSurfer, 2012 Dan Sunday
// This code may be freely used, distributed and modified for any purpose
// providing that this copyright notice is included with it.
// SoftSurfer makes no warranty for this code, and cannot be held
// liable for any real or imagined damage resulting from its use.
// Users of this code must verify correctness for their application.


// a Point is defined by its coordinates {int x, y;}
//===================================================================


// isLeft(): tests if a point is Left|On|Right of an infinite line.
//    Input:  three points P0, P1, and P2
//    Return: >0 for P2 left of the line through P0 and P1
//            =0 for P2  on the line
//            <0 for P2  right of the line
//    See: Algorithm 1 "Area of Triangles and Polygons"
ShapeAnalyzer.prototype.isLeft = function( P0, P1, P2 )
{
    return ( (P1.x - P0.x) * (P2.y - P0.y)
             - (P2.x -  P0.x) * (P1.y - P0.y) );
}
//===================================================================


// cn_PnPoly(): crossing number test for a point in a polygon
//      Input:   P = a point,
//               V[] = vertex points of a polygon V[n+1] with V[n]=V[0]
//      Return:  0 = outside, 1 = inside
// This code is patterned after [Franklin, 2000]

ShapeAnalyzer.prototype.crossingNumberPointPoly = function ( P, V )
{
    var n = V.length;
    var    cn = 0;    // the  crossing number counter

    // loop through all edges of the polygon
    for (var i=0; i<n; i++) {    // edge from V[i]  to V[i+1]
        var ip1 = (i+1)%n;
        if (((V[i].y <= P.y) && (V[ip1].y > P.y))     // an upward crossing
            || ((V[i].y > P.y) && (V[ip1].y <=  P.y))) { // a downward crossing
            // compute  the actual edge-ray intersect x-coordinate
            var vt = (P.y  - V[i].y) / (V[ip1].y - V[i].y);
            if (P.x <  V[i].x + vt * (V[ip1].x - V[i].x)) // P.x < intersect
                ++cn;   // a valid crossing of y=P.y right of P.x
        }
    }
    return (cn&1);    // 0 if even (out), and 1 if  odd (in)

}
//===================================================================


// wn_PnPoly(): winding number test for a point in a polygon
//      Input:   P = a point,
//               V[] = vertex points of a polygon V[n+1] with V[n]=V[0]
//      Return:  wn = the winding number (=0 only when P is outside)

ShapeAnalyzer.prototype.windingNumberPointPoly = function( P, V )
{
    var n = V.length;
    var wn = 0;    // the  winding number counter

    // loop through all edges of the polygon
    for (var i=0; i<n; i++) {   // edge from V[i] to  V[i+1]
        var ip1 = (i+1)%n;
        if (V[i].y <= P.y) {          // start y <= P.y
            if (V[ip1].y  > P.y)      // an upward crossing
                if (this.isLeft( V[i], V[ip1], P) > 0)  // P left of  edge
                    --wn;            // have  a valid up intersect
        }
        else {                        // start y > P.y (no test needed)
            if (V[ip1].y  <= P.y)     // a downward crossing
                if (this.isLeft( V[i], V[ip1], P) < 0)  // P right of  edge
                    ++wn;            // have  a valid down intersect
        }
    }
    return wn;
}
//===================================================================
