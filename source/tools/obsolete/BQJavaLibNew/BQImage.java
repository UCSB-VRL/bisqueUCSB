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
import java.lang.reflect.Array;
import org.w3c.dom.Element;
import org.w3c.dom.Document;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.net.URL;
import java.net.URLConnection;
import java.net.HttpURLConnection;
import java.io.File;
import java.io.Reader;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.EOFException;
import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.DataOutputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;

public class BQImage extends BQObject{

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

    BQImagePixels pixels;

    public BQImage(){
        super (null, "image");
    }
    public BQImage(String uri){
        super(uri, "image");
    }
    public BQImage(Integer x_, Integer y_, Integer ch_, Integer z_, Integer t_){
        x = x_;
        y = y_;
        z = z_;
        t = t_;
        ch = ch_;
    }
    public BQImage(Integer x_, Integer y_, Integer ch_, Integer z_,
                Integer t_, Integer d_, String type_, String filename_, Integer perm_){
        x = x_;
        y = y_;
        z = z_;
        t = t_;
        ch = ch_;
        d = d_;
        type = type_;
        filename = filename_;
        perm = perm_;
    }
    public void initializeXml(Element el){
        super.initializeXml(el);
        src   = BQXML.AttrStr(el,    "src");
        x     = BQXML.AttrInt(el,    "x");
        y     = BQXML.AttrInt(el,    "y");
        z     = BQXML.AttrInt(el,    "z");
        t     = BQXML.AttrInt(el,    "t");
        ch    = BQXML.AttrInt(el,    "ch");
        d     = BQXML.AttrInt(el,    "d");
    }
    public Element toXml(Document doc, Element el) {
        if (el == null ) 
            el = doc.createElement("image");
        super.toXml (doc, el);
        BQXML.IntAttr(el, "x", x);
        BQXML.IntAttr(el, "y", y);
        BQXML.IntAttr(el, "z", z);
        BQXML.IntAttr(el, "t", t);
        BQXML.IntAttr(el, "ch",ch);
        if (pixels != null)
            if (pixels.src != null)
                BQXML.StrAttr(el, "src", pixels.src);
        return el;
    }
    public void getInfo(){
        BQDataService ds = new BQDataService();
        BQImage image = (BQImage)ds.load(src + "?info");
        for (int i=0; i<image.tags.size(); i++){
            BQTag t = image.tags.get(i);
            if (t.equals("depth"))
                d = Integer.valueOf(t.getValue());
            if (t.equals("format"))
                f = t.getValue();
            if (t.equals("xRes"))
                xr = Double.valueOf(t.getValue());
            if (t.equals("yRes"))
                yr = Double.valueOf(t.getValue());
            if (t.equals("zRes"))
                zr = Double.valueOf(t.getValue());
            if (t.equals("endian"))
                e = t.getValue();
            if (t.equals("filename"))
                filename = t.getValue();
        }
    }
    public BQImagePixels getPixels(){
        if (pixels == null){
            if (src == null)
                pixels = new BQImagePixels();
            else
                pixels = new BQImagePixels(src);
        }
        return pixels;
    }
    // May be called on a brand-new image only.. 
    public BQImagePixels setPixels( Integer x_, Integer y_, Integer ch_, Integer z_, Integer t_,
                                    Integer d_, String type_, String filename_){
        if (pixels == null && src == null) {
            x = x_;
            y = y_;
            z = z_;
            t = t_;
            ch = ch_;
            d = d_;
            type = type_;
            filename = filename_;
            perm = 1;

            pixels = new BQImagePixels(x, y, ch, z, t, d, type, filename, this.perm);
            return pixels;
        }
        //throw IllegalOperation ("Image has pixels defined");
        return null;
    }
    public void savePerm(int p){ perm = p; }
    public void saveToFile(String path){
        try{
            getInfo();
            String encoding = BQAuthorization.getEncoded();
            URL server = new URL(src);
            HttpURLConnection connection = (HttpURLConnection)server.openConnection();
            connection.setUseCaches(true);
            connection.setDoInput(true);
            connection.setDoOutput(true);
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Connection", "Keep-Alive");            
            connection.setRequestProperty ("Authorization", "Basic " + encoding);
            connection.connect();
            DataInputStream data = new DataInputStream(new BufferedInputStream(connection.getInputStream(), 1024));
            OutputStream ostream = new FileOutputStream(path + filename);
            byte bytedata;
            try{
                byte[] buffer = new byte[4096];
                int byteCnt = 0;
                while (true){
                    int bytes = data.read(buffer);
                    if (bytes < 0) break;
                    byteCnt += bytes;
                    ostream.write(buffer, 0, bytes);
                }
                ostream.flush();
            }
            finally{
                data.close();
                ostream.close();
            }
        }
        catch (Exception e){
            System.out.println(e.getMessage());
            BQError.setLastError(e);
        }
    }
    public Object getData(){
        try{
            getInfo();
            System.out.println("Image paramaters (x,y,d,ch,t,z): "+x+","+y+","+d+","+ch+","+t+","+ z);
            int dimL = 2;
            if (ch > 1)    dimL++;
            if (z  > 1)    dimL++;
            if (t  > 1)    dimL++;
            int [] dim = new int[dimL];
            dim[0] = (int)y;
            dim[1] = (int)x;
            //if(channels > 1 && zsize == 1 && tsize == 1)
            if (ch >  1)                            dim[2] = (int)ch;
            if (ch == 1     && z >  1     && t == 1)    dim[2] = (int)z;
            if (ch == 1     && z == 1     && t >  1)    dim[2] = (int)t;
            if (ch == 1     && z >  1     && t >  1)    dim[3] = (int)t;
            if (ch >  1     && z >  1     && t == 1)    dim[3] = (int)z;
            if (ch >  1     && z == 1     && t >  1)    dim[3] = (int)t;
            if (ch >  1     && z >  1     && t >  1)    dim[4] = (int)t;
            //for(int i=0;i<dimL;i++) System.out.println(dim[i]);
            Object o = new int[1];
            Object array = Array.newInstance(BQUtil.getArrayComponent(o), dim);
            //System.out.println("Matrix dimention: " + BQUtil.getArrayDim(array));
            //String encoding = BQAuthorization.getEncoded();
            for(int ti=0; ti<t; ti++){
                for(int zi=0; zi<z; zi++){
                    String urlQuery = "?format=raw";
                    if (z > 1 && t > 1)        urlQuery = "?slice=,," + zi + "," + ti +","+"&format=raw";
                    if (z == 1 && t > 1)    urlQuery = "?slice=,,,"+ ti + "," +         "&format=raw";
                    if (z > 1 && t == 1)    urlQuery = "?slice=,," + zi + ",,"+            "&format=raw";
                    if (z == 1 && t == 1)    urlQuery = "?format=raw";
                    //System.out.println("URL: " + src + urlQuery);
                    URL server = new URL(src + urlQuery);
                    HttpURLConnection connection = (HttpURLConnection)server.openConnection();
                    //connection.setDoOutput(true);
                    //connection.setDoInput(true);
                    connection.setUseCaches(true);
                    connection.setDoInput(true);
                    connection.setReadTimeout(3000);
                    connection.setRequestMethod("GET");
                    connection.setRequestProperty("Connection", "Keep-Alive");            
                    //connection.setRequestProperty("Content-Type", "multipart/form-data; boundary="+boundary);
                    //connection.setRequestProperty ("Authorization", "Basic " + encoding);
                    BQAuthorization.addAuthorization(connection);
                    connection.connect();
                    System.out.println("Start reading image: " + uri);
                    DataInputStream data = new DataInputStream(new BufferedInputStream(connection.getInputStream(), 1024));
                    System.out.println("Reading is finished.");
                    int index = 0;
                    for (int chi=0; chi<ch; chi++){
                        for (int yi=0; yi<y; yi++){
                            for (int xi=0; xi<x; xi++){
                            //System.out.println(depth+","+t+","+z+","+ch+","+h+","+w);
                                if (d == 8){
                                    if (ch == 1 && z == 1 && t == 1)
                                        ((int[][])array)[yi][xi] = data.readUnsignedByte();
                                    if (ch > 1 && z == 1 && t == 1)
                                        ((int[][][])array)[yi][xi][chi] = data.readUnsignedByte();
                                    if (ch == 1 && z > 1 && t == 1)
                                        ((int[][][])array)[yi][xi][zi] = data.readUnsignedByte();
                                    if (ch == 1 && z == 1 && t > 1)
                                        ((int[][][])array)[yi][xi][ti] = data.readUnsignedByte();
                                    if (ch > 1 && z > 1 && t == 1)
                                        ((int[][][][])array)[yi][xi][chi][zi] = data.readUnsignedByte();
                                    if (ch > 1 && z == 1 && t > 1)
                                        ((int[][][][])array)[yi][xi][chi][ti] = data.readUnsignedByte();
                                    if (ch > 1 && z > 1 && t > 1)
                                        ((int[][][][][])array)[yi][xi][chi][zi][ti] = data.readUnsignedByte();
                                }
                                else if (d == 16){
                                    if (ch == 1 && z == 1 && t == 1)
                                        ((int[][])array)[yi][xi] = short2int(data.readByte(), data.readByte()); //((int[][])array)[h][w] = dataIn.readUnsignedShort();
                                        //((int[][])array)[h][w] = (int)Short.reverseBytes( dataIn.readShort());
                                    if (ch > 1 && z == 1 && t == 1)
                                        ((int[][][])array)[yi][xi][chi] = short2int(data.readByte(), data.readByte());;
                                    if (ch == 1 && z > 1 && t == 1)
                                        ((int[][][])array)[yi][xi][zi] = short2int(data.readByte(), data.readByte());;
                                    if (ch == 1 && z == 1 && t > 1)
                                        ((int[][][])array)[yi][xi][ti] = short2int(data.readByte(), data.readByte());;
                                    if (ch > 1 && z > 1 && t == 1)
                                        ((int[][][][])array)[yi][xi][chi][zi] = short2int(data.readByte(), data.readByte());;
                                    if (ch > 1 && z == 1 && t > 1)
                                        ((int[][][][])array)[yi][xi][chi][ti] = short2int(data.readByte(), data.readByte());;
                                    if (ch > 1 && z > 1 && t > 1)
                                        ((int[][][][][])array)[yi][xi][chi][zi][ti] = short2int(data.readByte(), data.readByte());;
                                }
                            }
                        }
                    }
                    data.close();
                    connection.disconnect();
                }
            }
            return array;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return null;
        }
    }
    public Object getDataCH(int selectedChannel){
        try{
            getInfo();
            int chS = 1;
            System.out.println("Image paramaters (x,y,d,ch,t,z):"+x+","+y+","+d+","+chS+","+t+","+ z);
            int dimL = 2;
            if (chS > 1) dimL++;
            if (z  > 1) dimL++;
            if (t  > 1) dimL++;
            int [] dim = new int[dimL];
            dim[0] = (int)y;
            dim[1] = (int)x;
            //if(channels > 1 && zsize == 1 && tsize == 1)
            if (chS >  1)                            dim[2] = (int)chS;
            if (chS == 1     && z >  1   && t == 1)  dim[2] = (int)z;
            if (chS == 1     && z == 1   && t >  1)  dim[2] = (int)t;
            if (chS == 1     && z >  1   && t >  1)  dim[3] = (int)t;
            if (chS >  1     && z >  1   && t == 1)  dim[3] = (int)z;
            if (chS >  1     && z == 1   && t >  1)  dim[3] = (int)t;
            if (chS >  1     && z >  1   && t >  1)  dim[4] = (int)t;
            //for(int i=0;i<dimL;i++) System.out.println(dim[i]);
            Object o = new int[1];
            Object array = Array.newInstance(BQUtil.getArrayComponent(o), dim);
            //System.out.println("Matrix dimention: " + BQUtil.getArrayDim(array));
            String encoding = BQAuthorization.getEncoded();
            for(int ti=0; ti<t; ti++){
                for(int zi=0; zi<z; zi++){
                    String urlQuery = "?remap="+selectedChannel+"&format=raw";
                    if (z > 1 && t > 1)     urlQuery = "?remap="+selectedChannel+"&slice=,," + new Integer(zi+1).toString() + "," + new Integer(ti+1).toString() +"&format=raw";
                    if (z == 1 && t > 1)    urlQuery = "?remap="+selectedChannel+"&slice=,,,"+ new Integer(ti+1).toString() +         "&format=raw";
                    if (z > 1 && t == 1)    urlQuery = "?remap="+selectedChannel+"&slice=,," + new Integer(zi+1).toString() + ","+         "&format=raw";
                    if (z == 1 && t == 1)   urlQuery = "?remap="+selectedChannel+"&format=raw";
                    System.out.println("URL: " + src + urlQuery);
                    URL server = new URL(src + urlQuery);
                    HttpURLConnection connection = (HttpURLConnection)server.openConnection();
                    //connection.setDoOutput(true);
                    //connection.setDoInput(true);
                    connection.setUseCaches(true);  
                    connection.setRequestMethod("GET");
                    connection.setRequestProperty("Connection", "Keep-Alive");          
                    //connection.setRequestProperty("Content-Type", "multipart/form-data; boundary="+boundary);
                    connection.setRequestProperty ("Authorization", "Basic " + encoding);
                    System.out.println("Connecting ...");
                    connection.connect();
                    System.out.println("Connected");
                    System.out.println("CODE: " + connection.getResponseCode());
                    System.out.println("Start reading image ...");
                    DataInputStream data = new DataInputStream(new BufferedInputStream(connection.getInputStream(), 1024));
                    System.out.println("Reading is finished :)");
                    int index = 0;
                    for (int chi=0; chi<chS; chi++){
                        System.out.println(d+","+ti+","+zi+","+chi);
                        for (int yi=0; yi<y; yi++){
                            for (int xi=0; xi<x; xi++){
                                if (d == 8){
                                    if (chS == 1 && z == 1 && t == 1)
                                        ((int[][])array)[yi][xi] = data.readUnsignedByte();
                                    if (chS > 1 && z == 1 && t == 1)
                                        ((int[][][])array)[yi][xi][chi] = data.readUnsignedByte();
                                    if (chS == 1 && z > 1 && t == 1)
                                        ((int[][][])array)[yi][xi][zi] = data.readUnsignedByte();
                                    if (chS == 1 && z == 1 && t > 1)
                                        ((int[][][])array)[yi][xi][ti] = data.readUnsignedByte();
                                    if (chS > 1 && z > 1 && t == 1)
                                        ((int[][][][])array)[yi][xi][chi][zi] = data.readUnsignedByte();
                                    if (chS > 1 && z == 1 && t > 1)
                                        ((int[][][][])array)[yi][xi][chi][ti] = data.readUnsignedByte();
                                    if (chS > 1 && z > 1 && t > 1)
                                        ((int[][][][][])array)[yi][xi][chi][zi][ti] = data.readUnsignedByte();
                                }
                                else if (d == 16){
                                    if (chS == 1 && z == 1 && t == 1)
                                        ((int[][])array)[yi][xi] = short2int(data.readByte(), data.readByte()); //((int[][])array)[h][w] = dataIn.readUnsignedShort();
                                        //((int[][])array)[h][w] = (int)Short.reverseBytes( dataIn.readShort());
                                    if (chS > 1 && z == 1 && t == 1)
                                        ((int[][][])array)[yi][xi][chi] = short2int(data.readByte(), data.readByte());;
                                    if (chS == 1 && z > 1 && t == 1)
                                        ((int[][][])array)[yi][xi][zi] = short2int(data.readByte(), data.readByte());;
                                    if (chS == 1 && z == 1 && t > 1)
                                        ((int[][][])array)[yi][xi][ti] = short2int(data.readByte(), data.readByte());;
                                    if (chS > 1 && z > 1 && t == 1)
                                        ((int[][][][])array)[yi][xi][chi][zi] = short2int(data.readByte(), data.readByte());;
                                    if (chS > 1 && z == 1 && t > 1)
                                        ((int[][][][])array)[yi][xi][chi][ti] = short2int(data.readByte(), data.readByte());;
                                    if (chS > 1 && z > 1 && t > 1)
                                        ((int[][][][][])array)[yi][xi][chi][zi][ti] = short2int(data.readByte(), data.readByte());;
                                }
                            }
                        }
                    }
                }
            }
            return array;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return null;
        }
    }
    public int byte2int(byte b){
        return (int)((b>=0)?b:(int)(256+b));
    }
    public int short2int(short s){
        return (int)((s>=0)?s:65536+(int)s);
    }
    public int short2int(byte b1, byte b2){
        //return (int)(((b2 & 0xFF) << 8) | (b2 & 0xFF));
        return (int)(((b2 & 0xFF) << 8) + (b1 & 0xFF));
    }
    public static void convertImageToRAWStream(Object image, String type,
                                               int width, int height, int channels, int zsize, int tsize, DataOutputStream os){
        try{
            int tmp = height; height = width; width = tmp;
            for (int t = 0; t < tsize; t++){
                for (int z = 0; z < zsize; z++){
                    for (int ch = 0; ch < channels; ch++){
                        for (int h = 0; h < height; h++){
                            for (int w = 0; w < width; w++){
                                //System.out.println(t+","+z+","+ch+","+h+","+w);
                                if (type.equals("uint8")){
                                    byte b = 0;
                                    if (channels == 1 && zsize == 1 && tsize == 1)
                                        b = ((byte[][])image)[h][w];
                                    else if (channels > 1 && zsize == 1 && tsize == 1)
                                        b = ((byte[][][])image)[h][w][ch];
                                    else if (channels == 1 && zsize > 1 && tsize == 1)
                                        b = ((byte[][][])image)[h][w][z];
                                    else if (channels == 1 && zsize == 1 && tsize > 1)
                                        b = ((byte[][][])image)[h][w][t];
                                    else if (channels > 1 && zsize > 1 && tsize == 1)
                                        b = ((byte[][][][])image)[h][w][ch][z];
                                    else if (channels > 1 && zsize == 1 && tsize > 1)
                                        b = ((byte[][][][])image)[h][w][ch][t];
                                    else if (channels > 1 && zsize > 1 && tsize > 1)
                                        b = (byte)((byte[][][][][])image)[h][w][ch][z][t];
                                    os.writeByte(b);
                                }
                                else if (type.equals("double")){
                                    double d = 0.0;
                                    if (channels == 1 && zsize == 1 && tsize == 1)
                                        d = ((double[][])image)[h][w];
                                    else if (channels > 1 && zsize == 1 && tsize == 1)
                                        d = ((double[][][])image)[h][w][ch];
                                    else if (channels == 1 && zsize > 1 && tsize == 1)
                                        d = ((double[][][])image)[h][w][z];
                                    else if (channels == 1 && zsize == 1 && tsize > 1)
                                        d = ((double[][][])image)[h][w][t];
                                    else if (channels > 1 && zsize > 1 && tsize == 1)
                                        d = ((double[][][][])image)[h][w][ch][z];
                                    else if (channels > 1 && zsize == 1 && tsize > 1)
                                        d = ((double[][][][])image)[h][w][ch][t];
                                    else if (channels > 1 && zsize > 1 && tsize > 1)
                                        d = ((double[][][][][])image)[h][w][ch][z][t];
                                    os.writeDouble(d);
                                }
                                else if (type.equals("uint16")){
                                    short s = 0;
                                    if (channels == 1 && zsize == 1 && tsize == 1)
                                        s = ((short[][])image)[h][w];
                                    else if (channels > 1 && zsize == 1 && tsize == 1)
                                        s = ((short[][][])image)[h][w][ch];
                                    else if (channels == 1 && zsize > 1 && tsize == 1)
                                        s = ((short[][][])image)[h][w][z];
                                    else if (channels == 1 && zsize == 1 && tsize > 1)
                                        s = ((short[][][])image)[h][w][t];
                                    else if (channels > 1 && zsize > 1 && tsize == 1)
                                        s = ((short[][][][])image)[h][w][ch][z];
                                    else if (channels > 1 && zsize == 1 && tsize > 1)
                                        s = ((short[][][][])image)[h][w][ch][t];
                                    else if (channels > 1 && zsize > 1 && tsize > 1)
                                        s = ((short[][][][][])image)[h][w][ch][z][t];
                                    os.writeShort(Short.reverseBytes(s));
                                }
                            }
                        }
                    }
                }
            }
        }
        catch (Exception e){
            BQError.setLastError(e);
        }
    }    
    public String postData(String serverUri, Object image){
        try{
            String response = null;
            String encoding = BQAuthorization.getEncoded();
            //String userPassword="admin:admin";
            //String encoding = new sun.misc.BASE64Encoder().encode (userPassword.getBytes());
            //String encoding = Base64Converter.encode (userPassword.getBytes());
            String boundary = "--------------------" + Long.toString(System.currentTimeMillis(), 30);
            int d = 8;
            if (type.equals("uint8"))    d = 8;
            if (type.equals("uint16"))    d = 16;
            if (type.equals("double"))    d = 32;
            String urlQuery = "?width=" + y + "&height=" + x + "&zsize=" + z + "&tsize=" + t +
                    "&channels=" + ch + "&depth=" + d + "&type=" + type + "&userPerm=" + perm +
                    "&endian=" + System.getProperties().getProperty("sun.cpu.endian") +
                    "&format=raw";
            String url = "http://bodzio.ece.ucsb.edu:8080/";
            //URL server = new URL(url + "/upload_raw_image" + urlQuery); //was '/bisquik/upload_raw_image'
            URL server = new URL(serverUri + "/bisquik/upload_raw_image" + urlQuery); //was '/bisquik/upload_raw_image'  
            //System.out.println(serverUri + "/upload_raw_image" + urlQuery);
            HttpURLConnection connection = (HttpURLConnection)server.openConnection();
            //Set post parameters;
            connection.setDoOutput(true);
            connection.setDoInput(true);
            connection.setUseCaches(false);
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Connection", "Keep-Alive");
            connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);
            connection.setRequestProperty("Authorization", "Basic " + encoding);
            connection.connect();
            DataOutputStream data = new DataOutputStream(new BufferedOutputStream(connection.getOutputStream(), 1024));
            data.writeBytes("--" + boundary + "\r\n");data.flush();
            data.writeBytes("Content-Disposition: form-data; name=\"upload\"; filename=\" " + filename + " \"\r\n");
            data.writeBytes("Content-Type: image/jpeg\r\n");
            data.writeBytes("Content-Transfer-Encoding: binary\r\n\r\n");
            //dataOut.writeBytes("\r\n");
            System.out.println("Start sending image ...");
            convertImageToRAWStream(image, type, x, y, ch, z, t, data);
            //System.out.println("Total memory: " + Runtime.getRuntime().totalMemory());
                        //System.out.println("Max memory: " + Runtime.getRuntime().maxMemory());
            //System.out.println("Free memory: " + Runtime.getRuntime().freeMemory());
            data.writeBytes("\r\n--" + boundary + "--\r\n");
            data.flush();
            data.close();
            System.out.println("Sending is finished.");
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
                    //System.out.println(response);
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
    public String postImageFromFile(String serverUri, String filePath){
        try{
            File file = new File(filePath);
            String response = null;
            String encoding = BQAuthorization.getEncoded();
            String boundary = "--------------------" + Long.toString(System.currentTimeMillis(), 30);
            URL server = new URL(serverUri + "/bisquik/upload_raw_image"); //was '/bisquik/upload_raw_image'  
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

            DataOutputStream data = new DataOutputStream(new BufferedOutputStream(connection.getOutputStream(), 1024));
            data.writeBytes("--" + boundary + "\r\n");
            data.writeBytes("Content-Disposition: form-data; name=\"upload\"; filename=\" " + file.getName() + " \"\r\n");
            data.writeBytes("Content-Type: application/octet-stream\r\n");
            data.writeBytes("\r\n");
//             // Write file contents to response.
//             while (contentLength-- > 0) {
//                 data.writeBytes(input.read());
//                 //System.out.println("File size: " + contentLength);
//             }
            FileInputStream fileInputStream = new FileInputStream(filePath);
            int bytesAvailable = fileInputStream.available();
            int maxBufferSize = 1024;
            int bufferSize = Math.min(bytesAvailable, maxBufferSize);
            byte[] buffer = new byte[bufferSize];
            // read file and write it into form...
            int bytesRead = fileInputStream.read(buffer, 0, bufferSize);
            while (bytesRead > 0) {
                data.write(buffer, 0, bufferSize);
                bytesAvailable = fileInputStream.available();
                bufferSize = Math.min(bytesAvailable, maxBufferSize);
                bytesRead = fileInputStream.read(buffer, 0, bufferSize);
            }
            fileInputStream.close();
            data.writeBytes("\r\n--" + boundary + "--\r\n");
            data.flush();
            data.close();
            System.out.println("Sending is finished :)");
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
                    //System.out.println(response);
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

}
