% gobjects2points - Scans input gobjects, finds point and retrieves 
%   vertices it will also get a tag value for probability
% 
%   INPUT:
%       filename - string of file name to write
%       myprob   - optional: name of probability tag, 
%                  default value: 'probability'
%
%   OUTPUT:
%       m        - nuclear positions, is a matrix of form:
%                   m(:,1) -> Y coordinate (starting at 1)
%                   m(:,2) -> X coordinate (starting at 1)
%                   m(:,3) -> Z coordinate (starting at 1)
%                   m(:,4) -> point IDs
%                   m(:,5) -> confidence [0:1]
%
%   AUTHOR:
%       Dmitry Fedorov, www.dimin.net
%
%   VERSION:
%       0.1 - 2011-03-29 First implementation 
%
% here i'm parsing something in the form:
%     <gobject type="Nuclear centroid" name="Nuclear centroid">
%         <gobject type="point">
%             <tag value="#da5700" name="color"/>
%             <vertex x="292.25" y="264.75" z="2" p="2"/>
%             <tag value="0" name="shape"/>
%             <tag value="1" name="line_width"/>
%         </gobject>
%     </gobject>
% the xpath based code will though work with points at any position
% and the probability tag MUST be within the point gobject

function m = gobjects2points ( filename, myprob )
    prob_name = 'probability';
    if nargin>1, prob_name=myprob; end    

    
    import javax.xml.xpath.*
    factory = XPathFactory.newInstance;
    xpath = factory.newXPath;
    
    doc = xmlread(filename);    
    
    % compile and evaluate the XPath Expression
    expression = xpath.compile('//gobject[@type=''point'']|//point');
    points = expression.evaluate(doc, XPathConstants.NODESET);
    
    expr_vrtx = xpath.compile('vertex');    
    expr_prob = xpath.compile(['tag[@name=''' prob_name ''']']);   
    
    m = zeros(points.getLength, 5);    
    for i = 0:points.getLength-1,
        g = points.item(i);
        
        vertex = expr_vrtx.evaluate(g, XPathConstants.NODE);
        tag_prob = expr_prob.evaluate(g, XPathConstants.NODE);
        
        x = str2double(vertex.getAttribute('x'));
        y = str2double(vertex.getAttribute('y'));
        z = str2double(vertex.getAttribute('z'));        
        
        probability=100;
        if ~isempty(tag_prob),
            probability = str2double(tag_prob.getAttribute('value')); 
        end
        
        m(i+1,:) = [y+1, x+1, z+1, i+1, probability/100.0];
    end    
    
    
%     % method using BOMatlab stuff, not the best...
%     
%     % use XPath instead of this stuff
%     javaaddpath('./bisque.jar'); 
%     import bisque.*
%     BQ = bisque.BQMatlab;
% 
%     %gobs = bisque.BQDataService.loadFile(filename);
%     gobs = BQ.loadObjectFromXMLFile(filename);
% 
%     gobjects = gobs.gobjects;
%   
%     m = zeros(gobjects.size(), 4);
%     for i = 0:gobjects.size()-1,
%         g = gobjects.get(i);
% 
%         point = g.gobjects.get(0);
%         x = point.vertices.get(0).y.doubleValue + 1;
%         y = point.vertices.get(0).x.doubleValue + 1;
%         z = point.vertices.get(0).z.doubleValue + 1;       
% 
%         prob = 100;
%         for j = 0:point.tags.size()-1
%             t = point.tags.get(j);
%             if strcmp(t.name, prob_name),
%               prob = str2double(t.values.get(0).value);
%               break;
%             end
%         end        
% 
%         % why, oh why are these objects reversed????????????
%         m(gobjects.size()-i,:) = [x, y, z, gobjects.size()-i, prob];
%     end 

end 
