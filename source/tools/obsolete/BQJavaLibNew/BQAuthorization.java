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
import java.net.URLEncoder;
import java.net.HttpURLConnection;
import java.io.UnsupportedEncodingException;

public class BQAuthorization{

    public static String user;
    public static String pass;
    public static BQMex mex;

    public static void setAuthorization (String u, String p){
        System.out.println("Authorization.");
        user = u; pass = p;
    }
    public static String getEncoded(){
        String userPassword = user + ":" + pass; 
        String encoding = new sun.misc.BASE64Encoder().encode (userPassword.getBytes());
        //Base64 dec = new Base64()
        //String encoding = URLEncoder.encode(userPassword, "UTF-8");
        return encoding;
    }
    public static void addAuthorization (HttpURLConnection connection){
        connection.setRequestProperty("Authorization", "Basic " + getEncoded());
        //if(mex != null)
            //connection.setRequestProperty("Authorization", "Bisque " + mex.uri);
    }

}