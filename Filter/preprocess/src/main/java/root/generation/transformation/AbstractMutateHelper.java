package root.generation.transformation;

import com.github.javaparser.ast.expr.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import root.manipulation.random.mutator.*;

import java.util.*;

public abstract class AbstractMutateHelper {

    public Logger logger = LoggerFactory.getLogger(this.getClass());

    public Map<Class<? extends Expression>, AbstractLiteralMutator> mutators;
    public Map<String, List<Class<? extends Expression>>> types;

    public boolean isKnownType(String className) {
        return types.containsKey(className);
    }

    /**********some methods need to be overridden**********/
    public void initializeTargetTypes() {
        //with default implementation
        //todo: whether to collect all values of different types in test file?
        mutators = new HashMap<>();
        mutators.put(BooleanLiteralExpr.class, new BooleanLiteralMutator());
        mutators.put(DoubleLiteralExpr.class, new DoubleLiteralMutator());
        mutators.put(IntegerLiteralExpr.class, new IntegerLiteralMutator());
        mutators.put(LongLiteralExpr.class, new LongLiteralMutator());
        mutators.put(StringLiteralExpr.class, new StringLiteralMutator());
        mutators.put(CharLiteralExpr.class, new CharLiteralMutator());
//        mutators.put(UnaryExpr.class, new UnaryMutator());

        types = new HashMap<>();
        types.put("boolean", Collections.singletonList(BooleanLiteralExpr.class));
        types.put("java.lang.Boolean", Collections.singletonList(BooleanLiteralExpr.class));
        types.put("int", Collections.singletonList(IntegerLiteralExpr.class));
        types.put("java.lang.Integer", Collections.singletonList(IntegerLiteralExpr.class));
        types.put("double", Collections.singletonList(DoubleLiteralExpr.class));
        types.put("java.lang.Double", Collections.singletonList(DoubleLiteralExpr.class));
        types.put("long", Collections.singletonList(LongLiteralExpr.class));
        types.put("java.lang.Long", Collections.singletonList(DoubleLiteralExpr.class));
        //todo char short?
        types.put("char", Collections.singletonList(CharLiteralExpr.class));
        types.put("java.lang.Character", Collections.singletonList(CharLiteralExpr.class));
        types.put("java.lang.String", Collections.singletonList(StringLiteralExpr.class));
        List<Class<? extends Expression>> list = Arrays.asList(
                BooleanLiteralExpr.class, IntegerLiteralExpr.class,
                DoubleLiteralExpr.class, StringLiteralExpr.class);
        types.put("Object", list);
        types.put("java.lang.Object", list);
    }
    /******************************************************/

    public abstract AbstractLiteralMutator getKnownMutator(String type);

    public abstract AbstractLiteralMutator getUnknownMutator(String type);
}
