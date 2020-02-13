/***************************************************************************
 *   Copyright (C) 2008 by Center for Bio-Image Informatics UCSB           *
 *   Boguslaw Obara - http://boguslawobara.net                             *
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
import java.lang.Class;

public class BQUtil{
    public static int getArrayDim(Object o){
        try{
            //Object o = new int[1][2][3];
            //int len = Array.getLength(o);  // 1
            int dim = 0;
            Class cls = o.getClass();
            while (cls.isArray()){
                //System.out.println (cls.toString());
                dim++;
                cls = cls.getComponentType();
            }
            return dim;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return 0;
        }
    }
    public static Class getArrayComponent(Object o){
        try{
            Class cls = o.getClass();
            while (cls.isArray()){
                cls = cls.getComponentType();
            }
            return cls;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return null;
        }
    }
    public static Object returnArray(){
        try{
            Object o = new int[3][2];
            return o;
        }
        catch (Exception e){
            BQError.setLastError(e);
            return null;
        }
    }

    /*public static void main(String args[]) {
        try {
            //---------------------------------------------------------
            Object o = new int[3][2];
            int dimA =  getArrayDim(o);
            System.out.println(dimA);                    
            //---------------------------------------------------------
            int [] dim = new int[3];
            dim[0] = 2;
            dim[1] = 3;
            dim[2] = 3;
            Object oo = Array.newInstance(getArrayComponent(o), dim);
            dimA =  getArrayDim(oo);
            System.out.println(dimA);
            //System.out.println("Here's result:\n" + s);
        } 
        catch (Exception e) {
            e.printStackTrace();
        }
    }*/
}