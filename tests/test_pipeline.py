"""
tests/test_pipeline.py
~~~~~~~~~~~~~~~~~~~~~~~
Tests for bangla_text_toolkit.pipeline.BanglaTextPipeline.
"""
import pytest
from bangla_text_toolkit.pipeline import BanglaTextPipeline
from bangla_text_toolkit.normalizer import BanglaTextNormalizer


class TestPipelineBasics:
      def test_empty_pipeline_is_identity(self):
                pipe = BanglaTextPipeline()
                assert pipe.run("আমি") == "আমি"

      def test_add_step_returns_self(self):
                pipe = BanglaTextPipeline()
                result = pipe.add_step(str.strip)
                assert result is pipe

      def test_method_chaining(self):
                pipe = BanglaTextPipeline()
                pipe.add_step(str.strip).add_step(str.lower)
                assert len(pipe) == 2

      def test_len_empty(self):
                assert len(BanglaTextPipeline()) == 0

      def test_len_with_steps(self):
                pipe = BanglaTextPipeline()
                pipe.add_step(str.strip).add_step(str.lower)
                assert len(pipe) == 2

      def test_repr(self):
                pipe = BanglaTextPipeline()
                assert "BanglaTextPipeline" in repr(pipe)
                assert "0" in repr(pipe)

      def test_repr_with_steps(self):
                pipe = BanglaTextPipeline()
                pipe.add_step(str.strip)
                assert "1" in repr(pipe)

      def test_non_callable_raises(self):
                with pytest.raises(TypeError, match="callable"):
                              BanglaTextPipeline().add_step("not_a_function")

            def test_non_string_input_raises(self):
                      with pytest.raises(TypeError, match="str"):
                                    BanglaTextPipeline().run(123)


class TestPipelineSteps:
      def test_single_step(self):
                pipe = BanglaTextPipeline()
                pipe.add_step(str.strip)
                assert pipe.run("  আমি  ") == "আমি"

    def test_steps_run_in_order(self):
              order = []
              pipe = BanglaTextPipeline()
              pipe.add_step(lambda t: (order.append(1) or t))
              pipe.add_step(lambda t: (order.append(2) or t))
              pipe.run("পরীক্ষা")
              assert order == [1, 2]

    def test_chained_transformations(self):
              pipe = BanglaTextPipeline()
              pipe.add_step(lambda t: t.replace("‍", ""))  # strip ZWJ
        pipe.add_step(str.strip)
        assert pipe.run("  গান‍গাই  ") == "গানগাই"

    def test_empty_string_through_pipeline(self):
              pipe = BanglaTextPipeline()
              pipe.add_step(str.strip)
              assert pipe.run("") == ""


class TestPipelineDefault:
      def test_default_has_one_step(self):
                pipe = BanglaTextPipeline.default()
                assert len(pipe) == 1

    def test_default_strips_whitespace(self):
              pipe = BanglaTextPipeline.default()
              assert pipe.run("  আমি  ") == "আমি"

    def test_default_removes_bom(self):
              pipe = BanglaTextPipeline.default()
              assert pipe.run("﻿আমি") == "আমি"

    def test_default_normalizes_curly_quotes(self):
              pipe = BanglaTextPipeline.default()
              assert pipe.run("‘hello’") == "'hello'"

    def test_default_returns_banglatext_pipeline(self):
              pipe = BanglaTextPipeline.default()
              assert isinstance(pipe, BanglaTextPipeline)


class TestPipelineWithNormalizer:
      def test_with_normalizer_step(self):
                n = BanglaTextNormalizer()
                pipe = BanglaTextPipeline()
                pipe.add_step(n.normalize)
                assert pipe.run("﻿আমি") == "আমি"

    def test_custom_step_after_normalizer(self):
              n = BanglaTextNormalizer()
              pipe = BanglaTextPipeline()
              pipe.add_step(n.normalize)
              pipe.add_step(lambda t: t.upper())
              assert pipe.run("  hello  ") == "HELLO"

    def test_digit_mode_ascii_in_pipeline(self):
              n = BanglaTextNormalizer(digit_mode="ascii")
              pipe = BanglaTextPipeline()
              pipe.add_step(n.normalize)
              result = pipe.run("০১২")
              assert result == "012"
      
