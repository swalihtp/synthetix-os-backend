class BaseAction:
    """
    Every action must inherit this and implement execute().
    execute() always receives:
      - config: dict from WorkflowStep.config
      - context: dict shared across all steps in a WorkflowRun
    execute() always returns a dict that gets merged into context.
    """
    def execute(self, config: dict, context: dict) -> dict:
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement execute()"
        )