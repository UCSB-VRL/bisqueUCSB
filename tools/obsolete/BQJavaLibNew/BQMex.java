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
import java.util.Iterator;
import java.util.ArrayList;
import org.w3c.dom.Element;
import org.w3c.dom.Document;

public class BQMex extends BQObject{

    public String status;
    public String module;

    public BQMex(){ 
        super (null, "mex");
    }
    public BQMex(String uri){
        super(uri, "image");
    }
    public void initializeXml(Element el){
        super.initializeXml(el);
        status      = BQXML.AttrStr(el, "status");
        module      = BQXML.AttrStr(el, "module");
    }
    public Element toXml(Document doc, Element el){
        if (el == null)
            el = doc.createElement("resource");
        super.toXml (doc, el);
        BQXML.StrAttr(el,"status",      status);
        BQXML.StrAttr(el,"module",      module);
        return el;
    }
}