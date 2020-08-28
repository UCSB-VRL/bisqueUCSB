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
// URL
import java.net.URL;
import java.net.URLConnection;
import java.net.HttpURLConnection;
// I/O
import java.io.DataInputStream;
import java.io.BufferedInputStream;
// Miscellaneous
import java.util.Iterator;
import java.util.ArrayList;

public class BQImagePixels {
    public String src;
    public String fullQuery;
    public ArrayList<String> queries;
    public Integer x, y, z, t, ch, d;	
    public ArrayList<BQImagePlane> planes;

    public BQImagePixels(String src_){
        src = src_;
        queries = new ArrayList();
        planes = new ArrayList<BQImagePlane>();
    }
    public void load(){
        try{
            System.out.println("Image paramaters (x,y,d,ch,t,z):"+x+","+y+","+d+","+ch+","+t+","+ z);
            for(int ti=0; ti<t; ti++){
                for(int zi=0; zi<z; zi++){
                    String urlQuery = fullQuery;
                    if (z > 1 && t > 1)     urlQuery += "slice=,," + zi + "," + ti +","+"&format=raw";
                    if (z == 1 && t > 1)    urlQuery += "slice=,,,"+ ti + "," +         "&format=raw";
                    if (z > 1 && t == 1)    urlQuery += "slice=,," + zi + ",,"+         "&format=raw";
                    if (z == 1 && t == 1)   urlQuery += "format=raw";
                    System.out.println("URL: " + urlQuery);
                    URL server = new URL(urlQuery);
                    HttpURLConnection connection = (HttpURLConnection)server.openConnection();
                    connection.setUseCaches(true);
                    connection.setDoInput(true);
                    connection.setReadTimeout(3000);
                    connection.setRequestMethod("GET");
                    //connection.setRequestProperty("Connection", "Keep-Alive");
                    BQAuthorization.addAuth(connection);
                    connection.connect();
                    System.out.println("Start reading image ...");
                    DataInputStream stream = new DataInputStream(new BufferedInputStream(connection.getInputStream(), 1024));
                    BQImagePlane plane = new BQImagePlane();
                    plane.readPlane( stream, x, y, ch, d );
                    //plane.info();
                    planes.add( plane );
                    stream.close();
                    connection.disconnect();
                    System.out.println("Reading is finished :)");
                }
            }
        }
        catch (Exception e){
            BQError.setLastError(e);
        }
    }
    public BQImagePlane getPlaneTZ(int tp, int zp) {
        BQImagePlane planeTZ = null;
        if(tp>t && tp<0) tp = 0;
        if(zp>z && zp<0) zp = 0;
        int ix = 0;
        for(int ti=0; ti<t; ti++)
            for(int zi=0; zi<z; zi++){
                if (ti==tp && zi==zp)
                    planeTZ = planes.get(ix); 
                ix++;
            }
        return planeTZ;
    }
    public void constructQuery() {
        fullQuery = "";
        //format("raw");
        Iterator<String> qi = queries.iterator();
        fullQuery = src;
        if (qi.hasNext()){
            fullQuery += "?";
            fullQuery += qi.next();
            while(qi.hasNext())
                fullQuery += "&" + qi.next();
            fullQuery += "&";
        }
        else
            fullQuery += "?";
    }
    public ArrayList<Integer> dim() {
        ArrayList<Integer> dimension = new ArrayList();
        constructQuery();
        String urlQuery = fullQuery;
        Iterator<String> qi = queries.iterator();
        if (qi.hasNext())
            urlQuery += "dims";
        else
            urlQuery += "dims";
        System.out.println(urlQuery);

        BQDataService ds = new BQDataService();
        BQImage image = (BQImage)ds.load(urlQuery);
        for (int i=0; i<image.tags.size(); i++){
            BQTag tag = image.tags.get(i);
            if (tag.equals("width"))
                x = Integer.valueOf(tag.getValue());
            if (tag.equals("height"))
                y = Integer.valueOf(tag.getValue());
            if (tag.equals("zsize"))
                z = Integer.valueOf(tag.getValue());
            if (tag.equals("tsize"))
                t = Integer.valueOf(tag.getValue());
            if (tag.equals("channels"))
                ch = Integer.valueOf(tag.getValue());
            if (tag.equals("depth"))
                d = Integer.valueOf(tag.getValue());
        }
        dimension.add(x);
        dimension.add(y);
        dimension.add(z);
        dimension.add(t);
        dimension.add(ch);
        dimension.add(d);
        return dimension;
    }
    public BQImagePixels slice(Integer x, Integer y, Integer z, Integer t) {
        StringBuffer query = new StringBuffer("slice=");
        if (x != null)
            query.append(x.toString());
        query.append(",");
        if (y != null)
            query.append(y.toString());
        query.append(",");
        if (z != null)
            query.append(z.toString());
        query.append(",");
        if (t != null)
            query.append(t.toString());
        query.append(",");
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels slice(String x, String y, String z, String t) {
        StringBuffer query = new StringBuffer("slice=");
        if (x != null)
            query.append(x);
        query.append(",");
        if (y != null)
            query.append(y);
        query.append(",");
        if (z != null)
            query.append(z);
        query.append(",");
        if (t != null)
            query.append(t);
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels roi(Integer x1, Integer y1, Integer x2, Integer y2) {
        StringBuffer query = new StringBuffer("roi=");
        if (x1 != null)
            query.append(x1.toString());
        query.append(",");
        if (y1 != null)
            query.append(y1.toString());
        query.append(",");
        if (x2 != null)
            query.append(x2.toString());
        query.append(",");
        if (y2 != null)
            query.append(y2.toString());
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels resize(Integer w, Integer h) {
        StringBuffer query = new StringBuffer("resize=");
        if (w != null)
            query.append(w.toString());
        query.append(",");
        if (h != null)
            query.append(h.toString());
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels resize(Integer w, Integer h, String m, String ar) {
        // ASK dima
        StringBuffer query = new StringBuffer("resize=");
        if (w != null)
            query.append(w.toString());
        query.append(",");
        if (h != null)
            query.append(h.toString());
        query.append(",");
        if (m != null)
            query.append(m);
        query.append(",");
        if (ar != null)
            query.append(ar);
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels format(String f) {
        StringBuffer query = new StringBuffer("format=");
        if (f != null)
            query.append(f);
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels thumbnail(Integer w, Integer h) {
        StringBuffer query = new StringBuffer("thumbnail=");
        if (w != null)
            query.append(w.toString());
        query.append(",");
        if (h != null)
            query.append(h.toString());
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels depth(Integer d, String p) {
        StringBuffer query = new StringBuffer("depth=");
        if (d != null)
            query.append(d.toString());
        query.append(",");
        if (p != null)
            query.append(p);
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels remap(String ch) {
        StringBuffer query = new StringBuffer("remap=");
        if (ch != null)
            query.append(ch);
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels rotate(Integer a) {
        StringBuffer query = new StringBuffer("rotate=");
        if (a != null)
            query.append(a.toString());
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels sampleframes(Integer n) {
        StringBuffer query = new StringBuffer("sampleframes=");
        if (n != null)
            query.append(n.toString());
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels projectmax() {
        StringBuffer query = new StringBuffer("projectmax");
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels projectmin() {
        StringBuffer query = new StringBuffer("projectmin");
        queries.add(query.toString());
        return this;
    }
    public BQImagePixels negative() {
        StringBuffer query = new StringBuffer("negative");
        queries.add(query.toString());
        return this;
    }
    public Object toMatrix(){
        Object[] tobject = new Object[t];
        int ix = 0;
        System.out.println("IN1");
        for(int ti=0; ti<t; ti++){
            Object[] zobject = new Object[z];
            tobject[ti] = zobject;
            System.out.println("IN1");
            for(int zi=0; zi<z; zi++){
                zobject[zi] = planes.get(ix).toMatrix();
                System.out.println("IN3");
                ix++;
            }
        }
        return tobject;
    }
}
