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
import javax.media.jai.JAI;
import com.sun.media.jai.operator.ImageReadDescriptor;
import java.net.URLEncoder;

public class BQ{

    static BQDataService ds;
    static BQClientService cs;
    static BQMex mex;

    //--------------------------------------------------------------
    // SERVER
    //--------------------------------------------------------------
    public static void initialize(String uri, String name, String pass, String module_id){
        BQAuthorization.setAuthorization(name, pass);
        if(mex != null)
            System.out.println("Error");
        else{
            cs = new BQClientService(uri);
            System.out.println(uri + name + pass + module_id);
            //cs.initialize_services();
            //ds = (BQDataService)cs.get_service("data_service");
            ds = new BQDataService("http://bodzio.ece.ucsb.edu:8080/ds");
            //ms = cs.get_service ("module_service");
        }
        mex = cs.begin_session(module_id);
    }
    public static void initialize (BQMex mex_) {
        mex = mex_;
        BQTag tag  = mex.findTag("client_service");
        String uri = null;
        if (tag!=null)
            uri = tag.getValue();
        // Fetch auth 
        cs = new BQClientService(uri);
        cs.initialize_services();
        ds = (BQDataService)cs.get_service("data_service");
    }
    public static void finish () {
        mex.status = "Finished";
        ds.save(mex); 
    }
    //--------------------------------------------------------------
    // OBJECT
    //--------------------------------------------------------------
    public static BQResource load(String uri) {
        BQResource o = ds.load(uri);
        return o;
    }
    //--------------------------------------------------------------
    // FACTORY
    //--------------------------------------------------------------
    public static BQResource create(String type){
        return (BQResource)BQFactory.create(type, null);
    }
    //--------------------------------------------------------------
    // SAVE
    //--------------------------------------------------------------
    public static void save(BQResource o){
        ds.save(o);
    }
    public static void save(BQResource o, String uri){
        // Save an object to a new URL .. 
        ds.save(o);
    }
    //--------------------------------------------------------------
    // QUERY
    //--------------------------------------------------------------
//     public static BQResource query(String type, String q){
//         String query_uri = BQ.cs.top_uri + "/ds/";
//         if(type.equals("image")){ query_uri += "images"; }
// 
//         query_uri += "?tag_query=" + URLEncoder.encode(q,"UTF-8");
//         BQResource o = ds.load(query_uri);
//         return o;
//     }
 }