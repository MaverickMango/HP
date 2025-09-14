package root.generation.transformation;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.comments.LineComment;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.quality.NotNull;
import com.github.javaparser.utils.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import root.analysis.ASTExtractor;
import root.entities.ci.BugRepository;
import root.generation.entities.Input;
import root.generation.entities.Skeleton;
import root.util.FileUtils;
import root.util.PatchHelper;

import java.io.File;
import java.util.*;
import java.util.stream.Collectors;

public class ConstructHelper {

    private final Logger logger = LoggerFactory.getLogger(ConstructHelper.class);
    public ASTExtractor ASTExtractor;
    Map<String, Skeleton> skeletons;//<absolutePath, Skeleton>

    public ConstructHelper(ASTExtractor astExtractor) {
        this.skeletons = new HashMap<>();
        ASTExtractor = astExtractor;
    }

    public Skeleton createASkeleton(String fileAbsPath, String clazzName, Input input) {
        ArrayList<Input> inputs = new ArrayList<>();
        inputs.add(input);
        return createASkeleton(fileAbsPath, clazzName, inputs);
    }

    public Skeleton createASkeleton(String fileAbsPath, String clazzName, List<Input> inputs) {
        if (inputs == null) {
            return null;
        }
//        boolean res = bugRepository.switchToOrg();
//        if (!res) {
//            logger.error("Error occurred when getting oracle in original commit! May be it cannot be compiled successfully.\n Null will be returned");
//            return null;
//        }//直接用orgRepository
        String filePath = fileAbsPath.replace("_buggy", "_org");
        CompilationUnit compilationUnit = ASTExtractor.getCompilationUnit(filePath);
        Skeleton skeleton = new Skeleton(filePath, compilationUnit, clazzName, inputs);
        return skeleton;
    }

    public boolean saveTests(CompilationUnit unit, String targetPath, boolean isOracle) {
        targetPath = isOracle ? targetPath.replace("_buggy", "_org")
                : targetPath.replace("_org", "_buggy");
        return FileUtils.writeToFile(unit.toString(), targetPath, false);
    }

    public String getIdentifier(Node node) {
        if (node instanceof MethodDeclaration) {
            String nameAsString = ((MethodDeclaration) node).getNameAsString();
            //todo ?
            return nameAsString;
        }
        return node.toString();
    }

    public List<Input> transformInput(Input oldInput, List<Pair<Expression, ? extends LiteralExpr>> values) {
        List<Input> inputs = new ArrayList<>();
        for (Pair<Expression, ? extends LiteralExpr> value :values) {
            Input newInput = transformInput(oldInput, value.a, value.b);
            inputs.add(newInput);
        }
        return inputs;
    }

    public Input transformInput(Input oldInput, Expression basicExpr, Object value) {
        if (oldInput.getInputExpr().getParentNode().isEmpty()) {
            logger.error("Node " + oldInput.getInputExpr() + " has lost its parent node, can't process further!");
            throw new IllegalArgumentException(oldInput.toString());
        }
        logger.debug("New input " + value.toString() + " has been transformed for " + basicExpr);
        FileUtils.writeToFile(basicExpr + "#" + value + "\n", Runner.generationOutput + File.separator + "inputs", true);

        Input newInput = oldInput.clone();
        Expression newInputExpr = (Expression) value;//transform(basicExpr, value);
        newInput.setBasicExprTransformed(basicExpr, newInputExpr);
        return newInput;
    }

    public void buildNewTestByInput(Skeleton skeleton, Input newInput) {
        String path = skeleton.getAbsolutePath();
        if (!this.skeletons.containsKey(path)) {
            this.skeletons.put(path, skeleton);
        }
        skeleton.constructSkeleton(newInput);
    }

    public void buildNewTestByInputs(Skeleton skeleton, List<Input> newInputs) {
        String path = skeleton.getAbsolutePath();
        if (!this.skeletons.containsKey(path)) {
            this.skeletons.put(path, skeleton);
        }
        skeleton.constructSkeleton(newInputs);
    }

    public CompilationUnit[] buildCompetitiveTests(Skeleton skeleton, List<Input> newInputs) {
        String path = skeleton.getAbsolutePath();
        if (!this.skeletons.containsKey(path)) {
            this.skeletons.put(path, skeleton);
        }
        return skeleton.constructCompetitiveSkeleton(newInputs);
    }

    public Map<String, List<String>> getTestInfos(String[] tests) {
        Map<String, List<String>> testsByClazz = new HashMap<>();
        logger.info("...Split test one by one.");
        for (String triggerTest : tests) {
            String[] split1 = triggerTest.split(":");
            String clazzName = split1[0];//.replaceAll("\\.", File.separator);
            String methodName = split1[1];
            int lineNumber = split1.length == 3 ? Integer.parseInt(split1[2]) : 0;
            if (!testsByClazz.containsKey(clazzName)) {
                testsByClazz.put(clazzName, new ArrayList<>());
            }
            testsByClazz.get(clazzName).add(methodName + ":" + lineNumber);
        }
        return testsByClazz;
    }

    public Map<String, MethodDeclaration> getOracleWithAssert(Skeleton skeleton, CompilationUnit instr,
                                                              Map<Input, MethodDeclaration> methodDeclarations) {
        List<String> oracles = FileUtils.readEachLine(skeleton.getOracleFilePath(true));
        Map<String, MethodDeclaration> map  = new HashMap<>();
        for (Map.Entry<Input, MethodDeclaration> entry :methodDeclarations.entrySet()) {
            MethodDeclaration methodDeclaration = entry.getValue();
            Input input = entry.getKey();
            List<String> collect = oracles.stream().filter(line -> !line.isEmpty() &&
                    line.split("::")[1].equals(methodDeclaration.getNameAsString())).collect(Collectors.toList());
            if (collect.isEmpty()) {
                ExpressionStmt stmt = new ExpressionStmt(input.getMethodCallExpr());
                LineComment comment = new LineComment("execution failed, original oracle is set.");
                stmt.setComment(comment);
                replaceLastStmt(methodDeclaration, input, stmt);
                map.put(skeleton.getTestNamePrefix(instr, methodDeclaration.getNameAsString()), methodDeclaration);
                continue;
            }
            String line = collect.get(0);
            String oracle = line.substring(line.lastIndexOf("::") + 2);
            MethodCallExpr methodCallExpr = input.getMethodCallExpr();
            NodeList<Expression> arguments = methodCallExpr.getArguments();
            Expression oldOracle = arguments.get(0);
            Expression newOracle = transform(oldOracle, oracle);
            arguments.replace(oldOracle, newOracle);
            ExpressionStmt stmt = new ExpressionStmt(methodCallExpr);
            replaceLastStmt(methodDeclaration, input, stmt);
            map.put(skeleton.getTestNamePrefix(instr, methodDeclaration.getNameAsString()), methodDeclaration);
        }
        return map;
    }

    private void replaceLastStmt(MethodDeclaration methodDeclaration, Input input, ExpressionStmt stmt) {
        Optional<BlockStmt> body = methodDeclaration.getBody();
        body.ifPresent(blockStmt -> {
            NodeList<Statement> statements = blockStmt.getStatements();
            Optional<Statement> last = statements.getLast();
            last.ifPresent(b -> {
                if (b.isBlockStmt()) {
                    statements.replace(b, stmt);
                }
            });
        });
    }

    @SuppressWarnings("deprecation")
    public Expression transform(@NotNull Expression basicExpr, Object value) {
        Class<? extends Expression> inputType = basicExpr.getClass();
        Expression newInputExpr = null;
        try {
            if (inputType.equals(BooleanLiteralExpr.class)) {
                newInputExpr = new BooleanLiteralExpr();
                ((BooleanLiteralExpr) newInputExpr).setValue(Boolean.parseBoolean((String) value));
            }
            if (inputType.equals(DoubleLiteralExpr.class)) {
                newInputExpr = new DoubleLiteralExpr();
                ((DoubleLiteralExpr) newInputExpr).setDouble(Double.parseDouble((String) value));
            }
            if (inputType.equals(IntegerLiteralExpr.class)) {
                newInputExpr = new IntegerLiteralExpr();
                ((IntegerLiteralExpr) newInputExpr).setInt(Integer.parseInt((String) value));
            }
            if (inputType.equals(CharLiteralExpr.class)) {
                newInputExpr = new CharLiteralExpr();
                ((CharLiteralExpr) newInputExpr).setChar((Character) value);
            }
            if (inputType.equals(LongLiteralExpr.class)) {
                newInputExpr = new LongLiteralExpr();
                ((LongLiteralExpr) newInputExpr).setLong(Long.parseLong((String) value));
            }
            if (inputType.equals(StringLiteralExpr.class)) {
                newInputExpr = new StringLiteralExpr();
                ((StringLiteralExpr) newInputExpr).setString((String) value);
            }
            if (inputType.equals(UnaryExpr.class)) {
                newInputExpr = (UnaryExpr) value;
            }
        } catch (ClassCastException e) {
            logger.error("Error casting while generate new input by argument '" + value + "'! " + e.getMessage());
            logger.info("No newInput was generated. OldInput return.");
        }
        if (newInputExpr == null) {
            throw new IllegalArgumentException("TBD. Unsupported type of Input has been given.");
        }
        return newInputExpr;
    }

    public List<Input> getOriginalTestsInputs(CompilationUnit compilationUnit,
                                                      List<String> testMths) {
        try {
            List<Input> inputs = new ArrayList<>();
            logger.info("Processing each test methods...");
            for (String testMth : testMths) {
                String[] split = testMth.split(":");
                String methodName = split[0];
                int lineNumber = split.length == 2 ? Integer.parseInt(split[1]) : 0;
                logger.info("Extracting test input for test " + methodName);
                Input input = ASTExtractor.extractInput(compilationUnit, methodName, lineNumber);
                inputs.add(input);
            }
            return inputs;
        } catch (Exception e) {
            logger.error(e.getMessage());
        }
        return null;
    }

}
