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
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

public class BQObject extends BQResource{

    public ArrayList<BQTag> tags;
    public ArrayList<BQGObject> gobjects;
    public Integer owner_id;
    public Integer perm;
    public String ts;
    public BQResource parent;
    public BQResource document;
    public BQMEX mex;

    public BQObject() {
        tags = new ArrayList <BQTag> ();
        gobjects = new ArrayList<BQGObject>();
    }
    public BQObject(String uri_, String type_){
        this();
        uri = uri_;
        type = type_;
    }
    public void initializeXml(Element el){
        super.initializeXml(el);
        owner_id    = BQXML.AttrInt(el, "owner_id");
        perm        = BQXML.AttrInt(el, "perm");
        ts          = BQXML.AttrStr(el, "ts");
    }
    public Element toXml(Document doc, Element el){
        //if (el == null)
        //    el = doc.createElement("resource");
        super.toXml(doc, el);
        BQXML.StrAttr(el,"uri",         uri);
        BQXML.StrAttr(el,"type",        type);
        BQXML.IntAttr(el,"owner_id",    owner_id);
        BQXML.IntAttr(el,"perm",        perm);
        BQXML.StrAttr(el,"ts",          ts);
        Iterator<BQTag> ti = tags.iterator();
        while(ti.hasNext()){
            BQTag t = ti.next();
            Element tel = t.toXml(doc, null);
            el.appendChild(tel);
        }
        Iterator<BQGObject> goi = gobjects.iterator();
        while(goi.hasNext()){
            BQGObject go = goi.next();
            Element goel = go.toXml(doc, null);
            el.appendChild(goel);
        }
        return el;
    }
//     public void parseResponse(String textXML){
//         Document doc = BQXML.stringToXML(textXML);
//         //System.out.println ("What was parsed=" + BQXML.xmlToString(doc));
//         BQXMLParser p = new BQXMLParser();
//         Element el = (Element)doc.getFirstChild();
//         List<Element> nodes = BQXML.getChildElements (el);
//         Iterator<Element> li = nodes.iterator();
//         while (li.hasNext()) {
//             el = li.next();
//             p.parseXml(el,this,null);
//             //System.out.println ("node " + el);
//         }
//     }
/*    public void load(){
        String response = BQXML.postXML (this.uri+"?view=deep", null, "GET");
        System.out.println(response);
        parseResponse(response);
    }
    public static BQObject load_resource (BQObject x) {
        BQObject r = (BQObject)BQXMLParser.factory (x.type);;
        String response = BQXML.postXML (x.uri+"?view=deep", null, "GET");
        r.parseResponse(response);
        return r;
    }*/
    public BQTag findTag(String name){
        Iterator<BQTag> ti = tags.iterator();
        BQTag tag = null;
        while(ti.hasNext()){
            BQTag t = ti.next();
            if (t.equals(name)) tag = t;
        }
        return tag;
    }
    public ArrayList<BQTag> findTags (String name){
        ArrayList<BQTag> tags = null;
        Iterator<BQTag> ti = tags.iterator();
        while (ti.hasNext()){
            BQTag t = ti.next();
            if (t.equals(name)) 
                tags.add(t);
        }
        return tags;
    }
    public ArrayList<BQTag> getTags(){
        Iterator ti = getIterator("tag");
        while (ti.hasNext()) {
            BQTag t = (BQTag)ti.next();
            //System.out.println("Tag: " + t.name);
        }
        return tags;
    }
    public ArrayList<BQGObject> getGObjects(){
        Iterator gi = getIterator("gobject");
        while (gi.hasNext()) {
            BQGObject go = (BQGObject)gi.next();
            //System.out.println("GObject: " + go.name);
        }
        return gobjects;
    }
    public Iterator getIterator (String type){
       return new BQResourceFilterIterator(type);
    }
    //-----------------------------------------------------------------------
    public BQTag createTag(String name, String value){
        BQTag tag = new BQTag(name, value);
        return tag;
    }
//     public BQTag addTag(BQTag tag){
//         tags.add(tag);
//         return tag;
//     }
    public BQTag addTag(String name, String value){
        BQTag tag = new BQTag(name, value);
        tags.add(tag);
        return tag;
    }
    public BQTag addTag(String name, double value){
        BQTag tag = new BQTag(name, new Double(value));
        tags.add(tag);
        return tag;
    }
    //-----------------------------------------------------------------------
    public void addGObject(BQGObject go){ gobjects.add(go); }
}