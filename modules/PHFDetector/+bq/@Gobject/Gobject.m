% bq.Gobject
% A class wrapping a Bisque gobject resource giving ability to access
% vertices
%   Constructor:
%       Gobject(doc, element, user, password)
%         doc      - URL string or DOM document
%         element  - optional: DOM element
%         user     - optional: string
%         password - optional: string
%   
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-06-27 First implementation
%

classdef Gobject < bq.Node
    
    methods

        % doc      - URL string or DOM document
        % element  - optional: DOM element
        % user     - optional: string
        % password - optional: string
        function [self] = Gobject(doc, element, user, password)
            supargs = {};
            if exist('doc', 'var'), supargs{1} = doc; end
            if exist('element', 'var'), supargs{2} = element; end            
            if exist('user', 'var'), supargs{3} = user; end 
            if exist('password', 'var'), supargs{4} = password; end             
            self = self@bq.Node(supargs{:});            
        end % constructor
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Vertex access - matrix: x y z t c index
        % if the vertex does not have specific value it's set to NaN
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        function v = getVertices(self)
            v = [];
            % find all <vertex> sub nodes            
            import javax.xml.xpath.*;
            factory = XPathFactory.newInstance;
            xpath = factory.newXPath;    
            xnodes = xpath.evaluate('vertex', self.element, XPathConstants.NODESET);
            if ~isempty(xnodes) && xnodes.getLength()>0,
                v = zeros(xnodes.getLength(), 6);
                for i=1:xnodes.getLength(),
                    n = xnodes.item(i-1);
                    v(i,1) = getVertexAttr(n, 'y');
                    v(i,2) = getVertexAttr(n, 'x');
                    v(i,3) = getVertexAttr(n, 'z');
                    v(i,4) = getVertexAttr(n, 't');
                    v(i,5) = getVertexAttr(n, 'c');
                    v(i,6) = getVertexAttr(n, 'index');
                end            
            end            
        end % getVertices   
        
        function v = setVertices(self, v)
            % find all <vertex> sub nodes            
            import javax.xml.xpath.*;
            factory = XPathFactory.newInstance;
            xpath = factory.newXPath;    
            xnodes = xpath.evaluate('vertex', self.element, XPathConstants.NODESET);
            % first get rid of all vertex nodes present
            if ~isempty(xnodes) && xnodes.getLength()>0,
                for i=1:xnodes.getLength(),
                    n = xnodes.item(i-1);
                    n.getParentNode().removeChild(n);     
                end            
            end            
          
            % set the new vertex nodes
            for i=1:size(v,1),
                n = self.doc.createElement('vertex');                
                if ~isempty(v(i,:)), setVertexAttr(n, 'y', v(i,1)); end                    
                if length(v(i,:))>1, setVertexAttr(n, 'x', v(i,2)); end
                if length(v(i,:))>2, setVertexAttr(n, 'z', v(i,3)); end
                if length(v(i,:))>3, setVertexAttr(n, 't', v(i,4)); end
                if length(v(i,:))>4, setVertexAttr(n, 'c', v(i,5)); end
                if length(v(i,:))>5, setVertexAttr(n, 'index', v(i,6)); end
                self.element.appendChild(n);
            end            
        end % setVertices   

    end % methods
  
end% classdef


function v = getVertexAttr(node, attr)
    if node.hasAttribute(attr),
        v = str2num(char(node.getAttribute(attr)))+1;
    else
        v = NaN;                        
    end
end

function setVertexAttr(node, attr, v)
    if isnan(v),
        return;
    end
    node.setAttribute(attr, num2str(v-1));
end

