%  bq.xml2str - converts XML document into string
%
%   INPUT:
%     doc - Document Object Model node or DOM node
%
%   OUTPUT:
%     str - string
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       1 - 2011-03-29 First implementation 
%

function str = xml2str(doc)
    % if the doc is actually a DOM doc
    if isa(doc, 'org.apache.xerces.dom.DocumentImpl') || ...
       isa(doc, 'org.apache.xerces.dom.DeferredDocumentImpl'),
        str = xmlwrite(doc);
    else % if the doc is actually a node
        %% create a new doc from subtree
        import javax.xml.parsers.*;
        factory = DocumentBuilderFactory.newInstance;
        builder = factory.newDocumentBuilder;
        newdoc = builder.newDocument;
        newdoc.appendChild(newdoc.adoptNode(doc.cloneNode(true)));

        %% create a string from DOM doc
        import javax.xml.transform.*;
        import javax.xml.transform.dom.*;
        import javax.xml.transform.stream.*;  
        tfactory = TransformerFactory.newInstance;
        transformer = tfactory.newTransformer;
        transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, 'yes');
        transformer.setOutputProperty(OutputKeys.INDENT, 'no');            
        stream = java.io.StringWriter;
        transformer.transform(DOMSource(newdoc), StreamResult(stream));
        str = char(stream.toString);        
    end
end 
