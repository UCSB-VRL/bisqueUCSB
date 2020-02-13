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

class BQValue extends BQResource {

    public String format;
    public String value;
    public Integer index;

    public BQValue(){}
    public BQValue(Double value_){
        value = Double.toString(value_);
        format  = "number";
    }
    public BQValue(String value_){
        value = value_;
        format  = "string";
    }
    public BQValue(BQObject value_){
        value = value_.uri;
        format = "resource";
    }
    public void initializeXml(Element el){
        format  = BQXML.AttrStr(el,    "type");
        value = BQXML.AttrStr(el,    "value");
        index = BQXML.AttrInt(el,    "index");
    }
    public void setParent (BQResource parent) {
        ((BQTag)parent).values.add(this);
    }
    public Element toXml(Document doc, Element el){
        if (el == null) 
            el = doc.createElement("value");
        BQXML.StrAttr(el, "type",      format);
        BQXML.StrAttr(el, "value",     value);
        BQXML.IntAttr(el, "index",     index);
        return el;
    }
}