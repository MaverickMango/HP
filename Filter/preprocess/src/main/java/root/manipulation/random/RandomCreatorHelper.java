package root.manipulation.random;

import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.LiteralExpr;
import com.github.javaparser.ast.expr.UnaryExpr;
import com.github.javaparser.utils.Pair;
import root.generation.entities.Input;
import root.util.Helper;
import root.generation.transformation.AbstractLiteralMutator;
import root.generation.transformation.AbstractCreatorHelper;

import java.util.*;

public class RandomCreatorHelper extends AbstractCreatorHelper {

    private final int maxMutantsNum;

    public RandomCreatorHelper(int maxMutatesNum) {
        this.maxMutantsNum = maxMutatesNum;
        setMutateHelper();
    }

    @Override
    public void setMutateHelper() {
        this.mutateHelper = new RandomMutateHelper();
    }

    @Override
    public List<Pair<Expression, ? extends LiteralExpr>> getInputMutants(Input oldInput){
        Random random = new Random(new Date().getTime());
        List<Expression> basicExprs = oldInput.getBasicExpr();
        Set<Pair<Expression, ? extends LiteralExpr>> mutants = new HashSet<>();
        AbstractLiteralMutator mutator;
        int cnt = 0;
        logger.debug("Start mutate input " + oldInput);
        while (cnt < maxMutantsNum && mutants.size() < maxMutantsNum) {
            if (Thread.currentThread().isInterrupted()) {
                logger.info("Thread times out, get-input-mutants phase ends.");
                break;
            }
            cnt ++;
            logger.debug("into while loop " + cnt);
            int idx = random.nextInt(basicExprs.size());
            Expression basicExpr = basicExprs.get(idx);
            // check whether type is known class,and apply its mutator to get its mutants.
            if (basicExpr instanceof UnaryExpr) {
                basicExpr = ((UnaryExpr) basicExpr).getExpression();
            }
            String qualifiedName = Helper.getType(basicExpr);
            logger.debug("get known mutator");
            if (mutateHelper.isKnownType(qualifiedName)) {
                mutator = mutateHelper.getKnownMutator(qualifiedName);
                LiteralExpr nextInput = mutator.getNextMutant(basicExpr.asLiteralExpr());
                logger.debug("add new mutant at round " + cnt);
                mutants.add(new Pair<>(basicExpr, nextInput));
            } else {
                //todo add other type
//                mutator = mutateHelper.getUnknownMutator(qualifiedName);
//                Object nextInput = mutator.getNextMutant(basicExpr);
//                mutants.add(new Pair<>(basicExpr, nextInput));
            }
        }
        return new ArrayList<>(mutants);
    }

    @Override
    public Pair<Expression, ? extends LiteralExpr> getInputMutant(Input oldInput) {
        Random random = new Random(new Date().getTime());
        List<Pair<Expression, ? extends LiteralExpr>> inputMutants = getInputMutants(oldInput);
        int idx = random.nextInt(inputMutants.size());
        return inputMutants.get(idx);
    }

}
