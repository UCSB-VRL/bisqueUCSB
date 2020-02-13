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
import org.w3c.dom.Node;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.w3c.dom.Document;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.util.Iterator;
import java.util.ArrayList;
import java.util.LinkedList;

public class BQXMLParser{

    public Document doc;

    BQXMLParser(){
        try{
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            doc = builder.newDocument();
        }
        catch (Exception e){
            e.printStackTrace();
        }
    }
    public void parseXml(Element el, BQXMLObject resource, BQXMLObject parent){
        LinkedList stack= new LinkedList();
        stack.add(new Object[]{el, resource, parent} );
        while(stack.size() > 0){
            Object[] item = (Object[])stack.removeLast();
            el          = (Element) item[0];
            resource    = (BQResource)item[1];
            parent      = (BQResource)item[2];
            String type = el.getNodeName();
            if (resource == null) 
                resource = BQFactory.create(type, null);
            System.out.println ("Got " + type + "=" + resource);// + " parent=" + parent);
            resource.initializeXml(el);
            if (parent != null) {
                resource.setParent((BQResource)parent);
                //resource.document = ((BQObject)parent).document;
            }
            Iterator<Element> li = BQXML.getChildElements(el).iterator();
            while (li.hasNext()) {
                Element child = li.next();
                stack.add(new Object[]{child, null, resource});
            }
        }
    }
    public void toXmlDocument(BQObject o) {
        Element root = o.toXml(doc, null);
        doc.appendChild(root);
    }
    public BQResource parseBQObjectDocument(String textXML){
        doc = BQXML.stringToXML(textXML);
        Element root  = (Element)doc.getDocumentElement(); // FIXME
        if (root.getNodeName().equals("response"))
            root  = BQXML.getChildElement((Element)doc.getDocumentElement());

        //System.out.println (textXML);
        System.out.println (root.getNodeName());
        String elType = root.getNodeName();
        BQXMLObject top = BQFactory.create(elType, null);
        parseXml(root, top, null);
        return (BQResource)top;
    }
    public Document toXml(BQObject o){
        o.toXml(doc, null);
        return doc;
    }
    public ArrayList<BQObject> parseBQResourceDocument(String textXML) {
        ArrayList<BQObject> results = new ArrayList();
        doc = BQXML.stringToXML(textXML);
        Iterator<Element> li = BQXML.getChildElements((Element)doc.getDocumentElement()).iterator();
        while (li.hasNext()){
            Element child = li.next();
            String elType = child.getNodeName();
            //BQXMLObject top = factory(elType);
            BQXMLObject top = BQFactory.create(elType, null);
            parseXml(child, top, null);
            results.add((BQObject)top);
        }
        return results;
    }
    public static ArrayList<BQObject> loadR(String uri){
        String response = BQXML.loadXML (uri, null, "GET");
        //System.out.println("loaded "+ uri +"=>" +response);
        BQXMLParser parser = new BQXMLParser();
        return parser.parseBQResourceDocument(response);
    }
}