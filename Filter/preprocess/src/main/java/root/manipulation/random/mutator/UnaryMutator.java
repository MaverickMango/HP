package root.manipulation.random.mutator;

import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.LiteralExpr;
import com.github.javaparser.ast.expr.UnaryExpr;
import root.generation.transformation.AbstractLiteralMutator;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class UnaryMutator extends AbstractLiteralMutator {
    private final Random random = new Random();
    List<UnaryExpr.Operator> cans;

    public UnaryMutator() {
        cans = new ArrayList<>();
        cans.add(UnaryExpr.Operator.PLUS);
        cans.add(UnaryExpr.Operator.MINUS);
    }

    private Object randomMutate(UnaryExpr oldValue) {
        UnaryExpr newValue = oldValue.clone();
        Expression expression = newValue.getExpression();
//        String type = Helper.getType(expression);//todo type must be resolved under a compilationUnit, now the oldValue is an orphan.
//        Expression nextInput = (Expression) MutatorHelper.getKnownMutator(type).getNextInput(expression);
//        newValue.setExpression(nextInput);
        UnaryExpr.Operator operator = newValue.getOperator();
        if (cans.contains(operator)) {
            operator = cans.get(0) == newValue.getOperator() ? cans.get(1) : cans.get(0);
            newValue.setOperator(operator);
        }
        return newValue;
    }

    @Override
    public <T extends LiteralExpr> T mutate(T oldValue) {
        return null;
    }
}
