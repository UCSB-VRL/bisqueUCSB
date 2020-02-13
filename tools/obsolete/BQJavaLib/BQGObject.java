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
import java.io.StringReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Iterator;
import org.w3c.dom.Node;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

public class BQGObject extends BQObject{

	public String name;
	public ArrayList<BQVertex> vertices;
	
	public BQGObject(){
		vertices = new ArrayList<BQVertex>();
	}
	public BQGObject(String type_){
		vertices = new ArrayList<BQVertex>();
		type = type_;
	}
	public BQGObject(String type_, String name_){
		vertices = new ArrayList<BQVertex>();
		type = type_;
		name = name_;
	}	
	public void initializeXml(Element el){
		super.initializeXml(el);
		name = BQXML.AttrStr(el, "name");
	}
	public void addParent(BQObject parent){
		parent.gobjects.add (this);
		this.parent = parent;
	}
	public Element toXml(Document doc, Element el){
		if (el == null ) 
			el = doc.createElement("gobject");
		super.toXml(doc, el);
		BQXML.StrAttr(el, "name", name);
		Iterator<BQVertex> vi = vertices.iterator();
		while(vi.hasNext()){
			BQVertex v = vi.next();
			Element vel = v.toXml(doc, null);
			el.appendChild(vel);
		}
		return el;
	}
	public void addVertices( double[] x, double[] y, double[] z, double[] t, int[] ch, int[] index){
		if (x.length != y.length && x.length != z.length 
				&& x.length != t.length && x.length != ch.length && x.length != index.length)
			//throw BQException('Arrays are not of equal length');
		for (int i=0; i < x.length; i++)
				vertices.add(new BQVertex((Double)x[i], (Double)y[i], (Double)z[i], (Double)t[i], (Integer)ch[i], (Integer)index[i]));
	}
	public double[][] toDouble(){
		double[][] v = new double[vertices.size()][6];
		System.out.println(vertices.size());
		for (int i = 0; i < vertices.size(); i++){	
			v[i][0] = vertices.get(i).x;
			v[i][1] = vertices.get(i).y;
			v[i][2] = vertices.get(i).z;
			v[i][3] = vertices.get(i).t;
			v[i][4] = vertices.get(i).ch;
			v[i][5] = vertices.get(i).index;
		}
		return v;
	}	
}
