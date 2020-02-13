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
import org.w3c.dom.Document;
import org.w3c.dom.Element;

//import javax.media.jai.JAI;
//import com.sun.media.jai.operator.ImageReadDescriptor;


public class BQMatlab{
	
	public static BQDataService ds;
	public static BQClientService cs;
    public static BQMEX mex;
	
	//--------------------------------------------------------------
	// SERVER
	//--------------------------------------------------------------
	public static void initServers(String ds_uri, String cs_uri){
		cs = new BQClientService(cs_uri);
		ds = new BQDataService(ds_uri);
	}

    // Initialze module from pre-existing MEX
    public static BQMEX initialize(String bisque_url, String mex_url, 
                                   String access_token) {
        cs = new BQClientService(bisque_url);
        ds = new BQDataService (bisque_url + "/ds");
        BQAuthorization.setAuthorization(access_token);

        mex = loadMEX(mex_url);

        return mex;
    }
    // Initialize module 
    public static BQMEX initialize(String bisque_url, String module_uri, String user, String pwd) {
        return null;
    }

    public static String finished(BQMEX mex, String msg){
        mex.status = "FINISHED";
        if (msg != null && msg != "") 
            addTag(mex, "message", msg);
        String response = updateMEX(mex);
        return response;
    }
    
    public static String failed(BQMEX mex, String msg){
        mex.status = "FAILED";
        if (msg != null && msg != "") 
            addTag(mex, "message", msg);
        String response = updateMEX(mex);
        return response;
    }

	public static void login(String name, String pass){
		BQAuthorization.setAuthorization(name, pass);
	}
	//--------------------------------------------------------------
	// IMAGE
	//--------------------------------------------------------------
	public static BQImage loadImage(String uri){
		BQImage image = (BQImage)ds.load(uri);
		return image;
	}
	public static Object loadImageData(BQImage image){
		Object imagedata = image.getData();
		return imagedata;
	}
    public static Object loadImageDataCH(BQImage image, int selectedChannel){
        Object imagedata = image.getDataCH(selectedChannel);
        return imagedata;
    }
    public static Object loadImageDataParam(BQImage image, String param){
		Object imagedata = image.getData(param);
		return imagedata;
	}

	public static BQImage initImage(int x, int y, int z, int t, int ch, int d, String type, String filename, int perm){
		BQImage image = new BQImage( new Integer(x), new Integer(y), new Integer(z), new Integer(t), new Integer(ch), new Integer(d), type, filename, new Integer(perm) );
		return image;
	}
	public static BQImage initImage(int x, int y, int z, int t, int ch, int d, String type, int perm){
		BQImage image = new BQImage( new Integer(x), new Integer(y), new Integer(z), new Integer(t), new Integer(ch), new Integer(d), type, "matlab.raw", new Integer(perm) );
		return image;
	}
	
	public static String saveImage(BQImage image, Object imagedata){
		// Send data to image server getting src
		// Prepare image with src and save to data server .
		//BQClientService.upload_raw (image, imagedata);
        BQObject response = cs.upload_image (image, imagedata);
		//String response = image.postData(cs.server_uri, imagedata);
        if (response != null) {
            image.uri = response.uri;
            return response.uri;
        }
        return null;
	}

	public static String saveFile(String path){
		// Send data to image server getting src
		// Prepare image with src and save to data server .
        BQObject response = cs.upload_file (path);
		//String response = image.postData(cs.server_uri, imagedata);
        if (response != null) {
            return response.src;
        }
        return null;
	}

	public static String saveImageData(BQImage image, Object imagedata){
		String response = image.postData(ds.server_uri, imagedata);
		image.uri = response;
		return response;
	}

	public static void deleteImage(String uri){
		BQImage image = (BQImage)ds.load(uri);
		image.deleteData(image.uri);
	}
	
	public static Object loadResizedImageData(BQImage image, int width, int height)
	{
		BQImagePixels pixels = image.getPixels();
  	        pixels.resize(width, height);
  	        pixels.constructQuery();
  	        pixels.load();
        	return pixels.toMatrix();
	}

	//--------------------------------------------------------------
	// Thumbnail
	//--------------------------------------------------------------
	public static Object loadThumbnailData(BQImage image, int width, int height){
		BQThumbnail th = new BQThumbnail();
		Object imagedata = th.getData(image.uri, width, height);
		return imagedata;
	}
	public static Object loadThumbnailData(String uri, int width, int height){
		BQThumbnail th = new BQThumbnail();
		Object imagedata = th.getData(uri, width, height);
		return imagedata;
	}
	//--------------------------------------------------------------
	// OBJECT
	//--------------------------------------------------------------
	public static BQObject loadObjectFromXMLFile(String filePath){
		BQDataService ds = new BQDataService();
		BQObject object = ds.loadFile(filePath);
		return object;
	}	
	public static void saveObjectToXMLFile(BQObject o, String filePath){
		BQDataService ds = new BQDataService();
		ds.saveFile(o, filePath);
	}	
	//--------------------------------------------------------------
	// TAG
	//--------------------------------------------------------------
	public static BQTag createTag(String name, String value){
		BQTag tag = new BQTag(name, value);
		return tag;
	}
	public static void addTag(BQObject object, BQTag tag){
		object.tags.add(tag);
	}
	public static BQTag addTag(BQObject object, String name, String value){
		BQTag r = new BQTag(name, value);
		object.tags.add(r);
		return r;
	}
	public static BQTag addTag(BQObject object, String name, double value){
		BQTag r = new BQTag(name, new Double(value));
		object.tags.add(r);
		return r;
	}
	public static String saveTag(BQObject object, BQTag tag){
		BQDataService dsn = new BQDataService(object.uri);
		String response = dsn.save(tag);
                Document doc = BQXML.stringToXML(response);
                Element root  = BQXML.getChildElement((Element)doc.getDocumentElement());
                response = BQXML.AttrStr (root, "uri");
                System.out.println("Tag is saved: " + response);
		return response;
	}
    public static void updateTag(BQObject object, BQTag tag){
        BQDataService dsn = new BQDataService(object.uri);
        dsn.update(tag);
    }
    public static String saveTagURL(BQObject object, BQTag tag){ // FIXME - remove
        BQDataService dsn = new BQDataService(object.uri);
        String response = dsn.save(tag);
        //System.out.println(response);
        Document doc = BQXML.stringToXML(response);
        Element root  = BQXML.getChildElement((Element)doc.getDocumentElement());
        response = BQXML.AttrStr (root, "uri");
        return response;
    }
	public static String findTag(BQObject object, String name){
		BQImage image = (BQImage)ds.load(object.uri + "?view=deep");
		BQTag tag  = image.findTag(name);
		if (tag!=null) return tag.getValue();
		else return null;
	}
    public static void deleteTagFull(BQObject image_or_tag){
        if(image_or_tag.uri != null) {
            System.out.println(image_or_tag.uri);
            ArrayList<BQTag> tags = image_or_tag.tags;
            Iterator<BQTag> li = tags.iterator();
            while (li.hasNext()){
                BQTag tag = li.next();
                System.out.println(tag.uri);
                BQDataService dsn = new BQDataService(tag.uri);
                dsn.delete(tag);
            }
        }
    }
	
    public static void deleteTag(BQObject object, String name){
        if(name != null) {
	   BQImage image = (BQImage)ds.load(object.uri + "?view=deep");
	   BQTag tag  = image.findTag(name);
	   if(tag!= null){
	           System.out.println(tag.uri);
        	   BQDataService dsn = new BQDataService(tag.uri);
        	   dsn.delete(tag);
		}		
            }
    }	
	//--------------------------------------------------------------
	// GOBJECT
	//--------------------------------------------------------------
	public static BQGObject createGObject(String type, String name){
		BQGObject gobject = new BQGObject(type, name);
		return gobject;
	}
	public static void addGObject(BQObject image_or_gobject, BQGObject gobject){
		image_or_gobject.gobjects.add(gobject);
	}	
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
	public static String saveGObject(BQObject image_or_gobject, BQGObject gobject){
        	BQDataService dsn = new BQDataService(image_or_gobject.uri);
        	String response = dsn.save(gobject);
        	Document doc = BQXML.stringToXML(response);
        	Element root  = BQXML.getChildElement((Element)doc.getDocumentElement());
        	response = BQXML.AttrStr (root, "uri");
        	System.out.println("GObject is saved: " + response);
            	return response;
	}	
    public static String saveGObjectURL(BQObject image_or_gobject, BQGObject gobject){
        BQDataService dsn = new BQDataService(image_or_gobject.uri);
        String response = dsn.save(gobject);
        Document doc = BQXML.stringToXML(response);
        Element root  = BQXML.getChildElement((Element)doc.getDocumentElement());
        response = BQXML.AttrStr (root, "uri");
        System.out.println("GObject saved at:" + response);
        return response;
    }
    public static void deleteGObjectFull(BQObject image_or_gobject){
        if(image_or_gobject.uri != null) {
            System.out.println(image_or_gobject.uri);
            ArrayList<BQGObject> objects = image_or_gobject.gobjects;
            Iterator<BQGObject> li = objects.iterator();
            while (li.hasNext()){
                BQGObject object = li.next();
                System.out.println(object.uri);
                BQDataService dsn = new BQDataService(object.uri);
                dsn.delete(object);
            }
        }
    }
    public static void deleteGObject(BQObject image_or_gobject){
        if(image_or_gobject.uri != null) {
            BQDataService dsn = new BQDataService(image_or_gobject.uri);
            dsn.delete(image_or_gobject);
        }
    }
    //--------------------------------------------------------------
    // MODULE
    //--------------------------------------------------------------
    public static BQMEX loadMEX(String uri){
        BQMEX mex = (BQMEX)ds.load(uri + "?view=deep");
        return mex;
    }
    public static String updateMEX(BQMEX mex){
        BQDataService dsn = new BQDataService(mex.uri);
        String response = dsn.save(mex);
        return response;
    }
    public static String updateProgress(BQMEX mex, int status){
        mex.status = Integer.toString(status) + "%"; 
        String response = updateMEX(mex);
        return response;
    }
    public static String updateProgress(BQMEX mex, String status){
        mex.status = status;
        String response = updateMEX(mex);
        return response;
    }
	//--------------------------------------------------------------
	// UTILs
	//--------------------------------------------------------------
	public static ArrayList<String> search(String query){
		ArrayList<String> results = new ArrayList();
		ArrayList<BQObject> objects = ds.search(query);
		Iterator<BQObject> li = objects.iterator();
		while (li.hasNext()){
			BQObject object = li.next();
			results.add(object.uri);
		}
		return results;
	}	
    public String postImageFile(String serverUri, String filePath) {
        BQImage im = new BQImage();
        String response = im.postImageFromFile(serverUri, filePath);
        return response;
    }
    //--------------------------------------------------------------
    // JAI
    //--------------------------------------------------------------
    public static Object loadImagePixels(BQImage image){
        BQImagePixels pixels = image.getPixels();
        //pixels.roi(10,10,145,132);
        pixels.load();
        return pixels.toMatrix();
    }
    public static Object loadImagePlane(BQImage image, int tp, int zp){
        BQImagePixels pixels = image.getPixels();
        //pixels.roi(10,10,145,132);
        pixels.load();
        return pixels.getPlaneTZ(tp-1,zp-1).toMatrix();
    }
    public Object getMyPixels(){
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
        Object data = null;
        return data;
    }
    // public void JAI(){
    //     //BQJAIInfo jai = new BQJAIInfo();
    //     ImageReadDescriptor descriptor = new ImageReadDescriptor (); 
    //     System.out.println("ImageRead ClassLoader: "+descriptor.getClass().getClassLoader()); 
    //     System.out.println("JAI ClassLoader: "+JAI.class.getClassLoader()); 
    // }
    //--------------------------------------------------------------
 }
