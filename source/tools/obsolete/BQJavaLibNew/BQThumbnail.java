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
import java.io.InputStream;
import java.io.DataInputStream;
import java.io.BufferedInputStream;
import java.net.URL;
import java.net.URLConnection;
import java.net.HttpURLConnection;
import java.util.Arrays;
import java.lang.reflect.Array;

public class BQThumbnail{
    public Object getData(String urlImage, int width, int height){
        try{
            BQDataService ds = new BQDataService();
            BQImage image = (BQImage)ds.load(urlImage);
            String srcImage = image.src;
            int channels = 3;
            int dimL = 3;
            int [] dim = new int[dimL];
            dim[0] = (int)height;
            dim[1] = (int)width;
            dim[2] = (int)channels;
            Object o = new int[1];
            Object array = Array.newInstance(BQUtil.getArrayComponent(o), dim);
            String encoding = BQAuthorization.getEncoded();
            String urlQuery = "?remap=display&slice=,,1,1&resize="+width+","+height+"&depth=8,d&format=raw";
            System.out.println("URL: " + srcImage + urlQuery);
            URL server = new URL(srcImage + urlQuery);
            HttpURLConnection connection = (HttpURLConnection)server.openConnection();
            connection.setUseCaches(true);
            connection.setRequestMethod("GET");
            connection.setRequestProperty("Connection", "Keep-Alive");
            //connection.setRequestProperty("Content-Type", "multipart/form-data; boundary="+boundary);
            connection.setRequestProperty ("Authorization", "Basic " + encoding);
            connection.connect();
            System.out.println("Start reading image ...");
            DataInputStream data = new DataInputStream(new BufferedInputStream(connection.getInputStream(), 1024));
            System.out.println("Reading is finished :)");
            int index = 0;
            for(int ch=0; ch<channels; ch++)
                for(int y=0; y<height; y++)
                    for(int x=0; x<width; x++)
                        ((int[][][])array)[y][x][ch] = data.readUnsignedByte();
            return array;
        }
        catch (Exception e){
            e.printStackTrace();
            return null;
        }
    }
}