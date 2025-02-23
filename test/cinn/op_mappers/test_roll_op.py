#!/usr/bin/env python3

# Copyright (c) 2023 CINN Authors. All Rights Reserved.
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
from op_mapper_test import OpMapperTest, logger
import paddle


class TestRollOp(OpMapperTest):
    def init_input_data(self):
        self.feed_data = {
            'x': np.array([1, 2, 3], dtype='float32'),
        }
        self.axis = [0]
        self.shifts = [1]

    def set_op_type(self):
        return "roll"

    def set_op_inputs(self):
        x = paddle.static.data(
            name='x',
            shape=self.feed_data['x'].shape,
            dtype=self.feed_data['x'].dtype,
        )
        return {'X': [x]}

    def set_op_attrs(self):
        return {"shifts": self.shifts, "axis": self.axis}

    def set_op_outputs(self):
        return {'Out': [str(self.feed_data['x'].dtype)]}

    def test_check_results(self):
        self.check_outputs_and_grads(all_equal=True)


class TestRollCase1(TestRollOp):
    def init_input_data(self):
        self.feed_data = {
            'x': self.random([1, 2, 3], 'float32'),
        }
        self.axis = [1]
        self.shifts = [3]


class TestRollCase2(TestRollOp):
    def init_input_data(self):
        self.feed_data = {
            'x': self.random([1], 'float32'),
        }
        self.axis = [0]
        self.shifts = [2]


class TestRollCase3(TestRollOp):
    def init_input_data(self):
        self.feed_data = {
            'x': self.random([1, 2, 3], 'float32'),
        }
        self.axis = [0, 1, 2, -1]
        self.shifts = [3, 4, 10, 3]


class TestRollCase4(TestRollOp):
    def init_input_data(self):
        self.feed_data = {
            'x': self.random([1, 2, 3], 'float32'),
        }
        self.axis = [0, 1]
        self.shifts = [3, -8]


class TestRollCase5(TestRollOp):
    def init_input_data(self):
        self.feed_data = {
            'x': self.random([1, 2, 3], 'float32'),
        }
        self.axis = [1]
        self.shifts = [121]


class TestRollCase6(TestRollOp):
    def init_input_data(self):
        self.feed_data = {
            'x': self.random([10, 2, 3], 'float32'),
        }
        self.axis = [1, 2]
        self.shifts = [121, 122]


class TestRollAxesEmpty(TestRollOp):
    def set_op_attrs(self):
        return {"shifts": self.shifts, "axis": []}


if __name__ == "__main__":
    unittest.main()
