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
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;

public class BQAuthorization{

    public static String user;
    public static String pass;
    public static String mextoken;
	
	public static void setAuthorization (String u, String p){
		System.out.println("Authorization.");
		user = u; pass = p;
	}
	public static void setAuthorization (String mex_token){
		System.out.println("Authorization.");
        mextoken = mex_token;
	}
	public static String getEncoded(){
		String userPassword = user + ":" + pass; 
		String encoding = new sun.misc.BASE64Encoder().encode (userPassword.getBytes());
        //Base64 dec = new Base64()
        //String encoding = URLEncoder.encode(userPassword, "UTF-8");
		return encoding;
	}
	public static void help(){
		System.out.println("---------------------------------------------");
		System.out.println("BQAuthorization class:");
		System.out.println("---------------------------------------------");
		System.out.println("BQAuthorization.setAuthorization('user name','password')");
		System.out.println("---------------------------------------------");
	}

    public static void addAuth(HttpURLConnection connection) {
        if (mextoken != null) {
            connection.setRequestProperty("Mex", mextoken);
        }else {
            String encoding = getEncoded();
            connection.setRequestProperty("Authorization", "Basic " + encoding);
        }
    }
}
