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
import java.io.StringWriter;
import java.io.File;
import java.io.Reader;
import java.io.StringReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.IOException;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.Transformer;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.dom.DOMSource;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import org.w3c.dom.Element;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import java.net.URL;
import java.net.HttpURLConnection;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.List;


public class BQXML{

	public void help(){
		System.out.println("---------------------------------------------");
		System.out.println("BQXML class:");
		System.out.println("---------------------------------------------");
		System.out.println("BQAuthorization.setAuthorization('user name','password')");
	}
	public static String xmlToString(Document document){
		try{
			TransformerFactory transfac = TransformerFactory.newInstance();
			Transformer trans = transfac.newTransformer();
			trans.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");
			trans.setOutputProperty(OutputKeys.INDENT, "yes");
			// create string from xml tree
			StringWriter sw = new StringWriter();
			StreamResult result = new StreamResult(sw);
			DOMSource source = new DOMSource(document);
			trans.transform(source, result);
			String xmlString = sw.toString();
			return xmlString;
		}
		catch (Exception e){
			BQError.setLastError(e);
			return null;
		}
	}
	public static Document stringToXML(String responseXML) {
		try{
			StringReader reader = new StringReader(responseXML);
			InputSource inputStringSource = new InputSource();
			inputStringSource.setCharacterStream(reader);
			DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
			factory.setNamespaceAware(true);
			factory.setIgnoringElementContentWhitespace(true);
			factory.setIgnoringComments(true);
			DocumentBuilder builder = factory.newDocumentBuilder();
			Document document = builder.parse(inputStringSource);
			return document;
		}
		catch (Exception e){
			System.out.println ("ag");
			BQError.setLastError(e);
			return null;
		}
	}
	public static Document loadXMLFile(String filePath){
		try{
			File file = new File(filePath);
			DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			DocumentBuilder db = dbf.newDocumentBuilder();
			Document doc = db.parse(file);
			return doc;
		}
		catch (Exception e){
			BQError.setLastError(e);
			return null;
		}
	}
	public static void saveXMLFile(Document doc, String filePath){
		try{
			TransformerFactory tFactory = TransformerFactory.newInstance();
			Transformer transformer = tFactory.newTransformer();
			DOMSource source = new DOMSource(doc);
			StreamResult result = new StreamResult(new File(filePath));
			transformer.transform(source, result);
		}
		catch (Exception e){
			BQError.setLastError(e);
		}
	}		
    public static String mexToken(BQMEX mex) {
        try {
            String mexuri = new URL(mex.uri).getPath();
            int    slash  = mexuri.lastIndexOf('/');
            return mexuri.substring (slash+1);
        } catch (java.net.MalformedURLException e) {
            return null;
        }
    }

	public static String postXML(String url, String textxml, String method){
		try{
			//System.out.println("BQXML->postText");
			String response = null;
			URL server = new URL(url);
			HttpURLConnection connection = (HttpURLConnection)server.openConnection();
			//Set post parameters;
			connection.setDoOutput(true);
			connection.setDoInput(true);
			connection.setUseCaches(false);
			connection.setRequestMethod(method);
			connection.setRequestProperty("Content-Type", "text/xml");
            BQAuthorization.addAuth(connection);

			connection.connect();
			if (method.equals("POST") || method.equals("PUT")){
				OutputStreamWriter out = new OutputStreamWriter(connection.getOutputStream(), "UTF-8");
				out.write(textxml);
				out.flush();
				if (connection.getResponseCode() == 200){
					Object contents = connection.getContent();
					InputStream contentStream = (InputStream)contents;
					if (connection.getContentType().compareTo("text/xml") == 0){
						try{
							DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
							factory.setNamespaceAware(true);
							factory.setIgnoringElementContentWhitespace(true);
							factory.setIgnoringComments(true);
							DocumentBuilder builder = factory.newDocumentBuilder();
							Document document = builder.parse(contentStream);
							response = xmlToString(document);
						}
						catch (Exception e){
							System.out.println(e);
							return null;
						}
					}
					else{
						StringBuffer sb = new StringBuffer();
						//Reader reader = new InputStreamReader(contentStream, "UTF-8");
						int c;
						while ((c = contentStream.read()) != -1) sb.append((char)c);
						response = sb.toString();
					}
				}
				else{
					System.out.println("Error connection, code:" + connection.getResponseCode() + "\n");
                    StringBuffer sb = new StringBuffer();
                    //Reader reader = new InputStreamReader(connection.getErrorStream(), "UTF-8");
                    InputStream contentStream = connection.getErrorStream();
                
                    int c;
                    while ((c = contentStream.read()) != -1) sb.append((char)c);
                    response = sb.toString();
                    System.out.println ("Error Response: " + response); 

					return null;
				}
				out.close();
				connection.disconnect();
				return response;
			}
			else{
				InputStream contentStream;
				contentStream = connection.getInputStream();
				DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
				factory.setNamespaceAware(true);
				factory.setIgnoringElementContentWhitespace(true);
				factory.setIgnoringComments(true);
				DocumentBuilder builder = factory.newDocumentBuilder();
				Document document = builder.parse(contentStream);
				response = xmlToString(document);
				connection.disconnect();
				return response;
			}
				
		}
		catch (Exception e)
		{
			BQError.setLastError(e);
			return null;
		}
	}
	public static Element getChildElement( Element el ){
		Node n = el.getFirstChild();
		while ( n != null && n.getNodeType() != Node.ELEMENT_NODE ){
			n = n.getNextSibling();
		}
		return (Element)n;
	}
	public static List<Element> getChildElements( Element el ){
		NodeList list = el.getChildNodes();
		List<Element> children = new ArrayList<Element>();
		for ( int i = 0, n = list.getLength(); i < n; ++i ){
			if ( list.item( i ).getNodeType() == Node.ELEMENT_NODE ){
				children.add( (Element)list.item( i ) );
			}
		}
		return children;
	}
	public static String AttrStr(Element el, String name){
		if (el.hasAttribute(name))
			return el.getAttribute(name);
		else
			return null;
	}
	public static Double AttrDouble(Element el, String name){
		if (el.hasAttribute(name))
			return Double.valueOf(el.getAttribute(name));
		else
			return null;
	}
	public static Integer AttrInt(Element el, String name){
		if (el.hasAttribute(name))
			return Integer.valueOf(el.getAttribute(name));
		else
			return null;
	}
	public static void StrAttr(Element el, String name, String value){
		if (value != null) 
			el.setAttribute(name, value);
	}
	public static void IntAttr(Element el, String name, Integer value){
		if (value != null) 
			el.setAttribute(name, value.toString());
	}
	public static void DoubleAttr(Element el, String name, Double value){
		if (value != null) 
			el.setAttribute(name, value.toString());
	}
}
