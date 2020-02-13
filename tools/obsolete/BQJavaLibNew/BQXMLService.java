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
import java.io.File;
import java.io.Reader;
import java.io.IOException;
import java.io.InputStream;
import java.io.StringReader;
import java.io.StringWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import org.w3c.dom.Node;
import org.w3c.dom.Element;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.Transformer;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.dom.DOMSource;
import java.net.URL;
import java.net.URLConnection;
import java.net.HttpURLConnection;
import java.util.List;
import java.util.ArrayList;

public class BQXMLService{
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
    public static String loadXMLFile(String filePath){
        try{
            //System.out.println(filePath);
            File file = new File(filePath);
            DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
            DocumentBuilder db = dbf.newDocumentBuilder();
            Document doc = db.parse(file);
            return xmlToString(doc);
        }
        catch (Exception e){
            BQError.setLastError(e);
            return null;
        }
    }
    public static void saveXMLFile(String textxml, String filePath){
        try{
            Document doc = stringToXML(textxml);
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
    public static boolean checkURI(String uri){
        boolean type = true;
        try{
            URL url = new URL(uri);
            if("file".equals(url.getProtocol()))
                type = false;
            else if("http".equals(url.getProtocol()))
                type = true;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return type;
        }
        return type;
    }
    public static String parseURI(String uri){
        String uriP = null;
        try{
            URL url = new URL(uri);
            if("file".equals(url.getProtocol())){
                //System.out.println("File ...");
                if ((url.getHost() != null) && !url.getHost().equals("")) {
                    uriP = url.getHost() + ":" + url.getFile(); //win
                }
                else{
                    uriP = url.getFile(); //linux
                }
            }
            else if("http".equals(url.getProtocol())){
                //System.out.println("Http ...");
                uriP = uri;
            }
            //System.out.println(uriP);
            return uriP;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return uriP;
        }
    }
    //  perform a GET returning a parseed resource
    public static BQResource load(String uri){
        String response = BQXML.loadXML (uri, null, "GET");
        //System.out.println("loaded "+ uri +"=>" +response);
        BQXMLParser parser = new BQXMLParser();
        return parser.parseBQObjectDocument(response);
    }    
    // Perform a POST request to the uri reurning resource
    public static BQResource load(String uri, String textxml) {
        String response = BQXML.loadXML (uri, textxml, "POST");
        //System.out.println("loaded "+ uri +"=>" +response);
        BQXMLParser parser = new BQXMLParser();
        return parser.parseBQObjectDocument(response);
    }
    public static String loadXML(String url, String textxml, String method){
        String uriP = parseURI(url);
        if (!checkURI(url))
            return loadXMLFile(uriP);
        else
            return postXML(uriP, textxml, method);
    }

    // Make an 

    public static String postXML(String url, String textxml, String method){
        try{
            //System.out.println("BQXML->postText");
            String response = null;
            //String encoding = BQAuthorization.getEncoded();
            URL server = new URL(url);
            HttpURLConnection connection = (HttpURLConnection)server.openConnection();
            //Set post parameters;
            connection.setDoOutput(true);
            connection.setDoInput(true);
            connection.setUseCaches(false);
            connection.setRequestMethod(method);
            connection.setRequestProperty("Content-Type", "text/xml");
            BQAuthorization.addAuthorization(connection);
            //connection.setRequestProperty("Authorization", "Basic " + encoding);

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
                        Reader reader = new InputStreamReader(contentStream, "UTF-8");
                        int c;
                        while ((c = contentStream.read()) != -1) sb.append((char)c);
                        response = sb.toString();
                    }
                }
                else{
                    System.out.println("Error connection, code:" + connection.getResponseCode() + "\n");
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
        catch (Exception e){
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
}