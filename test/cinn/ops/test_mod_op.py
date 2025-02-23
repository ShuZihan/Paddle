#!/usr/bin/env python3

# Copyright (c) 2022 CINN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import numpy as np
from op_test import OpTest, OpTestTool
from op_test_helper import TestCaseHelper
import paddle
import cinn
from cinn.frontend import *
from cinn.common import *


@OpTestTool.skip_if(
    not is_compiled_with_cuda(), "x86 test will be skipped due to timeout."
)
class TestModOp(OpTest):
    def setUp(self):
        print(f"\nRunning {self.__class__.__name__}: {self.case}")
        self.prepare_inputs()

    def prepare_inputs(self):
        self.x_np = self.random(
            shape=self.case["x_shape"],
            dtype=self.case["x_dtype"],
            low=self.case["x_low"],
            high=self.case["x_high"],
        )
        self.y_np = self.random(
            shape=self.case["y_shape"],
            dtype=self.case["y_dtype"],
            low=self.case["y_low"],
            high=self.case["y_high"],
        )
        self.y_np[self.y_np == 0] = 1

    def build_paddle_program(self, target):
        x = paddle.to_tensor(self.x_np, stop_gradient=True)
        y = paddle.to_tensor(self.y_np, stop_gradient=True)
        out = paddle.mod(x, y)
        self.paddle_outputs = [out]

    def build_cinn_program(self, target):
        builder = NetBuilder("pow")
        x = builder.create_input(
            self.nptype2cinntype(self.x_np.dtype), self.x_np.shape, "x"
        )
        y = builder.create_input(
            self.nptype2cinntype(self.y_np.dtype), self.y_np.shape, "y"
        )
        out = builder.mod(x, y)

        prog = builder.build()
        res = self.get_cinn_output(
            prog, target, [x, y], [self.x_np, self.y_np], [out]
        )

        self.cinn_outputs = [res[0]]

    def test_check_results(self):
        max_relative_error = (
            self.case["max_relative_error"]
            if "max_relative_error" in self.case
            else 1e-5
        )
        self.check_outputs_and_grads(max_relative_error=max_relative_error)


class TestModOpBase(TestCaseHelper):
    inputs = [
        {
            "x_shape": [32],
            "y_shape": [32],
        },
        {
            "x_shape": [32, 64],
            "y_shape": [32, 64],
        },
        {
            "x_shape": [2, 3, 4],
            "y_shape": [2, 3, 4],
        },
        {
            "x_shape": [16, 8, 4, 2],
            "y_shape": [16, 8, 4, 2],
        },
        {
            "x_shape": [16, 8, 4, 2, 1],
            "y_shape": [16, 8, 4, 2, 1],
        },
    ]

    dtypes = [
        {
            "x_dtype": "float32",
            "y_dtype": "float32",
        },
    ]

    attrs = [
        {"x_low": -100, "x_high": 100, "y_low": -100, "y_high": 100},
    ]

    def init_attrs(self):
        self.class_name = "TestModOpBase"
        self.cls = TestModOp


class TestModOpShapeTest(TestModOpBase):
    def init_attrs(self):
        self.class_name = "TestModOpShapeTest"
        self.cls = TestModOp
        self.inputs = [
            {
                "x_shape": [32],
                "y_shape": [32],
            },
            {
                "x_shape": [32, 64],
                "y_shape": [32, 64],
            },
            {
                "x_shape": [2, 3, 4],
                "y_shape": [2, 3, 4],
            },
            {
                "x_shape": [16, 8, 4, 2],
                "y_shape": [16, 8, 4, 2],
            },
            {
                "x_shape": [16, 8, 4, 1024],
                "y_shape": [16, 8, 4, 1024],
            },
            {
                "x_shape": [16, 8, 4, 2, 1],
                "y_shape": [16, 8, 4, 2, 1],
            },
            {
                "x_shape": [1, 1, 1, 1, 1],
                "y_shape": [1, 1, 1, 1, 1],
            },
            {
                "x_shape": [1],
                "y_shape": [1],
            },
            {
                "x_shape": [1024],
                "y_shape": [1024],
            },
            {
                "x_shape": [2048],
                "y_shape": [2048],
            },
            {
                "x_shape": [32768],
                "y_shape": [32768],
            },
            {
                "x_shape": [65536],
                "y_shape": [65536],
            },
            {
                "x_shape": [131072],
                "y_shape": [131072],
            },
        ]


class TestModOpDtypeTest(TestModOpBase):
    def init_attrs(self):
        self.class_name = "TestModOpDtypeTest"
        self.cls = TestModOp
        self.dtypes = [
            {
                "x_dtype": "float16",
                "y_dtype": "float16",
                "max_relative_error": 1e-3,
            },
            {
                "x_dtype": "int32",
                "y_dtype": "int32",
            },
            {
                "x_dtype": "int64",
                "y_dtype": "int64",
            },
            {
                "x_dtype": "float32",
                "y_dtype": "float32",
            },
            {
                "x_dtype": "float64",
                "y_dtype": "float64",
            },
        ]


class TestModOpPolarityTest(TestModOpBase):
    def init_attrs(self):
        self.class_name = "TestModOpPolarityTest"
        self.cls = TestModOp
        self.attrs = [
            {"x_low": -100, "x_high": 100, "y_low": -100, "y_high": -1},
            {"x_low": -100, "x_high": 100, "y_low": 1, "y_high": 100},
        ]


class TestModOpBroadcastTest(TestModOpBase):
    def init_attrs(self):
        self.class_name = "TestModOpBroadcastTest"
        self.cls = TestModOp
        self.inputs = [
            {
                "x_shape": [32],
                "y_shape": [1],
            },
            {
                "x_shape": [1],
                "y_shape": [32],
            },
            {
                "x_shape": [1, 64],
                "y_shape": [32, 1],
            },
            {
                "x_shape": [1, 64],
                "y_shape": [32, 64],
            },
            {
                "x_shape": [32, 1],
                "y_shape": [32, 64],
            },
            {
                "x_shape": [1, 1],
                "y_shape": [32, 64],
            },
            {
                "x_shape": [1, 3, 4],
                "y_shape": [2, 3, 4],
            },
            {
                "x_shape": [1, 3, 1],
                "y_shape": [2, 3, 4],
            },
            {
                "x_shape": [1, 1, 1],
                "y_shape": [2, 3, 4],
            },
            {
                "x_shape": [2, 1, 1],
                "y_shape": [1, 3, 4],
            },
            {
                "x_shape": [1, 8, 4, 2],
                "y_shape": [16, 8, 4, 2],
            },
            {
                "x_shape": [16, 8, 1, 1],
                "y_shape": [16, 8, 4, 2],
            },
            {
                "x_shape": [1, 8, 1, 1],
                "y_shape": [16, 8, 4, 2],
            },
            {
                "x_shape": [1, 1, 1, 1],
                "y_shape": [16, 8, 4, 2],
            },
            {
                "x_shape": [1, 8, 1, 2],
                "y_shape": [16, 1, 4, 1],
            },
            {
                "x_shape": [1, 8, 4, 2, 32],
                "y_shape": [16, 8, 4, 2, 32],
            },
            {
                "x_shape": [16, 1, 1, 2, 32],
                "y_shape": [16, 8, 4, 2, 32],
            },
            {
                "x_shape": [16, 1, 4, 1, 1],
                "y_shape": [16, 8, 4, 2, 32],
            },
            {
                "x_shape": [1, 1, 1, 1, 32],
                "y_shape": [16, 8, 4, 2, 32],
            },
            {
                "x_shape": [1, 1, 1, 1, 1],
                "y_shape": [16, 8, 4, 2, 32],
            },
            {
                "x_shape": [16, 1, 4, 1, 32],
                "y_shape": [1, 8, 1, 2, 1],
            },
        ]


if __name__ == "__main__":
    TestModOpShapeTest().run()
    TestModOpDtypeTest().run()
    TestModOpPolarityTest().run()
    TestModOpBroadcastTest().run()
