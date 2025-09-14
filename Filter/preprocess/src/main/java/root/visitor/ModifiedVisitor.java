package root.visitor;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.visitor.Visitable;

import java.util.List;
import java.util.Optional;

/**
 * 对应DependencyVisitor的右侧子节点
 * todo 判断父节点是否包含inputExpr
 */
public class ModifiedVisitor extends ModifierVisitor<List<Expression>> {

    private Expression inputExpr;
    private Expression basicExpr;
    private Expression transformed;

    public ModifiedVisitor(Expression inputExpr, Expression basicExpr, Expression transformed) {
        this.inputExpr = inputExpr;
        this.basicExpr = basicExpr;
        this.transformed = transformed;
    }

    @Override
    public Visitable visit(ArrayAccessExpr n, List<Expression> arg) {
        Expression value = n.getIndex();
        if (value.isUnaryExpr()) {
            Expression expression = value.asUnaryExpr().getExpression();
            if (expression.getRange().equals(basicExpr.getRange()) &&
                    expression.getClass().equals(basicExpr.getClass()) && expression.toString().equals(basicExpr.toString())) {
                value.asUnaryExpr().setExpression(transformed);
            }
        }
        if (value.getRange().equals(basicExpr.getRange()) &&
                value.getClass().equals(basicExpr.getClass()) && value.toString().equals(basicExpr.toString())) {
            n.setIndex(transformed);
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(ArrayInitializerExpr n, List<Expression> arg) {
        NodeList<Expression> values = n.getValues();
        for (Expression value :values) {
            if (value.isUnaryExpr()) {
                Expression expression = value.asUnaryExpr().getExpression();
                if (expression.getRange().equals(basicExpr.getRange()) &&
                        expression.getClass().equals(basicExpr.getClass()) && expression.toString().equals(basicExpr.toString())) {
                    value.asUnaryExpr().setExpression(transformed);
                }
            }
            if (value.getRange().equals(basicExpr.getRange()) &&
                    value.getClass().equals(basicExpr.getClass()) && value.toString().equals(basicExpr.toString())) {
                values.replace(value, transformed);
            }
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(VariableDeclarator n, List<Expression> arg) {
        Optional<Expression> initializer = n.getInitializer();
        initializer.ifPresent(value -> {
            if (value.isUnaryExpr()) {
                Expression expression = value.asUnaryExpr().getExpression();
                if (expression.getRange().equals(basicExpr.getRange()) &&
                        expression.getClass().equals(basicExpr.getClass()) && expression.toString().equals(basicExpr.toString())) {
                    value.asUnaryExpr().setExpression(transformed);
                }
            }
            if (value.getRange().equals(basicExpr.getRange()) &&
                    value.getClass().equals(basicExpr.getClass()) && value.toString().equals(basicExpr.toString())) {
                n.replace(value, transformed);
            }
        });
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(MethodCallExpr n, List<Expression> arg) {
        NodeList<Expression> arguments = n.getArguments();
        for (Expression value :arguments) {
            if (value.isUnaryExpr()) {
                Expression expression = value.asUnaryExpr().getExpression();
                if (expression.getRange().equals(basicExpr.getRange()) &&
                        expression.getClass().equals(basicExpr.getClass()) && expression.toString().equals(basicExpr.toString())) {
                    value.asUnaryExpr().setExpression(transformed);
                }
            }
            if (value.getRange().equals(basicExpr.getRange()) &&
                    value.getClass().equals(basicExpr.getClass()) && value.toString().equals(basicExpr.toString())) {
                arguments.replace(value, transformed);
            }
        }
        return super.visit(n, arg);
    }

    @Override
    public Visitable visit(ObjectCreationExpr n, List<Expression> arg) {
        NodeList<Expression> arguments = n.getArguments();
        for (Expression value :arguments) {
            if (value.isUnaryExpr()) {
                Expression expression = value.asUnaryExpr().getExpression();
                if (expression.getRange().equals(basicExpr.getRange()) &&
                        expression.getClass().equals(basicExpr.getClass()) && expression.toString().equals(basicExpr.toString())) {
                    value.asUnaryExpr().setExpression(transformed);
                }
            }
            if (value.getRange().equals(basicExpr.getRange()) &&
                    value.getClass().equals(basicExpr.getClass()) && value.toString().equals(basicExpr.toString())) {
                arguments.replace(value, transformed);
            }
        }
        return super.visit(n, arg);
    }


}
