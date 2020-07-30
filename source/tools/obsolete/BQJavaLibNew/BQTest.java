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
import java.util.Iterator;
import java.util.ArrayList;
import java.io.IOException;
import java.util.Random;
import javax.imageio.ImageIO;
import java.io.File;
import java.io.IOException;

public class BQTest{
    public BQTag testCreate_Tag(){
        BQTag tr = new BQTag();
        tr.setName ("ROI"); tr.setValue ("This is interested region.");
        return tr;
    }
    public BQGObject testCreate_GObject(){
        BQGObject roi = new BQGObject();
        roi.type = "ROI";
        roi.name = "My ROI";

        BQGObject circle = new BQGObject();
        circle.type = "circle";
        circle.name = "cancer cell";
        BQTag tc = new BQTag();
        tc.setName ("Cancer Cell"); tc.setValue ("Here is a discovery of new cancer cells.");
        BQVertex vc1 = new BQVertex(20.0,20.0,0.0,0.0,1,0);
        BQVertex vc2 = new BQVertex(50.0,50.0,0.0,0.0,1,1);
        ArrayList<BQVertex> vcl = new ArrayList<BQVertex>();
        vcl.add(vc1); vcl.add(vc2);
        circle.tags.add(tc);
        circle.vertices = vcl;

        BQGObject rect = new BQGObject();
        rect.type = "rectangle";
        rect.name = "ROI";
        BQTag tr = new BQTag();
        tr.setName ("ROI"); tr.setValue ("This is interested region.");
        BQVertex vr1 = new BQVertex(10.0,10.0,0.0,0.0,3,0);
        BQVertex vr2 = new BQVertex(100.0,100.0,0.0,0.0,3,1);
        ArrayList<BQVertex> vrl = new ArrayList<BQVertex>();
        vrl.add(vr1); vrl.add(vr2);
        rect.tags.add(tr);
        rect.vertices = vrl;

        roi.gobjects.add(rect);
        roi.gobjects.add(circle);
        return roi;
    }
    public BQImage testCreate_Image(){
        BQTest testBQ = new BQTest();
        BQImage image = new BQImage(100,100,5,5,3);
        BQTag ti = new BQTag();
        ti.setName("Experiment ID"); ti.setValue("3/BQ");
        image.tags.add(ti);
        BQGObject rect = testBQ.testCreate_GObject();
        //image.gobjects.add(rect);
        return image;
    }
    public void testParseXML_GObject(){
        //BQAuthorization.setAuthorization("kgk","testme");
        //String url = "http://loup.ece.ucsb.edu:8080/ds/images/100187/gobjects?view=full,canonical";        
        BQAuthorization.setAuthorization("admin","admin");
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/116/gobjects?view=full,canonical";
        BQImage image = new BQImage(url);
        image.load();
        Iterator<BQGObject> gi = image.gobjects.iterator();
        while ( gi.hasNext() ){
            BQGObject go = gi.next();
            System.out.println("gobject: type=" + go.type + ", uri="+ go.uri);
        }
    }
    public void testParseXML_Image(){
        BQAuthorization.setAuthorization("admin","admin");
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/601";
        BQDataService ds = new BQDataService();
        BQImage image = (BQImage)ds.load(url);
        System.out.println("Image: src="        + image.src         + "," +
                                    "x="        + image.x           + "," +
                                    "y="        + image.y           + "," +
                                    "z="        + image.z           + "," +
                                    "t="        + image.t           + "," +
                                    "ch="       + image.ch          + "," +
                                    "owner_id=" + image.owner_id    + "," +
                                    "perm="     + image.perm        + "," +
                                    "ts="       + image.ts);
    }
    public void testParseXML_ImageSrc(){
        BQAuthorization.setAuthorization("admin","admin");
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/124";
        BQDataService ds = new BQDataService();
        BQImage image = (BQImage)ds.load(url);
        System.out.println("Image:  src="       + image.src         + "," +
                                    "x="        + image.x           + "," +
                                    "y="        + image.y           + "," +
                                    "z="        + image.z           + "," +
                                    "t="        + image.t           + "," +
                                    "ch="       + image.ch          + "," +
                                    "owner_id=" + image.owner_id    + "," +
                                    "perm="     + image.perm        + "," +
                                    "ts="       + image.ts);

        image.getInfo();
        System.out.println("Image:  src="       + image.src         + "," +
                                    "d="        + image.d           + "," +
                                    "f="        + image.f           + "," +
                                    "xr="       + image.xr          + "," +
                                    "yr="       + image.yr          + "," +
                                    "zr="       + image.zr          + "," +
                                    "e="        + image.e);
    }
    public void testGenXML_Image(){
        BQAuthorization.setAuthorization("admin","admin");
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/108/gobjects";
        BQTest testBQ = new BQTest();
        //BQImage image = testBQ.testCreate_Image();
        //BQDataService ds = new BQDataService("http://bodzio.ece.ucsb.edu:8080/ds/images/108/tags");
        //BQTag tr = testBQ.testCreate_Tag();
        //ds.save(tr);        
        BQDataService ds = new BQDataService(url);
        BQGObject rect = testBQ.testCreate_GObject();
        ds.save(rect);
    }
    public void testSaveFile(){
        BQAuthorization.setAuthorization("admin","admin");
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/112";
        BQDataService ds = new BQDataService();
        BQImage image = (BQImage)ds.load(url);
        image.saveToFile("/home/boguslaw/Desktop/");
    }
    public void testSearch(){
        BQAuthorization.setAuthorization("admin","admin");
        String url = "http://bodzio.ece.ucsb.edu:8080";
        BQDataService ds = new BQDataService(url);
        ArrayList<BQObject> s = ds.search("");
        //image.saveToFile("/home/boguslaw/Desktop/");
    }
    public void testFindTag(){
        BQAuthorization.setAuthorization("admin","admin");
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/104?view=full";
        BQDataService ds = new BQDataService();
        BQImage image = (BQImage)ds.load(url);
        System.out.println(image.tags.size());
        BQTag tag  = image.findTag("me");
        if (tag!=null)
            System.out.println("VALUE = " + tag.getValue());
        else
            System.out.println("NO VALUE");
    }
    public void testLoadObjectFromXMLFile(){
        BQDataService ds = new BQDataService();
        //String filePath = "/home/boguslaw/Desktop/Matlab/Caltech_3D_v9/nuclei3DCaltech_1.4_0.22.xml";
        String filePath = "/home/boguslaw/Desktop/Matlab/Caltech_3D_v9/xml/combinedsubtractionsNew.xml";
        BQObject image = (BQObject)ds.loadFile(filePath);
        System.out.println(image.gobjects.size());
    }
    public void testSaveObjectToXMLFile(){
        BQDataService ds = new BQDataService();
        BQTest testBQ = new BQTest();
        BQGObject rect = testBQ.testCreate_GObject();
        String filePath = "/home/boguslaw/Desktop/myfile.xml";
        ds.saveFile(rect, filePath);
    }
    public void testParseXML_MEX(){
        BQAuthorization.setAuthorization("admin","admin");
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/mex/8139?view=full";
        BQDataService ds = new BQDataService();
        BQMEX mex = (BQMEX)ds.load(url);
        System.out.println("Mex:     uri="      + mex.uri         + "," +
                                    "module="   + mex.module      + "," +
                                    "status="   + mex.status      + "," +
                                    "owner_id=" + mex.owner_id    + "," +
                                    "perm="     + mex.perm        + "," +
                                    "ts="       + mex.ts);
    }
    public void testBQImagePixels(){
        BQAuthorization.setAuthorization("admin","admin");
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/14516";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/15065";
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/104?view=full";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/13017";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/14475";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/14477";

        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/14481";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/14475";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/14479";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/13829";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/14510";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/14527";
        //BQDataService ds = new BQDataService();
        //BQImage image = (BQImage)ds.load(url);
        BQ.initialize("http://bodzio.ece.ucsb.edu:8080", "admin", "admin", "http://bodzio.ece.ucsb.edu:8080/ds/modules/87");
        BQDataService ds = BQ.ds;
        System.out.println(ds.server_uri);
        BQImage image = (BQImage)BQDataService.load("http://bodzio.ece.ucsb.edu:8080/ds/images/104");
        //BQImagePixels pixels = image.getPixels();

        //p.slice(null,null,1,2).format("raw").slice("30-25",null,"1","2-5").roi(10,10,45,32).thumbnail(10,38).rotate(90).depth(8,"d").remap("3,2,1");
        //pixels.remap("1,2,3,3");
/*        ArrayList<Integer> d = pixels.dim();
        Iterator<Integer> di = d.iterator();
        while(di.hasNext())
            System.out.println(di.next());*/
        //pixels.dim();
        //pixels.load();
        //BQImagePlane plane = pixels.planes.get(0);
        //ArrayList<BQImagePlane> band = plane.getBands();
        //Object data = band.get(0).toMatrix();
        //byte[] x = plane.image_byte_data2();
        //byte[] y = band.get(0).image_byte_data2();
        //plane.readImage();
        //Object imagedata = plane.toMatrix();
        //System.out.println(((int[][][])imagedata)[0][0][2]);
        //plane.info();
        //pixels.filename = "image.raw";
        //pixels.perm = 1;
        //pixels.save("http://bodzio.ece.ucsb.edu:8080");
        
        Object im =  BQM.getPixels(image);
        BQImage image_new = (BQImage)BQM.create("image");
        BQM.setGeometry(image_new,512,760,3,1,1);
        BQM.setPixels(image_new, im);
        BQImagePixels pixels = image_new.getPixels();
        //pixels.save("file:///home/boguslaw/Desktop/im.raw");
        
        try{
        //plane.writePlaneToFile("/home/boguslaw/Desktop/im2.tif");
        }
        catch (Exception e){
            BQError.setLastError(e);
        }
        //plane.info();
        //Object imagedata = pixels.getPlaneTZ(0,0).toMatrix();
        //System.out.println("Number of planes: " + pixels.planes.size());
        //Object imagedata = pixels.getPlaneTZ(0,0).toMatrix();
        //BQImagePlane plane = pixels.planes.get(0);
        //plane.info();
        //plane.readImage();
        //plane.saveToFile("/home/boguslaw/Desktop/image.tif");
//         Object data = plane.toMatrix();
//         System.out.println(BQUtil.getArrayDim(data));
//         //object.getClass().isArray();
//         for(int xi=0;xi<pixels.x;xi++){
//             for(int yi=0;yi<pixels.y;yi++){
//                 for(int chi=0;chi<pixels.ch;chi++){
//                     System.out.println( ((Object[][][])data)[xi][yi][chi] );
//                 }
//             }
//         }
    }
    public void testBQImagePlane(){
        BQAuthorization.setAuthorization("admin","admin");
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/13017";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/112";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/104";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/13017";
        BQDataService ds = new BQDataService();
        BQImage image = (BQImage)ds.load(url);
        BQImagePixels pixels = image.getPixels();

        ArrayList<Integer> d = pixels.dim();
        Iterator<Integer> di = d.iterator();
        while(di.hasNext())
            System.out.println(di.next());
        pixels.load();
//        BQImagePlane plane = pixels.getPlaneTZ(0,0);//.toMatrix();
    }
    public void testBQResource(){
        BQAuthorization.setAuthorization("admin","admin");
        System.out.println("");
        String url = "file:///home/boguslaw/Desktop/image.xml";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/112";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/104";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/13017";
        BQDataService ds = new BQDataService();
        //BQImage image = (BQImage)ds.load(url);
        //String response = BQXML.loadXML(url, null, "GET");
        BQResource o = BQDataService.load(url);

//         Iterator<BQResource> chi = o.children.iterator();
//         //Iterator<BQTag> ti = i.getTags().iterator();
//         while (chi.hasNext()) {
//             BQResource ch = chi.next();
//             if (ch.type.equals("tags") || ch.type.equals("gobjects")) {
//                 System.out.println("Resource: " + ch.uri + "; Type: " + ch.type);
//             }
//         }
        
        System.out.println("");
        BQImage image = (BQImage)o;
        System.out.println("Image: src="        + image.src         + "," +
                                    "x="        + image.x           + "," +
                                    "y="        + image.y           + "," +
                                    "z="        + image.z           + "," +
                                    "t="        + image.t           + "," +
                                    "ch="       + image.ch          + "," +
                                    "owner_id=" + image.owner_id    + "," +
                                    "perm="     + image.perm        + "," +
                                    "ts="       + image.ts);

        //Iterator<BQTag> ti = image.tags.iterator();
        //Iterator<BQTag> ti = image.getTags().iterator();
        Iterator ti = image.getIterator("tag");
        //System.out.println ("Iterator is " + ti);
        while (ti.hasNext()) {
                //Object x = ti.next();
                //System.out.println ("iterator " + x);
                BQTag t = (BQTag)ti.next();
                System.out.println("Tag: " + t.name);
        }

//         Iterator<BQGObject> gi = image.getGObjects().iterator();
//         //Iterator<BQGObject> gi = image.gobjects.iterator();
//         while (gi.hasNext()) {
//                 BQGObject g = gi.next();
//                 System.out.println("GObject: " + g.name);
//         }

        //System.out.println(o.children.size());
        //System.out.println(
    }
    public void testBQResourceEmpty(){
        BQAuthorization.setAuthorization("admin","admin");
        System.out.println("");
        String url = "file:///home/boguslaw/Desktop/image.xml";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/112";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/104";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/13017";
        BQDataService ds = new BQDataService();
        //BQImage image = (BQImage)ds.load(url);
        //String response = BQXML.loadXML(url, null, "GET");
        BQResource o = BQDataService.load(url);
        System.out.println(o.getClass().getName());
        Iterator<BQResource> chi = o.children.iterator();
        //Iterator<BQTag> ti = i.getTags().iterator();
        while (chi.hasNext()) {
            BQResource ch = chi.next();
            System.out.println("Resource: " + ((BQObject)ch).uri);
        }

        System.out.println("");
        BQImage image = (BQImage)o;
        System.out.println("Image: src="        + image.src         + "," +
                                    "x="        + image.x           + "," +
                                    "y="        + image.y           + "," +
                                    "z="        + image.z           + "," +
                                    "t="        + image.t           + "," +
                                    "ch="       + image.ch          + "," +
                                    "owner_id=" + image.owner_id    + "," +
                                    "perm="     + image.perm        + "," +
                                    "ts="       + image.ts);

//         System.out.println("");
//         Iterator<BQTag> ti = image.getTags().iterator();
//         while (ti.hasNext()) {
//                 BQTag t = ti.next();
//                 System.out.println("Tag: " + t.name);
//         }
    }
    public void testBQClientService(){
        BQAuthorization.setAuthorization("admin","admin");
        System.out.println("");
        String uri = "http://bodzio.ece.ucsb.edu:8080/";

        BQClientService cs = new BQClientService(uri);
        cs.initialize_services();
        //System.out.println(o.getClass().getName());
    }
    public void testBQ(){
        //BQAuthorization.setAuthorization("admin","admin");
        System.out.println("");
        String uri = "http://bodzio.ece.ucsb.edu:8080";
        
        BQ.initialize(uri, "admin", "admin", "http://bodzio.ece.ucsb.edu:8080/ds/modules/87");
        BQDataService ds = BQ.ds;
        System.out.println(ds.server_uri);
        BQImage image = (BQImage)BQDataService.load("http://bodzio.ece.ucsb.edu:8080/ds/images/104");
        System.out.println("IMAGE: " + image.uri);
        Iterator ti = image.getIterator("tag");
        //System.out.println ("Iterator is " + ti);
        while (ti.hasNext()) {
                BQTag t = (BQTag)ti.next();
                System.out.println("Tag: " + t.name);
        }        

        BQImage im = (BQImage)BQ.create("image");
        Integer x = 100, y = 100, ch = 3, d = 8, z = 2, t = 0;
        String filename = "my image";
        String type = "uint8";
        //BQImagePixels pixels = im.setPixels(x,y,z,t,ch,d,type,filename);
        //Random randomGenerator = new Random();
        /*
        byte[][] array = new byte[ch][x*y];
        int ix = 0;
        for(int i=0; i<x; i++)
            for(int j=0; j<y; j++){
                array[0][ix] = (byte)randomGenerator.nextInt(256);
                array[1][ix] = (byte)randomGenerator.nextInt(256);
                array[2][ix] = (byte)randomGenerator.nextInt(256);
                ix++;
        }
        System.out.println(array[0].length);
        System.out.println("Planes - size: " + pixels.planes.size());
        pixels.setPlane(array,0);
        
        try {ImageIO.write(pixels.planes.get(0).plane, "png", new File("plane1.png")); } 
        catch (IOException e) { e.printStackTrace();}            

        byte[]array2 = new byte[x*y*ch];
        ix = 0;
        for(int i=0; i<x; i++)
            for(int j=0; j<y; j++){
                array2[ix++] = (byte)randomGenerator.nextInt(256);
                array2[ix++] = (byte)randomGenerator.nextInt(256);
                array2[ix++] = (byte)randomGenerator.nextInt(256);
        }
        pixels.setPlane(array,1);
        try {ImageIO.write(pixels.planes.get(1).plane, "png", new File("plane2.png")); } 
        catch (IOException e) { e.printStackTrace();}         
        */

//         byte[][][] array = new byte[z][ch][x*y];
//         for(int k=0; k<z; k++){
//         int ix = 0;
//         for(int i=0; i<x; i++)
//             for(int j=0; j<y; j++){
//                 array[k][0][ix] = (byte)randomGenerator.nextInt(256);
//                 array[k][1][ix] = (byte)randomGenerator.nextInt(256);
//                 array[k][2][ix] = (byte)randomGenerator.nextInt(256);
//                 ix++;
//         }
//         }
//         System.out.println(array[0].length);
//         System.out.println("Planes - size: " + pixels.planes.size());
//         pixels.setImage(array);
//         for(int k=0; k<z; k++)
//         try {ImageIO.write(pixels.planes.get(k).plane, "png", new File("plane" + k +".png")); }
//         catch (IOException e) { e.printStackTrace();}



    }





    public static void main(String args[]){
        //try{
            BQTest testBQ = new BQTest();
            //testBQ.testParseXML_GObject();
            //testBQ.testParseXML_Image();
            //testBQ.testParseXML_ImageSrc();
            //testBQ.testGenXML_Image();
            //testBQ.testSaveFile();
            //testBQ.testSearch();
            //testBQ.testFindTag();
            //testBQ.testLoadObjectFromXMLFile();
            //testBQ.testSaveObjectToXMLFile();
            testBQ.testBQImagePixels();
            //testBQ.testBQResource();
            //testBQ.testBQClientService();
            //testBQ.testBQ();
            //testBQ.testBQResourceEmpty();
            //BQImagePlane plane = new BQImagePlane();
            //plane.readPlaneFromFileTiff();
            //Object data = plane.toMatrix();
            //testBQ.testBQImagePlane();
            //testBQ.testJAI();

        //}
        //catch (Exception e){
        //    BQError.setLastError(e);
        //}
    }

}
