package root.manipulation.random.mutator;

import com.github.javaparser.ast.expr.LiteralExpr;
import com.github.javaparser.ast.expr.LongLiteralExpr;
import root.generation.transformation.AbstractLiteralMutator;

import java.util.Random;

public class LongLiteralMutator extends AbstractLiteralMutator {

    private final Random random = new Random();

    @Override
    public LongLiteralExpr mutate(LiteralExpr oldValue) {
        LongLiteralExpr expr = new LongLiteralExpr();
        expr.setLong(random.nextLong());
        return expr;
    }

}
