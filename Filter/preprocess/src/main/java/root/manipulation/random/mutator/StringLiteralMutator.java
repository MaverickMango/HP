package root.manipulation.random.mutator;

import com.github.javaparser.ast.expr.LiteralExpr;
import com.github.javaparser.ast.expr.StringLiteralExpr;
import root.generation.transformation.AbstractLiteralMutator;

import java.util.*;
import java.util.stream.Collectors;

public class StringLiteralMutator extends AbstractLiteralMutator {

    private Random random;
    private final String specialChars = "!@#$%^&*()+-=_[]{};:'\",./<>?|\\`~";
    Operator[] values = Operator.values();

    public enum Operator {
//        CAP,//大小写替换
        DEL,//删除一个字符
        REP,//replace 替换一个字符
        ADD//增加一个字符
    }

    @Override
    public StringLiteralExpr mutate(LiteralExpr oldValue) {
        random = new Random();
        StringLiteralExpr expr = new StringLiteralExpr();
        logger.debug("StringMutator!");
        expr.setString(randomStrMutate(((StringLiteralExpr)oldValue).getValue()));
        return expr;
    }

    private String randomStrMutate(String root) {
        String target = root;
        int idxS = 0, idxE = 0, opIdx;
        logger.debug("operator selection");
        //随机选取变异操作
        opIdx = random.nextInt(values.length);
        logger.debug(values[opIdx].toString());
        int i = random.nextInt(2);
        logger.debug("seed selection");
        //在第二次变异之后,有一半的概率从原始输入变为历史变体.
        if (historyMutants.size() > 1 && i == 1) {
            List<Object> collect = historyMutants.stream().collect(Collectors.toList());
            int cIdx = random.nextInt(historyMutants.size());
            do {
                target = ((StringLiteralExpr) collect.get(cIdx)).getValue();
            } while (target.isEmpty());
        }
        logger.debug("position selection for " + target);
        //随即变异挑选起始和结束位置.
        idxS = random.nextInt(target.length());
        idxE = random.nextInt(target.length());
        if (idxS > idxE) {
            int tmp = idxS;
            idxS = idxE;
            idxE = tmp;
        }
        //获得变体
        logger.debug("mutate");
        target = getMutants(new StringBuilder(target), idxS, idxE, values[opIdx]);
//        historyMutants.add(target);
        return target;
    }

    private String getMutants(StringBuilder old, int idxS, int idxE, Operator op) {
        StringBuilder curr = new StringBuilder(old);
        int length = curr.length();
        logger.debug("current input's length is " + length);
        CharLiteralMutator charMutator = new CharLiteralMutator();
        int count = idxS;
        char charAt;
        logger.debug("get newC");
        if (length <= count) {
            Collections.shuffle(charMutator.vocabulary);
            charAt = (char)charMutator.vocabulary.get(0).intValue();
        } else {
            charAt = curr.charAt(count);
        }
        Character newC = charMutator.randomCharMutate(charAt);
        logger.debug("get newS");
        StringBuilder newSbuilder = new StringBuilder(curr.substring(0, idxS));
        while (op.equals(Operator.REP) && length > newSbuilder.length()) {
            logger.debug("into loop");
            Character c = charMutator.randomCharMutate(curr.charAt(count++));
            newSbuilder.append(c);
        }
        logger.debug("replace");
        int i = random.nextInt(2);
        switch (op) {
            case DEL:
                curr.deleteCharAt(i == 0 ? idxS : idxE);
                break;
            case REP:
                curr = newSbuilder;
                break;
            case ADD:
                curr.insert(i == 0 ? idxS : idxE, newC);
                break;
            default:
                break;
//            case CAP:
//                curr.deleteCharAt(idx);
//                if (Character.isLowerCase(ch)) {
//                    curr.insert(idx, String.valueOf(ch).toUpperCase());
//                } else {
//                    curr.insert(idx, String.valueOf(ch).toLowerCase());
//                }
        }
        return curr.toString();
    }
}
