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
import java.io.IOException;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;
import java.util.Collection;

public class BQFactory {

    public enum OBJECTS {
        image,
        tag, value,
        gobject, vertex, rectangle, circle, point, polyline, polygon,
        mex, module,
        resource, response, request;
    }
    public static BQXMLObject create(String type_, Object arguments){
        BQResource r;
        switch (OBJECTS.valueOf(type_)) {
            case image    : r = new BQImage();      break;
            case tag      : r = new BQTag();        break;
            case value    : r = new BQValue();      break;
            case gobject  : r = new BQGObject();    break;
            case vertex   : r = new BQVertex();     break;
            case rectangle: r = new BQGObject();    break;
            case circle   : r = new BQGObject();    break;
            case point    : r = new BQGObject();    break;
            case polyline : r = new BQGObject();    break;
            case polygon  : r = new BQGObject();    break;
            case mex      : r = new BQMex();        break;
            case module   : r = new BQMex();        break;
            case response : r = new BQResource();   break;
            case request  : r = new BQObject();   break;
            default       : r = new BQObject();
        }
        r.type = type_;
        return r;
    }
}