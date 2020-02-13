// Shayne Steele  steele AT cs DOT fsu DOT edu
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.event.*;

public class Sample extends JApplet
{
    // assign default values to the font fields
    private int fontSize = 12;
    private int fontStyle = Font.BOLD;
    private String fontName = "Monospaced";

    public Sample(String args[])
    {
        // create the label and assign default values to its font
        String labelText ="";

        for (String arg:args){
            labelText += arg + "\n";
        }

        final JLabel label = new JLabel(labelText);
        label.setFont(new Font(fontName, fontStyle, fontSize));

        // add a JPanel with a GridBagLayout to the center of
        // the content pane (BorderLayout.CENTER).  Add the label to the
        // JPanel (the label will be in the center of the
        // JPanel since that is the default action of a GridBag layout)
        final JPanel labelPanel = new JPanel(new GridBagLayout());
        getContentPane().add(labelPanel, BorderLayout.CENTER);
        labelPanel.add(label);

        // set the background color of the labelPanel
        labelPanel.setBackground(Color.pink);

        // create a JToolBar to hold the controls and add to the North of
        // the content pane
        JToolBar toolBar = new JToolBar();
        getContentPane().add(toolBar, BorderLayout.NORTH);

        // create a panel for holding the font controls
        final JPanel fontPanel = new JPanel();

        // add a JComboBox for name selection
        fontPanel.add(new JLabel("font Name"));
        // for a JComboBox with an array of Objects passed to the constructor,
        // the first item in the list is the first one displayed
        final JComboBox fontNameComboBox =
            new JComboBox(new String[] { fontName, "Dialog", "DialogInput",
                                         "Serif", "SansSerif" });
        fontNameComboBox.addActionListener(new ActionListener()
            {
                public void actionPerformed(ActionEvent event)
                {
                    fontName = (String) fontNameComboBox.getSelectedItem();
                    label.setFont(new Font(fontName, fontStyle, fontSize));
                }
            });
        fontPanel.add(fontNameComboBox);

        // add a JSpinner for Size selection
        fontPanel.add(new JLabel("font Size"));
        // for SpinnerNumberModel first number is initial selection
        // second number is lower bounds, third number is upper bounds
        // fourth number is step size
        final JSpinner fontSizeSpinner =
            new JSpinner(new SpinnerNumberModel(fontSize, 0, 80, 4));
        fontSizeSpinner.addChangeListener(new ChangeListener()
            {
                public void stateChanged(ChangeEvent event)
                {
                    fontSize = ((Number) fontSizeSpinner.getValue()).intValue();
                    label.setFont(new Font(fontName, fontStyle, fontSize));
                }
            });
        fontPanel.add(fontSizeSpinner);

        // add a JComboBox for name selection
        fontPanel.add(new JLabel("font Style"));
        final JComboBox fontStyleComboBox =
            new JComboBox(new String[] { "Bold" , "Italic" , "Plain",
                                         "Bold & Italic" });
        fontStyleComboBox.addActionListener(new ActionListener()
            {
                public void actionPerformed(ActionEvent event)
                {
                    String string =
                        (String) fontStyleComboBox.getSelectedItem();
                    if ("Bold".equals(string))
                    {
                        fontStyle = Font.BOLD;
                    }
                    else if ("Italic".equals(string))
                    {
                        fontStyle = Font.ITALIC;
                    }
                    else if ("Plain".equals(string))
                    {
                        fontStyle = Font.PLAIN;
                    }
                    else
                    {
                        fontStyle = Font.BOLD | Font.ITALIC;
                    }
                    label.setFont(new Font(fontName, fontStyle, fontSize));
                }
            });
        fontPanel.add(fontStyleComboBox);

        // create a Panel for holding the color and enable/disable buttons
        final JPanel buttonPanel = new JPanel();

        // create a JButton for selecting background colors and add it
        // to the buttonPanel
        final JButton colorButton = new JButton("Choose Color");
        colorButton.addActionListener(new ActionListener()
            {
                public void actionPerformed(ActionEvent event)
                {
                    Color color =
                        JColorChooser.showDialog(labelPanel,
                                                 "Choose a background Color",
                                                 labelPanel.getBackground());
                    if (color != null)
                    {
                        labelPanel.setBackground(color);
                    }
                }
            });
        buttonPanel.add(colorButton);

        // add a disable/enable toggle button to the buttonbox
        final JButton toggleButton = new JButton("Disable");
        toggleButton.addActionListener(new ActionListener()
            {
                public void actionPerformed(ActionEvent event)
                {
                    // toggle to/from an enable/disable button
                    if ("Disable".equals(toggleButton.getText()))
                    {
                        colorButton.setEnabled(false);
                        enableChildren(fontPanel, false);
                        toggleButton.setText("Enable");
                    }
                    else
                    {
                        colorButton.setEnabled(true);
                        enableChildren(fontPanel, true);
                        toggleButton.setText("Disable");
                    }
                }
            });
        buttonPanel.add(toggleButton);

        // set the toolBar layout to a vertical box layout,
        // added to it the fontPanel and buttonPanel
        toolBar.setLayout(new BoxLayout(toolBar, BoxLayout.Y_AXIS));
        toolBar.add(fontPanel);
        toolBar.add(buttonPanel);
    }

    // enable (or disable) all children of a component
    private void enableChildren(Container container, boolean isEnabled)
    {
        // get an arry of all the components in this container
        Component[] components = container.getComponents();
        // for each element in the container enable/disable it
        for (int i = 0; i < components.length; i++)
        {
            components[i].setEnabled(isEnabled);
        }
    }

    public static void main(String[] args)
    {
        // create the frame with a title
        JFrame frame = new JFrame("Font and Background Color Selection");
        // exit the application when the JFrame is closed
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        // add the applet to the frame
        frame.getContentPane().add(new Sample(args));
        // set the size of the frame (applet will be width by height in size)
        int height = 300;
        int width = 450;
        // pack the frame to get correct insets
        frame.pack();
        Insets fI = frame.getInsets();
        frame.setSize(width + fI.right + fI.left, height + fI.top + fI.bottom);
        // center the frame on screen
        Dimension sD = Toolkit.getDefaultToolkit().getScreenSize();
        frame.setLocation((sD.width - width)/2, (sD.height - height)/2);
        // make the frame visible
        frame.setVisible(true);
    }
}
