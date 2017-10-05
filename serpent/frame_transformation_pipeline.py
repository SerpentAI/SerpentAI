from serpent.frame_transformer import FrameTransformer


class FrameTransformationPipelineError(BaseException):
    pass


class FrameTransformationPipeline:

    def __init__(self, pipeline_string=None):
        if pipeline_string is None or not isinstance(pipeline_string, str):
            raise FrameTransformationPipelineError("A 'pipeline_string' kwarg is expected...")

        self.game_frame_transformer = FrameTransformer()
        self.pipeline = self._parse_pipeline_string(pipeline_string)

    @property
    def pipeline_operations(self):
        return {
            "RESIZE": self.game_frame_transformer.resize,
            "RESCALE": self.game_frame_transformer.rescale,
            "GRAYSCALE": self.game_frame_transformer.grayscale
        }

    def transform(self, frame=None):
        for pipeline_func, args in self.pipeline:
            if args[0] != "":
                frame = pipeline_func(frame, *args)
            else:
                frame = pipeline_func(frame)

        return frame

    def _parse_pipeline_string(self, pipeline_string):
        pipeline = list()

        string_pipeline_operations = pipeline_string.split("|")

        for string_pipeline_operation in string_pipeline_operations:
            if ":" not in string_pipeline_operation:
                string_pipeline_operation += ":"

            operation_key, args = string_pipeline_operation.split(":")

            if operation_key in self.pipeline_operations:
                pipeline.append((self.pipeline_operations[operation_key], args.split(",")))

        return pipeline
