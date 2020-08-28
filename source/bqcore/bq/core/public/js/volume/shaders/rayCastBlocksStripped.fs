/*******************************************************************************

@Author John Delaney


*******************************************************************************/

/*
LICENSE

Center for Bio-Image Informatics, University of California at Santa Barbara

Copyright (c) 2007-2014 by the Regents of the University of California
All rights reserved

Redistribution and use in source and binary forms, in whole or in parts, with or without
modification, are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright
    notice, this list of conditions, and the following disclaimer.

    Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions, and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.

    Use or redistribution must display the attribution with the logo
    or project name and the project URL link in a location commonly
    visible by the end users, unless specifically permitted by the
    license holders.

THIS SOFTWARE IS PROVIDED BY THE REGENTS OF THE UNIVERSITY OF CALIFORNIA ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OF THE UNIVERSITY OF CALIFORNIA OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifdef GL_ES
precision highp float;
#endif

#define M_PI 3.14159265358979323846

uniform vec2 iResolution;

uniform vec3 BOX_SIZE;

uniform int setMaxSteps;

uniform int RED_CHANNEL;
uniform int GREEN_CHANNEL;
uniform int BLUE_CHANNEL;

uniform int   DITHERING;
uniform int   DITHER_SPACE;
uniform int   DITHER_LIGHTING;

uniform float GAMMA_MIN;
uniform float GAMMA_MAX;
uniform float GAMMA_SCALE;
uniform float brightness;
uniform float density;

//uniform sampler2D backGround;

uniform sampler2D textureAtlas;
uniform sampler2D transfer;
uniform int TRANSFER_SIZE;
uniform int USE_TRANSFER;

uniform sampler2D BACKGROUND_DEPTH;
uniform sampler2D BACKGROUND_COLOR;


//uniform sampler2D dataBase1[1];

uniform int TEX_RES_X;
uniform int TEX_RES_Y;
uniform int ATLAS_X;
uniform int ATLAS_Y;
uniform int SLICES;
uniform int BLOCK_RES_X;
uniform int BLOCK_RES_Y;
uniform int BLOCK_RES_Z;

uniform float CLIP_NEAR;
uniform float CLIP_FAR;

float rand(vec2 co){
  float threadId = gl_FragCoord.x/(gl_FragCoord.y + 1.0);
  float bigVal = threadId*1299721.0/911.0;
  float smallVal0 = threadId*7927.0/577.0;
  float smallVal1 = threadId*104743.0/1039.0;
  //return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
  return fract(sin(dot(co.xy ,vec2(smallVal0,smallVal1))) * bigVal);
}

vec4 getTransfer(float density){
  float t = density*float(TRANSFER_SIZE);
  //density += 0.01*rand(gl_FragCoord.yx/iResolution.xy);
  //return (density*vec4(1.0) + (1.0 - density)*vec4(0.0));
  return texture2D(transfer, vec2(density,0.0));
}

vec4 luma2Alpha(vec4 color, float min, float max, float C){
  //float x = sqrt(1.0/9.0*(color[0]*color[0] +color[1]*color[1] +color[2]*color[2]));
  float x = 1.0/3.0*(color[0] + color[1] + color[2]);
  x = clamp(x, 0.0, 1.0);
  float xi = (x-min)/(max-min);
  //float y = powf(xi,C);
  float y = xi;
  y = clamp(y,0.0,1.0);
  color[3] = y;
  return(color);
}

vec2 offsetBackFront(float t, float nx){
  vec2 os = vec2((1.0-mod(t,1.0))*nx-1.0, floor(t));
  return os;
}

vec2 offsetFrontBack(float t, float nx, float ny){
  vec2 os = vec2((mod(t,1.0))*nx, ny - floor(t) - 1.0);
  return os;
}


vec4 sampleAs3DTexture(sampler2D tex, vec4 pos) {
  //vec4 pos = -0.5*(texCoord - 1.0);
  //pos[0] = 1.0 - pos[0];
  //pos[1] = 1.0 - pos[1];
  //pos[2] = 1.0 - pos[2];
  //return pos;
  //vec4 pos = 0.5*(1.0 - texCoord);
  //return vec4(pos.xyz,0.05);
  pos = 0.5*(1.0 - pos);
  pos[0] = 1.0 - pos[0];
  //pos = clamp(pos,vec4(0.0),vec4(0.999));
  float bounds = float(pos[0] < 1.0 && pos[0] > 0.0 &&
                      pos[1] < 1.0 && pos[1] > 0.0 &&
                      pos[2] < 1.0 && pos[2] > 0.0 );
  float nx      = float(ATLAS_X);
  float ny      = float(ATLAS_Y);
  float nSlices = float(SLICES);
  float sx      = float(TEX_RES_X);
  float sy      = float(TEX_RES_Y);

  vec2 loc = vec2(pos.x/nx,pos.y/ny);
  loc[1] = 1.0/ny - loc[1];

  vec2 pix = vec2(1.0/nx,1.0/ny);

  float iz = pos.z*nSlices;
  float zs = floor(iz);
  float ty  = zs/nx;
  float typ = (zs+1.0)/nx;

  typ = clamp(typ, 0.0, nSlices);
  vec2 o0 = offsetFrontBack(ty,nx,ny)*pix;
  vec2 o1 = offsetFrontBack(typ,nx,ny)*pix;

  //return vec4(o0/vec2(nx,ny),0.0,0.5);

  float t = mod(iz, 1.0);
  vec4 slice0Color = texture2D(tex, loc + o0);
  vec4 slice1Color = texture2D(tex, loc + o1);
  return bounds*mix(slice0Color, slice1Color, t);
}

vec4 getNormal(sampler2D tex, vec4 texCoord){
  float nx      = float(ATLAS_X);
  float ny      = float(ATLAS_Y);
  /*
    float rx = rand(texCoord.xy);
    float ry = rand(texCoord.zy);
    float rz = rand(texCoord.xz);
    rx = clamp(rx, 0.25, 1.0);
    ry = clamp(rx, 0.25, 1.0);
    rz = clamp(rx, 0.25, 1.0);
  */
  float iz = 1.0/float(SLICES);
  float ix      = 1.0/float(TEX_RES_X);
  float iy      = 1.0/float(TEX_RES_Y);

  vec4 pos = texCoord;
  //s[0] = 1.0 - pos[0];
  float C = 2.0;
  float px = float(pos[0] >= (C*ix - 1.0));
  float py = float(pos[1] >= (C*iy - 1.0));
  float pz = float(pos[2] >= (C*iz - 1.0));
  float mx = float(pos[0] <= (1.0 - C*ix));
  float my = float(pos[1] <= (1.0 - C*iy));
  float mz = float(pos[2] <= (1.0 - C*iz));
  vec4 v0 = sampleAs3DTexture(tex, texCoord + px*vec4(ix, 0., 0., 0.));
  vec4 v1 = sampleAs3DTexture(tex, texCoord - vec4(ix, 0., 0., 0.));
  vec4 v2 = sampleAs3DTexture(tex, texCoord + py*vec4(0.,     iy,  0., 0.));
  vec4 v3 = sampleAs3DTexture(tex, texCoord - my*vec4(0.,     iy,  0., 0.));
  vec4 v4 = sampleAs3DTexture(tex, texCoord + vec4(0., 0., iz, 0.));
  vec4 v5 = sampleAs3DTexture(tex, texCoord - mz*vec4(0., 0., iz, 0.));
  v0 = luma2Alpha(v0, GAMMA_MIN, GAMMA_MAX, GAMMA_SCALE);
  v1 = luma2Alpha(v1, GAMMA_MIN, GAMMA_MAX, GAMMA_SCALE);
  v2 = luma2Alpha(v2, GAMMA_MIN, GAMMA_MAX, GAMMA_SCALE);
  v3 = luma2Alpha(v3, GAMMA_MIN, GAMMA_MAX, GAMMA_SCALE);
  v4 = luma2Alpha(v4, GAMMA_MIN, GAMMA_MAX, GAMMA_SCALE);
  v5 = luma2Alpha(v5, GAMMA_MIN, GAMMA_MAX, GAMMA_SCALE);

  if(USE_TRANSFER == 1){
    v0 = getTransfer(v0[3]);
    v1 = getTransfer(v1[3]);
    v2 = getTransfer(v2[3]);
    v3 = getTransfer(v3[3]);
    v4 = getTransfer(v4[3]);
    v5 = getTransfer(v5[3]);
  }

  float l0 = v0[3];
  float l1 = v1[3];
  float l2 = v2[3];
  float l3 = v4[3];
  float l4 = v4[3];
  float l5 = v5[3];

  vec3 grad = -vec3((l0-l1),(l2-l3),(l4-l5));
  grad *= px*py*pz*mx*my*mz;

  float a =  length(grad);

  if(a < 1e-9)
    return vec4(0.0);
  else
    return vec4(normalize(grad),a);

  //return grad;
}

bool intersectBox(in vec4 r_o, in vec4 r_d, in vec4 boxmin, in vec4 boxmax,
                  out float tnear, out float tfar)
{
  // compute intersection of ray with all six bbox planes
  vec4 invR = vec4(1.0,1.0,1.0,0.0) / r_d;
  vec4 tbot = invR * (boxmin - r_o);
  vec4 ttop = invR * (boxmax - r_o);

  // re-order intersections to find smallest and largest on each axis
  vec4 tmin = min(ttop, tbot);
  vec4 tmax = max(ttop, tbot);

  // find the largest tmin and the smallest tmax
  float largest_tmin  = max(max(tmin.x, tmin.y), max(tmin.x, tmin.z));
  float smallest_tmax = min(min(tmax.x, tmax.y), min(tmax.x, tmax.z));

  tnear = largest_tmin;
  tfar = smallest_tmax;

  return(smallest_tmax > largest_tmin);
}


//float turb(vec3 x){
//  float t =
//    snoise(256.0*x)*.375 + snoise(128.0*x)*.125;
//  t += 0.5*(0.5 - rand(x.xy));
//  return 1.25*t;
//}

float unpack (vec4 colour)
{

  const vec4 bitShifts = vec4(1.0 / (256.0 * 256.0),
                              1.0 / (256.0),
                              1.0,
                              0.0);

  return dot(colour , bitShifts);
}

vec4 integrateVolume(vec4 eye_o,vec4 eye_d,
                     vec4 boxMin, vec4 boxMax,vec4 boxScale,
                     sampler2D textureAtlas,
                     //sampler2D dataBase1[1],
                     ivec4 nBlocks){

  vec2 vUv = gl_FragCoord.xy/iResolution.xy;
  vec4 D = texture2D(BACKGROUND_DEPTH, vUv);
  vec4 C = texture2D(BACKGROUND_COLOR, vUv);

  float zNear = 0.01;
  float zFar = 20.0;
  float z_b = unpack(D);
  //return vec4(z_b);
  float z_n = 2.0 * z_b - 1.0;
  float z_e = 2.0 * zNear * zFar / (zFar + zNear - z_n * (zFar - zNear));


  //C = vec4(1.0, 0.0, 0.0, 0.0);

  if(z_e > 6.0) {
    //C = vec4(0.5);
      //C.r = 0.5*(1.0+sin(2.0*(z_e)));
      //C.g = 0.5*(1.0+sin(2.0*(z_e + 2.0/3.0*3.1417)));
      //C.b = 0.5*(1.0+sin(2.0*(z_e + 4.0/3.0*3.1417)));
  }


  float tnear, tfar;
  //return vec4(C.r,maxt,maxt,maxt);
  //return C;
  bool hit = intersectBox(eye_o, eye_d, boxMin, boxMax, tnear,  tfar);


  if (!hit || tnear > CLIP_FAR || tfar < CLIP_NEAR) {
    return vec4(0.5);
  }

  // march along ray from back to front, accumulating color
  float ray_mag = length(eye_d);
  float tobs   = z_e/ray_mag;
  //return vec4(float(tfar > tobs));
  if(tobs < tfar) tfar = tobs;
  //tobs = clamp(tobs, tobs, tfar);
  //tfar = clamp(tfar, tobs, tfar);
  float tbegin = tfar;
  float tend   = tnear;
  //determine slice plane normal.  half between the light and the view direction
  vec4 sliceP = -0.1*normalize(eye_o);
  /*
  vec4 sliceN = vec4(LIGHT_POSITION, 0.0) - vec4(0.0);
  sliceN = normalize(0.5*sliceN - 0.5*eye_d);
  */
  
  //estimate step length
  const int maxSteps = 512;
  float csteps = float(setMaxSteps);
  csteps = clamp(csteps,0.0,float(maxSteps));
  float isteps = 1.0/csteps;

  //figure out which box side is longest, w/respect to the view angle, use that to scale the stepsize
  /*
  vec4 eye_n = -normalize(eye_o);
  float dotSidex = eye_n.x*(boxMax.x - boxMin.x);
  float dotSidey = eye_n.y*(boxMax.y - boxMin.y);
  float dotSidez = eye_n.z*(boxMax.z - boxMin.z);

  float maxSide = max(abs(dotSidex), max(abs(dotSidey), abs(dotSidez)));
  float tstep = 0.4*maxSide*isteps;
  //float tstep = 0.3*isteps;

  //now that we have
  float tfarsurf = dot(sliceP - eye_o, sliceN)/dot(eye_d,sliceN); //project to far plane to determine overflow
  */
  float tstep = 0.3*isteps;
  float tfarsurf = 10.0;
  float overflow = (tfarsurf - tfar)/tstep;
  overflow -= floor(overflow); // we don't want uniform planes with dithering
  float r = 1.0*rand(eye_d.xy);

  float t = tbegin + (1.0 - float(DITHERING))*(overflow)*tstep;
  t = clamp(t, 0.0, CLIP_FAR);
  t += 1.0*float(DITHERING)*r*tstep;


  float A = 0.0;
  float     tdist    = 0.0;
  const int maxStepsLight = 32;

  float T = 1.0;
  int numSteps = 0;
  for(int i=0; i<maxSteps; i++){
    //if(t > maxt && maxt > 10.0) continue;
    vec4 pos = (eye_o + eye_d*t)/boxScale; // map position to [0, 1] coordinates
    vec4 smp = sampleAs3DTexture(textureAtlas,pos);
    vec4 col = luma2Alpha(smp, GAMMA_MIN, GAMMA_MAX, GAMMA_SCALE);
    //float x01 = 0.5*pos.x + 0.5;
    //col = vec4(x01,x01,x01,x01);
    float xfer = float(USE_TRANSFER);
    col =   xfer*getTransfer(col[3]) + (1.0 - xfer)*col;
    //col = vec4(col[3]);


    col.xyz *= brightness;

    float s = float(maxSteps)/float(setMaxSteps);
    
    col.w = 1.0 - pow(clamp(1.0 - col.w,0.0, 1.0),s);
    col.w *= density;
    col.xyz *= col.w;

    C = (1.0-col.w)*C + col;
    //float r0 = 0.5 + 1.0*rand(eye_d.xy);
    t -= tstep;
    numSteps = i;

    if (i > setMaxSteps || t  < tend || t < CLIP_NEAR ) break;
  }


  //if(!over) C += (1.0-C.w)*vec4(0.5);
  return C;
}

void main()
{
  vec4 eyeRay_d, eyeRay_o;
  vec2 fragCoord = gl_FragCoord.xy;
  //gl_FragColor = vec4(gl_FragCoord.xy/iResolution.xy,0.0,0.0);
  //return;

  //getRay(fragCoord, iResolution.xy, eyeRay_o, eyeRay_d);

  eyeRay_d.xy = 2.0*fragCoord.xy/iResolution.xy - 1.0;
  eyeRay_d[0] *= iResolution.x/iResolution.y;

  float fovr = 20.*M_PI/180.;
  eyeRay_d[2] = -1.0/tan(fovr*0.5);
  eyeRay_d   = eyeRay_d*viewMatrix;
  eyeRay_d[3] = 0.0;
  //ed = normalize(ed);
  eyeRay_o = vec4(cameraPosition,1.0);

  vec4 boxMin = vec4(-1.0);
  vec4 boxMax = vec4( 1.0);
  vec4 boxTrans = vec4(0.0, 0.0, 0.0, 0.0);
  vec4 boxScale = vec4(BOX_SIZE,1.0);
  //boxScale = vec4(0.5);
  boxMin *= boxScale;
  boxMax *= boxScale;
  boxMin += boxTrans;
  boxMax += boxTrans;
  ivec4 nBlocks = ivec4(BLOCK_RES_X,
                        BLOCK_RES_Y,
                        BLOCK_RES_Z,1);

  vec4 C = integrateVolume(eyeRay_o, eyeRay_d,
                           boxMin, boxMax, boxScale,
                           textureAtlas,nBlocks);

  gl_FragColor = C;
  return;

  //C *= brightness;
  //vec4 diff = vec4(vec3(0.5),0.0);
  //C += diff;

#if 0
  if ((gl_FragCoord[0] < 1.25*iResolution[0]) && (gl_FragCoord[1] < 1.25*iResolution[1])) {
    // write output color
    //C = clamp(C,0,1.0);
    gl_FragColor = C;
    //gl_FragColor = vec4(1.0-C[3]);
    //gl_FragColor = (eyeRay_o + eyeRay_d*t)/boxScale; // map position to [0, 1] coordinates
    //gl_FragColor = vec4(t/30.0);
    //gl_FragColor = eyeRay_d;
    //gl_FragColor = C + (1.0-C[3]*density)*vec4(vec3(0.75),0.0);
    //gl_FragColor = 0.1*vec4(t-tnear);
  }
#endif

}

