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
import org.w3c.dom.Element;
import org.w3c.dom.Document;
import java.util.ArrayList;
import java.net.URLEncoder;

public class BQDataService extends BQXMLService {
    public String server_uri;

    public BQDataService(){}
    public BQDataService(String uri_){
        server_uri = uri_;
    }
    // HTTP
//     public static BQResource load(String uri){
//         String response = BQXML.loadXML (uri, null, "GET");
//         //System.out.println("loaded "+ uri +"=>" +response);
//         BQXMLParser parser = new BQXMLParser();
//         return parser.parseBQObjectDocument(response);
//     }
//     public BQObject load(String uri){
//         String response = BQXML.postXML (uri, null, "GET");
//         //System.out.println(response);
//         BQXMLParser parser = new BQXMLParser();
//         return (BQObject)parser.parseBQObjectDocument(response);
//     }
    public String save(BQResource o){
        String uri;
        if (o.parent != null) uri = o.parent.uri;
        else uri = server_uri;

        BQXMLParser parser = new BQXMLParser();
        Element request = parser.doc.createElement("request");
        Element el = o.toXml(parser.doc, null);
        request.appendChild(el);
        parser.doc.appendChild(request);
        //System.out.println(BQXML.xmlToString(parser.doc));
        if (o.uri != null)
            return postXML(o.uri, xmlToString(parser.doc), "PUT");
        else {
            String response =  BQXML.postXML(server_uri, BQXML.xmlToString(parser.doc), "POST");
            Document doc = BQXML.stringToXML(response);
            Element root  = BQXML.getChildElement((Element)doc.getDocumentElement());
            String response_uri = BQXML.AttrStr (root, "uri");
            if (response_uri != null)
                o.uri = response_uri;
            return response;
        }
    }
    public void update(BQObject o){ /// FIXME - remove or call save function
        BQXMLParser parser = new BQXMLParser();
        Element request = parser.doc.createElement("request");
        Element el = o.toXml(parser.doc, null);
        request.appendChild(el);
        parser.doc.appendChild(request);
        System.out.println(BQXML.xmlToString(parser.doc));
        if (o.uri != null)
            postXML(o.uri, BQXML.xmlToString(parser.doc), "PUT");
        else
            postXML(server_uri, BQXML.xmlToString(parser.doc), "POST");
    }
    public void delete(BQObject o){
        System.out.println(o.uri);
        if (o.uri != null)
            postXML(o.uri, null, "DELETE");
    }
    // FILE
    public void saveFile(BQObject o, String filePath){
        String uri;
        if (o.parent != null) uri = o.parent.uri;
        else uri = server_uri;

        BQXMLParser parser = new BQXMLParser();
        Element request = parser.doc.createElement("request");
        Element el = o.toXml(parser.doc, null);
        request.appendChild(el);
        parser.doc.appendChild(request);
        //System.out.println(BQXML.xmlToString(parser.doc));
        saveXMLFile(BQXML.xmlToString(parser.doc), filePath);
    }
    public BQObject loadFile(String filePath){
        Document doc = BQXML.loadXMLFile(filePath);
        String response = BQXML.xmlToString(doc);
        //System.out.println(response);
        BQXMLParser parser = new BQXMLParser();
        return (BQObject)parser.parseBQObjectDocument(response);
    }
    // UTIL
    public ArrayList<BQObject> search(String query){
        try{
            // urlServer should be the base Dataserver url.
            // filter should be an expressions of tags to filter like 
            //  experimenter:aaa or a simply a value like Wildtype or
            // a combination of the above i.e. experimenter:aaa and Wildtype
            ArrayList<BQObject> results = new ArrayList();
            String query_uri = server_uri + "/ds/images";
            if (query != null)
                query_uri += "?tag_query=" + URLEncoder.encode(query,"UTF-8");
            String response = BQXML.postXML(query_uri, null, "GET");
            //System.out.println(response);
            BQXMLParser parser = new BQXMLParser();
            results = parser.parseBQResourceDocument(response);
            return results;
        }
        catch (Exception e){
            e.printStackTrace();
            return null;
        }
    }
}