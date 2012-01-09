#     Copyright 2012, Kay Hayen, mailto:kayhayen@gmx.de
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     If you submit patches or make the software available to licensors of
#     this software in either form, you automatically them grant them a
#     license for your part of the code under "Apache License 2.0" unless you
#     choose to remove this notice.
#
#     Kay Hayen uses the right to license his code under only GPL version 3,
#     to discourage a fork of Nuitka before it is "finished". He will later
#     make a new "Nuitka" release fully under "Apache License 2.0".
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, version 3 of the License.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#     Please leave the whole of this copyright notice intact.
#

from nuitka.transform import TreeOperations

# TODO: Find a place for this. Potentially as an attribute of nodes themselves.
def _couldBeNone( node ):
    if node is None:
        return True
    elif node.isExpressionMakeDict():
        return False
    elif node.isExpressionBuiltinGlobals() or node.isExpressionBuiltinLocals() or \
           node.isExpressionBuiltinDir() or node.isExpressionBuiltinVars():
        return False
    else:
        # assert False, node
        return True


class OverflowCheckVisitor( TreeOperations.VisitorNoopMixin ):
    def __init__( self, checked_node ):
        self.result = False

        self.is_class = checked_node.getParent().isExpressionClassBody()

    def onEnterNode( self, node ):
        def declareOverflow():
            self.result = True
            raise TreeOperations.ExitVisit

        if node.isStatementImportStar():
            declareOverflow()

        if node.isStatementExec() and _couldBeNone( node.getGlobals() ):
            declareOverflow()

        if node.isExpressionBuiltinExecfile():
            declareOverflow()

        if node.isStatementExecInline():
            declareOverflow()

        if self.is_class and node.isExpressionBuiltinLocals():
            declareOverflow()

    def getResult( self ):
        return self.result


def check( node ):
    visitor = OverflowCheckVisitor( node )

    TreeOperations.visitScope( node, visitor )

    return visitor.getResult()
