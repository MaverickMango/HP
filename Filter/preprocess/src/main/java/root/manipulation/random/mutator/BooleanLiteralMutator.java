package root.manipulation.random.mutator;

import com.github.javaparser.ast.expr.BooleanLiteralExpr;
import com.github.javaparser.ast.expr.LiteralExpr;
import root.generation.transformation.AbstractLiteralMutator;

import java.util.Random;

public class BooleanLiteralMutator extends AbstractLiteralMutator {

    private final Random random = new Random();

    @Override
    public BooleanLiteralExpr mutate(LiteralExpr oldValue) {
        //now is random, but not always!
        BooleanLiteralExpr expr = new BooleanLiteralExpr();
        expr.setValue(random.nextBoolean());
        return expr;
    }
}
