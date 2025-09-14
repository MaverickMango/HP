package root.manipulation.random.mutator;

import com.github.javaparser.ast.expr.IntegerLiteralExpr;
import com.github.javaparser.ast.expr.LiteralExpr;
import root.generation.transformation.AbstractLiteralMutator;

import java.util.Random;

public class IntegerLiteralMutator extends AbstractLiteralMutator {

    private final Random random = new Random();

    @Override
    public IntegerLiteralExpr mutate(LiteralExpr oldValue) {
        int old = Integer.parseInt(oldValue.toString());
        IntegerLiteralExpr expr = new IntegerLiteralExpr();
        int newOne = old - 1 + random.nextInt(old) + 2;
        expr.setInt(newOne);
        return expr;
    }

}
