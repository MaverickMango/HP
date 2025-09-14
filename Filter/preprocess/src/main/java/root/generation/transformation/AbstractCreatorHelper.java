package root.generation.transformation;

import com.github.javaparser.ast.expr.*;
import com.github.javaparser.utils.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import root.generation.entities.Input;

import java.util.*;

public abstract class AbstractCreatorHelper {

    public static final Logger logger = LoggerFactory.getLogger(AbstractCreatorHelper.class);

    public AbstractMutateHelper mutateHelper;

    public abstract void setMutateHelper();

    public abstract List<Pair<Expression, ? extends LiteralExpr>> getInputMutants(Input oldInput);

    public abstract Pair<Expression, ? extends LiteralExpr> getInputMutant(Input oldInput);


}
