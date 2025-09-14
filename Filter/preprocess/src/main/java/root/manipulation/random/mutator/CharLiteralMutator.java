package root.manipulation.random.mutator;

import com.github.javaparser.ast.expr.CharLiteralExpr;
import com.github.javaparser.ast.expr.LiteralExpr;
import root.generation.transformation.AbstractLiteralMutator;

import java.util.List;
import java.util.Random;
import java.util.stream.Collectors;

public class CharLiteralMutator extends AbstractLiteralMutator {

    private Random random = new Random();
    public List<Integer> vocabulary = null;

    public CharLiteralMutator() {
        vocabulary = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".chars().boxed().collect(Collectors.toList());
    }

    @Override
    public CharLiteralExpr mutate(LiteralExpr oldValue) {
        random = new Random();
        CharLiteralExpr expr = new CharLiteralExpr();
        expr.setChar(randomCharMutate(((CharLiteralExpr)oldValue).asChar()));
        return expr;
    }

    public Character randomCharMutate(Character old) {
        char newC;
        logger.debug("char mutator");
        String specialChars = "!@#$%^&*()+-=_[]{};:'\",./<>?|\\`~";
        if (specialChars.contains(String.valueOf(old))) {
            newC = (char) random.nextInt(129);
        } else {
            char tmp1 = (char) (random.nextInt(26) + 65);
            char tmp2 = (char) (random.nextInt(26) + 97);
            int i = random.nextInt(2);
            newC = i == 0 ? tmp1 : tmp2;
        }
        logger.debug("return newC " + newC);
        return newC;
    }
}
