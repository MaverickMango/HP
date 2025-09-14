package root.generation.transformation;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.CallableDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.LiteralExpr;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.utils.Pair;
import org.junit.Ignore;
import org.junit.jupiter.api.Test;
import root.generation.entities.Input;
import root.generation.entities.Skeleton;
import root.extraction.ASTExtractorTest;
import root.generation.helper.PreparationTest;
import root.analysis.ASTExtractor;
import root.manipulation.random.RandomRunner;
import root.manipulation.random.RandomCreatorHelper;
import root.util.ConfigurationProperties;

import java.io.File;
import java.util.*;

import static org.junit.Assert.assertEquals;
import static org.junit.jupiter.api.Assertions.*;

class InputRunnerHelperTest extends PreparationTest{

    @Test
    void transformInput() {
        ConstructHelper constructHelper = Runner.constructHelper;
        Input input = ASTExtractorTest.getInput();
        Pair<Expression, ? extends LiteralExpr> inputMutant = (new RandomCreatorHelper(10)).getInputMutant(input);
        Input newInput = constructHelper.transformInput(input, inputMutant.a, inputMutant.b);
        assertNotEquals(newInput.getTransformed().b, input.getBasicExpr());
    }

    @Test
    void transformInputs() {
        ConstructHelper constructHelper = Runner.constructHelper;
        Input input = ASTExtractorTest.getInput();
        List<Pair<Expression, ? extends LiteralExpr>> inputMutants = (new RandomCreatorHelper(10)).getInputMutants(input);
        assertEquals(10, inputMutants.size());
        List<Input> newInputs = constructHelper.transformInput(input, inputMutants);
        for (Input newInput :newInputs) {
            assertNotEquals(newInput.getTransformed(), input.getBasicExpr());
        }
    }

    @Test
    void createASkeleton() {
        Skeleton skeleton = getASkeleton();
        assertNotNull(skeleton);
    }

    public Skeleton getASkeleton() {
        CallableDeclaration methodDeclaration = ASTExtractorTest.getMethodDeclaration();
        MethodCallExpr methodCallExpr = Runner.constructHelper.ASTExtractor
                .extractAssertByLine(methodDeclaration, lineNumber);
        Input input =  Runner.constructHelper.ASTExtractor.extractInput(methodCallExpr);
        String absolutePath = new File(ASTExtractorTest.filePath).getAbsolutePath();
        Optional<ClassOrInterfaceDeclaration> ancestor = methodDeclaration.findAncestor(ClassOrInterfaceDeclaration.class);
        String clazzName = ancestor.get().getName().toString();
        Skeleton skeleton = Runner.constructHelper.createASkeleton(absolutePath, clazzName, input);
        return skeleton;
    }

    @Test
    void buildNewTestByInput() {
        ConstructHelper constructHelper = Runner.constructHelper;
        CallableDeclaration methodDeclaration = ASTExtractorTest.getMethodDeclaration();
        MethodCallExpr methodCallExpr = Runner.constructHelper.ASTExtractor
                .extractAssertByLine(methodDeclaration, lineNumber);
        Input input =  Runner.constructHelper.ASTExtractor.extractInput(methodCallExpr);
        Runner runner = new RandomRunner(null);
        String absolutePath = new File(ASTExtractorTest.filePath).getAbsolutePath();
        Pair<Expression, ? extends LiteralExpr> inputMutant = runner.creatorHelper.getInputMutant(input);
        Input newInput = constructHelper.transformInput(input, inputMutant.a, inputMutant.b);
        Optional<ClassOrInterfaceDeclaration> ancestor = methodDeclaration.findAncestor(ClassOrInterfaceDeclaration.class);
        String clazzName = ancestor.get().getName().toString();
        Skeleton skeleton = Runner.constructHelper.createASkeleton(absolutePath, clazzName, input);
        assert skeleton != null;
        constructHelper.buildNewTestByInput(skeleton, newInput);
        assertNotNull(skeleton.getGeneratedMethods());
    }

    @Test
    void buildNewTestByInputs() {
        ConstructHelper constructHelper = Runner.constructHelper;
        CallableDeclaration methodDeclaration = ASTExtractorTest.getMethodDeclaration();
        MethodCallExpr methodCallExpr = Runner.constructHelper.ASTExtractor
                .extractAssertByLine(methodDeclaration, lineNumber);
        Input input =  Runner.constructHelper.ASTExtractor.extractInput(methodCallExpr);
        Runner runner = new RandomRunner(null);
        List<Pair<Expression, ? extends LiteralExpr>> inputMutants = runner.creatorHelper.getInputMutants(input);
        List<Input> newInputs = constructHelper.transformInput(input, inputMutants);
        String absolutePath = new File(ASTExtractorTest.filePath).getAbsolutePath();
        Optional<ClassOrInterfaceDeclaration> ancestor = methodDeclaration.findAncestor(ClassOrInterfaceDeclaration.class);
        String clazzName = ancestor.get().getName().toString();
        Skeleton skeleton = Runner.constructHelper.createASkeleton(absolutePath, clazzName, input);
        assert skeleton != null;
        constructHelper.buildNewTestByInputs(skeleton, newInputs);
        assertEquals(10, skeleton.getGeneratedMethods().size());
    }

    @Test
    void mutateTests() {
        String absolutePath = new File(ASTExtractorTest.filePath).getAbsolutePath();
        CompilationUnit compilationUnit = Runner.constructHelper.ASTExtractor.getCompilationUnit(absolutePath);
        String testInfos = ConfigurationProperties.getProperty("testInfos");
        String[] split = testInfos.split("#")[0].split(":")[0].split("\\.");
        Skeleton skeleton = new Skeleton(absolutePath, compilationUnit, split[split.length - 1]);
        Input input = ASTExtractorTest.getInput();
        skeleton.addInput(input);
        Runner runner = new RandomRunner(null);
        runner.mutateTests(skeleton);
        assertEquals(10, skeleton.getGeneratedMethods().size());
    }

    @Test
    void applyPatch() {
        String absolutePath = new File(ASTExtractorTest.filePath).getAbsolutePath();
        CompilationUnit compilationUnit = Runner.constructHelper.ASTExtractor.getCompilationUnit(absolutePath);
        String testInfos = ConfigurationProperties.getProperty("testInfos");
        String[] split = testInfos.split("#")[0].split(":")[0].split("\\.");
        Skeleton skeleton = new Skeleton(absolutePath, compilationUnit, split[split.length - 1]);
        Input input = ASTExtractorTest.getInput();
        skeleton.addInput(input);
        Runner runner = new RandomRunner(null);
        runner.mutateTests(skeleton);
        assertNotNull(skeleton.getGeneratedMethods());
        //        PatchValidator validator = new PatchValidator();
//        boolean res = validator.validate(projectPreparation.patches, Collections.singletonList(skeleton));
//        assertTrue(res);
    }

    @Ignore
    void getCompiledClassesForTestExecution() {
        ConstructHelper constructHelper = Runner.constructHelper;
        ASTExtractor ASTExtractor = Runner.constructHelper.ASTExtractor;
        CallableDeclaration methodDeclaration = ASTExtractorTest.getMethodDeclaration();
        MethodCallExpr methodCallExpr = Runner.constructHelper.ASTExtractor
                .extractAssertByLine(methodDeclaration, lineNumber);
        Input input =  Runner.constructHelper.ASTExtractor.extractInput(methodCallExpr);
        Runner runner = new RandomRunner(null);
        String absolutePath = new File(ASTExtractorTest.filePath).getAbsolutePath();
        Pair<Expression, ? extends LiteralExpr> inputMutant = runner.creatorHelper.getInputMutant(input);
        Input newInput = constructHelper.transformInput(input, inputMutant.a, inputMutant.b);
        Optional<ClassOrInterfaceDeclaration> ancestor = methodDeclaration.findAncestor(ClassOrInterfaceDeclaration.class);
        String clazzName = ancestor.get().getName().toString();
        Skeleton skeleton = Runner.constructHelper.createASkeleton(absolutePath, clazzName, input);
        constructHelper.buildNewTestByInput(skeleton, newInput);
//        CompilationUnit buildNewTestByInput = new ArrayList<>(compilationUnitMap.keySet()).get(0);
//        Map<Skeleton, CompilationUnit> map = new HashMap<>();
//        map.put(skeleton, buildNewTestByInput);
//        Map<String, String> javaSources = Helper.getJavaSources(map);
//        Map<String, JavaFileObject> compiledClassesForTestExecution = projectPreparation.getCompiledClassesForTestExecution(javaSources);
//        assertNotNull(compiledClassesForTestExecution);
    }
}