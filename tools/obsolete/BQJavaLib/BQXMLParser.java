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
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Iterator;

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
			el 			= (Element) item[0];
			resource 	= (BQObject)item[1];
			parent 		= (BQObject)item[2];
			String type = el.getNodeName();
			if (resource == null) 
				resource = factory(el);
			//System.out.println ("Got " + type + "=" + resource + " parent=" + parent);
			
			resource.initializeXml(el);
			if (parent != null) {
				resource.addParent ((BQObject)parent);
			}
			Iterator<Element> li = BQXML.getChildElements(el).iterator();
			while (li.hasNext()) {
				Element child = li.next();
				stack.add(new Object[]{child, null, resource});
			}
		}
	}
	private static BQXMLObject factory(Element e){
	    String name = e.getNodeName();
	    if (name.equals ("resource"))
		name = BQXML.AttrStr(e, "type");
	    
		if (name.equals("vertex"))
			return new BQVertex();
		if (name.equals("value"))
			return new BQValue();
		if (name.equals("tag"))
			return new BQTag(); 
		if (name.equals("image")) 
			return new BQImage();
		if (name.equals("mex")) 
		    return new BQMEX();
		if (name.equals("gobject")	|| name.equals("circle") || 
			name.equals("rectangle")|| name.equals("point")  || 
			name.equals("polyline")	|| name.equals("polygon")) 
			return new BQGObject();	
		return new BQObject();
	}
	public void toXmlDocument(BQObject o) {
		Element root = o.toXml(doc, null);
		doc.appendChild(root);
	}
	public BQObject parseBQObjectDocument(String textXML){
		//System.out.println (textXML);
		doc = BQXML.stringToXML(textXML);
		System.out.println(BQXML.xmlToString(doc));
		//Element r  = (Element)doc.getDocumentElement();
		//System.out.println(r.getNodeName());
		//Element root  = (Element)doc.getDocumentElement().getFirstChild().getFirstChild();
		//Element root  = (Element)doc.getDocumentElement().getFirstChild();
		//Element root  = BQXML.getChildElement((Element)doc.getDocumentElement());
        Element root = (Element)doc.getDocumentElement();
        if (root.getNodeName() == "response") 
            root = BQXML.getChildElement(root);
		BQXMLObject top = factory(root);
		parseXml(root, top, null);
		return (BQObject)top;
	}
	public Document toXml(BQObject o){
		o.toXml(doc, null);
		return doc;
	}
	public ArrayList<BQObject> parseBQObjectDocumentSearch(String textXML) {
		ArrayList<BQObject> results = new ArrayList();
		doc = BQXML.stringToXML(textXML);
		Iterator<Element> li = BQXML.getChildElements((Element)doc.getDocumentElement()).iterator();
		while (li.hasNext()){
			Element child = li.next();
			BQXMLObject top = factory(child);
			parseXml(child, top, null);
			results.add((BQObject)top);
		}
		return results;
	}
}
