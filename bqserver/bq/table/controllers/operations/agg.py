#---------------------------------------------------------------------------------------
# Table Operations: Aggregation
#---------------------------------------------------------------------------------------

from pylons.controllers.util import abort

from bq.table.controllers.table_operation import TableOperation
from bq.table.controllers.table_base import TableQueryParser, ParseError


class AggOperation(TableOperation):
    name = 'agg'

    """ Perform aggregation on slices/columns
        Condition syntax:
           AGG_OP     ::=  agg_cond | agg_cond ( "," agg_cond )+ 
           agg_cond   ::=  agg_fct "(" cell_sel ")" ( "AS" <aliasname> )?
           agg_fct    ::=  "STD" | "MEAN" | "MIN" | "MAX" | ...
        Example:
           .../agg:mean(row=0:10,"field"="depth") AS avgdepth, max(row=0:10,"field"="depth") AS maxdepth/...
           .../agg:max(0:10,0:10,0:10)/...
    """
        
    def __init__(self):
        pass

    def execute(self, table, args):
        try:
            table.t_ops.append({'agg':TableQueryParser().parse_agg(args, table.get_columns())})
        except ParseError as e:
            abort(400, str(e))
        return table.read()  # TODO: try to delay the read as much as possible by combining t_ops
    
