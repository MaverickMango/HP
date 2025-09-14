package root.manipulation.random;

import com.github.javaparser.ast.expr.*;
import root.generation.transformation.AbstractMutateHelper;
import root.generation.transformation.AbstractLiteralMutator;

import java.util.*;

public class RandomMutateHelper extends AbstractMutateHelper {

    public RandomMutateHelper() {
        initializeTargetTypes();
    }

    @Override
    public AbstractLiteralMutator getKnownMutator(String type) {
        if (types.containsKey(type)) {
            List<Class<? extends Expression>> classes = types.get(type);
            //Now, here is a random getter for mutators.
            Random random = new Random();
            int idx = random.nextInt(classes.size());
            Class<? extends Expression> target = classes.get(idx);
            return mutators.get(target);
        } else {
            return getUnknownMutator(type);
        }
    }

    @Override
    public AbstractLiteralMutator getUnknownMutator(String type) {
        //todo
        logger.error("Unsupported type of mutator!");
        throw new IllegalArgumentException("Illegal argument: " + type);
//        return this.mutators.get(Expression.class);
    }
}
