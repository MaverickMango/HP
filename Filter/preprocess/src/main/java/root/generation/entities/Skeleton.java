package root.generation.entities;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.PackageDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.nodeTypes.NodeWithSimpleName;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.Statement;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import root.entities.ci.BugRepository;
import root.generation.transformation.Runner;
import root.util.Helper;
import root.util.PatchHelper;
import root.visitor.ModifiedVisitor;
import root.util.FileUtils;

import java.io.File;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

/**
 * a method declaration of test, the last statement is the one before trigger assert.
 * if all statements before are $ASSERT, Prefix will have an empty body.
 */
public class Skeleton implements Cloneable {

    private static final Logger logger = LoggerFactory.getLogger(Skeleton.class);

    String oracleFilePath;
    String absolutePath;
    CompilationUnit clazz;
//    CompilationUnit mutant;
    String clazzName;
    Map<String, MethodDeclaration> originalMethod;//key: input's identifier
    Map<Input, MethodDeclaration> transformedMethod;//key: input's identifier
    boolean isSplit;//是否完成对多余断言的删除
    List<Input> inputs;
    Map<String, MethodDeclaration> generatedMethods;
    int generatedTestsIdx;
    int generatedClazzIdx;

    public Skeleton(String absolutePath, CompilationUnit clazz, String clazzName) {
        this.absolutePath = absolutePath;
        this.clazz = clazz;
        this.originalMethod = new HashMap<>();
        this.clazzName = clazzName;
        this.isSplit = false;
        this.inputs = new ArrayList<>();
        this.generatedMethods = new HashMap<>();
        this.generatedTestsIdx = 0;
        this.generatedClazzIdx = 0;
        oracleFilePath = PatchHelper.oracleOutputs;
        File file = new File(getOracleFilePath(true));
        if (file.exists()) {
            file.delete();
        }
    }

    public Skeleton(String absolutePath, CompilationUnit clazz, String clazzName, List<Input> inputs) {
//        if (originalMethod.keySet().stream().anyMatch(n -> n.getParentNode().isEmpty())) {
//            throw new IllegalArgumentException("one of the originalMethod doesn't have parent node!");
//        }
//        if (originalMethod.keySet().stream().anyMatch(n -> !(n.getParentNode().get() instanceof ClassOrInterfaceDeclaration))) {
//            throw new IllegalArgumentException("Unsupported method type. May be one of the originalMethod is anonymous!");
//        }
        this.absolutePath = absolutePath;
        this.clazz = clazz;
        this.originalMethod = new HashMap<>();
        this.inputs = new ArrayList<>();
        setInputs(inputs);
        this.clazzName = clazzName;
        this.isSplit = false;
        this.generatedMethods = new HashMap<>();
        this.generatedTestsIdx = 0;
        this.generatedClazzIdx = 0;
        oracleFilePath = PatchHelper.oracleOutputs;
    }
//
//    public CompilationUnit getMutant() {
//        return mutant;
//    }

    public String getOracleFilePath(boolean isOracle) {
        return isOracle ? oracleFilePath : oracleFilePath.replace("_org", "_pat");
    }

    public String getAbsolutePath() {
        return absolutePath;
    }

    public void setClazz(CompilationUnit clazz) {
        this.clazz = clazz;
    }

    public CompilationUnit getClazz() {
        return clazz;
    }

    public String getClazzName() {
        return clazzName;
    }

    public Map<String, MethodDeclaration> getOriginalMethod() {
        return originalMethod;
    }

    public Map<Input, MethodDeclaration> getTransformedMethod() {
        return transformedMethod;
    }

    public void addInput(Input input) {
        Optional<MethodDeclaration> ancestor = input.getMethodCallExpr().findAncestor(MethodDeclaration.class);
        if (ancestor.isPresent()) {
            MethodDeclaration methodDeclaration = ancestor.get();
            this.originalMethod.putIfAbsent(input.getIdentifier(), methodDeclaration);
        }
        this.inputs.add(input);
    }

    public void setInputs(List<Input> inputs) {
        for (Input input :inputs) {
            addInput(input);
        }
    }

    public List<Input> getInputs() {
        return this.inputs;
    }

    public boolean isSplit() {
        return isSplit;
    }

    public CompilationUnit[] constructCompetitiveSkeleton(List<Input> newInputs) {
        logger.info("Constructing Skeleton...");
        if (!isSplit()) {
            logger.info("Removing Assertion in test method...");
            splitAssert();//删除原有的assert语句
        }
        logger.info("Apply all new inputs, transforming test method...");
        applyTransform(newInputs);
        logger.info("Getting competitve testClass...");
        return getCompetitive(newInputs);
    }

    public void constructSkeleton(List<Input> newInputs) {
        logger.info("Constructing Skeleton...");
        if (!isSplit()) {
            logger.info("Removing Assertion in test method...");
            splitAssert();//删除原有的assert语句
        }
        logger.info("Apply all new inputs, transforming test method...");
        applyTransform(newInputs);
        List<Input> collect = newInputs.stream().filter(input -> !input.isCompleted()).collect(Collectors.toList());
        List<Input> collect1 = newInputs.stream().filter(Input::isCompleted).collect(Collectors.toList());
        if (!collect.isEmpty()) {
            logger.info("Getting oracles...");
            Map<String, MethodDeclaration> oracle = getOracle(newInputs);//需要oracle的语句则需要先执行一遍
            //todo 并不能通过参数数量来确定是否需要oracle，还可能是assertrue这种
            addGeneratedMethods(oracle);
        }
        if (!collect1.isEmpty()) {
            logger.info("Constructing methods without oracle...");
            Map<Input, MethodDeclaration> methodDeclarationInputMap = addStatementsAtLast(collect1);//对于不需要oracle的语句，直接根据input更新method
            for (Map.Entry<Input, MethodDeclaration> entry: methodDeclarationInputMap.entrySet()) {
                String testNamePrefix = getTestNamePrefix(getClazz(), entry.getValue().getNameAsString());
                addGeneratedMethod(testNamePrefix, entry.getValue());//putIfAbsent?
            }
        }
    }

    public void constructSkeleton(Input newInput) {
        if (!isSplit())
            splitAssert();//删除原有的assert语句
        applyTransform(newInput);
        if (!newInput.isCompleted()) {
            Map<String, MethodDeclaration> newUnit = getOracle(newInput);
            addGeneratedMethods(newUnit);//需要oracle的语句则需要先执行一遍
        } else {
            MethodCallExpr methodCallExpr = newInput.getMethodCallExpr();
            ExpressionStmt stmt = new ExpressionStmt(methodCallExpr);
            MethodDeclaration methodDeclaration = addStatementAtLast(newInput, stmt);//对于不需要oracle的语句，直接根据input更新method
            String testNamePrefix = getTestNamePrefix(getClazz(), methodDeclaration.getNameAsString());
            addGeneratedMethod(testNamePrefix, methodDeclaration);
        }
    }

    public void addGeneratedMethod(String testName, MethodDeclaration methodDeclaration) {
        generatedMethods.put(testName, methodDeclaration);

        //保存生成的测试
        String test = testName.split("::")[1];
        FileUtils.writeToFile(methodDeclaration.toString(),
                Runner.generationOutput + File.separator + "instr" + File.separator + test,
                false);
    }

    public void addGeneratedMethods(Map<String, MethodDeclaration> map) {
        for (Map.Entry<String, MethodDeclaration> entry : map.entrySet()) {
            addGeneratedMethod(entry.getKey(), entry.getValue());
        }
    }

    public Map<String, MethodDeclaration> getGeneratedMethods() {
        return generatedMethods;
    }

    public void splitAssert() {
        Map<String, MethodDeclaration> map = new HashMap<>();
        for (String identifier :originalMethod.keySet()) {
            MethodDeclaration clone = originalMethod.get(identifier).clone();
            (clone.getBody().get()).findAll(ExpressionStmt.class).forEach((stmt) -> {
                if (Helper.isAssertion(stmt)) {
                    stmt.remove();
                }
            });
            map.put(identifier, clone);
        }
        this.originalMethod = map;
        this.transformedMethod = new HashMap<>();
        this.isSplit = true;
    }

    public MethodDeclaration addStatementAtLast(Input input, Statement stmt) {
        MethodDeclaration methodDeclaration = transformedMethod.get(input);
        MethodDeclaration clone = methodDeclaration.clone();
        String newMethodName = getNewMethodName(clone.getNameAsString(), true);
        clone.setName(newMethodName);
        addStatementAtLast(input, clone, stmt);
        return clone;
    }

    public void addStatementAtLast(Input input, MethodDeclaration clone, Statement stmt) {
        Optional<BlockStmt> body = clone.getBody();
        if (body.isPresent()) {
            BlockStmt blockStmt = body.get();
            NodeList<Statement> statements = blockStmt.getStatements();
            statements.addLast(stmt);
        } else {
            logger.error("methodDeclaration in skeleton has been initialized with error. Empty skeleton will be create.");
            BlockStmt blockStmt = new BlockStmt(new NodeList<>());
            blockStmt.getStatements().addLast(stmt);
        }
    }

    public Map<Input, MethodDeclaration> addStatementsAtLast(List<Input> inputs) {
        Map<Input, MethodDeclaration> methodDeclarations = new HashMap<>();
        for (Input newInput : inputs) {
            MethodCallExpr methodCallExpr = newInput.getMethodCallExpr();
            ExpressionStmt stmt = new ExpressionStmt(methodCallExpr);
            MethodDeclaration methodDeclaration = addStatementAtLast(newInput, stmt);
            methodDeclarations.put(newInput, methodDeclaration);
        }
        return methodDeclarations;
    }

    public CompilationUnit addMethods2CompilationUnit(CompilationUnit unit, Collection<MethodDeclaration> methodDeclarations) {
        CompilationUnit clone = unit.clone();
        if (clone.getClassByName(clazzName).isEmpty()) {
            logger.error("unit: \n" + unit.toString());
            logger.error("clazzName: " + clazzName);
            return null;
        }
        ClassOrInterfaceDeclaration classOrInterfaceDeclaration = clone.getClassByName(clazzName).get();
        List<String> collect = classOrInterfaceDeclaration.getMethods().stream()
                .map(NodeWithSimpleName::getNameAsString).collect(Collectors.toList());
        NodeList<ImportDeclaration> imports = clone.getImports();
        ImportDeclaration importDeclaration = new ImportDeclaration("java.io", false, true);
        imports.add(importDeclaration);
        importDeclaration = new ImportDeclaration("java.nio.charset.StandardCharsets", false, false);
        imports.add(importDeclaration);
        for (MethodDeclaration methodDeclaration: methodDeclarations) {
            if (!collect.contains(methodDeclaration.getNameAsString()))
                classOrInterfaceDeclaration.addMember(methodDeclaration);
        }
        return clone;
    }

    public CompilationUnit addMethod2CompilationUnit(CompilationUnit unit, MethodDeclaration methodDeclaration) {
        CompilationUnit clone = unit.clone();
        ClassOrInterfaceDeclaration classOrInterfaceDeclaration = clone.getClassByName(clazzName).get();
        List<String> collect = classOrInterfaceDeclaration.getMethods().stream()
                .map(NodeWithSimpleName::getNameAsString).collect(Collectors.toList());
        if (!collect.contains(methodDeclaration.getNameAsString()))
            classOrInterfaceDeclaration.addMember(methodDeclaration);
        //add imports
        /*
            import java.io.*;
            import java.nio.charset.StandardCharsets;
         */
        NodeList<ImportDeclaration> imports = clone.getImports();
        ImportDeclaration importDeclaration = new ImportDeclaration("java.io", false, true);
        imports.add(importDeclaration);
        importDeclaration = new ImportDeclaration("java.nio.charset.StandardCharsets", false, false);
        imports.add(importDeclaration);
        return clone;
    }

    private String getNewMethodName(String oldName, boolean isOracle) {
        return oldName + "_generatedTest" + generatedTestsIdx ++;
    }

    private String getNewClazzName(String oldName) {
        return oldName + "_generatedTest" + generatedClazzIdx ++;
    }

    public void applyTransform(Input transformedInput) {
        Expression inputExpr = transformedInput.getInputExpr().clone();
        Expression basicExpr = transformedInput.getTransformed().a;
        Expression transformed = transformedInput.getTransformed().b;
        List<Expression> collector = new ArrayList<>();
        ModifiedVisitor visitor = new ModifiedVisitor(inputExpr, basicExpr, transformed);
        if (transformedInput instanceof ObjectInput) {
            MethodDeclaration preTransformedMethod = originalMethod.get(transformedInput.getIdentifier());
            MethodDeclaration methodDeclaration = preTransformedMethod.clone();
            methodDeclaration.accept(visitor, collector);
            this.transformedMethod.put(transformedInput, methodDeclaration);
            transformedInput.setTransformed(true);
        } else if (transformedInput instanceof BasicInput) {
            MethodCallExpr clone = transformedInput.getMethodCallExpr().clone();
            clone.accept(visitor, collector);
            transformedInput.setMethodCallExpr(clone);
            transformedInput.setTransformed(true);
            this.transformedMethod.put(transformedInput, originalMethod.get(transformedInput.getIdentifier()));
        }
    }

    public void applyTransform(List<Input> inputs) {
        for (Input input :inputs) {
            applyTransform(input);
        }
    }

    public Statement getSkeletonStmt(CompilationUnit compilationUnit, String methodName, Expression expression, boolean isOracle) {
        EnclosedExpr expr = new EnclosedExpr();
        BinaryExpr binaryExpr = new BinaryExpr();
        binaryExpr.setOperator(BinaryExpr.Operator.PLUS);
        binaryExpr.setRight(expression);
        StringLiteralExpr stringLiteralExpr = new StringLiteralExpr("\n" + getTestNamePrefix(compilationUnit, methodName) + "::");
        binaryExpr.setLeft(stringLiteralExpr);
        expr.setInner(binaryExpr);
        return Helper.constructFileOutputStmt2Instr(PatchHelper.oracleOutputs, expr);
    }

    private MethodDeclaration getMethodInstrumented(Input input, boolean isOracle) {
        //插入一个输出语句用于获取变量在original版本的oracle。
        Expression inputExpr = input.getInputExpr();
        MethodDeclaration methodDeclaration = transformedMethod.get(input);
        inputExpr = input.getMethodCallExpr().getArgument(input.getArgIdx());
        MethodDeclaration clone = methodDeclaration.clone();
        String newMethodName = getNewMethodName(methodDeclaration.getNameAsString(), isOracle);
        clone.setName(newMethodName);
        Statement stmt = getSkeletonStmt(clazz, newMethodName, inputExpr, isOracle);
        addStatementAtLast(input, clone, stmt);
        return clone;
    }
    
    public CompilationUnit[] getCompetitive(List<Input> inputs) {
        CompilationUnit[] mutants = new CompilationUnit[2];
        Map<Input, MethodDeclaration> methodintrs = new HashMap<>();
        int start = generatedTestsIdx;
        for (Input input : inputs) {
            MethodDeclaration methodInstrumented = getMethodInstrumented(input, true);
            methodintrs.put(input, methodInstrumented);
        }
        mutants[0] = addMethods2CompilationUnit(clazz, methodintrs.values());
        Runner.constructHelper.saveTests(mutants[0], getAbsolutePath(), true);
        logger.info("Saving generated tests in original repository");

        //**important** 生成测试的序号要和oracle版本一致
        generatedTestsIdx = start;
        for (Input input :inputs) {
            MethodDeclaration methodInstrumented = getMethodInstrumented(input, false);
            methodintrs.put(input, methodInstrumented);
        }
        mutants[1] = addMethods2CompilationUnit(clazz, methodintrs.values());
        for (Map.Entry<Input, MethodDeclaration> entry: methodintrs.entrySet()) {
            String testNamePrefix = getTestNamePrefix(getClazz(), entry.getValue().getNameAsString());
            addGeneratedMethod(testNamePrefix, entry.getValue());
        }
        Runner.constructHelper.saveTests(mutants[1], getAbsolutePath(), false);
        logger.info("Saving generated tests in buggy repository");
        return mutants;
    }

    public Map<String, MethodDeclaration> getOracle(List<Input> inputs) {
        Map<Input, MethodDeclaration> methodintrs = new HashMap<>();
        for (Input input :inputs) {
            MethodDeclaration methodInstrumented = getMethodInstrumented(input, true);
            methodintrs.put(input, methodInstrumented);
        }
        CompilationUnit transformedCompilationUnit = addMethods2CompilationUnit(clazz, methodintrs.values());

        StringBuilder testName = new StringBuilder();
        for (MethodDeclaration method :methodintrs.values()) {
            testName.append(getTestNamePrefix(transformedCompilationUnit, method.getNameAsString()) + " ");
        }
        logger.info("Executing tests in original commit...");
        boolean res = Runner.constructHelper.saveTests(transformedCompilationUnit, getAbsolutePath(), true);
        if (!res) {
            return null;
        }
        List<String> failed = tests4All(testName.toString(), true);
        //失败的测试就不需要了
        Map<Input, MethodDeclaration> withOracle = new HashMap<>();
        for (Map.Entry<Input, MethodDeclaration> entry : methodintrs.entrySet()) {
            if (!failed.contains(entry.getValue().getName().toString())) {
                withOracle.put(entry.getKey(), entry.getValue());
            }
        }
        inputs.forEach(input -> input.setCompleted(true));
        logger.info("Constructing methods with oracles....");
        Map<String, MethodDeclaration> oracleWithAssert = Runner.constructHelper.getOracleWithAssert(this, transformedCompilationUnit, withOracle);
        return oracleWithAssert;
    }

    public Map<String, MethodDeclaration> getOracle(Input input) {
        MethodDeclaration methodInstrumented = getMethodInstrumented(input, true);
        //这个时候不需要插入断言
//        MethodDeclaration methodDeclaration = addStatementAtLast(input.getMethodCallExpr());
        CompilationUnit transformedCompilationUnit = addMethod2CompilationUnit(clazz, methodInstrumented);

        input.setCompleted(true);
        boolean res = Runner.constructHelper.saveTests(transformedCompilationUnit, getAbsolutePath(), true);
        if(!res) {
            return null;
        }
        String testName = getTestNamePrefix(transformedCompilationUnit, methodInstrumented.getNameAsString());
        List<String> failed = tests4All(testName, true);
        //失败的测试就不需要了
        if (!failed.contains(methodInstrumented.getNameAsString())) {
            return null;
        }
        Map<Input, MethodDeclaration> map = new HashMap<>();
        map.put(input, methodInstrumented);
        Map<String, MethodDeclaration> oracleWithAssert = Runner.constructHelper.getOracleWithAssert(this, transformedCompilationUnit, map);
        return oracleWithAssert;
    }
    
    public List<String> runGeneratedTests(Map<String, MethodDeclaration> map) {
        logger.info("Transforming test for buggy version, add generated methods.");
        CompilationUnit transformedCompilationUnit = addMethods2CompilationUnit(clazz, map.values());

        StringBuilder testNames = new StringBuilder();
        for (String testName :map.keySet()) {
            testNames.append(testName).append(" ");
        }
        logger.info("Running test to predict patch correctness...");
        Runner.constructHelper.saveTests(transformedCompilationUnit, getAbsolutePath(), false);
        return tests4All(testNames.toString(), false);
    }

    public List<String> tests4All(String testNames, boolean isOracle) {
        BugRepository repo = isOracle ? Runner.orgRepository : PatchHelper.patchRepository;
        List<String> tests = new ArrayList<>();
        boolean flag = false;
        for (String test :testNames.split(" ")) {
            List<String> r = repo.testWithRes(test);
            if (r.isEmpty() || !r.get(0).equals("0")) {
                logger.info("Test execution error! :\n" + FileUtils.getStrOfIterable(r, "\n"));
                continue;
            }
            Collections.reverse(r);
            if (!r.get(0).equals("Failing tests: 0")) {
                tests.add(test);
                if (!isOracle) {
                    String failing = repo.getBug().getWorkingDir() + File.separator + "failing_tests";//failing_tests
                    String testName = test.split("::")[1];
                    FileUtils.copy(new File(failing), new File(Runner.testsResults + File.separator + testName));
                }
            }
            flag = true;
        }
        if (!flag) {
            return null;
        }
        return tests;
    }

    public String getTestNamePrefix(CompilationUnit compilationUnit, String methodName) {
        Optional<PackageDeclaration> packageDeclaration = compilationUnit.getPackageDeclaration();
        AtomicReference<String> pack = new AtomicReference<>("");
        packageDeclaration.ifPresent(p -> pack.set(p.getNameAsString()));
        String testName = pack.get() + "." + getClazzName() + "::" + methodName;
        return testName;
    }

    @Override
    public Skeleton clone() {
        try {
            Skeleton clone = (Skeleton) super.clone();
            return clone;
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}
