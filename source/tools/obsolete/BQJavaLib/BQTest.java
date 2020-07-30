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
import java.util.Iterator;
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
		System.out.println("Image: 	src="		+ image.src			+ "," +
									"x="		+ image.x			+ "," +
									"y="		+ image.y			+ "," +
									"z="		+ image.z			+ "," +
									"t="		+ image.t			+ "," +
									"ch="		+ image.ch			+ "," +
									"owner_id="	+ image.owner_id	+ "," +
									"perm="		+ image.perm		+ "," +
									"ts="		+ image.ts);	
	}
	public void testParseXML_ImageSrc(){
		BQAuthorization.setAuthorization("admin","admin");
		String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/124";
		BQDataService ds = new BQDataService();
		BQImage image = (BQImage)ds.load(url);
		System.out.println("Image: 	src="		+ image.src			+ "," +
									"x="		+ image.x			+ "," +
									"y="		+ image.y			+ "," +
									"z="		+ image.z			+ "," +
									"t="		+ image.t			+ "," +
									"ch="		+ image.ch			+ "," +
									"owner_id="	+ image.owner_id	+ "," +
									"perm="		+ image.perm		+ "," +
									"ts="		+ image.ts);	
		
		image.getInfo();
		System.out.println("Image: 	src="		+ image.src			+ "," +
									"d="		+ image.d			+ "," +
									"f="		+ image.f			+ "," +
									"xr="		+ image.xr			+ "," +
									"yr="		+ image.yr			+ "," +
									"zr="		+ image.zr			+ "," +
									"e="		+ image.e);	
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
		BQObject image = ds.loadFile(filePath);
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
        String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/104";
        //String url = "http://bodzio.ece.ucsb.edu:8080/ds/images/13017";
        BQDataService ds = new BQDataService();
        BQImage image = (BQImage)ds.load(url);
        BQImagePixels pixels = image.getPixels();
        //p.slice(null,null,1,2).format("raw").slice("30-25",null,"1","2-5").roi(10,10,45,32).thumbnail(10,38).rotate(90).depth(8,"d").remap("3,2,1");
        pixels.roi(10,10,45,32);
        ArrayList<Integer> d = pixels.dim();
        Iterator<Integer> di = d.iterator();
        while(di.hasNext())
            System.out.println(di.next());
        pixels.load();
        //System.out.println("Number of planes: " + pixels.planes.size());
        //Object imagedata = pixels.getPlaneTZ(0,0).toMatrix();
        //BQImagePlane plane = pixels.planes.get(0);
        //plane.info();
        //plane.readImage();
        //Object data = plane.toMatrix();
        //System.out.println(BQUtil.getArrayDim(data));
//         object.getClass().isArray();
//         for(int xi=0;xi<pixels.x;xi++){
//             for(int yi=0;yi<pixels.y;yi++){
//                 for(int chi=0;chi<pixels.ch;chi++){
//                     System.out.println( ((Object[][][])data)[xi][yi][chi] );
//                 }
//             }
//         }
    }
    public void testJAI(){
        //BQJAI bm = new BQJAI();
        //bm.createRGBTiledImage(); 
        //bm.readImageFromURL("");
        //bm.readRGBTiledImage("rgbpattern.tif"); 

    }
    public static void main(String args[]){
        try{
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
            //testBQ.testJAI();

        }
        catch (Exception e){
            BQError.setLastError(e);
        }
    }

}

