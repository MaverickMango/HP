package root.extraction;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.CallableDeclaration;
import com.github.javaparser.ast.expr.MethodCallExpr;
import org.junit.jupiter.api.Test;
import root.analysis.ASTExtractor;
import root.generation.entities.Input;
import root.generation.helper.PreparationTest;
import root.generation.transformation.Runner;

import static org.junit.jupiter.api.Assertions.*;

public class ASTExtractorTest extends PreparationTest{

    @Test
    void extractMethodByName() {
        CallableDeclaration extractInput = getMethodDeclaration();
        assertNotNull(extractInput);
    }

    public static CallableDeclaration getMethodDeclaration() {
        CompilationUnit compilationUnit = Runner.constructHelper.ASTExtractor.getCompilationUnit(filePath);
        CallableDeclaration extractInput = Runner.constructHelper.ASTExtractor
                .extractMethodByName(
                        compilationUnit,
                        methodName);
        return extractInput;
    }

    @Test
    void extractMethodCallByLine() {
        CompilationUnit compilationUnit = Runner.constructHelper.ASTExtractor.getCompilationUnit(filePath);
        CallableDeclaration extractInput = Runner.constructHelper.ASTExtractor
                .extractMethodByName(
                        compilationUnit,
                        methodName);
        ASTExtractor ASTExtractor = Runner.constructHelper.ASTExtractor;
        MethodCallExpr methodCallExpr = ASTExtractor.extractAssertByLine(extractInput, lineNumber);
        assertEquals(3, methodCallExpr.getArguments().size());
    }

    @Test
    void extractInput() {
        Input input = getInput();
        assertEquals("java.lang.Double", input.getType());
    }

    public static Input getInput() {
        CallableDeclaration extractInput = getMethodDeclaration();
        MethodCallExpr methodCallExpr = Runner.constructHelper.ASTExtractor
                .extractAssertByLine(extractInput, lineNumber);
        return Runner.constructHelper.ASTExtractor.extractInput(methodCallExpr);
    }
}