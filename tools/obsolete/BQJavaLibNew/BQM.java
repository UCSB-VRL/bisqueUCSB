/***************************************************************************
 *   Copyright (C) 2008 by Center for Bio-Image Informatics UCSB           *
 *                                                                         *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the                         *
 *   Free Software Foundation, Inc.,                                       *
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
 ***************************************************************************/
package bisque;
import java.util.ArrayList;
import java.lang.reflect.Array;
import java.util.Iterator;
import java.awt.image.DataBuffer;
import java.awt.image.DataBufferByte;
import java.awt.image.DataBufferUShort;
import java.awt.image.DataBufferDouble;

import java.io.File;
import java.io.FileOutputStream;
import java.io.DataOutputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.nio.ByteOrder;
import javax.imageio.ImageIO;
import java.lang.Class;

public class BQM extends BQ{

    //--------------------------------------------------------------
    // GOBJECT
    //--------------------------------------------------------------
    public static void addVertices(BQGObject gobject, double[][] v){
        for (int i=0; i < v.length; i++ ){
            Double x = null;
            Double y = null;
            Double z = null;
            Double t = null;
            Integer ch = null;
            Integer index = null;

            x = new Double(v[i][0]);
            y = new Double(v[i][1]);
            if (v[i].length > 2)
                z = new Double(v[i][2]);
            if (v[i].length > 3)
                t = new Double(v[i][3]);
            if (v[i].length > 4)
                ch = new Integer(new Double(v[i][4]).intValue());
            if (v[i].length > 5)
                index= new Integer(new Double(v[i][5]).intValue());

            gobject.vertices.add(new BQVertex(x, y, z, t, ch, index));
        }
    }
    public static void deleteGObjects(BQObject object){
        if(object.uri != null) {
            System.out.println(object.uri);
            ArrayList<BQGObject> gos = object.gobjects;
            Iterator<BQGObject> goi = gos.iterator();
            while (goi.hasNext()){
                BQGObject go = goi.next();
                System.out.println(go.uri);
                ds.delete(go);
            }
        }
    }
    //--------------------------------------------------------------
    // TAG
    //--------------------------------------------------------------
    public static void deleteTags(BQObject object){
        if(object.uri != null) {
            System.out.println(object.uri);
            ArrayList<BQTag> tags = object.tags;
            Iterator<BQTag> ti = tags.iterator();
            while (ti.hasNext()){
                BQTag tag = ti.next();
                System.out.println(tag.uri);
                ds.delete(tag);
            }
        }
    }
    //--------------------------------------------------------------
    // IMAGE
    //--------------------------------------------------------------
    public static String getObjectType(Object o){
        String type;
        Class cls = o.getClass();
        type = cls.getName();
        while (cls.isArray()){
            cls = cls.getComponentType();
            type = cls.getName();
        }
        return type;
    }
    public static int checkObjectType(Object o) { 
        String type = getObjectType(o);
        //         B            byte
        //         C            char
        //         D            double
        //         F            float
        //         I            int
        //         J            long
        //         Lclassname;  class or interface
        //         S            short
        //         Z            boolean
        if(type.equals("B")){ return 8; }
        if(type.equals("S")){ return 16; }
        if(type.equals("I")){ return 32; }
        if(type.equals("F")){ return 32; }
        if(type.equals("D")){ return 64; }
        return 8;
    }
    //Object allocatePixelMatrix (image)
    public static void setType(BQImage image, String type) { 
        BQImagePixels pixels = image.getPixels();
        pixels.setType(type);
        if(type.equals("uint8")) { pixels.setDepth(8); }
        if(type.equals("uint16")){ pixels.setDepth(16); }
        if(type.equals("uint32")){ pixels.setDepth(32); }
        if(type.equals("double")){ pixels.setDepth(64); }
    }
    public static void setGeometry(BQImage image, int x, int y, int ch, int z, int t) {
        image.setPixels(x, y, ch, z, t,  null, null, "matlab.raw");
    }
    public static int[] getGeometry(BQImage image){
        int [] geom = {image.x, image.y, image.ch, image.z, image.t, image.d};
        return geom;
    }
    public static void setPixels(BQImage image, Object matrix){
        //ArrayList<DataBuffer> 
        BQImagePixels pixels = image.getPixels();
        System.out.println("OBJECT: " + matrix.getClass().getName() );
        if(checkObjectType(matrix) == pixels.d) {
            System.out.println("PIXELS: " + pixels.x +","+ pixels.y +","+ pixels.ch +","+ pixels.z +","+ pixels.t +","+ pixels.d);
            pixels.setPixels(convertMatlabToJava(matrix, pixels.x, pixels.y, pixels.ch, pixels.z, pixels.t, pixels.d));
        }
        //else
        //    throw new Exception("Message: !!!!");
    }
    public static Object getPixels(BQImage image) {
        BQImagePixels pixels = image.getPixels();
        pixels.load();
        //pixels.save("file:///home/boguslaw/Desktop/im.raw");
        ArrayList<DataBuffer> dataBuffers = pixels.getPixels();
        return convertJavaToMatlab(dataBuffers, pixels.x, pixels.y, pixels.ch, pixels.z, pixels.t, pixels.d);
    }
    public static ArrayList<DataBuffer> convertMatlabToJava( Object image, int x, int y, int ch, int z, int t, int d ){
        ArrayList<DataBuffer> dataBuffers = new ArrayList<DataBuffer>();
        int tmp = y; y = x; x = tmp;
        for (int ti = 0; ti < t; ti++){
            for (int zi = 0; zi < z; zi++){
                if (d == 8) { dataBuffers.add(convertByteToBuffer(  image, x, y, ch, z, t, zi, ti)); }
                if (d == 16){ dataBuffers.add(convertUShortToBuffer(image, x, y, ch, z, t, zi, ti)); }
                if (d == 32){ dataBuffers.add(convertDoubleToBuffer(image, x, y, ch, z, t, zi, ti)); }
            }
        }
        return dataBuffers;
    }

    public static Object convertJavaToMatlab(ArrayList<DataBuffer> dataBuffers, int x, int y, int ch, int z, int t, int d){
        Object image = allocatePixelMatrix (x, y, ch, z, t, d);
        System.out.println("PIXELS: " +x+","+y+","+ch+","+z+","+t+","+d);
        int tmp = y; y = x; x = tmp;
        for (int ti = 0; ti < t; ti++){
            for (int zi = 0; zi < z; zi++){
                if (d == 8) { convertBufferToByte(  image, dataBuffers, x, y, ch, z, t, zi, ti); }
                if (d == 16){ convertBufferToUShort(image, dataBuffers, x, y, ch, z, t, zi, ti); }
                if (d == 32){ convertBufferToDouble(image, dataBuffers, x, y, ch, z, t, zi, ti); }
            }
        }
        return image;
    }
    public static void convertBufferToByte( Object image, ArrayList<DataBuffer> dataBuffers, int x, int y, int ch, int z, int t, int zi, int ti ){
        for (int chi = 0; chi < ch; chi++){
            DataBufferByte buffer = (DataBufferByte)dataBuffers.get(ti*z+zi);
            byte[] array = buffer.getData(chi);
            int ix = 0;
            for (int yi = 0; yi < x; yi++){
                for (int xi = 0; xi < y; xi++){
                    if (ch == 1 && z == 1 && t == 1)
                        ((int[][])image)[yi][xi] = byte2int(array[ix++]);
                    else if (ch > 1 && z == 1 && t == 1)
                        ((int[][][])image)[yi][xi][chi] = byte2int(array[ix++]);
                    else if (ch == 1 && z > 1 && t == 1)
                        ((int[][][])image)[yi][xi][zi] = byte2int(array[ix++]);
                    else if (ch == 1 && z == 1 && t > 1)
                        ((int[][][])image)[yi][xi][ti] = byte2int(array[ix++]);
                    else if (ch > 1 && z > 1 && t == 1)
                        ((int[][][][])image)[yi][xi][chi][zi] = byte2int(array[ix++]);
                    else if (ch > 1 && z == 1 && t > 1)
                        ((int[][][][])image)[yi][xi][chi][ti] = byte2int(array[ix++]);
                    else if (ch > 1 && z > 1 && t > 1)
                        ((int[][][][][])image)[yi][xi][chi][zi][ti] = byte2int(array[ix++]);
                }
            }
        }
    }
    public static void convertBufferToUShort( Object image, ArrayList<DataBuffer> dataBuffers, int x, int y, int ch, int z, int t, int zi, int ti ){
        for (int chi = 0; chi < ch; chi++){
            DataBufferUShort buffer = (DataBufferUShort)dataBuffers.get(ti*z+zi);
            short[] array = buffer.getData(chi);
            int ix = 0;
            for (int yi = 0; yi < x; yi++){
                for (int xi = 0; xi < y; xi++){
                    if (ch == 1 && z == 1 && t == 1)
                        ((int[][])image)[yi][xi] = short2int(array[ix++]);
                    else if (ch > 1 && z == 1 && t == 1)
                        ((int[][][])image)[yi][xi][chi] = short2int(array[ix++]);
                    else if (ch == 1 && z > 1 && t == 1)
                        ((int[][][])image)[yi][xi][zi] = short2int(array[ix++]);
                    else if (ch == 1 && z == 1 && t > 1)
                        ((int[][][])image)[yi][xi][ti] = short2int(array[ix++]);
                    else if (ch > 1 && z > 1 && t == 1)
                        ((int[][][][])image)[yi][xi][chi][zi] = short2int(array[ix++]);
                    else if (ch > 1 && z == 1 && t > 1)
                        ((int[][][][])image)[yi][xi][chi][ti] = short2int(array[ix++]);
                    else if (ch > 1 && z > 1 && t > 1)
                        ((int[][][][][])image)[yi][xi][chi][zi][ti] = short2int(array[ix++]);
                }
            }
        }
    }
    public static void convertBufferToDouble( Object image, ArrayList<DataBuffer> dataBuffers, int x, int y, int ch, int z, int t, int zi, int ti ){
        for (int chi = 0; chi < ch; chi++){
            DataBufferDouble buffer = (DataBufferDouble)dataBuffers.get(ti*z+zi);
            double[] array = buffer.getData(chi);
            int ix = 0;
            for (int yi = 0; yi < x; yi++){
                for (int xi = 0; xi < y; xi++){
                    if (ch == 1 && z == 1 && t == 1)
                        ((double[][])image)[yi][xi] = array[ix++];
                    else if (ch > 1 && z == 1 && t == 1)
                        ((double[][][])image)[yi][xi][chi] = array[ix++];
                    else if (ch == 1 && z > 1 && t == 1)
                        ((double[][][])image)[yi][xi][zi] = array[ix++];
                    else if (ch == 1 && z == 1 && t > 1)
                        ((double[][][])image)[yi][xi][ti] = array[ix++];
                    else if (ch > 1 && z > 1 && t == 1)
                        ((double[][][][])image)[yi][xi][chi][zi] = array[ix++];
                    else if (ch > 1 && z == 1 && t > 1)
                        ((double[][][][])image)[yi][xi][chi][ti] = array[ix++];
                    else if (ch > 1 && z > 1 && t > 1)
                        ((double[][][][][])image)[yi][xi][chi][zi][ti] = array[ix++];
                }
            }
        }
    }
    private static Object allocatePixelMatrix(int x, int y, int ch, int z, int t, int d) {
            int size = 2;
            if (ch > 1) size++;
            if (z  > 1) size++;
            if (t  > 1) size++;
            int [] dim = new int[size];
            dim[0] = (int)y;
            dim[1] = (int)x;
            //if(channels > 1 && zsize == 1 && tsize == 1)
            if (ch >  1)                            dim[2] = (int)ch;
            if (ch == 1     && z >  1   && t == 1)  dim[2] = (int)z;
            if (ch == 1     && z == 1   && t >  1)  dim[2] = (int)t;
            if (ch == 1     && z >  1   && t >  1)  dim[3] = (int)t;
            if (ch >  1     && z >  1   && t == 1)  dim[3] = (int)z;
            if (ch >  1     && z == 1   && t >  1)  dim[3] = (int)t;
            if (ch >  1     && z >  1   && t >  1)  dim[4] = (int)t;
            for(int i=0;i<size;i++) System.out.println(dim[i]);
            Object o = null;
            if (d == 8 ){ o = new int[1]; }
            if (d == 16){ o = new int[1]; }
            if (d == 32){ o = new double[1]; }
            Object array = Array.newInstance(BQUtil.getArrayComponent(o), dim);
        return array;
    }
    public static DataBuffer convertByteToBuffer( Object image, int y, int x, int ch, int z, int t, int zi, int ti ){
        byte[][] dataArray = new byte[ch][x*y];
        for (int chi = 0; chi < ch; chi++){
            int ix = 0;
            for (int yi = 0; yi < y; yi++){
                for (int xi = 0; xi < x; xi++){
                    byte b = 0;
                    if (ch == 1 && z == 1 && t == 1)
                        b = ((byte[][])image)[yi][xi];
                    else if (ch > 1 && z == 1 && t == 1)
                        b = ((byte[][][])image)[yi][xi][chi];
                    else if (ch == 1 && z > 1 && t == 1)
                        b = ((byte[][][])image)[yi][xi][zi];
                    else if (ch == 1 && z == 1 && t > 1)
                        b = ((byte[][][])image)[yi][xi][ti];
                    else if (ch > 1 && z > 1 && t == 1)
                        b = ((byte[][][][])image)[yi][xi][chi][zi];
                    else if (ch > 1 && z == 1 && t > 1)
                        b = ((byte[][][][])image)[yi][xi][chi][ti];
                    else if (ch > 1 && z > 1 && t > 1)
                        b = ((byte[][][][][])image)[yi][xi][chi][zi][ti];
                    dataArray[chi][ix++] = b;
                }
            }
        }
        return new DataBufferByte(dataArray, x*y*ch);
    }
    public static DataBuffer convertUShortToBuffer( Object image, int y, int x, int ch, int z, int t, int zi, int ti ){
        short[][] dataArray = new short[ch][x*y];
        for (int chi = 0; chi < ch; chi++){
            int ix = 0;
            for (int yi = 0; yi < y; yi++){
                for (int xi = 0; xi < x; xi++){
                    short s = 0;
                    if (ch == 1 && z == 1 && t == 1)
                        s = ((short[][])image)[yi][xi];
                    else if (ch > 1 && z == 1 && t == 1)
                        s = ((short[][][])image)[yi][xi][chi];
                    else if (ch == 1 && z > 1 && t == 1)
                        s = ((short[][][])image)[yi][xi][zi];
                    else if (ch == 1 && z == 1 && t > 1)
                        s = ((short[][][])image)[yi][xi][ti];
                    else if (ch > 1 && z > 1 && t == 1)
                        s = ((short[][][][])image)[yi][xi][chi][zi];
                    else if (ch > 1 && z == 1 && t > 1)
                        s = ((short[][][][])image)[yi][xi][chi][ti];
                    else if (ch > 1 && z > 1 && t > 1)
                        s = ((short[][][][][])image)[yi][xi][chi][zi][ti];
                    dataArray[chi][ix++] = s;
                }
            }
        }
        return new DataBufferUShort(dataArray, x*y*ch);
    }
    public static DataBuffer convertDoubleToBuffer( Object image, int y, int x, int ch, int z, int t, int zi, int ti ) {
        double[][] dataArray = new double[ch][x*y];
        for (int chi = 0; chi < ch; chi++){
            int ix = 0;
            for (int yi = 0; yi < y; yi++){
                for (int xi = 0; xi < x; xi++){
                    double d = 0;
                    if (ch == 1 && z == 1 && t == 1)
                        d = ((double[][])image)[yi][xi];
                    else if (ch > 1 && z == 1 && t == 1)
                        d = ((double[][][])image)[yi][xi][chi];
                    else if (ch == 1 && z > 1 && t == 1)
                        d = ((double[][][])image)[yi][xi][zi];
                    else if (ch == 1 && z == 1 && t > 1)
                        d = ((double[][][])image)[yi][xi][ti];
                    else if (ch > 1 && z > 1 && t == 1)
                        d = ((double[][][][])image)[yi][xi][chi][zi];
                    else if (ch > 1 && z == 1 && t > 1)
                        d = ((double[][][][])image)[yi][xi][chi][ti];
                    else if (ch > 1 && z > 1 && t > 1)
                        d = ((double[][][][][])image)[yi][xi][chi][zi][ti];
                    dataArray[chi][ix++] = d;
                }
            }
        }
        return new DataBufferDouble(dataArray, x*y*ch);
    }
    public static int byte2int(byte b) { return (int)((b>=0)?b:(int)(256+b)); }
    public static int short2int(short s) { return (int)((s>=0)?s:65536+(int)s); }
 }