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

class BQVertex extends BQResource{

    public Double x;
    public Double y;
    public Double z;
    public Double t;
    public Integer ch;
    public Integer index;

    public BQVertex(){}
    public BQVertex(Double x_, Double y_, Double z_, Double t_, Integer ch_, Integer index_){
        x = x_;
        y = y_;
        z = z_;
        t = t_;
        ch = ch_;
        index = index_;
        //System.out.println(x+","+y+","+z+","+t+","+ch+","+index);
    }
    public void initializeXml(Element el){
        //super.initializeXml(el);
        x = BQXML.AttrDouble(el,     "x");
        y = BQXML.AttrDouble(el,     "y");
        z = BQXML.AttrDouble(el,     "z");
        t = BQXML.AttrDouble(el,     "t");
        ch = BQXML.AttrInt(el,       "ch");
        index = BQXML.AttrInt(el,    "index");
    }
    public void setParent (BQResource parent){
        ((BQGObject)parent).addVertex (this);
    }
    public Element toXml(Document doc, Element el){
        if (el == null )
            el = doc.createElement("vertex");
        BQXML.DoubleAttr(el, "x",     x);
        BQXML.DoubleAttr(el, "y",     y);
        BQXML.DoubleAttr(el, "z",     z);
        BQXML.DoubleAttr(el, "t",     t);
        BQXML.IntAttr(el,   "ch",     ch);
        BQXML.IntAttr(el,"index",     index);
        return el;
    }
}