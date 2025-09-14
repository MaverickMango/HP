package root.execution;

import root.generation.entities.Skeleton;

import java.util.List;

public interface IPatchValidator {
    //todo 测试结果统计
    boolean validate(List<Skeleton> mutateRes);
}
