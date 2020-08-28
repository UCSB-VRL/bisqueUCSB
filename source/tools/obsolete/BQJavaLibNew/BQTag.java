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
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import java.util.Arrays;
import java.util.Iterator;
import java.util.ArrayList;

public class BQTag extends BQObject{

    public  String name;
    public  ArrayList<BQValue> values;

    public BQTag(){
        values = new ArrayList<BQValue>();
    }
    public BQTag(String name_, String value_){
        name = name_;
        values = new ArrayList<BQValue>(); 
        values.add( new BQValue(value_) );
    }
    public BQTag(String name_, Double value_){
        name = name_;
        values = new ArrayList<BQValue>();
        values.add( new BQValue(value_) );
    }
    public BQTag(String name_, ArrayList<BQValue> values_){
        name = name_;
        values = new ArrayList(Arrays.asList(values_));
    }
    public void initializeXml(Element el){
        super.initializeXml(el);
        setName( BQXML.AttrStr (el, "name"));
        setValue(BQXML.AttrStr (el, "value"));
    }
    public Element toXml(Document doc, Element el) {
        if (el == null ) 
            el = doc.createElement("tag");
        super.toXml(doc, el);
        BQXML.StrAttr(el, "name", name);
        if (values.size() == 1){
            BQXML.StrAttr(el, "value", getValue());
        }
        else {
            Iterator<BQValue> vi = values.iterator();
            while (vi.hasNext()){
                BQValue val = vi.next();
                Element vel = val.toXml(doc, null);
                el.appendChild(vel);
            }
        }
        return el;
    }
    public void setParent (BQResource parent) {
        parent.addTag(this);
        this.parent = parent;
    }
    public void setName(String name_){ name = name_; }
    public void setValue(String value_){ values.add( new BQValue(value_) ); }
    public void setValue(Double x){ values.add( new BQValue(x) ); }
    //public void setValue(ArrayList<BQValue> values_){
    //    values = new ArrayList(Arrays.asList(values_));
    //}
    public String getValue(){ 
        //System.out.println(values.size());
        if (values != null && values.size() > 0){
            //System.out.println(values.get(0).value);
            return values.get(0).value;
        }
        else
            return null;
    }
    public boolean equals(String nm){ return name.equals(nm); }
    public boolean equals(BQTag t) { return name.equals (t.name); }
    public ArrayList<BQValue> getValues(){ return values; }
}