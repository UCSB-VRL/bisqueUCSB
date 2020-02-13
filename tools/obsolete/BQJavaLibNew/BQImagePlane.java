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
import java.io.File;
import java.io.IOException;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.ObjectOutputStream;
// Images
import java.awt.Dimension;
import java.awt.Transparency;
import java.awt.image.Raster;
import java.awt.RenderingHints;
import java.awt.image.DataBuffer;
import java.awt.image.ColorModel;
import java.awt.image.SampleModel;
import java.awt.image.BufferedImage;
import java.awt.image.RenderedImage;
import java.awt.image.WritableRaster;
import java.awt.image.DataBufferByte;
import java.awt.image.DataBufferInt;
import java.awt.image.DataBufferShort;
import java.awt.image.DataBufferUShort;
import java.awt.image.DataBufferFloat;
import java.awt.image.DataBufferDouble;
import java.awt.image.BandedSampleModel;
import java.awt.image.ComponentSampleModel;
import java.awt.image.PixelInterleavedSampleModel;

//import java.awt.image.DataBufferByte;
//import java.awt.image.renderable.ParameterBlock;
import com.sun.media.jai.operator.ImageReadDescriptor;
import com.sun.media.jai.operator.ImageWriteDescriptor;
//import com.sun.media.imageio.stream.RawImageInputStream;
//import com.sun.media.imageioimpl.plugins.raw.RawImageReader;
//import com.sun.media.imageioimpl.plugins.raw.RawImageReaderSpi;
// JAI 
import javax.media.jai.JAI;
import javax.imageio.ImageIO;
import javax.imageio.ImageWriter;
import javax.media.jai.RenderedOp;
import javax.media.jai.TiledImage;
import javax.media.jai.ImageLayout;
import javax.media.jai.PlanarImage;
//import javax.media.jai.RegistryMode;
import javax.imageio.ImageReadParam;
import javax.media.jai.RasterFactory;
import javax.media.jai.ParameterBlockJAI;
import java.awt.image.renderable.ParameterBlock;
import javax.media.jai.ComponentSampleModelJAI;
//import javax.media.jai.iterator.RectIter;
//import javax.media.jai.iterator.RandomIter;
//import javax.media.jai.OperationRegistry;
//import javax.imageio.ImageTypeSpecifier;
//import com.sun.media.jai.widget.DisplayJAI;
import javax.imageio.stream.ImageInputStream;
import javax.imageio.stream.ImageOutputStream;
//import javax.media.jai.iterator.RectIterFactory;
//import javax.media.jai.iterator.RandomIterFactory;
//import javax.media.jai.AttributedImageCollection;
import javax.imageio.stream.FileImageOutputStream;
// Miscellaneous
import java.lang.reflect.Array;
import java.nio.ByteOrder;
import java.util.Iterator;
import java.util.ArrayList;
import java.awt.Point;

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
    public void setData(byte[] dataArray, Integer x, Integer y, Integer ch){
        DataBuffer dataBuffer = new DataBufferByte(dataArray, x*y*ch);
        setPlanarImage(x, y, ch, DataBuffer.TYPE_BYTE, dataBuffer);
    }    
    public void setData(short[] dataArray, Integer x, Integer y, Integer ch){
        DataBuffer dataBuffer = new DataBufferUShort(dataArray, x*y*ch);
        setPlanarImage(x, y, ch, DataBuffer.TYPE_USHORT, dataBuffer);
    }
    public void setData(double[] dataArray, Integer x, Integer y, Integer ch){
        DataBuffer dataBuffer = new DataBufferDouble(dataArray, x*y*ch);
        setPlanarImage(x, y, ch, DataBuffer.TYPE_DOUBLE, dataBuffer);
    }

    public void setData(byte[][] dataArray, Integer x, Integer y, Integer ch){
        DataBuffer dataBuffer = new DataBufferByte(dataArray, x*y);
        setPlanarImage(x, y, ch, DataBuffer.TYPE_BYTE, dataBuffer);
    }
    public void setData(short[][] dataArray, Integer x, Integer y, Integer ch){
        DataBuffer dataBuffer = new DataBufferUShort(dataArray, x*y);
        setPlanarImage(x, y, ch, DataBuffer.TYPE_USHORT, dataBuffer);
    }
    public void setData(double[][] dataArray, Integer x, Integer y, Integer ch){
        DataBuffer dataBuffer = new DataBufferDouble(dataArray, x*y);
        setPlanarImage(x, y, ch, DataBuffer.TYPE_DOUBLE, dataBuffer);
    }
    public void setPlanarImage(Integer x, Integer y, Integer ch, Integer dataType, DataBuffer dataBuffer){
        SampleModel sampleModel = RasterFactory.createBandedSampleModel(dataType, x, y, ch);
        ColorModel colorModel = PlanarImage.createColorModel(sampleModel);
        Raster raster = RasterFactory.createWritableRaster(sampleModel, dataBuffer, new Point(0, 0));
        TiledImage tiledImage = new TiledImage(0, 0, x, y, 0, 0, sampleModel, colorModel);
        tiledImage.setData(raster);
        plane = tiledImage;
    }

    public void readPlane(DataInputStream stream, Integer x, Integer y, Integer ch, Integer d) throws IOException {
        ImageInputStream iis = ImageIO.createImageInputStream(stream);
        iis.setByteOrder(ByteOrder.LITTLE_ENDIAN);
        int dataType = DataBuffer.TYPE_BYTE;
        if( d == 16 )
            dataType = DataBuffer.TYPE_USHORT;
        else if( d == 32)
            dataType = DataBuffer.TYPE_DOUBLE;
        SampleModel sampleModel = RasterFactory.createBandedSampleModel(dataType,x,y,ch);
        ColorModel colorModel = PlanarImage.createColorModel(sampleModel);
        ImageLayout il = new ImageLayout();
        il.setColorModel(colorModel);
        il.setSampleModel(sampleModel);

        RenderingHints hints = new RenderingHints(JAI.KEY_IMAGE_LAYOUT,il);
        ParameterBlock pbjImageRead = new ParameterBlock();
        pbjImageRead.add(iis);

        plane = JAI.create("ImageRead", pbjImageRead, hints);
        plane.getData();
        //writePlaneToFile("/home/boguslaw/Desktop/im.tif","TIFF");
        //plane = JAI.create("ImageRead", iis);
        //plane.getData();
        //JAI.create("filestore",plane,"/home/boguslaw/Desktop/im.tif","TIFF");
        //readImage();
    }
    public void writePlane(DataOutputStream stream) throws IOException {
        //info();
        ImageOutputStream ois = ImageIO.createImageOutputStream(stream);
        ois.setByteOrder(ByteOrder.LITTLE_ENDIAN);
        SampleModel sm = plane.getSampleModel();
        switch(sm.getDataType()){
            case DataBuffer.TYPE_BYTE:     writeByte(ois);   break;
            case DataBuffer.TYPE_SHORT:    writeShort(ois);  break;
            case DataBuffer.TYPE_USHORT:   writeUShort(ois); break;
            case DataBuffer.TYPE_INT:      writeInt(ois);    break;
            case DataBuffer.TYPE_FLOAT:    writeFloat(ois);  break;
            case DataBuffer.TYPE_DOUBLE:   writeDouble(ois); break;
        }
        ois.flush();
    }
    public void writePlaneToFile(String filename, String format) throws IOException {
        JAI.create("filestore", plane, filename, format);
    }
    public void writeByte(ImageOutputStream stream) throws IOException {
        byte[][] array = readByte();
        int rows = array.length;
        int columns = 0;
        if(rows > 0) 
            columns = array[0].length;
        for(int j=0; j<rows; j++) 
            stream.write(array[j], 0, columns);
    }
    public void writeShort(ImageOutputStream stream) throws IOException {
        short[][] array = readShort();
        int rows = array.length;
        int columns = 0;
        if(rows > 0)
            columns = array[0].length;
        for(int i=0; i<rows; i++) 
            for(int j=0; j<columns; j++)
                stream.writeShort(array[i][j]);
    }
    public void writeUShort2(ImageOutputStream stream) throws IOException {
        short[][] array = readUShort();
        int rows = array.length;
        int columns = 0;
        if(rows > 0)
            columns = array[0].length;
        short max = -1;
        short min = 1000;
        for(int i=0; i<rows; i++) 
            for(int j=0; j<columns; j++){
                if (array[i][j]> max)
                    max = array[i][j];
                if (array[i][j]< min)
                    min = array[i][j];
                stream.writeShort(array[i][j]);
            }
        System.out.println("min: " + min);
        System.out.println("max: " + max);
    }
    public void writeUShort(ImageOutputStream stream) throws IOException {
        short[][] array = readUShort();
        int rows = array.length;
        int columns = 0;
        if(rows > 0)
            columns = array[0].length;
        short max = -1;
        short min = 1000;
        for(int i=0; i<rows; i++) 
            stream.writeShorts(array[i], 0, columns);
    }
    public void writeInt(ImageOutputStream stream) throws IOException {
        int[][] array = readInt();
        int rows = array.length;
        int columns = 0;
        if(rows > 0)
            columns = array[0].length;
        for(int i=0; i<rows; i++) 
            for(int j=0; j<columns; j++)
                stream.writeInt(array[i][j]);
    }
    public void writeFloat(ImageOutputStream stream) throws IOException {
        float[][] array = readFloat();
        int rows = array.length;
        int columns = 0;
        if(rows > 0)
            columns = array[0].length;
        for(int i=0; i<rows; i++) 
            for(int j=0; j<columns; j++)
                stream.writeFloat(array[i][j]);
    }
    public void writeDouble(ImageOutputStream stream) throws IOException {
        double[][] array = readDouble();
        int rows = array.length;
        int columns = 0;
        if(rows > 0)
            columns = array[0].length;
        for(int i=0; i<rows; i++) 
            for(int j=0; j<columns; j++)
                stream.writeDouble(array[i][j]);
    }
    public byte[][] readByte(){
        WritableRaster raster = plane.copyData();
        if (canUseBankData(plane, 1, DataBuffer.TYPE_BYTE, DataBufferByte.class)) {
            return ((DataBufferByte) raster.getDataBuffer()).getBankData();
        }
        //return getBytes(makeType(image, dataType));
        int w = plane.getWidth(), h = plane.getHeight(), c = raster.getNumBands();
        byte[][] samples = new byte[c][w * h];
        int[] buf = new int[w * h];
        for (int i=0; i<c; i++) {
            raster.getSamples(0, 0, w, h, i, buf);
            for (int j=0; j<buf.length; j++) samples[i][j] = (byte) buf[j];
        }
        return samples;
        //Raster raster = plane.getData();
        //DataBufferByte buffer = (DataBufferByte)raster.getDataBuffer();
        //return buffer.getBankData();
    }
    public short[][] readShort(){
        Raster raster = plane.getData();
        DataBufferShort buffer = (DataBufferShort)raster.getDataBuffer();
        return buffer.getBankData();
    }
    public short[][] readUShort(){
        Raster raster = plane.getData();
        DataBufferUShort buffer = (DataBufferUShort)raster.getDataBuffer();
        return buffer.getBankData();
    }
    public int[][] readInt(){
        Raster raster = plane.getData();
        DataBufferInt buffer = (DataBufferInt)raster.getDataBuffer();
        return buffer.getBankData();
    }
    public float[][] readFloat(){
        Raster raster = plane.getData();
        DataBufferFloat buffer = (DataBufferFloat)raster.getDataBuffer();
        return buffer.getBankData();
    }
    public double[][] readDouble(){
        Raster raster = plane.getData();
        DataBufferDouble buffer = (DataBufferDouble)raster.getDataBuffer();
        return buffer.getBankData();
    }
    public DataBuffer readDataBuffer(){
        Raster raster = plane.getData();
        return raster.getDataBuffer();
    }
    public boolean canUseBankData(PlanarImage image,
        int bytesPerPixel, int transferType, Class dataBufferClass) {
        WritableRaster r = image.copyData();
        int tt = r.getTransferType();
        if (tt != transferType) return false;
        DataBuffer buffer = r.getDataBuffer();
        if (!dataBufferClass.isInstance(buffer)) return false;
        SampleModel model = r.getSampleModel();
        if (!(model instanceof ComponentSampleModel)) return false;
        ComponentSampleModel csm = (ComponentSampleModel) model;
        int pixelStride = csm.getPixelStride();
        if (pixelStride != 1) return false;
        int w = r.getWidth();
        int scanlineStride = csm.getScanlineStride();
        if (scanlineStride != w) return false;
        int c = r.getNumBands();
        int[] bandOffsets = csm.getBandOffsets();
        if (bandOffsets.length != c) return false;
        for (int i=0; i<bandOffsets.length; i++) {
            if (bandOffsets[i] != 0) return false;
        }
        int[] bankIndices = csm.getBankIndices();
        for (int i=0; i<bandOffsets.length; i++) {
            if (bandOffsets[i] != i) return false;
        }
        return true;
    }
    public void untileImage() {
        System.setProperty("com.sun.media.jai.disableMediaLib", "true"); 
        final ParameterBlockJAI pbj = new ParameterBlockJAI("format");
        pbj.addSource(plane);
        pbj.setParameter("dataType", plane.getSampleModel().getTransferType());

        final ImageLayout layout = new ImageLayout(plane);
        layout.unsetTileLayout();
        layout.setTileGridXOffset(0);
        layout.setTileGridYOffset(0);
        layout.setTileHeight(plane.getHeight());
        layout.setTileWidth(plane.getWidth());
        layout.setValid(ImageLayout.TILE_GRID_X_OFFSET_MASK
                | ImageLayout.TILE_GRID_Y_OFFSET_MASK
                | ImageLayout.TILE_HEIGHT_MASK | ImageLayout.TILE_WIDTH_MASK);

        final RenderingHints hints = new RenderingHints(JAI.KEY_IMAGE_LAYOUT,layout);
        plane = JAI.create("format", pbj, hints);//.createInstance();
    }
    public Object toMatrix(){
        Object matrix = null;
//         SampleModel sm = plane.getSampleModel();
//         switch(sm.getDataType()){
//             case DataBuffer.TYPE_BYTE:     matrix = readIntImage(); break;
//             case DataBuffer.TYPE_SHORT:    matrix = readIntImage(); break;
//             case DataBuffer.TYPE_USHORT:   matrix = readIntImage(); break;
//             case DataBuffer.TYPE_INT:      matrix = readIntImage(); break;
//             case DataBuffer.TYPE_FLOAT:    matrix = readFloatImage(); break;
//             case DataBuffer.TYPE_DOUBLE:   matrix = readDoubleImage(); break;
//         }
//         System.out.println(matrix);
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
                    System.out.print(+pixels[offset+chi]+" ");
                System.out.println();
            }
        }
    }
    public ArrayList<BQImagePlane> getBands(){
        SampleModel sm = plane.getSampleModel();
        ArrayList<BQImagePlane> bands = new ArrayList<BQImagePlane>();
        ParameterBlockJAI pb;
        for(int chi=0;chi<sm.getNumBands();chi++){
        //for(int chi=0;chi<1;chi++){
            pb = new ParameterBlockJAI("BandSelect");
            pb.addSource(plane);
            pb.setParameter("bandIndices", new int[]{chi});
            PlanarImage pi = JAI.create("BandSelect", pb);
            BQImagePlane p = new BQImagePlane();
            p.plane = pi;
            p.untileImage();
            bands.add(p);
        }
        return bands;
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
        int transferType = sm.getTransferType();
        System.out.print("SM type: ");
        if(sm instanceof PixelInterleavedSampleModel)
             System.out.println("TYPE_PIXEL_INTERLEAVED");
        if(sm  instanceof BandedSampleModel)
            System.out.println("TYPE_BANDED");
        if(sm instanceof ComponentSampleModelJAI ||
                      transferType == DataBuffer.TYPE_FLOAT ||
                      transferType == DataBuffer.TYPE_DOUBLE)
            System.out.println("TYPE_COMPONENT_JAI");

        // Display info about the ColorModel of the image.
        ColorModel cm = plane.getColorModel();
        if (cm != null){
            System.out.println("Number of color components: "+ cm.getNumComponents());
            System.out.println("Bits per pixel: "   +cm.getPixelSize());
            System.out.println("Color space type: " +cm.getColorSpace().getType());
            System.out.println("Transfer type: "    +cm.getTransferType());
            System.out.print("Transparency: ");
            switch(cm.getTransparency()){
                case Transparency.OPAQUE:       System.out.println("opaque"); break;
                case Transparency.BITMASK:      System.out.println("bitmask"); break;
                case Transparency.TRANSLUCENT:  System.out.println("translucent"); break;
            }
        }
        else System.out.println("No color model.");
    }
    public void saveToFile(String name) {
        JAI.create("filestore",plane,name,"TIFF");
    }


/*
    public Object readIntImage(){
        SampleModel sm = plane.getSampleModel();
        int x = plane.getHeight();
        int y = plane.getWidth();
        int ch = sm.getNumBands();
        int[] pixels = new int[ch*y*x];
        Raster inputRaster = plane.getData();
        inputRaster.getPixels(0,0,y,x,pixels);
        int offset;
        int[][][] xobject = new int[x][][];
        for(int xi=0;xi<x;xi++){
            int[][] yobject = new int[y][];
            xobject[xi] = yobject;
            for(int yi=0;yi<y;yi++){
                offset = xi*y*ch+yi*ch;
                int[] pixel = new int[ch];
                for(int chi=0;chi<ch;chi++)
                    pixel[chi] = pixels[offset+chi];
                yobject[yi] = pixel;
            }
        }
        return xobject;
    }
    public Object readFloatImage(){
        SampleModel sm = plane.getSampleModel();
        int x = plane.getHeight();
        int y = plane.getWidth();
        int ch = sm.getNumBands();
        float[] pixels = new float[ch*y*x];
        Raster inputRaster = plane.getData();
        inputRaster.getPixels(0,0,y,x,pixels);
        int offset;
        float[][][] xobject = new float[x][][];
        for(int xi=0;xi<x;xi++){
            float[][] yobject = new float[y][];
            xobject[xi] = yobject;
            for(int yi=0;yi<y;yi++){
                offset = xi*y*ch+yi*ch;
                float[] pixel = new float[ch];
                for(int chi=0;chi<ch;chi++)
                    pixel[chi] = pixels[offset+chi];
                yobject[yi] = pixel;
            }
        }
        return xobject;
    }
    public Object readDoubleImage(){
        SampleModel sm = plane.getSampleModel();
        int x = plane.getHeight();
        int y = plane.getWidth();
        int ch = sm.getNumBands();
        double[] pixels = new double[ch*y*x];
        Raster inputRaster = plane.getData();
        inputRaster.getPixels(0,0,y,x,pixels);
        int offset;
        double[][][] xobject = new double[x][][];
        for(int xi=0;xi<x;xi++){
            double[][] yobject = new double[y][];
            xobject[xi] = yobject;
            for(int yi=0;yi<y;yi++){
                offset = xi*y*ch+yi*ch;
                double[] pixel = new double[ch];
                for(int chi=0;chi<ch;chi++)
                    pixel[chi] = pixels[offset+chi];
                yobject[yi] = pixel;
            }
        }
        return xobject;
    }
    public void writePlaneToFile(String filename) throws IOException {
        ImageOutputStream ois = ImageIO.createImageOutputStream(new File(filename));
        plane = untileImage(plane);
        ParameterBlockJAI pb = new ParameterBlockJAI("ImageWrite");
        pb.addSource(plane); 
        pb.setParameter("Output", ois); 
        pb.setParameter("Format", "tiff");
        RenderedOp wOp = JAI.create("ImageWrite", pb);
        Object o = wOp.getProperty(ImageWriteDescriptor.PROPERTY_NAME_IMAGE_WRITER);
        if (o instanceof ImageWriter)
            ((ImageWriter) o).dispose();
        ois.flush();
        ois.close();
    }
*/









    /*public void ListRegistry() {
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
    }*/
    /*public void displayJAI(){
        // Create a frame for display.
        JFrame frame = new JFrame();
        frame.setTitle("DisplayJAI: "+ filename);
        Container contentPane = frame.getContentPane();
        contentPane.setLayout(new BorderLayout());
        DisplayJAI dj = new DisplayJAI(plane);
        contentPane.add(new JScrollPane(dj),BorderLayout.CENTER);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400,200); // adjust the frame size.
        frame.setVisible(true); // show the frame.
    }*/
    /*public void readPlaneRaw(DataInputStream stream, Integer x, Integer y, Integer ch, Integer d) throws IOException {
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

        plane = JAI.create("ImageRead", pbjImageRead, hints);
        info();
        plane.getData();
        readImage();
    }*/
    /*private Object readIntImageIterator(){ // Old version
        SampleModel sm = plane.getSampleModel();
        int x = plane.getWidth();
        int y = plane.getHeight();
        int ch = sm.getNumBands();
        info();

        RectIter iterator = RectIterFactory.create(plane, null);
        //RandomIter iterator = RandomIterFactory.create(plane, null);
        int[][][] xobject = new int[x][][];
        for(int xi=0;xi<x;xi++){
            int[][] yobject = new int[y][];
            xobject[xi] = yobject;
            for(int yi=0;yi<y;yi++){
                System.out.println("x: " + xi+ ";   y: " +yi+";");
                int[] pixel = new int[ch];
                iterator.getPixel(pixel);
                //iterator.getPixel(x,y,pixel);
                //System.out.print(pixel[1]);
                yobject[yi] = pixel;
                iterator.nextPixel();
            }
        }
        return xobject;
    }*/
/*
    public void writePlane(DataOutputStream stream) throws IOException {
//         System.setProperty("com.sun.media.jai.disableMediaLib", "true");   
//         ObjectOutputStream ois = new ObjectOutputStream(stream);
//         BQImagePlane band = new BQImagePlane();
//         ParameterBlockJAI pb;
//         SampleModel sm = plane.getSampleModel();
//         for(int chi=0;chi<sm.getNumBands();chi++){
//             pb = new ParameterBlockJAI("BandSelect");
//             pb.addSource(plane);
//             pb.setParameter("bandIndices", new int[]{chi});
//             band.plane = JAI.create("BandSelect", pb);
//             //band.plane = untileImage(band.plane);
//             //band.writePlaneToFile("/home/boguslaw/Desktop/im" +chi+ ".tif");
//             //band.writePlaneToFile2("/home/boguslaw/Desktop/im" +chi+ ".raw", "raw");
//             band.info();
//             Object imagedata = band.toMatrix();
//             ois.writeObject(imagedata);
//         }
        //ois.flush();
        //ois.close();





        

       System.setProperty("com.sun.media.jai.disableMediaLib", "true"); 
        //ImageOutputStream ois = ImageIO.createImageOutputStream(stream);
        ObjectOutputStream ois = new ObjectOutputStream(stream);
        //ois.setByteOrder(ByteOrder.LITTLE_ENDIAN);
        plane = untileImage(plane);
        //SampleModel sm = plane.getSampleModel();


//         File tmpRaw = new File("/home/boguslaw/Desktop/im2.raw");
// 
//   // Write source in file using "raw" format.
//         if (true) {
//             ImageIO.write(plane, "raw", tmpRaw);
//         } else {
//             final Iterator writers = ImageIO.getImageWritersByFormatName("raw");
//             if (!writers.hasNext()) {
//                 throw new IOException("There is no writer.");
//             }
//             final ImageWriter writer = (ImageWriter) writers.next();
//             ParameterBlock block2 = (new ParameterBlock()).addSource(plane);
//             block2 = block2.add(tmpRaw);
//             block2 = block2.add(null);
//             block2 = block2.add(Boolean.TRUE);
//             block2 = block2.add(Boolean.TRUE);
//             block2 = block2.add(Boolean.TRUE);
//             block2 = block2.add(Boolean.TRUE);
//             block2 = block2.add(new Dimension(plane.getWidth(), plane.getHeight()));
//             block2 = block2.add(null);
//             block2 = block2.add(null);
//             block2 = block2.add(null);
//             block2 = block2.add(null);
//             block2 = block2.add(writer.getLocale());
//             block2 = block2.add(writer.getDefaultWriteParam());
//             block2 = block2.add(writer);
//             final RenderedImage img2 = JAI.create("ImageWrite", block2,hints)
//         }










//         ParameterBlockJAI pb;
        //for(int chi=0;chi<sm.getNumBands();chi++){
//         for(int chi=0;chi<1;chi++){
//             pb = new ParameterBlockJAI("BandSelect");
//             pb.addSource(plane);
//             pb.setParameter("bandIndices", new int[]{chi});
//             band.plane = JAI.create("BandSelect", pb);
//             band.plane = untileImage(band.plane);
//             //band.writePlaneToFile("/home/boguslaw/Desktop/im" +chi+ ".tif");
//             //band.writePlaneToFile2("/home/boguslaw/Desktop/im" +chi+ ".raw", "raw");
//             band.info();
//             Object image = bands.get(0).toMatrix();
//             for (int h = 0; h < bands.get(0).plane.getHeight(); h++){
//                 for (int w = 0; w < bands.get(0).plane.getWidth(); w++){
//                 //System.out.println(t+","+z+","+ch+","+h+","+w);
//                     byte b = 0;
//                     b = (byte)(((byte[][][])image)[w][h][0]);
//                     ois.writeByte(b);
//                     //ois.writeObject(b);
//                 }
//             }
*/


}
