package root.generation.transformation;

import com.github.javaparser.ast.expr.LiteralExpr;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;

public abstract class AbstractLiteralMutator {

    public Logger logger = LoggerFactory.getLogger(this.getClass());

    public Set<Object> historyMutants = new HashSet<>();

    public abstract <T extends LiteralExpr> T mutate(T oldValue);

    public <T extends LiteralExpr> T getNextMutant(T oldValue) {
        T mutatant;
        boolean terminate;
        logger.debug("Getting next mutant for " + oldValue.toString());
        int cnt = 0;
        do {
            logger.debug("into while loop " + cnt ++);
            mutatant = this.mutate(oldValue);
            if (Thread.currentThread().isInterrupted()) {
                logger.info("Thread times out, get-input-mutants phase ends.");
                break;
            }
            Object finalMutatant = mutatant;
            logger.debug("deduplication for " + finalMutatant.toString() + " in " + historyMutants.size());
            terminate = historyMutants.stream().noneMatch(i -> i.toString().equals(finalMutatant.toString()));
        } while(!terminate);
        historyMutants.add(mutatant);
        return mutatant;
    }

    List<Object> getHistoryMutants() {
        return Arrays.asList(this.historyMutants.toArray());
    }
}
