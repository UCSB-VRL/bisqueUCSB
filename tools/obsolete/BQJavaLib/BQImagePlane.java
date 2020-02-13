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
// I/O
import java.io.IOException;
import java.io.DataInputStream;
// Images
import java.awt.Dimension;
import java.awt.Transparency;
import java.awt.image.Raster;
import java.awt.RenderingHints;
import java.awt.image.DataBuffer;
import java.awt.image.ColorModel;
import java.awt.image.SampleModel;
import java.awt.image.DataBufferByte;
import java.awt.image.renderable.ParameterBlock;
//import com.sun.media.jai.operator.ImageReadDescriptor;
import com.sun.media.imageio.stream.RawImageInputStream;
import com.sun.media.imageioimpl.plugins.raw.RawImageReader;
import com.sun.media.imageioimpl.plugins.raw.RawImageReaderSpi;
// JAI 
import javax.media.jai.JAI;
import javax.imageio.ImageIO;
import javax.media.jai.TiledImage;
import javax.media.jai.ImageLayout;
import javax.media.jai.PlanarImage;
import javax.media.jai.RegistryMode;
import javax.imageio.ImageReadParam;
import javax.media.jai.RasterFactory;
import javax.media.jai.AttributedImage;
import javax.media.jai.iterator.RectIter;
import javax.media.jai.OperationRegistry;
import javax.imageio.ImageTypeSpecifier;
import com.sun.media.jai.widget.DisplayJAI;
import javax.imageio.stream.ImageInputStream;
import javax.media.jai.iterator.RectIterFactory;
import javax.media.jai.AttributedImageCollection;
// Miscellaneous
import java.lang.reflect.Array;

public class BQImagePlane{
    public PlanarImage plane;
    public BQImagePlane(){
        plane = null;
    }
    public BQImagePlane(PlanarImage plane_){
        plane = plane_;
    }
    public PlanarImage getNativeImagePlane(){
        return plane;
    }
    public void readPlane(DataInputStream stream, Integer x, Integer y, Integer ch, Integer d) throws IOException {
        ImageInputStream iis = ImageIO.createImageInputStream(stream);
        //iis.setByteOrder(ByteOrder.BIG_ENDIAN);
        //iis.setByteOrder(ByteOrder.LITTLE_ENDIAN);
        int dataType = DataBuffer.TYPE_BYTE;
        if( d == 16 )
            dataType = DataBuffer.TYPE_USHORT;
        else if( d== 32)
            dataType = DataBuffer.TYPE_DOUBLE;
        SampleModel sampleModel = RasterFactory.createBandedSampleModel(dataType,x,y,ch);
        // Create a compatible ColorModel.
        ColorModel colorModel = PlanarImage.createColorModel(sampleModel);
        ImageTypeSpecifier its = new ImageTypeSpecifier(colorModel, sampleModel);
        // Finally, build the plane input stream
        RawImageInputStream raw = new RawImageInputStream(iis, its, new long[] { 0 }, new Dimension[] { new Dimension(x,y) });
        //long[] planeOffsets = { x*y*1*(d/8)};
        //RawImageInputStream raw = new RawImageInputStream(iis, its, planeOffsets, new Dimension[] { new Dimension(x,y) });
        ImageLayout il = new ImageLayout();
        il.setColorModel(colorModel);
        il.setSampleModel(sampleModel);

        RenderingHints hints = new RenderingHints(JAI.KEY_IMAGE_LAYOUT,il);
        ParameterBlock pbjImageRead = new ParameterBlock();
        pbjImageRead.add(raw);

        ListRegistry();
        //BQJAIInfo jai = new BQJAIInfo();
        //ImageReadDescriptor descriptor = new ImageReadDescriptor (); 
        //System.out.println("ImageRead ClassLoader: "+descriptor.getClass().getClassLoader()); 
        //System.out.println("JAI ClassLoader: "+JAI.class.getClassLoader()); 
        plane = JAI.create("ImageRead", pbjImageRead, hints);
        //plane = JAI.create("stream",raw);
        //Raster inputRaster = plane.getData();
        //readImage();
        plane.getTiles();
        //JAI.create("filestore",plane,"/home/boguslaw/Desktop/rgbpattern.tif","TIFF");
        //plane.dispose();
    }
    public void info() {
        // Show the plane dimensions and coordinates.
        System.out.print("Dimensions: ");
        System.out.print(plane.getWidth()+"x"+plane.getHeight()+" pixels");
        // Remember getMaxX and getMaxY return the coordinate of the next point!
        System.out.println(" (from "+plane.getMinX()+","+plane.getMinY()+" to " + (plane.getMaxX()-1)+","+(plane.getMaxY()-1)+")");
        if ((plane.getNumXTiles() != 1)||(plane.getNumYTiles() != 1)){ // Is it tiled?
            // Tiles number, dimensions and coordinates.
            System.out.print("Tiles: ");
            System.out.print(plane.getTileWidth()+"x"+plane.getTileHeight()+" pixels"+
                        " ("+plane.getNumXTiles()+"x"+plane.getNumYTiles()+" tiles)");
            System.out.print(" (from "+plane.getMinTileX()+","+plane.getMinTileY()+
                        " to "+plane.getMaxTileX()+","+plane.getMaxTileY()+")");
            System.out.println(" offset: "+plane.getTileGridXOffset()+","+
                            plane.getTileGridXOffset());
        }
        // Display info about the SampleModel of the plane.
        SampleModel sm = plane.getSampleModel();
        System.out.println("Number of bands: "+sm.getNumBands());
        System.out.print("Data type: ");
        switch(sm.getDataType()){
            case DataBuffer.TYPE_BYTE:     System.out.println("byte"); break;
            case DataBuffer.TYPE_SHORT:    System.out.println("short"); break;
            case DataBuffer.TYPE_USHORT:   System.out.println("ushort"); break;
            case DataBuffer.TYPE_INT:      System.out.println("int"); break;
            case DataBuffer.TYPE_FLOAT:    System.out.println("float"); break;
            case DataBuffer.TYPE_DOUBLE:   System.out.println("double"); break;
            case DataBuffer.TYPE_UNDEFINED:System.out.println("undefined"); break;
        }
        // Display info about the ColorModel of the image.
        ColorModel cm = plane.getColorModel();
        if (cm != null){
            System.out.println("Number of color components: "+ cm.getNumComponents());
            System.out.println("Bits per pixel: "+cm.getPixelSize());
            System.out.print("Transparency: ");
            switch(cm.getTransparency()){
                case Transparency.OPAQUE:       System.out.println("opaque"); break;
                case Transparency.BITMASK:      System.out.println("bitmask"); break;
                case Transparency.TRANSLUCENT:  System.out.println("translucent"); break;
            }
        }
        else System.out.println("No color model.");
    }
    private Object readIntImage(){
        SampleModel sm = plane.getSampleModel();
        int y = plane.getWidth();
        int x = plane.getHeight();
        int ch = sm.getNumBands();
        int[] pixel = new int[ch];
        RectIter iterator = RectIterFactory.create(plane, null);
        Object[] xobject = new Object[x];
        for(int xi=0;xi<x;xi++){
            Object[] yobject = new Object[y];
            xobject[xi] = yobject;
            for(int yi=0;yi<y;yi++){
                iterator.getPixel(pixel);
                yobject[yi] = pixel;
            }
        }
        return xobject;
    }
    private Object readDoubleImage(){
        SampleModel sm = plane.getSampleModel();
        int y = plane.getWidth();
        int x = plane.getHeight();
        int ch = sm.getNumBands();
        double[] pixel = new double[ch];
        RectIter iterator = RectIterFactory.create(plane, null);
        Object[] xobject = new Object[x];
        for(int xi=0;xi<x;xi++){
            Object[] yobject = new Object[y];
            xobject[xi] = yobject;
            for(int yi=0;yi<y;yi++){
                iterator.getPixel(pixel);
                System.out.print(pixel[0]);
                yobject[yi] = pixel;
            }
        }
        return xobject;
    }
    private Object readFloatImage(){
        SampleModel sm = plane.getSampleModel();
        int y = plane.getWidth();
        int x = plane.getHeight();
        int ch = sm.getNumBands();
        float[] pixel = new float[ch];
        RectIter iterator = RectIterFactory.create(plane, null);
        Object[] xobject = new Object[x];
        for(int xi=0;xi<x;xi++){
            Object[] yobject = new Object[y];
            xobject[xi] = yobject;
            for(int yi=0;yi<y;yi++){
                iterator.getPixel(pixel);
                yobject[yi] = pixel;
            }
        }
        return xobject;
    }
    public Object toMatrix(){
        Object matrix = null;
        SampleModel sm = plane.getSampleModel();
        int y = plane.getWidth();
        int x = plane.getHeight();
        int ch = sm.getNumBands();
        switch(sm.getDataType()){
            case DataBuffer.TYPE_BYTE:     matrix = readIntImage(); break;
            case DataBuffer.TYPE_SHORT:    matrix = readIntImage(); break;
            case DataBuffer.TYPE_USHORT:   matrix = readIntImage(); break;
            case DataBuffer.TYPE_INT:      matrix = readIntImage(); break;
            case DataBuffer.TYPE_FLOAT:    matrix = readFloatImage(); break;
            case DataBuffer.TYPE_DOUBLE:   matrix = readDoubleImage(); break;
        }
        return matrix;
    }
    public void readImage(){
        SampleModel sm = plane.getSampleModel();
        int y = plane.getWidth();
        int x = plane.getHeight();
        int ch = sm.getNumBands();
        int[] pixels = new int[ch*y*x];
        Raster inputRaster = plane.getData();
        inputRaster.getPixels(0,0,y,x,pixels);
        int offset;
        for(int xi=0;xi<x;xi++){
            for(int yi=0;yi<y;yi++){
                offset = xi*y*ch+yi*ch;
                System.out.print("at ("+xi+","+yi+"): ");
                for(int chi=0;chi<ch;chi++)
                    System.out.print(pixels[offset+chi]+" ");
                System.out.println();
            }
        }
    }
    //--------------------------------------------------------------
    public void ListRegistry() {
        OperationRegistry or = JAI.getDefaultInstance().getOperationRegistry();
        String[] modeNames = RegistryMode.getModeNames();
        String[] descriptorNames;
        for (int i = 0; i < modeNames.length; i++) {
            System.out.println("For registry mode: " + modeNames[i]);
            descriptorNames = or.getDescriptorNames(modeNames[i]);
            for (int j = 0; j < descriptorNames.length; j++) {
                System.out.print("\tRegistered Operator: ");
                System.out.println(descriptorNames[j]);
            }
        }
        System.out.println("<p>JAI version: "+JAI.getBuildVersion()+"</p>");
    }
    public void displayJAI(){
        // Create a frame for display.
        /*JFrame frame = new JFrame();
        frame.setTitle("DisplayJAI: "+ filename);
        Container contentPane = frame.getContentPane();
        contentPane.setLayout(new BorderLayout());
        DisplayJAI dj = new DisplayJAI(plane);
        contentPane.add(new JScrollPane(dj),BorderLayout.CENTER);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400,200); // adjust the frame size.
        frame.setVisible(true); // show the frame.*/
    }
}