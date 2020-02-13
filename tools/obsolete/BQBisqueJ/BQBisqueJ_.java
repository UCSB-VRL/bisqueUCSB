/***************************************************************************
 *   Copyright (C) 2008 by Boguslaw Obara                                  *
 *   http://boguslawobara.net                                              *
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
/*
 * BQBisqueJ_
 * Version: 
 * 0.1 - 01/01/2008 First implementation.
 */

import java.awt.Toolkit;
import java.text.NumberFormat;
import java.text.ParseException;
import java.util.Locale;
import javax.swing.text.*; 
// specific end

import java.io.*;
import java.awt.*;
import java.awt.image.*;
import java.awt.event.*;
import java.awt.Color.*;
import java.awt.geom.Rectangle2D;
import java.util.ArrayList;
import java.util.Arrays;
import java.lang.Object;
import ij.text.TextWindow;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.colorchooser.*;
import javax.swing.border.*;
import ij.*;
import ij.io.*;
import ij.process.*;
import ij.plugin.*;
import ij.plugin.frame.*;
import ij.plugin.PlugIn;
import ij.text.TextWindow;
import ij.plugin.filter.Convolver;
import ij.plugin.filter.Duplicater;
import java.lang.Math;
import ij.gui.*;
import java.util.ArrayList;
import java.util.Iterator;


import bisque.*;
//------------------------------------------------------------------------------
//------------------------------------------------------------------------------
//------------------------------------------------------------------------------
//------------------------------------------------------------------------------
public class BQBisqueJ_ implements PlugIn{

	public GUI theGUI;
	public int initial_tooltip_delay;
	/* ImageJ plugin entry point of BQBisqueJ */

	public void run(String args ){
		if (args.equals("about")){
			showAbout();
		}
		else{
			IJ.showStatus("Plugin BQBisqueJ started.");
			theGUI = new GUI();
			theGUI.init();
			initial_tooltip_delay = ToolTipManager.sharedInstance().getInitialDelay();
		}
	}

	void showAbout() {
		IJ.showMessage("About BQBisqueJ",
		"Copyright (C) 2008 Boguslaw Obara\n" +
		"http://boguslawobara.net\n" +
		"Email: obara@ece.ucsb.edu\n"+
		"Please send bug reports and wishes to the above email address.\n"
		);
	}
//******************************************************************************
//******************************************************************************
/* class GUI start */
//******************************************************************************
//******************************************************************************
public class GUI {
	public JFrame baseFrame;
	private JPanel allPanel, dbPanel, upPanel, serverPanel, connectPanel, dblistPanel, listPanel, downloadPanel, searchPanel;
	private Dimension ScreenDimension = Toolkit.getDefaultToolkit().getScreenSize();
	private int ScreenX = (int) ScreenDimension.getWidth();
	private int ScreenY = (int) ScreenDimension.getHeight();
	private int baseFrameXsize = (int)(ScreenX/3.6);
	private int baseFrameYsize = (int)(ScreenY/2);
	private int baseFrameXlocation = (int)((11*ScreenX/12) - baseFrameXsize);
	private int baseFrameYlocation = (int)((8.5*ScreenY/12) - baseFrameYsize);

	private smallButton connectButton = new smallButton("Connect","Connect the Bisque DataBase");
	private smallButton downloadButton = new smallButton("Download Image", "Download Image");
	private smallButton uploadButton = new smallButton("Upload Image", "Upload Image");
	
	Label userLabel = new Label("User");
	Label passLabel = new Label("Password");
	Label serverLabel = new Label("Server");
	Label searchLabel = new Label("Search");
	TextField userTF = new TextField("admin");
	TextField passTF = new TextField("admin");
	TextField serverTF = new TextField("http://bodzio.ece.ucsb.edu:8080");
	TextField searchTF = new TextField("search criteria");
	Color labelBG = new Color(0, 0, 0);
	Font labelFont = new Font("Monospaced", Font.PLAIN, 12);
	JList list = new JList();
	Checkbox tagsChBox = new Checkbox("Tags");


	/** Initiates the GUI, setting its layout*/
	public void init() {
		baseFrame = new JFrame();
		baseFrame.setTitle("BQBisqueJ 0.1");
		baseFrame.setSize(baseFrameXsize,baseFrameYsize);
		//baseFrame.setResizable(false);
		baseFrame.setLocation(baseFrameXlocation,baseFrameYlocation);
		baseFrame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
		allPanel = new JPanel();
		allPanel.setSize(baseFrameXsize, baseFrameYsize);
		allPanel.setForeground(SystemColor.window);
		//allPanel.setLayout(new FlowLayout());
		allPanel.setLayout(new GridLayout(2,1,2,2));
		
		dbPanel = new JPanel();
		dbPanel.setForeground(SystemColor.window);
		dbPanel.setLayout(new GridLayout(4, 1)); 
		upPanel = new JPanel();
		upPanel.setLayout(new FlowLayout());
		serverPanel = new JPanel();
		serverPanel.setLayout(new FlowLayout());
		searchPanel = new JPanel();
		searchPanel.setLayout(new FlowLayout());
		connectPanel = new JPanel();
		connectPanel.setLayout(new FlowLayout());
		dbPanel.setBorder(BorderFactory.createTitledBorder(BorderFactory.createLineBorder(Color.black, 1), "Bisque Settings"));

		userLabel.setForeground(labelBG);
		userLabel.setFont(labelFont);
		passLabel.setForeground(labelBG);
		passLabel.setFont(labelFont);
		serverLabel.setForeground(labelBG);
		serverLabel.setFont(labelFont);
		searchLabel.setForeground(labelBG);
		searchLabel.setFont(labelFont);
		userTF.setForeground(labelBG);
		userTF.setFont(labelFont);
		passTF.setForeground(labelBG);
		passTF.setFont(labelFont);
		serverTF.setForeground(labelBG);
		serverTF.setFont(labelFont);
		searchTF.setForeground(labelBG);
		searchTF.setFont(labelFont);

		upPanel.add(userLabel);
		upPanel.add(userTF);
		upPanel.add(passLabel);
		upPanel.add(passTF);
		serverPanel.add(serverLabel);
		serverPanel.add(serverTF);
		searchPanel.add(searchLabel);
		searchPanel.add(searchTF);
		searchPanel.add(tagsChBox);
		connectPanel.add(connectButton);
		connectPanel.add(downloadButton);
		connectPanel.add(uploadButton);
		dbPanel.add(upPanel);
		dbPanel.add(serverPanel);
		dbPanel.add(searchPanel);
		dbPanel.add(connectPanel);
		allPanel.add(dbPanel);

		listPanel = new JPanel();
		listPanel.setLayout(new GridLayout(1, 1));
		
		JScrollPane scrollingList = new JScrollPane(list);
		scrollingList.setSize(baseFrameXsize, baseFrameYsize/4);
		scrollingList.setBorder(BorderFactory.createTitledBorder(BorderFactory.createLineBorder(Color.black, 1), "List of Images"));
		listPanel.add(scrollingList);

		allPanel.add(listPanel);
		baseFrame.getContentPane().add(allPanel);
		
		addDownloadListener(downloadButton, baseFrame);
		addConnectListener(connectButton, baseFrame);
		addUploadListener(uploadButton, baseFrame);
		//baseFrame.show();
		baseFrame.setVisible(true);
		searchTF.setText("");
	}

	
	/* Action listeners for the buttons*/
	//----------------------------------------------------------------------
	//----------------------------------------------------------------------
	private void addUploadListener(final JButton button, final JFrame parent)	{
		button.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent e){
				uploadImage();
			}
		});
	}

	private void addDownloadListener(final JButton button, final JFrame parent){
		button.addActionListener(new ActionListener () {
			public void actionPerformed(ActionEvent e) {
				downloadImage();
			}
		});
	}
	private void addConnectListener(final JButton button, final JFrame parent){
		button.addActionListener(new ActionListener(){
			public void actionPerformed(ActionEvent e){
				connectBisquik();
			}
		});
	}
	private void addExitListener(final JButton button, final JFrame parent) {
		button.addActionListener(new ActionListener () {
			public void actionPerformed(ActionEvent e) {
				baseFrame.dispose();
			}
		});
	}
	
	/* FUNCTIONS*/
	//----------------------------------------------------------------------
	public void downloadImage() { 
		try
		{
			if (list.isSelectionEmpty())
				IJ.showMessage("Select image to be downloaded");
			else
			{
				IJ.showStatus("Connecting ...");
				String selectedURL = (String)list.getSelectedValue();
				BQAuthorization.setAuthorization(userTF.getText(), passTF.getText());
				BQDataService ds = new BQDataService(serverTF.getText());
				BQImage image = (BQImage)ds.load(selectedURL);
				image.getInfo();
				int tsize = image.t;
				int zsize = image.z;
				int height = image.y;
				int width = image.x;
				int depth = image.d;
				int channels = image.ch;
				String infoz = Integer.toString(zsize);
				String infot = Integer.toString(tsize);
				String infoh = Integer.toString(height);
				String infow = Integer.toString(width);
				String infod = Integer.toString(depth);
				String infoch = Integer.toString(channels);	
						
// 				ArrayList<BQImageInfo> arrayImageInfo = BQImage.getImageInfo(selectedURL);
// 				String infoz = BQImage.searchImageInfo(arrayImageInfo, "zsize");
// 				String infot = BQImage.searchImageInfo(arrayImageInfo, "tsize");
// 				String infoh = BQImage.searchImageInfo(arrayImageInfo, "height");
// 				String infow = BQImage.searchImageInfo(arrayImageInfo, "width");
// 				String infod = BQImage.searchImageInfo(arrayImageInfo, "depth");
// 				String infoch = BQImage.searchImageInfo(arrayImageInfo, "channels");
// 				int tsize = Integer.parseInt(infot);
// 				int zsize = Integer.parseInt(infoz);
// 				int height = Integer.parseInt(infoh);
// 				int width = Integer.parseInt(infow);
// 				int depth = Integer.parseInt(infod);
// 				int channels = Integer.parseInt(infoch);
				//Thread thread = Thread.currentThread();
				IJ.showStatus("Downloading ...");
				Object ImageData = image.getData();//BQImage.getImage(selectedURL);
				IJ.showStatus("Converting ...");
				if (depth ==8 && channels == 1 && zsize == 1 && tsize == 1)
				{
					ByteProcessor bp = new ByteProcessor(width, height);
					ImagePlus byteImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", bp);
					for (int h = 0; h < height; h++)
					{
						for (int w = 0; w < width; w++)
						{
							bp.putPixel(w, h, (int)((int[][])ImageData)[h][w]);
						}
					}
					byteImage.show();
				}
				else if (depth == 8 && channels == 2 && zsize == 1 && tsize == 1)
				{
					ColorProcessor cp = new ColorProcessor(width, height);
					ImagePlus colorImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", cp);
					for (int h = 0; h < height; h++)
					{
						for (int w = 0; w < width; w++)
						{
							int[] RGB = { (int)((int[][][])ImageData)[h][w][0], (int)((int[][][])ImageData)[h][w][1], 0 };
							cp.putPixel(w, h, RGB);
						}
					}
					colorImage.show();
				}
				else if (depth == 8 && channels == 3 && zsize == 1 && tsize == 1)
				{
					ColorProcessor cp = new ColorProcessor(width, height);
					ImagePlus colorImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", cp);
					for (int h = 0; h < height; h++)
					{
						for (int w = 0; w < width; w++)
						{
							int[] RGB = { (int)((int[][][])ImageData)[h][w][0], (int)((int[][][])ImageData)[h][w][1], (int)((int[][][])ImageData)[h][w][2] };
							cp.putPixel(w, h, RGB);
						}
					}
					colorImage.show();
				}
				else if (depth == 8 && channels == 1 && zsize == 1 && tsize > 1)
				{
					ImageStack stackImage = new ImageStack(width, height); 
					ByteProcessor bp = new ByteProcessor(width, height);
					for (int t = 0; t < tsize; t++){
						ByteProcessor bpt = new ByteProcessor(width, height);
						for (int h = 0; h < height; h++)
						{
							for (int w = 0; w < width; w++){
								bpt.putPixel(w, h, (int)((int[][][])ImageData)[h][w][t]);
							}
						}
						bp = bpt;
						stackImage.addSlice(selectedURL + Integer.toString(t), bp);
					}
					
					ImagePlus byteImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", stackImage);
					byteImage.show();
				}
				else if (depth == 8 && channels == 3 && zsize == 1 && tsize > 1)
				{
					ImageStack stackImage = new ImageStack(width, height);
					ColorProcessor bp = new ColorProcessor(width, height);
					for (int t = 0; t < tsize; t++)
					{
						ColorProcessor bpt = new ColorProcessor(width, height);
						for (int h = 0; h < height; h++)
						{
							for (int w = 0; w < width; w++)
							{
								int[] RGB = { (int)((int[][][][])ImageData)[h][w][0][t], (int)((int[][][][])ImageData)[h][w][1][t], (int)((int[][][][])ImageData)[h][w][2][t] };
								bpt.putPixel(w, h, RGB);
							}
						}
						bp = bpt;
						stackImage.addSlice(selectedURL + Integer.toString(t), bp);
					}

					ImagePlus byteImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", stackImage);
					byteImage.show();
				}
				else if (depth == 8 && channels == 1 && zsize > 1 && tsize == 1)
				{
					ImageStack stackImage = new ImageStack(width, height); 
					ByteProcessor bp = new ByteProcessor(width, height);
					for (int z = 0; z < zsize; z++){
						ByteProcessor bpt = new ByteProcessor(width, height);
						for (int h = 0; h < height; h++)
						{
							for (int w = 0; w < width; w++){
								bpt.putPixel(w, h, (int)((int[][][])ImageData)[h][w][z]);
							}
						}
						bp = bpt;
						stackImage.addSlice(selectedURL + Integer.toString(z), bp);
					}
					
					ImagePlus byteImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", stackImage);
					byteImage.show();
				}
				else if (depth == 8 && channels == 3 && zsize > 1 && tsize == 1)
				{
					ImageStack stackImage = new ImageStack(width, height);
					ColorProcessor bp = new ColorProcessor(width, height);
					for (int z = 0; z < zsize; z++)
					{
						ColorProcessor bpt = new ColorProcessor(width, height);
						for (int h = 0; h < height; h++)
						{
							for (int w = 0; w < width; w++)
							{
								int[] RGB = { (int)((int[][][][])ImageData)[h][w][0][z], (int)((int[][][][])ImageData)[h][w][1][z], (int)((int[][][][])ImageData)[h][w][2][z] };
								bpt.putPixel(w, h, RGB);
							}
						}
						bp = bpt;
						stackImage.addSlice(selectedURL + Integer.toString(z), bp);
					}

					ImagePlus byteImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", stackImage);
					byteImage.show();
				}
				else if (depth == 16 && channels == 1 && zsize == 1 && tsize == 1)
				{
					ShortProcessor sp = new ShortProcessor(width, height);
					ImagePlus shortImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", sp);
					for (int h = 0; h < height; h++)
					{
						for (int w = 0; w < width; w++)
						{
							sp.putPixel(w, h, (int)((int[][])ImageData)[h][w]);
						}
					}
					shortImage.show();
				}
				else if (depth == 16 && channels == 1 && zsize == 1 && tsize > 1)
				{
					ImageStack stackImage = new ImageStack(width, height);
					ShortProcessor bp = new ShortProcessor(width, height);
					for (int t = 0; t < tsize; t++)
					{
						ShortProcessor bpt = new ShortProcessor(width, height);
						for (int h = 0; h < height; h++)
						{
							for (int w = 0; w < width; w++)
							{
								bpt.putPixel(w, h, (int)((int[][][])ImageData)[h][w][t]);
							}
						}
						bp = bpt;
						stackImage.addSlice(selectedURL + Integer.toString(t), bp);
					}

					ImagePlus byteImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", stackImage);
					byteImage.show();
				}
				else if (depth == 16 && channels == 1 && zsize > 1 && tsize == 1)
				{
					ImageStack stackImage = new ImageStack(width, height);
					ShortProcessor bp = new ShortProcessor(width, height);
					for (int z = 0; z < zsize; z++)
					{
						ShortProcessor bpt = new ShortProcessor(width, height);
						for (int h = 0; h < height; h++)
						{
							for (int w = 0; w < width; w++)
							{
								bpt.putPixel(w, h, (int)((int[][][])ImageData)[h][w][z]);
							}
						}
						bp = bpt;
						stackImage.addSlice(selectedURL + Integer.toString(z), bp);
					}

					ImagePlus byteImage = new ImagePlus(selectedURL+"|"+infow+","+infoh+","+ infod+","+infoch+","+infoz+","+infot+"|", stackImage);
					byteImage.show();
				}
				else
					IJ.error("ERROR - Image paramaters (w,h,d,ch,t,z):" + infow + "," + infoh + "," + infod + "," + infoch + "," + infot + "," + infoz);

				IJ.showStatus(""); 
			}
		}
		catch (Exception e){
			IJ.showMessage(e.getMessage());
		}
	}
	//----------------------------------------------------------------------
	public void connectBisquik(){
		try
		{
			IJ.showStatus("Connecting ...");
			BQAuthorization.setAuthorization(userTF.getText(), passTF.getText());
			BQDataService ds = new BQDataService(serverTF.getText());
			//ArrayList LI = BQImage.getImagesList(serverTF.getText(), searchTF.getText());
			
			ArrayList<String> LI = new ArrayList<String>();
			ArrayList<BQObject> objects = ds.search(searchTF.getText());
			Iterator<BQObject> li = objects.iterator();
			while (li.hasNext()){
				BQObject object = li.next();
				LI.add(object.uri);
			}
			list.setListData(LI.toArray());
			IJ.showStatus("");
		}
		catch (Exception e){
			IJ.showMessage(e.getMessage());
		}
	}
	//----------------------------------------------------------------------
	public void uploadImage()
	{
		try
		{	
			if(WindowManager.getCurrentImage()!=null){
				IJ.showStatus("Converting ...");
				ImagePlus img = WindowManager.getCurrentImage();
				if (img.getBitDepth() == 8 && img.getStackSize() == 1)
				{
					ImageProcessor ip = img.getProcessor();
					byte[][] pixelArray = new byte[ip.getHeight()][ip.getWidth ( )];
					for (int h = 0; h < ip.getHeight(); h++)
					{
						for (int w = 0; w < ip.getWidth(); w++)
						{
							pixelArray[h][w] = (byte)ip.getPixel(w, h);
						}
					}
					IJ.showStatus("Uploading ...");
					BQAuthorization.setAuthorization(userTF.getText(), passTF.getText());
					BQImage image = new BQImage( ip.getHeight(), ip.getWidth(), 1, 1, 1, 8, "uint8", "imagejImage.raw", 1);
					String response = image.postData(serverTF.getText(), pixelArray);
					//String response = BQImage.postImage(serverTF.getText(), pixelArray, "uint8", ip.getHeight(), ip.getWidth(), 1, 1, 1, 1);
					if (tagsChBox.getState())
						showInBrowser(serverTF.getText() + "/bisquik/svgedit?resource=" + response, null);
					//IJ.showMessage(response);
					IJ.showStatus("");
				}
				else if (img.getBitDepth() == 8 && img.getStackSize() > 1)
				{
					IJ.showStatus("Converting ...");
					ImageStack stack = img.getStack();
					byte[][][] pixelArray = new byte[stack.getHeight()][stack.getWidth()][img.getStackSize()];
					//IJ.showMessage(Integer.toString(img.getStackSize()));
					for (int t = 0; t < img.getStackSize(); t++)
					{
						ImagePlus img2 = new ImagePlus("tmp", stack.getProcessor(t + 1).duplicate());
						ImageProcessor ip = img2.getProcessor();
						//img2.show();
						for (int h = 0; h < stack.getHeight(); h++)
						{
							for (int w = 0; w < stack.getWidth(); w++)
							{
								pixelArray[h][w][t] = (byte)ip.getPixel(w, h);
							}
						}
					}
					IJ.showStatus("Uploading ...");
					BQAuthorization.setAuthorization(userTF.getText(), passTF.getText());
					BQImage image = new BQImage( stack.getHeight(), stack.getWidth(), 1, img.getStackSize(), 1, 8, "uint8", "imagejImage.raw", 1);
					String response = image.postData(serverTF.getText(), pixelArray);
					
					//String response = BQImage.postImage(serverTF.getText(), pixelArray, "uint8", stack.getHeight(), stack.getWidth(), 1, 1, img.getStackSize(), 1);
					if (tagsChBox.getState())
						showInBrowser(serverTF.getText() + "/bisquik/svgedit?resource=" + response, null);
					//IJ.showMessage(response);
					IJ.showStatus("");
				}
				else if (img.getBitDepth() == 16 && img.getStackSize() > 1)
				{
					IJ.showStatus("Converting ...");
					ImageStack stack = img.getStack();
					short[][][] pixelArray = new short[stack.getHeight()][stack.getWidth()][img.getStackSize()];
					//IJ.showMessage(Integer.toString(img.getStackSize()));
					for (int t = 0; t < img.getStackSize(); t++)
					{
						ImagePlus img2 = new ImagePlus("tmp", (ShortProcessor)stack.getProcessor(t+1).duplicate());
						ShortProcessor ip = (ShortProcessor)img2.getProcessor();
						//img2.show();
						for (int h = 0; h < stack.getHeight(); h++)
						{
							for (int w = 0; w < stack.getWidth(); w++)
							{
								pixelArray[h][w][t] = (short)ip.getPixel(w, h);
							}
						}
					}
					IJ.showStatus("Uploading ...");
					BQAuthorization.setAuthorization(userTF.getText(), passTF.getText());
					BQImage image = new BQImage( stack.getHeight(), stack.getWidth(), 1, img.getStackSize(), 1, 16, "uint16", "imagejImage.raw", 1);
					String response = image.postData(serverTF.getText(), pixelArray);					
					//String response = BQImage.postImage(serverTF.getText(), pixelArray, "uint16", stack.getHeight(), stack.getWidth(), 1, 1, img.getStackSize(), 1);
					if (tagsChBox.getState())
						showInBrowser(serverTF.getText() + "/bisquik/svgedit?resource=" + response, null);
					IJ.showMessage(response);
					IJ.showStatus("");
				}
				else if (img.getBitDepth() == 16 && img.getStackSize() == 1)
				{
					ShortProcessor ip = (ShortProcessor)img.getProcessor();
					short[][] pixelArray = new short[ip.getHeight()][ip.getWidth ( )];
					for (int h = 0; h < ip.getHeight(); h++)
					{
						for (int w = 0; w < ip.getWidth(); w++)
						{
							short s = 
							pixelArray[h][w] = (short)ip.getPixel(w, h);
						}
					}
					IJ.showStatus("Uploading ...");
					BQAuthorization.setAuthorization(userTF.getText(), passTF.getText());
					BQImage image = new BQImage( ip.getHeight(), ip.getWidth(), 1, 1, 1, 8, "uint8", "imagejImage.raw", 1);
					String response = image.postData(serverTF.getText(), pixelArray);								
					//String response = BQImage.postImage(serverTF.getText(), pixelArray, "uint16", ip.getHeight(), ip.getWidth(), 1, 1, 1, 1);
					if (tagsChBox.getState())
						showInBrowser(serverTF.getText() + "/bisquik/svgedit?resource=" + response, null);
					//IJ.showMessage(Integer.toString(min));
					IJ.showStatus("");
				}
				else if ((img.getBitDepth() == 32 || img.getBitDepth() == 24) && img.getStackSize() > 1)
				{
					IJ.showStatus("Converting ...");
					ImageStack stack = img.getStack();
					byte[][][][] pixelArray = new byte[stack.getHeight()][stack.getWidth()][3][img.getStackSize()];
					//IJ.showMessage(Integer.toString(img.getStackSize()));
					for (int t = 0; t < img.getStackSize(); t++)
					{
						ImagePlus img2 = new ImagePlus("tmp", stack.getProcessor(t+1).duplicate());
						ColorProcessor ip = (ColorProcessor)img2.getProcessor();
						for (int h = 0; h < stack.getHeight(); h++)
						{
							for (int w = 0; w < stack.getWidth(); w++)
							{
								int[] p = new int[3];
								ip.getPixel(w, h, p);
								pixelArray[h][w][0][t] = (byte)p[0];
								pixelArray[h][w][1][t] = (byte)p[1];
								pixelArray[h][w][2][t] = (byte)p[2];
							}
						}
					}
					IJ.showStatus("Uploading ...");
					BQAuthorization.setAuthorization(userTF.getText(), passTF.getText());
					BQImage image = new BQImage( stack.getHeight(), stack.getWidth(), 1, img.getStackSize(), 3, 8, "uint8", "imagejImage.raw", 1);
					String response = image.postData(serverTF.getText(), pixelArray);								
					
					//String response = BQImage.postImage(serverTF.getText(), pixelArray, "uint8", stack.getHeight(), stack.getWidth(), 3, 1, img.getStackSize(), 1);
					if (tagsChBox.getState())
						showInBrowser(serverTF.getText() + "/bisquik/svgedit?resource=" + response, null);
					//IJ.showMessage(response);
					IJ.showStatus("");
				}
				else if ((img.getBitDepth() == 32 || img.getBitDepth() == 24) && img.getStackSize() == 1)
				{
					IJ.showStatus("Converting ...");
					ImageStack stack = img.getStack();
					byte[][][] pixelArray = new byte[stack.getHeight()][stack.getWidth()][3];
					//IJ.showMessage(Integer.toString(img.getStackSize()));
					ColorProcessor ip = (ColorProcessor)img.getProcessor();
					for (int h = 0; h < stack.getHeight(); h++)
					{
						for (int w = 0; w < stack.getWidth(); w++)
						{
							int[] p = new int[3];
							ip.getPixel(w, h, p);
							pixelArray[h][w][0] = (byte)p[0];
							pixelArray[h][w][1] = (byte)p[1];
							pixelArray[h][w][2] = (byte)p[2];
						}
					}
					IJ.showStatus("Uploading ...");
					BQAuthorization.setAuthorization(userTF.getText(), passTF.getText());
					BQImage image = new BQImage( stack.getHeight(), stack.getWidth(), 1, 1, 3, 8, "uint8", "imagejImage.raw", 1);
					String response = image.postData(serverTF.getText(), pixelArray);					
					//String response = BQImage.postImage(serverTF.getText(), pixelArray, "uint8", stack.getHeight(), stack.getWidth(), 3, 1, 1, 1);
					if (tagsChBox.getState())
						showInBrowser(serverTF.getText() + "/bisquik/svgedit?resource=" + response, null);
					//IJ.showMessage(response);
					IJ.showStatus("");
				}
				else
					IJ.error("ERROR - unsupported image type" + img.getBitDepth()); 
			}
			else
				IJ.showMessage("Select image !!!");
		}
		catch (Exception e)
		{
			IJ.showMessage(e.getMessage());
		}
	}
	//----------------------------------------------------------------------
	public void showInBrowser(String url, Frame frame)
	{
		//minimizes the app
		if (frame != null)
			frame.setExtendedState(JFrame.ICONIFIED);

		String os = System.getProperty("os.name").toLowerCase();
		Runtime rt = Runtime.getRuntime();
		try
		{
			if (os.indexOf("win") >= 0)
			{
				String[] cmd = new String[4];
				cmd[0] = "cmd.exe";
				cmd[1] = "/C";
				cmd[2] = "start";
				cmd[3] = url;
				rt.exec(cmd);
			}
			else if (os.indexOf("mac") >= 0)
			{
				rt.exec("open " + url);
			}
			else
			{
				//prioritized 'guess' of users' preference
				String[] browsers = {"epiphany", "firefox", "mozilla", "konqueror",
                  "netscape","opera","links","lynx"};

				StringBuffer cmd = new StringBuffer();
				for (int i = 0; i < browsers.length; i++)
					cmd.append((i == 0 ? "" : " || ") + browsers[i] + " \"" + url + "\" ");

				rt.exec(new String[] { "sh", "-c", cmd.toString() });
				//rt.exec("firefox http://www.google.com");
				//System.out.println(cmd.toString());

			}
		}
		catch (IOException e)
		{
			e.printStackTrace();
			JOptionPane.showMessageDialog(frame,
												"\n\n The system failed to invoke your default web browser while attempting to access: \n\n " + url + "\n\n",
												"Browser Error",
												JOptionPane.WARNING_MESSAGE);
		}
	}
	//----------------------------------------------------------------------
}/* GUI class end*/
}/* BOBisquikDB class end*/
//******************************************************************************
//******************************************************************************
class smallButton extends JButton {
	public smallButton(String buttonText, String tooltipText) {
		Font dafont = new Font(null);
		float fontsize = 11;
		dafont = dafont.deriveFont(fontsize);
		dafont = dafont.deriveFont(Font.BOLD);
		this.setFont(dafont);
		this.setText(buttonText);
		this.setToolTipText(tooltipText);
	}
}
