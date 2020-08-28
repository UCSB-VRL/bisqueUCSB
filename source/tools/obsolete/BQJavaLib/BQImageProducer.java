/***************************************************************************
 *   Copyright (C) 2009 by Center for Bio-Image Informatics UCSB           *
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


import java.io.DataOutputStream;

public class BQImageProducer implements BQDataProducer {

    String type;
    int width;
    int height;
    int channels;
    int zsize; 
    int tsize;
    Object image_matrix;

    public BQImageProducer (BQImage image, Object array) {
        type = image.type;
        width = image.x;
        height = image.y;
        channels = image.ch;
        zsize = image.z; 
        tsize = image.t;
        image_matrix = array;
    }
    public String getName(){
        return "localimage.tiff";
    }

    public void convertToStream (DataOutputStream os){
		try{
			int tmp = height; height = width; width = tmp;
			for (int t = 0; t < tsize; t++){
				for (int z = 0; z < zsize; z++){
					for (int ch = 0; ch < channels; ch++){
						for (int h = 0; h < height; h++){
							for (int w = 0; w < width; w++){
								//System.out.println(t+","+z+","+ch+","+h+","+w);
								if (type.equals("uint8")){
									byte b = 0;
									if (channels == 1 && zsize == 1 && tsize == 1)
										b = ((byte[][])image_matrix)[h][w];
									else if (channels > 1 && zsize == 1 && tsize == 1)
										b = ((byte[][][])image_matrix)[h][w][ch];
									else if (channels == 1 && zsize > 1 && tsize == 1)
										b = ((byte[][][])image_matrix)[h][w][z];
									else if (channels == 1 && zsize == 1 && tsize > 1)
										b = ((byte[][][])image_matrix)[h][w][t];
									else if (channels > 1 && zsize > 1 && tsize == 1)
										b = ((byte[][][][])image_matrix)[h][w][ch][z];
									else if (channels > 1 && zsize == 1 && tsize > 1)
										b = ((byte[][][][])image_matrix)[h][w][ch][t];
									else if (channels > 1 && zsize > 1 && tsize > 1)
										b = (byte)((byte[][][][][])image_matrix)[h][w][ch][z][t];
									os.writeByte(b);
								}
								else if (type.equals("double")){
									double d = 0.0;
									if (channels == 1 && zsize == 1 && tsize == 1)
										d = ((double[][])image_matrix)[h][w];
									else if (channels > 1 && zsize == 1 && tsize == 1)
										d = ((double[][][])image_matrix)[h][w][ch];
									else if (channels == 1 && zsize > 1 && tsize == 1)
										d = ((double[][][])image_matrix)[h][w][z];
									else if (channels == 1 && zsize == 1 && tsize > 1)
										d = ((double[][][])image_matrix)[h][w][t];
									else if (channels > 1 && zsize > 1 && tsize == 1)
										d = ((double[][][][])image_matrix)[h][w][ch][z];
									else if (channels > 1 && zsize == 1 && tsize > 1)
										d = ((double[][][][])image_matrix)[h][w][ch][t];
									else if (channels > 1 && zsize > 1 && tsize > 1)
										d = ((double[][][][][])image_matrix)[h][w][ch][z][t];
									os.writeDouble(d);
								}
								else if (type.equals("uint16")){
									short s = 0;
									if (channels == 1 && zsize == 1 && tsize == 1)
										s = ((short[][])image_matrix)[h][w];
									else if (channels > 1 && zsize == 1 && tsize == 1)
										s = ((short[][][])image_matrix)[h][w][ch];
									else if (channels == 1 && zsize > 1 && tsize == 1)
										s = ((short[][][])image_matrix)[h][w][z];
									else if (channels == 1 && zsize == 1 && tsize > 1)
										s = ((short[][][])image_matrix)[h][w][t];
									else if (channels > 1 && zsize > 1 && tsize == 1)
										s = ((short[][][][])image_matrix)[h][w][ch][z];
									else if (channels > 1 && zsize == 1 && tsize > 1)
										s = ((short[][][][])image_matrix)[h][w][ch][t];
									else if (channels > 1 && zsize > 1 && tsize > 1)
										s = ((short[][][][][])image_matrix)[h][w][ch][z][t];
									os.writeShort(Short.reverseBytes(s));
								}
							}
						}
					}
				}
			}
		}
		catch (Exception e){
			BQError.setLastError(e);
		}
    }
}
