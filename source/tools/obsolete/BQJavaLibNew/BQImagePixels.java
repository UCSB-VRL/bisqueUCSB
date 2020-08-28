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
import java.io.FileOutputStream;
import java.io.Reader;
import java.io.InputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
// Miscellaneous
import java.util.Iterator;
import java.util.ArrayList;
// XML
import org.w3c.dom.Element;
import org.w3c.dom.Document;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import java.awt.image.DataBuffer;
import java.awt.image.DataBufferByte;
import java.awt.image.DataBufferUShort;
import java.awt.image.DataBufferDouble;
import javax.imageio.ImageIO;
import java.nio.ByteOrder;
import javax.imageio.stream.ImageOutputStream;

public class BQImagePixels {
    public String src;
    public Integer x;
    public Integer y;
    public Integer z;
    public Integer t;
    public Integer ch;

    public Integer d;//depth
    public String  f;//format
    public Double  xr;//xRes
    public Double  yr;//yRes
    public Double  zr;//zRes
    public String  e;//endian
    public String  filename;
    public String  type;

    public Integer perm;

    public String fullQuery;
    public ArrayList<String> queries;

    public ArrayList<BQImagePlane> planes;

    public BQImagePixels(){}
    public BQImagePixels(String src_){
        src = src_;
        queries = new ArrayList();
        planes = new ArrayList<BQImagePlane>();
        dim();
    }
    public BQImagePixels(Integer x_, Integer y_, Integer ch_, Integer z_, Integer t_,
                            Integer d_, String type_, String filename_, Integer perm_){
        x = x_;
        y = y_;
        z = z_;
        t = t_;
        ch = ch_;
        d = d_;
        type = type_;
        filename = filename_;
        perm = perm_;
        planes = new ArrayList<BQImagePlane>(z*t);
    }
    public BQImagePixels(BQImage image){
        x = image.x;
        y = image.y;
        z = image.z;
        t = image.t;
        ch = image.ch;
        d = image.d;
        type = image.type;
        filename = image.filename;
        perm = image.perm;
    }
    public void setType (String type_) {
        type = type_;
    }
    public void setDepth (int d_) {
        d = d_;
    }
    public void setPixels (byte[] buffer, int ti, int zi) {
        setPixels(buffer, ti*z+zi);
    }
    public void setPixels (short[] buffer, int ti, int zi) {
        setPixels(buffer, ti*z+zi);
    }
    public void setPixels (double[] buffer, int ti, int zi) {
        setPixels(buffer, ti*z+zi);
    }
    public void setPixels (byte[][] buffer, int ti, int zi) {
        setPixels(buffer, ti*z+zi);
    }
    public void setPixels (short[][] buffer, int ti, int zi) {
        setPixels(buffer, ti*z+zi);
    }
    public void setPixels (double[][] buffer, int ti, int zi) {
        setPixels(buffer, ti*z+zi);
    }
    public void setPixels (byte[] buffer, int ix) {
        BQImagePlane p = new BQImagePlane();
        p.setData(buffer, x, y, ch);
        planes.add(ix, p);
    }
    public void setPixels (short[] buffer, int ix) {
        BQImagePlane p = new BQImagePlane();
        p.setData(buffer, x, y, ch);
        planes.add(ix, p);
    }
    public void setPixels (double[] buffer, int ix) {
        BQImagePlane p = new BQImagePlane();
        p.setData(buffer, x, y, ch);
        planes.add(ix, p);
    }
    public void setPixels (byte[][] buffer, int ix) {
        BQImagePlane p = new BQImagePlane();
        p.setData(buffer, x, y, ch);
        planes.add(ix, p);
    }
    public void setPixels (short[][] buffer, int ix) {
        BQImagePlane p = new BQImagePlane();
        p.setData(buffer, x, y, ch);
        planes.add(ix, p);
    }
    public void setPixels (double[][] buffer, int ix) {
        BQImagePlane p = new BQImagePlane();
        p.setData(buffer, x, y, ch);
        planes.add(ix, p);
    }
    public void setPixels (byte[][][] buffer) {
        for(int zi=0; zi<(z+t); zi++){
            BQImagePlane p = new BQImagePlane();
            p.setData(buffer[zi], x, y, ch);
            planes.add(p);
        }
        src = save(BQ.cs.top_uri);
    }
    public void setPixels (short[][][] buffer) {
        for(int zi=0; zi<(z*t); zi++){
            BQImagePlane p = new BQImagePlane();
            p.setData(buffer[zi], x, y, ch);
            planes.add(p);
        }
        src = save(BQ.cs.top_uri);
    }
    public void setPixels (double[][][] buffer) {
        for(int zi=0; zi<(z*t); zi++){
            BQImagePlane p = new BQImagePlane();
            p.setData(buffer[zi], x, y, ch);
            planes.add(p);
        }
        src = save(BQ.cs.top_uri);
    }
    public void setPixels (ArrayList<DataBuffer> buffers) {
        for(int zi=0; zi<(z*t); zi++){
            BQImagePlane p = new BQImagePlane();
           System.out.println("BUFFER: " + buffers.get(zi).getNumBanks());
            if (buffers.get(zi).getDataType() == DataBuffer.TYPE_BYTE)
                p.setData(((DataBufferByte)buffers.get(zi)).getBankData(), x, y, ch);
            if (buffers.get(zi).getDataType() == DataBuffer.TYPE_USHORT) 
                p.setData(((DataBufferUShort)buffers.get(zi)).getBankData(), x, y, ch);
            if (buffers.get(zi).getDataType() == DataBuffer.TYPE_DOUBLE) 
                p.setData(((DataBufferDouble)buffers.get(zi)).getBankData(), x, y, ch);
            planes.add(p);
        }
        src = save(BQ.cs.top_uri);
    }
    public ArrayList<DataBuffer> getPixels () {
        ArrayList<DataBuffer> buffers = new ArrayList<DataBuffer>();
        Iterator<BQImagePlane> pi = planes.iterator();
        while (pi.hasNext()) {
            BQImagePlane p = pi.next();
            p.untileImage();
            //System.out.println("Image paramaters (x,y,d,ch,t,z):"+x+","+y+","+d+","+ch+","+t+","+ z);
            buffers.add(p.readDataBuffer());
        }
        return buffers;
    }
    public void load(){
        try{
            System.out.println("Image paramaters (x,y,d,ch,t,z):"+x+","+y+","+d+","+ch+","+t+","+ z);
            String encoding = BQAuthorization.getEncoded();
            for(int ti=0; ti<t; ti++){
                for(int zi=0; zi<z; zi++){
                    String urlQuery = fullQuery;
                    if (z > 1 && t > 1)     urlQuery += "slice=,," + zi + "," + ti +","+"&format=tiff,compression,none";
                    if (z == 1 && t > 1)    urlQuery += "slice=,,,"+ ti + "," +         "&format=tiff,compression,none";
                    if (z > 1 && t == 1)    urlQuery += "slice=,," + zi + ",,"+         "&format=tiff,compression,none";
                    if (z == 1 && t == 1)   urlQuery += "format=tiff,compression,none";
                    System.out.println("URL: " + urlQuery);
                    URL server = new URL(urlQuery);
                    HttpURLConnection connection = (HttpURLConnection)server.openConnection();
                    connection.setUseCaches(true);
                    connection.setDoInput(true);
                    connection.setReadTimeout(3000);
                    connection.setRequestMethod("GET");
                    connection.setRequestProperty("Connection", "Keep-Alive");
                    connection.setRequestProperty ("Authorization", "Basic " + encoding);
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

    public String save(String uri){
        try{
            String response = null;
            URL url = new URL(uri);
            if("file".equals(url.getProtocol())){
                System.out.println("Save to file ...");
                if ((url.getHost() != null) && !url.getHost().equals("")) {
                    response = saveToFile(url.getHost() + ":" + url.getFile()); //win
                }
                else{
                    response = saveToFile(url.getFile()); //linux
                }
            }
            else if("http".equals(url.getProtocol())){
                System.out.println("Save to http ...");
                response = saveToHTTP(uri);
            }
            return response;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return null;
        }
    }
    public String saveToFile(String uri){
        try{
            DataOutputStream data = new DataOutputStream(new BufferedOutputStream(new FileOutputStream(uri), 1024));
            Iterator<BQImagePlane> pi = planes.iterator();
            while (pi.hasNext()) {
                BQImagePlane p = pi.next();
                p.writePlane(data);
                System.out.println("sending ....");
            }
            data.flush();
            data.close();
            return uri;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return null;
        }
    }
    public String saveToHTTP(String serverUri){
        try{
            String response = null;
            String encoding = BQAuthorization.getEncoded();
            String boundary = "--------------------" + Long.toString(System.currentTimeMillis(), 30);
            //int d = 8;
            //if (type.equals("uint8"))     d = 8;
            //if (type.equals("uint16"))    d = 16;
            //if (type.equals("double"))    d = 32;
            if (d==8)  type = "uint8";
            if (d==16) type = "uint16";
            if (d==32) type = "double";
            String urlQuery =
                    "?width="       + x +   "&height="  + y + "&zsize=" + z +       "&tsize="       + t +
                    "&channels="    + ch +  "&depth="   + d + "&type="  + type +    "&userPerm="    + perm +
                    "&endian="      + System.getProperties().getProperty("sun.cpu.endian" )+
                    "&format=raw";
            System.out.println(urlQuery);
            URL server = new URL(serverUri + "/bisquik/upload_raw_image" + urlQuery);
            HttpURLConnection connection = (HttpURLConnection)server.openConnection();
            //Set post parameters;
            connection.setDoOutput(true);
            connection.setDoInput(true);
            connection.setUseCaches(false);
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Connection", "Keep-Alive");
            connection.setRequestProperty("Authorization", "Basic " + encoding);
            connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);
            //connection.setRequestProperty("Content-Disposition", "form-data; name=\"upload\"; filename=\" " + file.getName() + " \"");
            connection.connect();
            //------------------------------------------------------
            DataOutputStream data = new DataOutputStream(new BufferedOutputStream(connection.getOutputStream(), 1024));
            data.writeBytes("--" + boundary + "\r\n");
            data.writeBytes("Content-Disposition: form-data; name=\"upload\"; filename=\" " +  filename + " \"\r\n");
            data.writeBytes("Content-Type: application/octet-stream\r\n");
            data.writeBytes("\r\n");
            //------------------------------------------------------
            Iterator<BQImagePlane> pi = planes.iterator();
            while (pi.hasNext()) {
                BQImagePlane p = pi.next();
                p.writePlane(data);
                System.out.println("sending ....");
            }
            //------------------------------------------------------
            data.writeBytes("\r\n--" + boundary + "--\r\n");
            data.flush();
            data.close();
            //------------------------------------------------------
            //Response
            if (connection.getResponseCode() == 200){
                Object contents = connection.getContent();
                InputStream contentStream = (InputStream)contents;
                if (connection.getContentType().compareTo("text/xml") == 0){
                    try{
                        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
                        DocumentBuilder builder = factory.newDocumentBuilder();
                        Document document = builder.parse(contentStream);
                        response = BQXML.xmlToString(document);
                    }
                    catch (Exception e){
                        System.out.println(e);
                        return null;
                    }
                }
                else{
                    StringBuffer sb = new StringBuffer();
                    Reader reader = new InputStreamReader(contentStream, "UTF-8");
                    int c;
                    while ((c = contentStream.read()) != -1) sb.append((char)c);
                    response = sb.toString();
                    System.out.println(response);
                }
            }
            else{
                System.out.println("Error connection, code:" + connection.getResponseCode() + "\n");
                return null;
            }
            connection.disconnect();
            return response;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return null;
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
