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

#define LIGHTING 0
#define PHONG 0

uniform vec2 iResolution;

uniform vec3 BOX_SIZE;

uniform int setMaxSteps;

uniform int RED_CHANNEL;
uniform int GREEN_CHANNEL;
uniform int BLUE_CHANNEL;

uniform int   DITHERING;
uniform int   DITHER_SPACE;
uniform int   DITHER_LIGHTING;

#if LIGHTING || PHONG
uniform vec3 LIGHT_POSITION;
#endif

#if LIGHTING
uniform int   LIGHT_SAMPLES;
uniform float LIGHT_DEPTH;
uniform float LIGHT_SIG;

uniform float DISP_SIG;
uniform float DISPERSION;
#endif

#if PHONG
uniform int   NORMAL_MULT;
uniform float KA;
uniform float KD;
uniform float NORMAL_INTENSITY;
uniform float SPEC_SIZE;
uniform float SPEC_INTENSITY;
#endif

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


float powf(float a, float b){
  //dirty low precision pow function
  float g[20];
 g[0] = 1.0;
  g[1] = 0.5;
  g[2] = 0.333333333;
  g[3] = 0.25;
  g[4] = 0.2;
  g[5] = 0.1666666667;
  g[6] = 0.1428571428571429;
  g[7] = 0.125;
  g[8] = 0.11111111111111;
  g[9] = 0.1;
  g[10] = 0.090909090909;
  g[11] = 0.0833333333333;
  g[12] = 0.07692307692307692307692307692308;
  g[13] = 0.07142857142857142857142857142857;
  g[14] = 0.06666666666666666666666666666667;
  g[15] = 0.0625;
  g[16] = 0.05882352941176470588235294117647;
  g[17] = 0.05555555555555555555555555555556;
  g[18] = 0.05263157894736842105263157894737;
  g[19] = 0.05;

  float f[13];
  f[0] = 1.0;
  f[1] = 0.5;
  f[2] = 1.6666666667e-1;
  f[3] = 4.1666666667e-2;
  f[4] = 8.3333333333e-3;
  f[5] = 1.3888888888e-3;
  f[6] = 1.984126984126984e-4;
  f[7] = 2.48015873015873e-5;
  f[8] = 2.755731922398589e-6;
  f[9] = 2.755731922398589e-7;
  f[10] = 2.505210838544172e-8;
  f[11] = 2.08767569878681e-9;
  f[12] = 1.605904383682161e-10;

  float x = 1.0 - a;
  float xa = x;
  float y = 0.0;

  for(int i = 0; i < 20; i++){
    y -= xa*g[i];
    xa *= x;
  }

  float logy = 1.0;
  y *= b;
  float ya = y;
  for(int i = 0; i < 13; i++){
    logy += ya*f[i];
    ya *= y;
  }

  return logy;
  //return exp(y*log(x));
}

float rand(vec2 co){
  float threadId = gl_FragCoord.x/(gl_FragCoord.y + 1.0);
  float bigVal = threadId*1299721.0/911.0;
  float smallVal0 = threadId*7927.0/577.0;
  float smallVal1 = threadId*104743.0/1039.0;
  //return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
  return fract(sin(dot(co.xy ,vec2(smallVal0,smallVal1))) * bigVal);
}

vec4 getTransfer(float density){
  float t = clamp(density,0.0,1.0);//float(TRANSFER_SIZE);
  //density += 0.01*rand(gl_FragCoord.yx/iResolution.xy);
  vec4 cola = (density*vec4(1.0) + (1.0 - density)*vec4(0.0));
  vec4 col  = texture2D(transfer, vec2(t,0.0));
  return col;
}

vec4 luma2Alpha(vec4 color, float min, float max, float C){
  //float x = sqrt(1.0/9.0*(color[0]*color[0] +color[1]*color[1] +color[2]*color[2]));
  float x = 1.0/3.0*(color[0] + color[1] + color[2]);

  //x = clamp(x, 0.0, 1.0);
  float xi = (x-min)/(max-min);
  xi = clamp(xi,0.0,1.0);
  //float b = 0.5*(max + min);
  //float xi = 1.0 / (1.0 + exp(-((x-b)/0.001)));
  float y = pow(xi,C);
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
  //pos = clamp(pos,0.1,0.9);
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

  float tnear, tfar;

  bool hit = intersectBox(eye_o, eye_d, boxMin, boxMax, tnear,  tfar);

  float eyeDist  = length(eye_o.xyz);
  float rayMag   = length(eye_d);

  //float clipNear = eyeDist - (1.0 - CLIP_NEAR);
  float clipNear = eyeDist/rayMag - 0.275 + 0.55*CLIP_NEAR;
  float clipFar = eyeDist/rayMag  + 0.275 - 0.55*CLIP_FAR;//+ (0.25 - CLIP_FAR);
  //clipFar = CLIP_FAR;
 if (!hit || tnear > clipFar || tfar < clipNear) {
    return vec4(0.5);
  }

  // march along ray from back to front, accumulating color

  float tobs   = z_e/rayMag;
  if(tobs < tfar) tfar = tobs;

  float tbegin = tfar;
  float tend   = tnear;
  //determine slice plane normal.  half between the light and the view direction


  //estimate step length
  const int maxSteps = 512;
  float csteps = float(setMaxSteps);
  csteps = clamp(csteps,0.0,float(maxSteps));
  float isteps = 1.0/csteps;

  float tstep = 0.5*isteps;
  float tfarsurf = 1.0;
  float overflow = mod((tfarsurf - tfar),tstep);

  float r = 1.5*rand(eye_d.xy);

  float t = tbegin + overflow;
  //float t = 0.5*(tnear + tfar) + overflow;
  //t = clamp(t, 0.0, tbegin);
  t = clamp(t, 0.0, clipFar);
  t -= 1.0*float(DITHERING)*r*tstep;


  float A = 0.0;
  float     tdist    = 0.0;
  const int maxStepsLight = 32;

#if LIGHTING || PHONG
  float absorption = 1.;
  vec4 lightPos = 2.0*vec4(LIGHT_POSITION,.0);
#endif

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

    //col =   getTransfer(col[3]);
    //col = vec4(col[3]);
#if LIGHTING || PHONG
    vec4 dl = lightPos - pos;
#endif

#define HIGHLIGHT 1
#if HIGHLIGHT || PHONG
    vec4 N = getNormal(textureAtlas,pos);
#endif

#if HIGHLIGHT
    col.xyz *= (1.5 -  N[3]);
#endif

#if PHONG
    //vec4 N = getNormal(textureAtlas,pos);
    float lum = N[3];

    float dist = length(dl);
    dl = normalize(dl);
    vec4 V = -normalize(eye_d);
    vec4 H = dl + V;
    H = normalize(H);

    float lightVal = dot(dl.xyz, N.xyz);
    float spec = pow(abs(dot( N.xyz, H.xyz )),SPEC_SIZE);
    spec = clamp(spec, 0.0, spec);
    // += vec4(vec3(spec),0.0);

    float kn = pow(abs(0.0*N[3]),NORMAL_INTENSITY);
    float ka = KA;
    float kd = KD;
    float ks = 4.0*SPEC_INTENSITY;
    kn = clamp(kn,0.0,1.0);
    //float kn = 1.0;
    col *= (ka + kd*vec4(vec3(lightVal),kn));
    col += col[3]*ks*N[3]*vec4(spec);
    col = clamp(col, 0.0, 1.0);
    //col += H;
    //col = N;
#endif

#if LIGHTING
    float lstep = LIGHT_DEPTH/float(LIGHT_SAMPLES);
    float Dl = 0.0;

    vec3 DISP_BIAS = vec3(100.5, 200.3, 0.004);
    dl = normalize(dl);

    vec3 dtemp = cross(dl.xyz,vec3(1.0,1.0,1.0)); dtemp = normalize(dtemp);
    vec3 N1 = cross(dl.xyz,dtemp);
    vec3 N2 = cross(dl.xyz,N1);
    //N1 = normalize(N1);
    //N2 = normalize(N2);
      float r0 = 1.0 - 2.0*rand(pos.xy + eye_d.zx); //create three random numbers for each dimension
      float r1 = 1.0 - 2.0*rand(pos.yz + eye_d.zx);
      float r2 = 1.0 - 2.0*rand(pos.xz + eye_d.yx);
    for(int j=0; j<maxStepsLight; j++){ //*/
      if (j > LIGHT_SAMPLES) break;

      float lti = (float(j))*lstep;
      vec4 Ni   = DISPERSION*(r0*dl + vec4(r1*N1 + r2*N2, 0.0));

      vec4 lpos = pos + lti*dl;

      r0 = 1.0 - 2.0*rand(lpos.xy + eye_d.zx); //create three random numbers for each dimension
      r1 = 1.0 - 2.0*rand(lpos.yz + eye_d.zx);
      r2 = 1.0 - 2.0*rand(lpos.xz + eye_d.yx);

      lpos += lti*Ni;

      vec4 dsmp = sampleAs3DTexture(textureAtlas,lpos);
      vec4 dens = luma2Alpha(dsmp, GAMMA_MIN, GAMMA_MAX, GAMMA_SCALE);
      if(USE_TRANSFER == 1){ dens = getTransfer(dens[3]);}
      float Kdisp = DISP_SIG;
      float sl = float(maxStepsLight)/float(LIGHT_SAMPLES);
      //lti *= dens.w;

      //dens.w = 1.0 - pow(abs(1.0-dens.w), sl);
      dens.w *= 1.0*density;
      //dens.w = clamp(dens.w, 0.0, 1.0);
      Dl =  (1.0-Dl)*dens.w + Dl;
      //Dl =  (1.0-dens.w)*Dl + dens.w;
    }
    //Dl = clamp(Dl,0.0,1.0);
    //col *= (1.0 - exp(-Dl));
    col.xyz *= (1.0 - Dl);
    col.xyz *= 2.0*brightness;
#else
    col.xyz *= brightness;
#endif
    float s = 512.0/csteps;
    //float s = float(maxSteps)/float(setMaxSteps);
    //s = 10.0;
    col.w = 1.0 - pow(abs((1.0-col.w)),s);
    col.w *= density;
    col.xyz *= col.w;

    C = (1.0-col.w)*C + col;
    //float r0 = 0.5 + 1.0*rand(eye_d.xy);
    t -= tstep;
    numSteps = i;

    if (i > setMaxSteps || t  < tend || t < clipNear ) break;
  }


  //if(!over) C += (1.0-C.w)*vec4(0.5);
  return C;
}

void main()
{
  vec4 eyeRay_d, eyeRay_o;
  vec2 fragCoord = gl_FragCoord.xy;
  //gl_FragColor = vec4(gl_FragCoord.xy/iResolution.xy,0.0,0.0);
  //vec2 coord = gl_FragCoord.xy/iResolution.xy;
  //gl_FragColor = texture2D(transfer, );
  //return;

  //getRay(fragCoord, iResolution.xy, eyeRay_o, eyeRay_d);

  eyeRay_d.xy = 2.0*fragCoord.xy/iResolution.xy - 1.0;
  eyeRay_d[0] *= iResolution.x/iResolution.y;

  float fovr = 40.*M_PI/180.;
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

