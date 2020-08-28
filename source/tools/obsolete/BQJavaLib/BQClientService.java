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
import java.util.Arrays;

import java.net.URL;
import java.net.HttpURLConnection;
import java.net.URLConnection;

import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.BufferedOutputStream;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.io.Reader;

public class BQClientService{
	
	public String server_uri;

	public BQClientService(String uri_){
		server_uri = uri_;
	}

    public String  post_multipart (String target, BQDataProducer[] producers) {
        HttpURLConnection connection=null;
        try{
            String response = null;
            String boundary = "--------------------" + Long.toString(System.currentTimeMillis(), 30);
            URL server = new URL(server_uri + "/upload_files"); 
            connection = (HttpURLConnection)server.openConnection();
            //Set post parameters;
            connection.setDoOutput(true);
            connection.setDoInput(true);
            connection.setUseCaches(false);
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Connection", "Keep-Alive");
            connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);
            BQAuthorization.addAuth(connection);
            
            //connection.setRequestProperty("Content-Disposition", "form-data; name=\"upload\"; filename=\" " + file.getName() + " \"");
            connection.connect();

            DataOutputStream data = new DataOutputStream(new BufferedOutputStream(connection.getOutputStream(), 1024));
            for (BQDataProducer p  : Arrays.asList(producers)) {
                data.writeBytes("--" + boundary + "\r\n");
                data.writeBytes("Content-Disposition: form-data; name=\"upload\"; filename=\"" + p.getName() + "\"\r\n");
                data.writeBytes("Content-Type: application/octet-stream\r\n");
                data.writeBytes("\r\n");
                p.convertToStream (data);

                data.writeBytes("\r\n--" + boundary + "--\r\n");
            }
            data.flush();
            data.close();
            System.out.println("Sending is finished :)");
            //Response
            if (connection.getResponseCode() == 200){
				Object contents = connection.getContent();
				InputStream contentStream = (InputStream)contents;

                StringBuffer sb = new StringBuffer();
                
                Reader reader = new InputStreamReader(contentStream, "UTF-8");
                int c;
                while ((c = contentStream.read()) != -1) sb.append((char)c);
                response = sb.toString();
                
                //System.out.println(response);
            } else{
                System.out.println("Error connection, code:" + connection.getResponseCode() + "\n");
				InputStream contentStream = (InputStream)connection.getErrorStream();

                StringBuffer sb = new StringBuffer();
                
                Reader reader = new InputStreamReader(contentStream, "UTF-8");
                int c;
                while ((c = contentStream.read()) != -1) sb.append((char)c);
                response = sb.toString();
                System.out.println(response);

                return null;
            }
            return response;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return null;
        } finally {
            if (connection != null)
                connection.disconnect();
        }
    }

    public BQObject  upload_image(BQImage image, Object image_data){
        BQDataProducer p = new BQImageProducer (image, image_data);
        String response= post_multipart (server_uri + "/upload_images", 
                                         new BQDataProducer [] { p } );

        // The response document a resource with children.
        // In this case there should only be one child.
        if (response != null ) {
            BQXMLParser parser = new BQXMLParser ();
            BQObject o = parser.parseBQObjectDocument (response);

            return o.children.get (0);
        }
        return null;
    }

	public BQObject upload_file (String filePath){
        BQDataProducer p = new FileProducer (filePath);

        String response =  post_multipart (server_uri + "/upload_files", 
                                           new BQDataProducer [] { p } );

        // The response document a resource with children.
        // In this case there should only be one child.
        if (response != null ) {
            BQXMLParser parser = new BQXMLParser ();
            BQObject o = parser.parseBQObjectDocument (response);
            return o.children.get (0);
        }
        return null;
    }
}
