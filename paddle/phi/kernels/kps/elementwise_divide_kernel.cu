// Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "paddle/phi/backends/gpu/gpu_context.h"
#ifndef PADDLE_WITH_XPU_KP
#include "paddle/phi/common/complex.h"
#include "paddle/phi/common/float16.h"
#endif
#include "paddle/phi/core/kernel_registry.h"
#include "paddle/phi/kernels/impl/elementwise_kernel_impl.h"

namespace phi {

template <typename T, typename Context>
void DivideKernel(const Context& dev_ctx,
                  const DenseTensor& x,
                  const DenseTensor& y,
                  DenseTensor* out) {
  std::vector<const DenseTensor*> inputs;
  inputs.reserve(2);
  std::vector<DenseTensor*> outputs;
  outputs.reserve(1);
  inputs.emplace_back(&x);
  inputs.emplace_back(&y);
  outputs.emplace_back(out);
  dev_ctx.template Alloc<T>(out);
  funcs::BroadcastKernel<T>(
      dev_ctx, inputs, &outputs, funcs::DivideFunctor<T>(), -1);
}

}  // namespace phi

#ifdef PADDLE_WITH_XPU_KP
PD_REGISTER_KERNEL(divide, KPS, ALL_LAYOUT, phi::DivideKernel, float) {}
#else

using float16 = phi::dtype::float16;
using bfloat16 = phi::dtype::bfloat16;
using complex64 = ::phi::dtype::complex<float>;
using complex128 = ::phi::dtype::complex<double>;

PD_REGISTER_KERNEL(divide,
                   KPS,
                   ALL_LAYOUT,
                   phi::DivideKernel,
                   float,
                   double,
                   int,
                   int64_t,
                   float16,
                   bfloat16,
                   complex64,
                   complex128) {}

#endif
