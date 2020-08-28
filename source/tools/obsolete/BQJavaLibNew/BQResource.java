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
import java.util.Collection;
import java.util.Iterator;
import java.util.ListIterator;
import java.util.List;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Collections;
import java.util.AbstractCollection;


public class BQResource extends AbstractCollection implements BQXMLObject {
    protected BQResource parent;
    public String uri;
    public String type;
    public String flags;
    public ArrayList children = new ArrayList(); 

    public BQResource(){ }
    public void initializeXml(Element el) {
        uri = BQXML.AttrStr(el, "uri");
        if (type.equals("resource"))
            type = BQXML.AttrStr(el, "type");
    }
    public Element toXml(Document doc, Element el) { 
        if (el == null)
            el = doc.createElement("resource");
        BQXML.StrAttr(el,"uri",         uri);
        BQXML.StrAttr(el,"type",        type);
        Iterator chi = children.iterator();
        while(chi.hasNext()){
            BQResource r = (BQResource)chi.next();
            Element tel = r.toXml(doc, null);
            el.appendChild(tel);
        }
        return el;
    }
    public BQResourceIterator iterator() {
        return null; //new BQResourceIterator();
    }
    public Collection getChildren(){
        return children;
    }
    public void setParent(BQResource parent_){
        parent = parent_;
        parent.children.add (this) ;
    }
    protected BQResource remove_resource (String type) {
        Iterator<BQResource> kids = children.iterator() ;
        BQResource kid = new BQResource();
        while (kids.hasNext()) {
            BQResource actualkids = kids.next();
            if (actualkids.type.equals(type)) {
                kids.remove();
                kid.children.add(actualkids);
            }
        }
        return kid;
    }
    public void clear(){}
    public int size(){ return 0; }
    public void addChild (BQResource o) { children.add (o); }
    public void addTag (BQTag o) { children.add(o); }
    public void addGObject(BQGObject o) { children.add(o); }
    public void load() { }
    public String toString() { return getClass().getName()+"["+type+"]"; }


    //-----------------------------------------------------------
    public class BQResourceIterator implements Iterator {
        Iterator iter;

        public BQResourceIterator () {
            iter = children.iterator();
        }
        public boolean hasNext() {
           return iter.hasNext();
        }
        public Object next() {
            BQResource next = (BQResource) iter.next();
            //System.out.println("TYPE1a " + next.type);
            if (next.type.equals("tags")) {
                System.out.println("TYPE2a " + next.uri);
                iter.remove();  // Remove the <resource > item from the childlist
                BQResource actualkids = BQDataService.load (next.uri); // Fetch the resource 
                Iterator ki = actualkids.children.iterator();
                while (ki.hasNext()) {
                   children.add(ki.next());
                }
                return iter.next();
            }
            return next;
        }
        public void remove () {
            throw new UnsupportedOperationException();
        }
    }

    //-----------------------------------------------------------
    public class BQResourceFilterIterator implements Iterator {
        ListIterator iter;
        String filter;
        BQResource object_next;

        public BQResourceFilterIterator (String filter) {
            iter = children.listIterator();
            this.filter = filter;
        }
       // <image...> 
       // <resource type="application/bisque-resource-extended" uri="/ds/images?offset=100"
        private BQResource check_resource (BQResource r) {
            //System.out.println("TYPE1 " + r.type);
            if (r.type.equals("bisque-resource-"+filter)) {
                //System.out.println("TYPE2 " + r.uri);
                iter.remove();  // Remove the <resource > item from the childlist
                BQResource actualkids = BQDataService.load (r.uri); // Fetch the resource 
                Iterator ki = actualkids.children.iterator();
                int ln = actualkids.children.size();
                while (ki.hasNext()) {
                    Object x = ki.next();
                    //System.out.println ("Add kid "+x );
                    iter.add(x);
                }
                while (ln > 0) { ln -= 1; iter.previous(); }
                BQResource x = (BQResource)iter.next();
                return x;
            }
            return r;
        }
        public boolean hasNext() {
            while (iter.hasNext()) {
                object_next = (BQResource)iter.next();
                object_next = check_resource(object_next);
                if (object_next.type.equals( filter) ) return true;
            }
            return false;
        }
        public Object next() {
            BQResource next = null;
            if (object_next != null) {
                BQResource x = object_next;
                object_next = null;
                return x;
            }
            while(iter.hasNext()){
                next = (BQResource)iter.next();
                next = check_resource(next);
                if (!next.type.equals( filter) )
                    continue;
            }
            return next;
        }
        public void remove () {
            throw new UnsupportedOperationException();
        }
    }
    //-----------------------------------------------------------
}