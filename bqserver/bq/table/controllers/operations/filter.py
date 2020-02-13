#---------------------------------------------------------------------------------------
# Table Operations: Filter
#---------------------------------------------------------------------------------------

from pylons.controllers.util import abort

from bq.table.controllers.table_operation import TableOperation
from bq.table.controllers.table_base import TableQueryParser, ParseError


class FilterOperation(TableOperation):
    name = 'filter'

    """ Filter table with some condition
        Condition syntax:
          QUERY       ::=  ( "[" cell_sel "]" ( "," "[" cell_sel "]" )* )? ( "{" FILTER_COND "}" )?
          FILTER_COND ::=  or_cond  |  "(" or_cond ")"
          or_cond     ::=  and_cond  ( "or" and_cond )*
          and_cond    ::=  comp_cond  ( "and" comp_cond )*
          comp_cond   ::=  "[" cell_sel "]"  ("="|"!="|"<"|">"|"<="|">=")  <value>
          cell_sel    ::=  ( [ <dimname> "=" ] [ <colname> ] [ ":"|";" ] [ <colname> ]  ","  )+
        Example:
          .../:,"Ocean_flag"{["field"="temperature"] >= 0 and ["field"="temperature"] <= 100}/... 
          .../[:,"Ocean_flag"],[:,"Depth"]{["field"="temperature"] >= 0 and ["field"="temperature"] <= 100}/... 
          .../{["x"=0:10, "y"=0:10, "c"="infrared", "field"="r"] > 0.5}/...        (x/y/z/c/t will be set for cells with "r > 0.5")  
          .../{[0:10,0:10,50,:,"abc"] > 0.5}/...                                   (no field=> cell has to be numeric, not compound)
    """

    def __init__(self):
        pass

    def execute(self, table, args):
        try:
            table.t_ops.append({'filter':TableQueryParser().parse_filter(args, table.get_columns())})
        except ParseError as e:
            abort(400, str(e))
        return table.read()  # TODO: try to delay the read as much as possible by combining t_ops
