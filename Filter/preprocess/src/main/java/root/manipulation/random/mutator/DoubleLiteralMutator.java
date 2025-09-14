package root.manipulation.random.mutator;

import com.github.javaparser.ast.expr.DoubleLiteralExpr;
import com.github.javaparser.ast.expr.LiteralExpr;
import root.generation.transformation.AbstractLiteralMutator;

import java.util.Random;

public class DoubleLiteralMutator extends AbstractLiteralMutator {

    private final Random random = new Random();

    @Override
    public DoubleLiteralExpr mutate(LiteralExpr oldValue) {
        DoubleLiteralExpr expr = new DoubleLiteralExpr();
        expr.setDouble(random.nextDouble());
        return expr;
    }
}
