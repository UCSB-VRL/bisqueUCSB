# -*- mode: python -*-
"""Main server for graph}
"""
import os
import logging
import pkg_resources
from lxml import etree
from collections import namedtuple

from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import expose, flash, request
from repoze.what import predicates
from bq.core.service import ServiceController

from bq import data_service
from bq.util.hash import is_uniq_code


log = logging.getLogger("bq.graph")

SummaryNodeBase = namedtuple("SummaryNode", ["type", "node_ids", "value"])
class SummaryNode(SummaryNodeBase):
    def __hash__(self):
        return hash(self.value)


def _find_new_node_id(new_nodes, node_id):
    for new_node in new_nodes:
        if not isinstance(new_node, SummaryNode) and node_id == new_node[0]:
            return new_node[0]
        elif isinstance(new_node, SummaryNode) and node_id in new_node.node_ids:
            return new_node.value
    return None

def _summarize_nodes(query_node, nodes, edges, members, summ_by_types=False):
    """
    Partition nodes by input/output edges and summarize them.
    query_node always remains individual node.
    Returns: (nodes, edges, members)
    """
    new_nodes = set()
    new_edges = set()
    new_members = set()    
    # map (sorted input IDs, sorted output IDs) -> set of nodes
    partitions = {}
    neighbors_of_query = [n1 for (n1,n2) in edges if n2==query_node[0]] + [n2 for (n1,n2) in edges if n1==query_node[0]]
    for node in nodes:
        if node[0] != query_node[0]:
            inputs = [n1 for (n1,n2) in edges if n2==node[0]]
            outputs = [n2 for (n1,n2) in edges if n1==node[0]]
            if summ_by_types:
                inputs = [ntype for (nid,ntype) in nodes if nid in inputs]
                outputs = [ntype for (nid,ntype) in nodes if nid in outputs]
                if not node[1].startswith('mex'):
                    # if node is not a mex, only unique types of inputs/outputs matter
                    # for mex, we have to distinguish input [table,table] from input [table] (different signature!)
                    inputs = set(inputs)
                    outputs = set(outputs)
            # partition by node type, inputs, outputs (but do not group direct neighbors of query node) 
            node_id = node[0] if query_node[1].startswith('mex') and node[0] in neighbors_of_query else -1
            key = (node[1], node_id, tuple(sorted(inputs)), tuple(sorted(outputs)))
            try:
                partition = partitions[key]
            except KeyError:
                partition = []
                partitions[key] = partition
            finally:
                partition.append(node)
    # go through partitions... create summary nodes and correct edges
    new_nodes.add(query_node) 
    summarize_id = 1
    for key in partitions:
        # create summary node
        if len(partitions[key]) > 1:
            sum_node = SummaryNode(type='multi %s' % key[0], node_ids=[node[0] for node in partitions[key]], value='%s/%s' % (query_node[0], summarize_id))
            summarize_id += 1
        else:
            # singleton => keep node itself
            sum_node = partitions[key][0]
        new_nodes.add(sum_node)    
    for (n1,n2) in edges:
        # add edges from/to summary nodes
        new_n1 = _find_new_node_id(new_nodes, n1)
        new_n2 = _find_new_node_id(new_nodes, n2)
        new_edges.add((new_n1, new_n2))
    return (new_nodes, new_edges, new_members)

def _add_resource_inputs_outputs(xnode, edges, checked, unchecked):
    """
    For the given xnode, find all other nodes that are connected to it by direct edges.
    For MEX type, input is all links in "inputs" section, output is all links in "outputs" section.
    For other types, input is all MEXs with it in "outputs" section, output is all MEXs with it in "inputs" section.
    
    Inputs: any ref in top "inputs" section without self-references
    Outputs: any ref in top "outputs" section without self-references or input references
    """
    node = xnode.get ('resource_uniq')
    if xnode.tag == 'mex':
        points_from_list = [ x.rsplit('/',1)[1] for x in xnode.xpath('./tag[@name="inputs"]/tag/@value') if x.startswith("http") ]
        points_to_list = [ x.rsplit('/',1)[1] for x in xnode.xpath('./tag[@name="outputs"]/tag/@value') if x.startswith("http") ]
    else:
        points_from_list = []
        points_to_list = []
        # TODO: the following will be very slow on large DBs... change to new query in 0.6!
        mexes_ref_node = data_service.query ('mex', tag_query='"http*/%s"' % node, cache=False)
        for mex_ref_node in mexes_ref_node:
            mex_deep = data_service.resource_load (uniq=mex_ref_node.get('resource_uniq'),view='full')
            if mex_deep:
                found_in_inputs = False
                inputs_tag = mex_deep.xpath('./tag[@name="inputs"]')
                if inputs_tag:
                    input_id = inputs_tag[0].get('uri')
                    input_deep = data_service.get_resource(resource=input_id, view='full,clean')
                    if input_deep and len(input_deep.xpath('./tag[@value="%s"]' % xnode.get("uri"))) > 0:
                        # found node in MEX's inputs
                        points_to_list.append(mex_ref_node.get('resource_uniq'))
                        found_in_inputs = True
                if not found_in_inputs:
                    outputs_tag = mex_deep.xpath('./tag[@name="outputs"]')
                    if outputs_tag:
                        output_id = outputs_tag[0].get('uri')
                        output_deep = data_service.get_resource(resource=output_id, view='full,clean')
                        if output_deep and len(output_deep.xpath('./tag[@value="%s"]' % xnode.get("uri"))) > 0:
                            # found node in MEX's outputs
                            points_from_list.append(mex_ref_node.get('resource_uniq'))
                
    # add edge unless it points to mex recursively
    points_from_list = [ x for x in points_from_list if is_uniq_code(x) and x != node ]
    # add edge unless it points to mex recursively or back to an input 
    points_to_list = [ x for x in points_to_list if is_uniq_code(x) and x != node and x not in points_from_list ]
    
    log.debug ("points_to_list %s", points_to_list)
    log.debug ("points_from_list %s", points_from_list)
    
    for xlink in points_from_list:        
        if (xlink, node) not in edges:
            log.debug ("ADDING IN EDGE : %s" % str( (xlink, node) ))
            edges.add( (xlink, node) )
        if xlink not in checked:
            unchecked.add (xlink)
        
    for xlink in points_to_list:
        if (node, xlink) not in edges:
            log.debug ("ADDING OUT EDGE : %s" % str( (node, xlink) ))
            edges.add( (node, xlink) )
        if xlink not in checked:
            unchecked.add (xlink)

class graphController(ServiceController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = predicates.not_anonymous()
    service_type = "graph"

    def __init__(self, server_url):
        super(graphController, self).__init__(server_url)

    @expose(content_type="text/xml")
    def index(self, **kw):
        # nothing to do for now => return empty resource
        resource = etree.Element('resource')
        return etree.tostring(resource)

    @expose(content_type="text/xml")
    def _default(self, *path, **kw):
        path = list(path)

        res_uniq = path[0]
        query = path[0]
        # if path is of format "<resource_uniq>/<multi_node_id>", return the contents of the multi node as a "virtual" dataset
        if len(path) > 1 and path[1].isdigit():            
            multi_node_id = "%s/%s" % (path[0], path[1])
            res_uniq = "%s-%s" % (path[0], path[1])
        else:
            multi_node_id = None
        extra = path[-1] if len(path)>1 and not path[-1].isdigit() else None   # could be 'auth', 'value', or 'tag'

        view = kw.pop('view', 'short')
        offset = kw.pop('offset', 0)
        limit = kw.pop('limit', 1000)
        tag_query = kw.pop('tag_query', None)
        tag_order = kw.pop('tag_order', None)
        extract = kw.pop('extract', None)        
        request_url = request.url
        
        if extra == 'auth' or extra == 'tag':
            # no sharing etc and no tags
            response = etree.Element('resource', uri=request_url)
            return etree.tostring (response)            

        big_types=('table', 'image', 'file')   # types with many instances (treat as identical for collapsing)
        nodes = set()
        edges = set()
        resources = set()
        datasets = {}   # dataset uniq -> [ member id, member id, ... ]
        checked = set()
        unchecked = set()
        unchecked.add (query)        
        query_node = None
        while unchecked:
            log.debug ( "graph unchecked %s", unchecked)
            node = unchecked.pop()
                        
            # Find everybody this node references:
            xnode = data_service.resource_load (uniq=node,view='short')
            if xnode is None:
                log.error ('could not load %s', node)
                edges = set([(n1,n2) for (n1,n2) in edges if n1 != node and n2 != node])  # remove edges from/to node
                continue
            node_type = xnode.tag
            if node_type == 'resource':
                node_type = xnode.get ('resource_type') or xnode.tag
            if node_type.startswith('mex') or node_type.startswith('dataset'):
                xnode = data_service.resource_load (uniq=node,view='deep')   # TODO: this is too expensive... replace with 0.6 query!
            if node_type not in big_types:
                node_type = "%s(%s)" % (node_type, xnode.get('name', 'unknown')) 

            nodes.add( (node, node_type) )
            if node == query:
                query_node = (node, node_type)
            checked.add (node)
            
            # find all inputs/outputs to this node and update edges and unchecked
            _add_resource_inputs_outputs(xnode, edges, checked, unchecked)
            
            # add dataset reference information
            if node_type.startswith('mex'):
                # treat Mex's submex outputs as a dataset
                datasets[node] = [ x.rsplit('/',1)[1] for x in xnode.xpath('./mex/tag[@name="outputs"]/tag/@value') if x.startswith('http') ]
            else:
                if node_type.startswith('dataset'):
                    datasets[node] = [ x.rsplit('/',1)[1] for x in xnode.xpath("./value/text()") ]
                else:
                    resources.add(node)
                    
        log.debug ( "pre-summary Nodes : %s, Edges : %s" % (nodes, edges) )

        # check if any resource is member of a dataset => add membership link
        members = set()
        for node in resources:
            for dataset in datasets:
                if node in datasets[dataset]:
                    members.add( (node, dataset) )

        # summarize graph
        (nodes, edges, members) = _summarize_nodes(query_node, nodes, edges, members, summ_by_types=True)

        log.debug ( "post-summary Nodes : %s, Edges : %s" % (nodes, edges) )

        if multi_node_id:
            # caller wants specific multi node back as dataset            
            response = etree.Element('dataset', uri=request_url, resource_uniq=res_uniq) # data_service.uri() + ('vd-%s' % multi_node_id))
            if view != 'short' or extra == 'value':
                if extra == 'value':
                    # ask data_service to expand all elements
                    for node in nodes:
                        if isinstance(node, SummaryNode) and node.value == multi_node_id:
                            response = data_service.query( cache=False, resource_uniq='|'.join(node.node_ids), view=view, offset=offset, limit=limit, tag_query=tag_query, tag_order=tag_order, extract=extract )
                            response.set('uri', request_url)
                            break
                else:
                    for node in nodes:
                        if isinstance(node, SummaryNode) and node.value == multi_node_id:
                            response.set('name', node.type)
                            idx = 0
                            for node_id in node.node_ids:
                                el = etree.SubElement (response, 'value', type='object', index=str(idx))
                                el.text = data_service.uri() + node_id
                                idx += 1
        else:
            response = etree.Element('graph', value=query)
            if view == 'count':
                for node in nodes:
                    if isinstance(node, SummaryNode):
                        response = etree.Element ('resource')
                        etree.SubElement(response, 'resource', count = str(len(node.node_ids)))
                        break
            elif view != 'short':
                for node in nodes:
                    if isinstance(node, SummaryNode):
                        etree.SubElement (response, 'node', value=str(node.value), type=node.type, count=str(len(node.node_ids))) 
                    else:
                        etree.SubElement (response, 'node', value = node[0], type=node[1])
                node_uniqs = [ n[0] if not isinstance(n, SummaryNode) else n.value for n in nodes ]
                for edge in edges:
                    if edge[0] in node_uniqs  and edge[1] in node_uniqs:
                        etree.SubElement (response, 'edge', value = "%s:%s" % edge)
                    else:
                        log.error ("Skipping edge %s due to missing nodes", edge)
                for edge in members:
                    if edge[0] in node_uniqs  and edge[1] in node_uniqs:
                        etree.SubElement (response, 'member', value = "%s:%s" % edge)
                    else:
                        log.error ("Skipping edge %s due to missing nodes", edge)
        return etree.tostring (response)

def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize " + uri)
    service =  graphController(uri)
    #directory.register_service ('graph', service)

    return service

def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqserver")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'graph', 'public'))]

def get_model():
    from bq.graph import model
    return model

__controller__ =  graphController
