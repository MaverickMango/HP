package root.visitor;

import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import root.entities.PathFlow;

public class ConstantVisitor extends VoidVisitorAdapter<PathFlow> {

    @Override
    public void visit(BooleanLiteralExpr n, PathFlow arg) {
        arg.addConstans(n.getValue());
    }

    @Override
    public void visit(CharLiteralExpr n, PathFlow arg) {
        arg.addConstans(n.getValue());
    }

    @Override
    public void visit(DoubleLiteralExpr n, PathFlow arg) {
        arg.addConstans(n.getValue());
    }

    @Override
    public void visit(IntegerLiteralExpr n, PathFlow arg) {
        arg.addConstans(n.getValue());
    }

    @Override
    public void visit(LongLiteralExpr n, PathFlow arg) {
        arg.addConstans(n.getValue());
    }

    @Override
    public void visit(NullLiteralExpr n, PathFlow arg) {
        arg.addConstans(n.toString());
    }

    @Override
    public void visit(StringLiteralExpr n, PathFlow arg) {
        arg.addConstans(n.getValue());
    }
}
