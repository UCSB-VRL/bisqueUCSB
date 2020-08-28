

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, ForeignKeyConstraint, create_engine
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Session, relationship, backref



Base = declarative_base()

class TreeNode (Base):
    __tablename__ = 'node'
    id = Column (Integer, primary_key=True)
    parent_id = Column (Integer, ForeignKey ( id , ondelete='cascade'))
    root_id   = Column (Integer, ForeignKey ( id , ondelete='cascade'))
    node_index  = Column(Integer)
    info = Column (String (50))

    #parent = relationship ('TreeNode', remote_side = [ id ])
    children = relationship ("TreeNode", lazy=True, passive_deletes=True,
                             cascade = "all, delete-orphan",
                             order_by ="TreeNode.node_index",
                             primaryjoin = "TreeNode.id == TreeNode.parent_id ",
                             collection_class = ordering_list ('node_index'),
                             backref = backref ('parent', remote_side =  id ),
                             )
    allnodes = relationship('TreeNode', lazy=True, passive_deletes=True,
                            cascade = "all, delete-orphan",
                            primaryjoin = "TreeNode.id == TreeNode.root_id ",
                            backref = backref ('root',   remote_side = id),
                            post_update = True,
                            )

    def __init__(self, **kw):
        super (TreeNode, self).__init__(**kw)
        if 'root' not in kw:
            self.root  = self




if __name__ == '__main__':
    engine = create_engine('sqlite://', echo=True)
    #engine = create_engine ('postgresql://localhost:5432/testing', echo=True)
    Base.metadata.create_all(engine)
    session = Session(engine)


    root = TreeNode(info = 'root')

    print

    for k in range (4):
        kid = TreeNode(info = "kid %s" % k)
        kid.children.append (TreeNode (info="sub", root=root))
        root.children.append (kid)


    session.add (root)
    session.commit()

    del root.children[3]
    session.commit ()
